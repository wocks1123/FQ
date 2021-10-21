import base64
import zlib

import cv2
import numpy as np


class FrameDecoder:

    class Base:
        @classmethod
        def encode(cls, img):
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 100]
            result, encoded_img = cv2.imencode('.jpg', img, encode_param)
            data = np.array(encoded_img)
            compressed_data = zlib.compress(data, -1)
            string_data = base64.b64encode(compressed_data).decode("ascii")
            return string_data

        @classmethod
        def decode(cls, data):
            decoded_data = base64.b64decode(data.encode("ascii"))
            decompressed_data = zlib.decompress(decoded_data)
            nparr = np.frombuffer(decompressed_data, np.uint8)
            img = cv2.imdecode(nparr, 1)
            return img
