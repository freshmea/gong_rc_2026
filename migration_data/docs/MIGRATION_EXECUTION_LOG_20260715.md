# Xavier NX 마이그레이션 실행 로그 (2026-07-15)

대상: `soda@192.168.0.34`  
원칙: 기능 동작 우선, JetPack 5.1.6/L4T 35.6.4와 호환되는 범위에서 가능한 최신 버전 사용  
로그 위치: `migration_data/docs/MIGRATION_EXECUTION_LOG_20260715.md`

## 기록 규칙

각 단계가 끝날 때 다음 내용을 누적한다.

- 실행한 작업과 주요 명령
- 실제 결과와 버전
- 발생한 문제, 원인, 해결 방법
- 기능 검증 결과
- 남은 작업과 수동 안전 확인 항목

비밀번호, 토큰, API 키는 기록하지 않는다. 모터, 조향, GPIO 출력은 차체 고정과 비상 정지 준비 전 자동 실행하지 않는다.

## 0. 전일 작업 인계 상태

### 완료

- Xavier NX Developer Kit(P3668/P3509)을 JetPack 5.1.6 기반으로 클린 플래시했다.
- 현재 OS는 Ubuntu 20.04.6 LTS, Jetson Linux는 L4T R35.6.4, 커널은 `5.10.216-tegra`다.
- 사용자 `soda`, SSH, `iptime5G` 자동 연결을 구성했다.
- Wi-Fi 주소 `192.168.0.34`와 USB RNDIS 주소 `192.168.55.1`에서 SSH 동작을 확인했다.
- `nvfancontrol` 기본 프로필을 NVIDIA 제공 `cool`로 변경했다. 설정 원본은 `/etc/nvpower/nvfancontrol/nvfancontrol_p3668.conf.before-cool`에 보존했다.

### 주의사항

- USB 장치를 `usbipd attach --auto-attach`로 WSL에 넘기면 Windows의 RNDIS 어댑터가 생겼다가 사라질 수 있다. 일반 운용 시 Jetson USB 복합 장치는 Windows에 두고, 플래시 작업 때만 WSL에 연결한다.
- 새 rootfs에는 아직 전체 JetPack 개발 구성요소와 수업 개발 도구가 설치되지 않았다.

## 1. 2026-07-15 기준선 재점검

### 저장소 및 백업

- `migration_data`에 이전 시스템 설정, 수업 코드, ROS/LiDAR 소스, vendor Python 소스와 비파괴 테스트가 보존되어 있다.
- 정적 검증 결과: 노트북 46개, 하드웨어 관련 노트북 25개, 노트북 오류 0개, Python 파일 19개, 구문 경고 0개.
- Git 작업 트리에는 사용자 파일 `data/7_14_간담회 참가 체크 리스트.md`와 `migration_data/docs/flashingjetsonnx.jpg`가 추적되지 않은 상태로 존재한다. 이 파일들은 변경하지 않는다.

### 새 Jetson 실측

| 항목 | 결과 |
|---|---|
| OS | Ubuntu 20.04.6 LTS |
| L4T | R35.6.4 |
| Kernel | 5.10.216-tegra, aarch64 |
| RootFS | 57 GiB 중 약 49 GiB 가용 |
| Python | 3.8.10 |
| JetPack meta package | 미설치 |
| nvidia-l4t-core | 35.6.4-20260126234748 |
| SSH / NetworkManager / nvargus-daemon / nvfancontrol | active |
| I2C | `/dev/i2c-0`~`10`, `101` 확인 |
| Camera | `/dev/video0` 확인 |
| LiDAR USB | CP210x `10c4:ea60`, `/dev/ttyUSB0` 확인 |
| 사용자 그룹 | sudo, audio, video, i2c, gpio 포함; dialout 추가 필요 |
| pip/Jupyter/tmux/zsh/ROS | 미설치 |

### 진행 중 발생 사항

- Windows에서 WSL을 동시에 여러 번 호출했을 때 `Wsl/Service/E_ACCESSDENIED`가 발생했다. 저장소나 Jetson 문제는 아니며 WSL 호출을 순차 실행하고 필요한 경우 관리자 권한으로 실행해 해결했다.
- Windows PowerShell, WSL bash, 원격 SSH 명령의 따옴표가 겹친 명령은 Windows에서 먼저 해석되어 실패했다. 이후 긴 명령을 작은 단계로 분리했다.

