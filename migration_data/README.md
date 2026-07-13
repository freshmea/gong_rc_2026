# Xavier NX migration_data

이 디렉터리는 2026-07-13 현재 `soda@192.168.0.34` Jetson Xavier NX의 Ubuntu 18.04 / JetPack 4 계열 환경을 Ubuntu 20.04 기반 JetPack 5로 재구축할 때 사용할 기준선 자료다.

## 먼저 볼 문서

- [현재 시스템 기준선](docs/CURRENT_SYSTEM_BASELINE.md)
- [Ubuntu 20.04 마이그레이션 가이드](docs/UBUNTU_20_04_MIGRATION_GUIDE.md)
- [복원 체크리스트](docs/RESTORE_CHECKLIST.md)
- [테스트 매트릭스](docs/TEST_MATRIX.md)
- [정상 사용 코드 인덱스](docs/KNOWN_WORKING_CODE_INDEX.md)

## 디렉터리

- `raw/reports/system_inventory.txt`: OS, L4T, 커널, 장치, ALSA, I2C, CUDA, Python/pip/apt, 설치 이력, Jupyter, tmux, ROS, udev, systemd의 통합 인벤토리
- `raw/reports/privileged_hardware_inventory.txt`: dmesg 하드웨어 요약과 root 권한 I2C 스캔
- `raw/configs/home/`: 마스킹된 `.bashrc`, `.zshrc`, `.profile`, history, Jupyter, tmux 설정
- `artifacts/class_notebooks_and_code/`: 수업 노트북과 Python 코드
- `artifacts/ros_lidar_sources/`: RPLidar 및 Hector SLAM catkin 소스
- `artifacts/hanback_board_config/`: 보드 설정과 CAN 보조 스크립트
- `artifacts/vendor_python_sources/`: 기존 Python 3.6용 pop/rplidar/PyAudio 소스
- `tests/`: 이전 이미지와 새 이미지에 동일하게 실행할 비파괴 검증 코드
- `reports/baseline_tests/`: 2026-07-13 구 이미지에서 실행한 실제 기준선 결과
- `SHA256SUMS`: 파일 무결성 확인용 해시

## 보안과 안전

수집 과정에서 password, token, API key 형태의 값은 `[REDACTED]`로 바꿨다. 접속 암호는 파일에 저장하지 않으며 재수집 시 환경 변수로만 전달한다.

모터, 조향, LED, GPIO 출력, 스피커 재생 코드는 자동 실행하지 않았다. LiDAR 검사는 정보와 health만 읽고 항상 motor stop 및 disconnect를 수행한다. 노트북은 JSON/구문 정적 검사만 했다.

## 재실행

Windows에 PuTTY plink가 있고 장치가 같은 주소에 있을 때 WSL에서 실행한다.

```bash
cd /home/aa/gong_rc_2026
REMOTE_PASSWORD='<password>' migration_data/scripts/collect_inventory_only.sh
REMOTE_PASSWORD='<password>' migration_data/scripts/run_baseline_tests.sh
python3 migration_data/tests/validate_artifacts.py
sha256sum -c migration_data/SHA256SUMS
```

전체 아카이브를 다시 수집할 때만 `collect_remote.sh`을 사용한다. 기존 장치의 상태를 바꾸지 않는 읽기 위주 수집기다.
