# 테스트 매트릭스

## 자동 실행 가능

| 스크립트 | 검사 | 장치 상태 변경 | 기준선 |
|---|---|---|---|
| `remote_health_check.sh` | OS/L4T, 명령, 장치 노드, ALSA, 소스, Python import | 없음 | PASS 25 / FAIL 0 |
| `test_i2c_inventory.sh` | adapter와 bus 0/1/8 read-byte scan | 읽기 트랜잭션 | 기준 주소 재현 |
| `test_audio.sh` | ALSA card/playback/capture 열거 | 없음 | PASS |
| `test_camera.sh` | V4L2 node, OpenCV/GStreamer, nvargus-daemon | 없음 | PASS |
| `test_gpio_can.sh` | GPIO chip, CAN link, Hanback 설정, GPIO import | 없음 | PASS |
| `test_jupyter_tmux.sh` | 임시 tmux 및 localhost Jupyter HTTP | 임시 프로세스 | PASS |
| `test_lidar.sh` | udev, serial info, health | LiDAR serial 연결; 종료 시 motor stop | PASS, Good |
| `validate_artifacts.py` | ipynb JSON, 코드 cell/Python AST | 수업 코드 미실행 | 46 notebooks, 19 py, 오류 0 |

## 옵션 실행

`test_audio.sh --active`는 1초 녹음과 ALSA 샘플 재생을 한다. 스피커 음량과 마이크 default route를 확인한 사람이 현장에 있을 때만 실행한다.

## 자동 실행 금지

다음 노트북은 실제 액추에이터나 GPIO 출력을 만들 수 있으므로 정적 검사만 한다.

- `a12_led.ipynb`, `a13_8_led.ipynb`
- `a29_wheel_alignment.ipynb`
- `a30_car_balancing.ipynb`
- `a31_collision_avoid.ipynb`, `a31_tracking.ipynb`
- AutoCar board test, mini project, face tracking 계열

현장 시험 전에는 차체를 받침대에 고정하고 바퀴를 지면에서 띄우며, 전원 차단 수단을 준비한다. 조향 PWM은 저장된 값을 바로 재사용하지 말고 새 보드에서 중립점부터 좁은 범위로 교정한다.

## 결과 위치

- 구 이미지 실측: `reports/baseline_tests/`
- 정적 검증 요약: `reports/artifact_validation.txt`
- 새 이미지 결과는 덮어쓰지 말고 `reports/post_migration_YYYYMMDD/`에 저장해 diff한다.