## 2. 실행 계획

1. 백업 SHA-256 무결성 확인 및 새 장치로 복사
2. JetPack 개발 구성요소와 기본 시스템 도구 설치
3. 사용자 그룹, udev, 셸, tmux, Jupyter 서비스 복원
4. Python 가상환경과 수업/AI 패키지 설치
5. Ubuntu 20.04 arm64 공식 바이너리 기반 ROS 2 Foxy 네이티브 구성
6. I2C, 오디오, 카메라, LiDAR, GPIO/CAN 비파괴 검사
7. 수업 코드 정적/기능 테스트 및 결과 비교
8. 재부팅 후 서비스·네트워크·팬·장치 지속성 최종 확인

### ROS 2 배포판 결정

- 사용자 결정에 따라 ROS 2 Humble 컨테이너 계획을 취소하고 ROS 2 Foxy를 호스트에 네이티브 설치한다.
- ROS 공식 문서에서 Foxy는 Ubuntu 20.04 Focal의 `amd64`와 `arm64`를 Tier 1 대상으로 제공하며 Debian 패키지 설치를 권장한다.
- Foxy는 현재 EOL이므로 보안 지원이 계속되는 최신 배포판으로 취급하지 않는다. 이 장치에서는 Ubuntu 20.04와 기존 수업 호환성을 위한 고정 환경으로 사용한다.
- 설치 후 `ros2 doctor`, C++ talker/Python listener 통신, colcon 빌드를 검증한다.

## 3. 단계별 실행 기록

후속 작업 결과를 이 아래에 계속 추가한다.

### 3.1 백업 무결성 및 정적 검사

- 노트북 46개와 Python 파일 19개의 정적 검사가 통과했다.
- `sha256sum -c SHA256SUMS`에서 ROS 소스 복사본 내부의 `.git/index` 한 파일만 불일치했다.
- 해당 중첩 Git 저장소는 `git status --short`가 비어 있고 `git fsck --no-dangling`이 통과했다. 실제 ROS 소스 손상이 아니라 Git 인덱스 재생성에 따른 메타데이터 변화로 판정했다.
- 원본 `artifacts/ros_lidar_sources.tar.gz`는 별도 보존되어 있다.

### 3.2 JetPack 5.1.6 전체 구성요소 설치

- NVIDIA apt 저장소에서 `nvidia-jetpack 5.1.6-b5` arm64 후보를 확인했다.
- 첫 설치 호출은 로컬 명령 제한시간을 1초로 잘못 지정해 SSH만 종료됐다. 원격 `apt-get`/`dpkg` 프로세스와 패키지 변경이 없음을 확인한 뒤 재실행했다.
- 재실행은 약 18분 소요됐고 성공했다. 3,492 MB를 내려받아 약 9,201 MB를 추가 사용했다.
- 설치 완료 버전:
  - CUDA compiler 11.4.315
  - cuDNN 8.6.0.166
  - TensorRT 8.5.2.2
  - VPI 2.4.8
  - NVIDIA OpenCV 4.5.4
  - Docker 26.1.3 및 NVIDIA container runtime
- `dpkg --audit` 결과는 비어 있으며 docker, containerd, nvfancontrol, nvargus-daemon은 모두 active다.
- Python 3.8에서 `cv2`, `tensorrt`, `vpi` import가 성공했다.
- OpenCV `cv2.cuda.getCudaEnabledDeviceCount()`는 0을 반환했다. JetPack 제공 OpenCV CUDA 모듈 구성과 별개로 PyTorch GPU 검증을 추가한다.
- VPI import 시 PVA unavailable 경고가 발생했다. 설치 후 최종 재부팅 뒤 다시 확인한다.
- 설치 후 rootfs 여유 공간은 약 36 GiB다.

### 3.3 기본 개발환경과 ROS 2 Foxy

