# /video 카메라 정보가 나오는것
# flask 로 서버를 열것
# cam = Util.gstrmer(width=640, height=480, fps=30, flip=0)
# cap = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)

import time
from threading import Thread

import cv2
from flask import Flask, Response

# for _ in range(120):
#     ret, frame = cap.read()
#     if not ret:
#         print(ret)
#         continue
#     cv2.imshow("frame", frame)
# cap.release()
# 위 코드를 기준으로 해서 작성
# jpg 압축 60% 해서 데이터 보내기
# 5000 번 포트로 api 열기
# 쓰레드 사용
# scp camera_api.py soda@192.168.0.34:/home/soda


# 카메라 열기
cam = Util.gstrmer(width=640, height=480, fps=30, flip=0)
cap = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    raise RuntimeError("Camera open failed")

app = Flask(__name__)

latest_frame = None


def capture_loop():
    global latest_frame

    while True:
        ret, frame = cap.read()

        if ret:
            latest_frame = frame

        time.sleep(0.01)


def encode_jpeg(frame, quality=80):
    ret, jpeg = cv2.imencode(
        ".jpg",
        frame,
        [cv2.IMWRITE_JPEG_QUALITY, quality]
    )

    if not ret:
        return None

    return jpeg.tobytes()


@app.route("/")
def index():
    return """
    <html>
        <head>
            <title>Jetson Camera API</title>
        </head>
        <body>
            <h2>Jetson Camera API</h2>

            <p>실시간 영상</p>
            <img src="/video" width="640" height="480">

            <hr>

            <p>API 주소</p>
            <ul>
                <li><a href="/video">/video</a> : MJPEG 실시간 스트림</li>
                <li><a href="/snapshot.jpg">/snapshot.jpg</a> : 현재 프레임 1장</li>
            </ul>
        </body>
    </html>
    """


@app.route("/video")
def video():
    def generate():
        while True:
            if latest_frame is None:
                time.sleep(0.05)
                continue

            jpg = encode_jpeg(latest_frame, quality=80)

            if jpg is None:
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                jpg +
                b"\r\n"
            )

            time.sleep(0.03)

    return Response(
        generate(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


@app.route("/snapshot.jpg")
def snapshot():
    if latest_frame is None:
        return "No frame", 503

    jpg = encode_jpeg(latest_frame, quality=90)

    return Response(
        jpg,
        mimetype="image/jpeg"
    )


def run_server():
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )


# 카메라 캡처 스레드 시작
capture_thread = Thread(target=capture_loop)
capture_thread.daemon = True
capture_thread.start()

# Flask 서버 스레드 시작
server_thread = Thread(target=run_server)
server_thread.daemon = True
server_thread.start()

print("Camera API server started")
print("브라우저에서 http://젯슨IP:5000 으로 접속")