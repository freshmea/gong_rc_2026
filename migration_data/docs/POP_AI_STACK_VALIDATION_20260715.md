# POP AI 스택 설치 및 검증 기록 — 2026-07-15

## 결론

PyTorch가 없으면 `pop.Pilot` import 단계에서 실패하므로 Pilot 기반 CNN과
AlexNet 수업을 진행할 수 없다. TensorFlow가 없으면 `pop.Util`의
`tensorflow.one_hot`과 `pop.AI.DNN/CNN`을 사용할 수 없다. POP의
YOLOv4-tiny 경로는 `yolov4.tf`를 사용하므로 TensorFlow가 별도로 필요하다.

세 경로를 Jetson Xavier NX에서 독립 프로세스로 실행해 모두 통과했다.

## 설치 버전

- Python 3.8 가상환경: `/home/soda/venvs/gong-rc`
- NumPy 1.23.5
- NVIDIA PyTorch `2.1.0a0+41361538.nv23.06`
- torchvision 0.16.0
- NVIDIA TensorFlow 2.12.0 (`2.12.0+nv23.6` 배포본)
- librosa 0.10.2.post1
- yolov4 2.1.0
- websock 1.0.4
- h5py 2.10.0 (Ubuntu arm64 `python3-h5py`)
- POP Debian 패키지 `gong-rc-pop 0.2.0+20260715`

## 발견한 의존성

- `pop.Pilot`는 모듈 로딩 시 `torch`, `torchvision`, `tensorrt`를 import한다.
- `Pilot.Data_Collector`의 클래스 속성 초기화가 AutoCar와 joystick을 만들기
  때문에 `websock.WebSocketServer`도 import 시점에 필요하다.
- `pop.Util`은 `librosa`와 TensorFlow의 `one_hot`을 import한다.
- `pop.AI.DNN`과 `pop.AI.CNN`은 TensorFlow/Keras 모델이다.
- `Pilot.Object_Follow`의 POP category 4/5/6 경로는 `yolov4.tf.YOLOv4`,
  `model/yolov4-tiny/coco.names`, `yolov4-tiny.weights`를 사용한다.

## 설치 중 발생한 사항

- TensorFlow 2.12의 요구 조건 때문에 NumPy를 1.24.4에서 1.23.5로 낮췄다.
- pip가 aarch64 h5py를 소스에서 빌드하다 실패하고 장시간 소요됐다.
  JetPack/Ubuntu와 호환되는 `python3-h5py`를 apt로 설치해 해결했다.
- SciPy/OpenCV/YOLO import 순서에서 ARM64 static TLS 오류가 발생했다.
  Jupyter 서비스와 검증 명령에 다음 설정을 적용했다.

  `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1`

- PyTorch와 TensorFlow를 한 Python 프로세스에서 연속 GPU 실행하면 cuDNN
  handle 할당이 실패했다. 수업 및 검증에서는 두 프레임워크의 커널 또는
  프로세스를 분리해야 한다.

## 검증 결과

### PyTorch / Pilot

- `pop.Pilot` import: PASS
- CUDA CNN forward: PASS, 출력 `(1, 4, 1, 1)`, 장치 `cuda:0`
- torchvision AlexNet 생성: PASS, 출력 클래스 1000
- 테스트: `migration_data/tests/test_pop_pytorch.py`

### TensorFlow / Util / DNN / CNN

- TensorFlow GPU 인식: PASS, GPU 1개
- `pop.Util` import: PASS
- TensorFlow 행렬 곱: PASS
- `pop.AI.DNN` forward: PASS, 출력 `(1, 1)`
- `pop.AI.CNN` forward: PASS, 출력 `(1, 2)`
- 테스트: `migration_data/tests/test_pop_tensorflow.py`

### YOLOv4-tiny

- 패키지의 COCO 클래스와 실제 `yolov4-tiny.weights` 로딩: PASS
- 224x224 blank frame 추론: PASS, 반환 detection 1개
- 테스트: `migration_data/tests/test_pop_yolov4_tiny.py`

## 알려진 제한과 운용 지침

- PyPI aarch64 torchvision 0.16.0의 선택 기능 `torchvision.io.image`는 NVIDIA
  사전 릴리스 PyTorch와 ABI 경고가 있다. 현재 POP 수업에서 사용하는
  PIL, ImageFolder, models, transforms, AlexNet 경로는 정상 검증됐다.
- YOLOv4-tiny는 추론에 성공했지만 GPU 메모리 allocator 경고가 발생했다.
  TensorFlow memory growth를 유지하고 배치 1, 작은 입력 크기, 불필요한
  Jupyter 커널 종료를 권장한다.
- `pop.Pilot.Data_Collector`가 import 시 하드웨어 객체를 생성하는 구조는
  향후 지연 초기화로 개선할 수 있지만, 이번 기능 우선 마이그레이션에서는
  원본 동작을 보존하고 의존성을 설치했다.

## 재현 파일

- 설치기: `migration_data/scripts/install_pop_ai_dependencies.sh`
- Debian 빌드: `migration_data/scripts/build_pop_deb.sh`
- 산출물: `migration_data/packages/gong-rc-pop_0.2.0+20260715_arm64.deb`
- SHA-256: `f44f1de215b75ae9bebf030fedd8daf984ec98353eebd0c04d06c0b4bdfe2f1e`
