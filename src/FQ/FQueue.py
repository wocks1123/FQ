from dotenv import load_dotenv
import zmq, zmq.asyncio

import asyncio
from contextlib import suppress
import os
import curses
from curses import wrapper
from queue import Queue

from FQ.Utils import load_config, timeformat_to_seconds


class FrameQueue:
    MAX_SIZE = 9000

    def __init__(self, stdscr=None):
        load_config()

        self.stdscr = stdscr
        self.ctx = zmq.asyncio.Context()

        self.sub_port = int(os.environ.get("FQ_SUB_PORT"))
        self.rep_port = int(os.environ.get("FQ_REP_PORT"))

        self.sub_sock = self.ctx.socket(zmq.SUB)
        self.sub_sock.setsockopt_string(zmq.SUBSCRIBE, "")
        self.sub_sock.bind(f"tcp://*:{self.sub_port}")

        self.rep_sock = self.ctx.socket(zmq.REP)
        self.rep_sock.bind(f"tcp://*:{self.rep_port}")

        self.frame_queue = dict()

        if self.stdscr:
            self.stdscr.addstr(0, 0, "Queue...")
            self.stdscr.refresh()

    async def collect(self):
        with suppress(asyncio.CancelledError):
            while True:
                data = await self.sub_sock.recv_json()

                if not data:
                    break

                video_src = data.get("video_src")
                w = data.get("w")
                h = data.get("h")
                fps = data.get("fps")
                frame_num = data.get("frame_num")
                frame = data.get("frame")
                time = data.get("time")

                if video_src not in self.frame_queue:
                    self.frame_queue[video_src] = Queue(FrameQueue.MAX_SIZE)
                if self.frame_queue[video_src].qsize() == FrameQueue.MAX_SIZE:
                    self.frame_queue[video_src].get()
                self.frame_queue[video_src].put({
                    "video_src": video_src,
                    "w": w,
                    "h": h,
                    "fps": fps,
                    "frame_num": frame_num,
                    "frame": frame,
                    "time": time
                })
                # print("self.", self.frame_queue)
                #
                # #########################################################
                # print("\033c")
                # print("Queue...")
                # for src, que in self.frame_queue.items():
                #     print(f"{src}: {que.queue[0]['frame_num']} ~ {que.queue[-1]['frame_num']}({que.qsize()}frames)")
                if self.stdscr:
                    for i, (src, que) in enumerate(self.frame_queue.items()):
                        msg = f"{src}({que.qsize()}frames): {que.queue[0]['time']}({que.queue[0]['frame_num']}) ~ {que.queue[-1]['time']}({que.queue[-1]['frame_num']})"
                        self.stdscr.addstr(i + 2, 0, msg)

                    self.stdscr.refresh()

        self.sub_sock.close()

    async def send_frame(self):
        while True:
            message = await self.rep_sock.recv_json()

            video_src = message["video_src"]
            start_time = message["start_time"]
            end_time = message["end_time"]
            idx = message["idx"]
            extract_fps = message["fps"]

            if video_src not in self.frame_queue:
                response = {
                    "result": "fail",
                    "body": "frame is not exist in buffer..."
                }
                self.rep_sock.send_json(response)
                continue

            fps = self.frame_queue[video_src].queue[0]['fps']
            start_fn = round(timeformat_to_seconds(start_time) * fps)
            end_fn = timeformat_to_seconds(end_time) * fps

            v = idx * max(round(fps / extract_fps), 1)

            req_fn = start_fn + v
            flag = False
            for frame_info in self.frame_queue[video_src].queue:
                frame_num = frame_info.get("frame_num")
                frame = frame_info.get("frame")
                time = frame_info.get("time")
                if req_fn == frame_num:
                    response = {
                        "result": "succ",
                        "body": {
                            "frame": frame,
                            "frame_num": frame_num,
                            "time": time,
                        }
                    }
                    self.rep_sock.send_json(response)
                    flag = True
                    break
            if not flag:
                response = {
                    "result": "fail",
                    "body": "frame is not exist in buffer..."
                }
                self.rep_sock.send_json(response)

    async def run(self):
        loop = asyncio.get_event_loop()
        loop.create_task(self.collect())
        loop.create_task(self.send_frame())
        with suppress(asyncio.CancelledError):
            if self.stdscr:
                self.stdscr.addstr(0, 0, "Queue")
            while True:
                await asyncio.sleep(0.1)


def curmain(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)

    try:
        # asyncio.run(main())
        fq = FrameQueue(stdscr)
        loop = asyncio.get_event_loop()
        result = loop.run_until_complete(fq.run())
    except KeyboardInterrupt:
        print("exit")


def run_queue():
    wrapper(curmain)


if __name__ == "__main__":
    wrapper(curmain)
