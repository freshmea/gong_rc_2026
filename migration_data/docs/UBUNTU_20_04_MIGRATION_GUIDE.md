# Xavier NX Ubuntu 20.04 마이그레이션 가이드

## 결론

이 Xavier NX는 일반 Ubuntu의 `do-release-upgrade`로 올리지 말고 JetPack 5.1.6 / Jetson Linux 35.6.4를 새로 플래시하는 것이 기준 경로다. NVIDIA 문서상 이 조합은 Linux 5.10과 Ubuntu 20.04 rootfs를 제공하고 Xavier NX Developer Kit을 지원한다.

- [NVIDIA JetPack 5.1.6](https://developer.nvidia.com/embedded/jetpack-sdk-516)
- [Jetson Linux 35.6.4 release notes](https://docs.nvidia.com/jetson/archives/r35.6.4/ReleaseNotes/Jetson_Linux_Release_Notes_r35.6.4.pdf)

처음 JetPack 5.x를 쓰는 Xavier NX Developer Kit은 SD 이미지 부팅 전에 QSPI 업데이트가 필요하다. SDK Manager 플래시는 QSPI까지 처리할 수 있다. 보드 SKU와 저장장치가 microSD인지 eMMC인지 반드시 먼저 확인한다.

주의: NVIDIA는 JetPack 5 지원 종료를 2026년 3분기로 예고했다. 수업 호환성을 위해 20.04가 꼭 필요하면 유효한 선택이지만, 장기 신규 시스템이면 Orin + JetPack 6/Ubuntu 22.04 또는 더 최신 플랫폼도 함께 평가한다.

## ROS 선택

Ubuntu 20.04의 자연스러운 ROS 1 조합은 Noetic이다. 현재 Melodic workspace는 Noetic/Python 3로 포팅한다.

ROS 2 Humble의 기본 대상은 Ubuntu 22.04다. 따라서 “Ubuntu 20.04로 플래시하면서 Humble을 네이티브 apt 설치”하는 구성은 권장되지 않는다. Humble 실습이 필수라면 다음 중 하나를 택한다.

1. Orin 계열에서 JetPack 6 / Ubuntu 22.04 사용
2. Xavier NX의 JetPack 5 호스트에서 Ubuntu 22.04 기반 컨테이너를 사용하고 GPU·USB·I2C 장치를 명시적으로 전달
3. 수업을 Noetic과 Humble 장비로 분리

## 1. 플래시 전 동결

1. `migration_data/SHA256SUMS`를 별도 PC와 외장 저장소에 복제한다.
2. 학생 데이터와 모델, ROS bag, 학습 결과가 `/home/soda/Project` 밖에 없는지 확인한다.
3. microSD/eMMC/NVMe 모델과 파티션을 사진 또는 텍스트로 기록한다.
4. 카메라, LiDAR, I2C 보드, 오디오 연결 위치를 사진으로 남긴다.
5. `raw/reports/system_inventory.txt`와 기준선 보고서를 읽어 예상 장치를 확정한다.
6. 구 이미지의 coreutils 손상 때문에 이 이미지에서 in-place 업그레이드는 시도하지 않는다.

## 2. 클린 플래시

권장 방식은 Ubuntu x86_64 20.04 호스트의 NVIDIA SDK Manager다.

1. Xavier NX를 Force Recovery Mode로 진입한다.
2. SDK Manager에서 정확한 Xavier NX module/carrier/storage 대상을 선택한다.
3. JetPack 5.1.6 또는 NVIDIA가 제공하는 5.1.5 SD 이미지 후 5.1.6 업데이트 절차를 따른다.
4. 최초 JetPack 5라면 QSPI 갱신이 완료되었는지 확인한다.
5. 여러 boot media에 서로 다른 JetPack major image를 동시에 두지 않는다. NVIDIA 35.6.4 release note는 major가 다른 media 혼용 시 UEFI/DTB overlay 충돌과 냉각 장치 문제 가능성을 경고한다.
6. 첫 부팅에서 사용자 `soda`를 만들고 SSH를 활성화한다.
7. L4T, 커널, Ubuntu 버전을 확인한 뒤에만 복원을 시작한다.

```bash
cat /etc/nv_tegra_release
cat /etc/os-release
uname -a
dpkg-query -W nvidia-jetpack
```

## 3. 다시 설치해야 하는 것과 복사 가능한 것

| 구 환경 | 새 환경 원칙 |
|---|---|
| Python 3.6 site-packages | 복사 금지. Python 3.8용으로 재설치/포팅 |
| CUDA 10.2 / cuDNN / TensorRT | JetPack 5가 제공하는 버전 사용 |
| TensorFlow 2.2 cp36 NVIDIA wheel | 복사 금지. JetPack 5 호환 NVIDIA wheel/컨테이너 선택 |
| TensorRT engine 파일 | GPU/버전 종속이므로 새 환경에서 재생성 |
| OpenCV 4.3 | JetPack 버전을 우선하고 API 회귀 테스트 |
| ROS Melodic | ROS Noetic + Python 3로 포팅 |
| catkin source | 소스만 복원, `build/devel/log`은 삭제 후 재빌드 |
| `.bashrc/.zshrc` | 줄 단위로 선별 병합, 통째 덮어쓰기 금지 |
| udev rule | VID/PID 확인 후 새 rule로 복원 |
| Jupyter config | 경로/IP만 이식, password/token은 새로 생성 |
| tmux config | 복사 가능, TPM plugin은 재설치 |
| vendor `pop` 소스 | 참고용. Python 3.8 및 JetPack 5 GPIO/I2C에서 패치·시험 후 설치 |

`/lib`, `/usr/lib`, `/usr/local/cuda`, 이전 커널 모듈, 이전 `.so`를 백업본에서 덮어쓰지 않는다.

## 4. 복원 순서

1. OS 업데이트와 JetPack 상태 확인
2. 사용자 group 설정: `dialout`, `i2c`, `gpio`, `audio`, 필요 시 `video`
3. `i2c-tools`, ALSA 도구, tmux, zsh, Jupyter 및 개발 도구 설치
4. udev rule 복원 후 reload/trigger
5. Python virtual environment 생성 후 requirements를 새 버전으로 재구성
6. 수업 노트북과 순수 Python 코드 복원
7. ROS Noetic 설치, `rosdep`, catkin source 재빌드
8. Jupyter 설정과 systemd service를 새 경로에 맞춰 생성
9. Hanback/pop 호환성 패치
10. 아래 테스트를 낮은 위험부터 순서대로 실행

## 5. 회귀 테스트 순서

```bash
# 새 Jetson으로 migration_data를 복사한 뒤
bash migration_data/tests/remote_health_check.sh
sudo bash migration_data/tests/test_i2c_inventory.sh
bash migration_data/tests/test_audio.sh
bash migration_data/tests/test_jupyter_tmux.sh
bash migration_data/tests/test_lidar.sh /dev/rplidar
python3 migration_data/tests/validate_artifacts.py
```

그 다음에만 카메라 단일 프레임, 오디오 1초 녹음/재생, LED, 조향 중앙값, 바퀴를 띄운 모터 테스트를 사람이 현장에서 단계적으로 수행한다.

## 6. 합격 기준

- OS/L4T/커널이 JetPack 5.1.6 기준과 일치
- I2C 장치 주소가 배선표와 일치
- `/dev/rplidar`가 재부팅 후에도 생성되고 health가 Good
- ALSA playback/capture가 열거되고 실제 입출력이 현장 확인됨
- Jupyter가 서비스 재시작과 재부팅 후 올라오며 새 인증 정보가 적용됨
- Noetic workspace가 Python 3로 clean build
- 수업 노트북 46개가 열리고 핵심 수업 순서가 재현됨
- 모터/조향은 비상 정지와 기구 고정 후 최종 현장 합격
