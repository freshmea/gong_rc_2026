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
