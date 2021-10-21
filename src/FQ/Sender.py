import argparse
import asyncio
from contextlib import suppress
import curses
import os

import cv2
from dotenv import load_dotenv
import zmq, zmq.asyncio

from FQ.FrameDecoder import FrameDecoder
from FQ.Utils import to_hhmmssfff


load_dotenv('.fq')


class FrameSender:

    def __init__(self, video_sources, stdscr=None):
        self.stdscr = stdscr

        self.video_sources = video_sources
        self.video_indice = {v: i + 2 for i, v in enumerate(video_sources)}

        self.ctx = zmq.asyncio.Context()

        self.host = os.environ.get("FQ_HOST")
        self.sub_port = int(os.environ.get("FQ_SUB_PORT"))
        self.rep_port = int(os.environ.get("FS_REP_PORT"))

        self.loop = asyncio.get_event_loop()

        try:
            self.sock = self.ctx.socket(zmq.PUB)
            self.sock.setsockopt(zmq.LINGER, 1)
            self.sock.connect(f"tcp://{self.host}:{self.sub_port}")

            self.rep_sock = self.ctx.socket(zmq.REP)
            self.rep_sock.bind(f"tcp://*:{self.rep_port}")
        except OSError:
            print("connection fail")
            exit(1)

    async def run(self):
        self.stdscr.addstr(0, 0, "Sending...")
        result = await asyncio.gather(*[self.send_frame(vs) for vs in self.video_sources])
        with suppress(asyncio.CancelledError):
            while True:
                await asyncio.sleep(0.01)

    async def send_frame(self, video_src):
        frame_num = 0
        cap = cv2.VideoCapture(video_src)

        w = int(round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)))
        h = int(round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fps = cap.get(cv2.CAP_PROP_FPS)

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            encoded_frame = FrameDecoder.Base.encode(frame)
            data = {
                "video_src": video_src,
                "w": w,
                "h": h,
                "fps": fps,
                "frame_num": frame_num,
                "frame": encoded_frame,
                "time": to_hhmmssfff(frame_num / fps)
            }

            msg = f"{video_src}({data['w']}x{data['h']})(fps:{round(data['fps'], 2)}) : {data['time']}({data['frame_num']})"
            self.stdscr.addstr(self.video_indice[video_src], 0, msg)
            self.stdscr.refresh()
            await self.sock.send_json(data)
            frame_num += 1
            await asyncio.sleep(0.0001)

    def close(self):
        self.ctx.term()


def curmain(stdscr, video_sources):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    fs = FrameSender(video_sources, stdscr)
    try:
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(fs.run())
    except KeyboardInterrupt:
        print("exit")


def run_sender(video_sources):
    video_sources = video_sources.replace(" ", "").split(",")
    curses.wrapper(curmain, video_sources)