- `migration_data/scripts/post_flash_setup.sh`를 추가하고 Jetson에서 실행했다.
- 설치 항목: build tools, git/rsync/jq/tmux/zsh, I2C/ALSA/V4L2/FFmpeg, Python 개발 도구, ROS 개발 도구.
- ROS 공식 저장소를 keyring 방식으로 등록하고 Ubuntu 20.04 arm64용 `ros-foxy-desktop`을 설치했다.
- 첫 스크립트 실행은 ROS 저장소 등록 전 `python3-colcon-common-extensions`를 요청해 중단됐다. colcon 설치를 저장소 등록 뒤로 이동했다.
- 두 번째 실행 중 Ubuntu 저장소의 구버전 `python3-catkin-pkg`, `python3-rospkg`, `python3-rosdistro`와 ROS 저장소의 `*-modules` 패키지가 동일 파일을 제공해 dpkg 충돌이 발생했다.
- 구버전 3개 패키지만 dpkg 등록에서 제거하고 `apt-get --fix-broken install`로 736개 미구성 패키지를 정상 구성했다.
- 재현 스크립트에서는 `python3-rosdep`도 ROS 저장소 등록 후 설치하도록 옮겨 같은 충돌을 방지했다.
- 최종 설치 버전:
  - `ros-foxy-desktop 0.9.2-1focal.20230606.054757`
  - `python3-colcon-common-extensions 0.3.0-100`
  - `python3-rosdep 0.26.0-1`
- rosdep Foxy 인덱스 갱신에 성공했다.
- `soda` 사용자는 `dialout`, `audio`, `video`, `i2c`, `gpio`, `docker` 그룹에 포함됐다.
- LiDAR udev 규칙은 `0660 root:dialout`과 `/dev/rplidar -> ttyUSB0`를 생성한다.
- `migration_data/tests/test_ros2_foxy.sh`를 추가했다. 첫 버전은 `set -u`와 Foxy setup 스크립트가 충돌해 테스트가 중단됐고 setup 이후 strict mode를 켜도록 수정했다.
- 최종 DDS 검사: C++ talker가 발행한 `Hello World`를 Python listener가 수신해 `ROS2_DDS_MESSAGE_TEST=PASS`.
- 현재 rootfs 여유 공간은 약 33 GiB다.

### 3.4 Python 3.8 가상환경과 JupyterLab

- `/home/soda/venvs/gong-rc`를 `--system-site-packages`로 생성해 JetPack의 TensorRT, VPI, OpenCV Python 모듈을 함께 사용하도록 했다.
- Python 3.8에서 호환되는 범위의 최신 패키지를 설치했다. 주요 버전은 JupyterLab 4.3.8, Notebook 7.3.3, NumPy 1.23.5, SciPy 1.10.1, Pandas 2.0.3, scikit-learn 1.3.2, ONNX 1.16.2다. NumPy는 TensorFlow 2.12 호환 범위에 맞췄다.
- ARM64에서 SciPy/scikit-learn 뒤에 OpenCV를 import하면 static TLS 오류가 발생했다. Jupyter systemd 서비스에 `LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libGLdispatch.so.0:/usr/lib/aarch64-linux-gnu/libgomp.so.1`을 설정한 뒤 OpenCV와 YOLO import가 통과했다.
- 사용자 승인에 따라 Jupyter를 `0.0.0.0:8888`에 공개했다. WSL에서 `http://192.168.0.34:8888/lab` 요청 시 로그인 페이지로 `302` 응답하는 것을 확인했다.
- 설정 파일 갱신 뒤 `systemctl enable --now`만 실행하면 기존 프로세스가 재시작되지 않는 문제가 있어 설치 스크립트를 `enable` 후 `restart`하도록 수정했다.
- Jupyter 비밀번호는 Argon2 해시만 설정 파일에 저장하며 원문은 문서와 스크립트에 기록하지 않는다.

### 3.5 POP 소스 패키지화와 설치

