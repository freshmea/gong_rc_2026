# 수업 및 정상 사용 코드 인덱스

원본 아카이브: `artifacts/class_notebooks_and_code.tar.gz`  
추출 위치: `artifacts/class_notebooks_and_code/`

## 2026 수업 순서

- `a01_test` ~ `a03_haar_cascade`: 카메라, 윤곽, Haar cascade
- `a04_sound_blocking` ~ `a10_googleAssistance`: 블로킹/논블로킹 오디오, tone, 녹음, 재생, gTTS, 음성 도우미
- `a11_lidar`: RPLidar
- `a12_led`, `a13_8_led`: GPIO/LED
- `a14_linear_regresstion` ~ `a20_cnn`: ML/DL 기초
- `a21_dqn`, `a22_cartpole`: 강화학습
- `a23_tensorflow` ~ `a28_v2_dnn`: TensorFlow 1/2 스타일 비교와 신경망
- `a29_wheel_alignment`: 조향 교정
- `a30_car_balancing`: 차량 균형/제어
- `a31_collision_avoid`: 충돌 회피

## 추가 정상 사용 자료

- `Audio.ipynb`, `Tone.ipynb`, `non_block_tone.*`
- `CV.ipynb/.py`, `CV2.ipynb/.py`
- `face_tracking.*`, `mini_project.*`
- `AIoT_AutoCar_Code.ipynb`
- `AIoT AutoCar Prime Board Test*.ipynb`
- `autocar_module_test.ipynb`
- `camera_api.py`

## ROS/LiDAR

`artifacts/ros_lidar_sources/catkin_ws/src/RPLidar_Hector_SLAM/`에 다음이 있다.

- `rplidar_ros/launch/rplidar.launch`
- `rplidar_ros/launch/test_rplidar.launch`
- `rplidar_ros/launch/view_rplidar.launch`
- `rplidar_ros/rviz/rplidar.rviz`
- Hector mapping, map server, geotiff, trajectory, IMU 도구 및 launch/rviz 설정

## 이식 시 주의

“정상 사용했던 코드”라는 사실은 Python 3.8/Noetic/JetPack 5에서 무수정 동작을 보장하지 않는다. 특히 TensorFlow 2.2 wheel, GPIO pin mapping, pop vendor module, OpenCV camera pipeline, ROS Python 2 코드는 새 환경에 맞게 포팅해야 한다.

검증 스크립트는 노트북 46개와 Python 파일 19개를 실행하지 않고 파싱했으며 구문 경고는 0개였다. 하드웨어 관련 노트북 25개는 반드시 단계별 현장 시험을 거친다.
