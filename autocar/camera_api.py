# /video 카메라 정보가 나오는것
# flask 로 서버를 열것
# cam = Util.gstrmer(width=640, height=480, fps=30, flip=0)
# cap = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)

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