- 원본은 `autocar/pop`에만 있고 setup.py, wheel, deb가 없었다. 원본 크기는 약 151MB이며 포함된 `libssd_tensorrt.so`와 `LiDAR/_rplidar.so`는 ARM aarch64 ELF임을 확인했다.
- 최신 Adafruit Blinka가 `board` import 중 GPIO 모드를 먼저 설정해 구형 POP의 무조건적인 `GPIO.setmode(GPIO.BCM)`이 실패했다. 기존 모드가 BCM이 아니면 `GPIO.cleanup()` 후 BCM을 설정하는 최소 호환 패치를 `autocar/pop/__init__.py`에 적용했다.
- `migration_data/scripts/build_pop_deb.sh`를 추가해 소스, 모델, 네이티브 라이브러리를 포함한 ARM64 Debian 패키지를 생성한다. 캐시와 pyc는 제외하며 설치 권한은 디렉터리 0755, 파일 0644로 정규화한다.
- 첫 의존성 스크립트는 Ubuntu 20.04에 없는 `python3-spidev`를 요청해 중단됐다. `python3-smbus`는 apt, `spidev`는 PyPI 빌드로 분리했다.
- 패키지 0.1.0은 `python3-rpi.gpio`를 의존해 NVIDIA의 `python3-jetson-gpio`와 파일 충돌이 발생했다. 반설치 패키지를 제거하고 `apt-get --fix-broken install`로 dpkg 상태를 복구한 뒤 의존성을 `python3-jetson-gpio`로 교체했다.
- 이전 시험 버전에서 유지된 0750 디렉터리 권한 때문에 Python이 POP를 namespace 패키지로 해석했다. 0.1.3의 postinst에서 `chmod -R a+rX`를 실행해 신규 설치와 업그레이드 모두 보정하도록 했다.
- 최종 산출물: `migration_data/packages/gong-rc-pop_0.1.3+20260715_arm64.deb`, SHA-256 `a759902999b248bb0ecbe6d965326d79d98611c0d0d7479b611e4dd2fa55741a`.
- Jetson 설치 상태는 `install ok installed`, 버전 `0.1.3+20260715`이며 `dpkg --audit` 출력은 없다.
- 가상환경 검증 결과 `POP_IMPORT=PASS`, 로드 경로 `/usr/lib/python3/dist-packages/pop/__init__.py`, `POP_CATEGORY=6`, Camera/Audio/PixelDisplay/checkI2C 심볼이 모두 존재했다. 테스트는 액추에이터를 구동하지 않았다.

### 3.6 POP AI 의존성과 수업 코드 검증

- `pop.Pilot`의 PyTorch/torchvision/TensorRT, `pop.Util`의 librosa/TensorFlow, `pop.AI.DNN/CNN`의 TensorFlow/Keras, `Pilot.Object_Follow`의 yolov4.tf 의존성을 소스에서 확인했다.
- NVIDIA PyTorch `2.1.0a0+41361538.nv23.06`, torchvision 0.16.0, NVIDIA TensorFlow 2.12.0, librosa 0.10.2.post1, yolov4 2.1.0, websock 1.0.4를 설치했다.
- pip의 aarch64 h5py 소스 빌드 실패는 Ubuntu `python3-h5py 2.10.0`으로 해결했다. `Pilot.Data_Collector` import 시 필요한 숨은 websock 의존성도 설치기에 추가했다.
- PyTorch와 TensorFlow의 GPU 테스트를 같은 Python 프로세스에서 실행하면 cuDNN 메모리 할당 충돌이 발생하므로 독립 프로세스 테스트로 분리했다.
- 최종 PyTorch CUDA CNN, torchvision AlexNet, TensorFlow GPU matmul, `pop.AI.DNN`, `pop.AI.CNN`, 실제 POP `yolov4-tiny.weights` 추론이 모두 PASS다.
- YOLOv4-tiny 추론 중 GPU 메모리 allocator 경고가 있어 memory growth, 배치 1, 작은 입력, 불필요한 Jupyter 커널 종료를 운용 원칙으로 기록했다.
- torchvision의 선택 기능 `torchvision.io.image`는 NVIDIA 사전 릴리스 PyTorch와 ABI 경고가 남지만 수업에서 쓰는 PIL/ImageFolder/models/transforms/AlexNet 경로는 정상이다.
- AI 설치기를 포함한 새 산출물은 `migration_data/packages/gong-rc-pop_0.2.0+20260715_arm64.deb`, SHA-256 `f44f1de215b75ae9bebf030fedd8daf984ec98353eebd0c04d06c0b4bdfe2f1e`다.
- Jetson 설치 상태는 `install ok installed`, 버전 `0.2.0+20260715`, Jupyter는 새 preload 설정으로 active, `dpkg --audit` 출력은 없다.
- 상세 기록: `migration_data/docs/POP_AI_STACK_VALIDATION_20260715.md`.
