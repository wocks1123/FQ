import asyncio
import os

from dotenv import load_dotenv
import zmq, zmq.asyncio

from FQ.FrameDecoder import FrameDecoder
from FQ.Utils import timeformat_to_seconds


load_dotenv('.fq')


class FrameReceiver:

    def __init__(self, *, video_src, start_time, end_time, fps):
        self.ctx = zmq.Context()

        self.fps = fps
        self.video_src = video_src
        self.start_time = start_time
        self.end_time = end_time

        self.host = os.environ.get("FQ_HOST")
        self.port = int(os.environ.get("FQ_REP_PORT"))
        try:
            self.sock = self.ctx.socket(zmq.REQ)
            self.sock.connect(f"tcp://{self.host}:{self.port}")
        except Exception:
            print("connection fail")

    def __iter__(self):
        start_fn = timeformat_to_seconds(self.start_time) * self.fps
        end_fn = timeformat_to_seconds(self.end_time) * self.fps
        for i in range(end_fn - start_fn):
            message = {
                "video_src": self.video_src,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "idx": i,
                "fps": self.fps
            }

            self.sock.send_json(message)
            response = self.sock.recv_json()
            if response["result"] == "fail":
                print("frame not exist...")
                continue
            else:
                body = response["body"]

                if body == "END":
                    break

                frame_num = body["frame_num"]
                time = body["time"]
                frame = FrameDecoder.Base.decode(body["frame"])
                yield frame, frame_num, time

        self.sock.close()
        self.ctx.term()


if __name__ == "__main__":
    import cv2

    start = "00:04:40"
    end = "00:04:45"
    fps = 1
    video_src = "/path/to/video.mp4"
    for i, (frame, frame_num, time) in enumerate(FrameReceiver(video_src=video_src, start_time=start, end_time=end, fps=fps)):
        cv2.imwrite(f"00{i}.jpg", frame)
