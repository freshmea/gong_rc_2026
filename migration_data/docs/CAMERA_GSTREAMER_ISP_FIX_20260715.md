# 카메라 GStreamer 및 ISP 보정 결과 (2026-07-15)

## 결론

- `Cannot query video position` 경고는 파일 위치와 재생 길이가 없는 실시간 `appsink` 스트림에 OpenCV가 위치 조회를 시도해서 발생한다. 프레임 캡처 실패나 색상·왜곡의 원인은 아니다.
- 기존 `Util.gstrmer()`는 `flip` 인자를 무시하고 `__main__._camera_flip_method`를 사용했으며, IMX219에 존재하지 않는 `640x480@30` 센서 모드를 직접 요청했다.
- 정상 기체 `192.168.0.46`에는 NVIDIA ISP 보정 파일이 있었지만 마이그레이션 기체 `192.168.0.34`에는 없었다. 이것이 붉은 색조 변화의 주원인이었다.
- 정상 기체의 JetPack 4 ISP 파일을 JetPack 5에 그대로 넣으면 일부 구형 속성이 거부된다. 18–51행의 구형 HDR·톤매핑 항목을 제거하고 AWB, 색상 행렬, optical black, 렌즈 셰이딩 보정은 유지한 호환본을 적용했다.
- ISP 파일은 색상과 렌즈 주변부 밝기 보정용이며 어안 렌즈의 기하학적 배럴 왜곡을 펴는 파일은 아니다. 직선 휨 제거에는 체커보드 캘리브레이션으로 K/D 계수를 얻은 뒤 `cv2.fisheye.initUndistortRectifyMap()`과 `cv2.remap()`을 사용해야 한다.

## 적용한 코드 변경

`autocar/pop/Util.py`의 `gstrmer()`를 다음과 같이 변경했다.

- `width`, `height`: OpenCV에 전달되는 출력 크기
- 기본 30 fps 입력: IMX219 지원 모드 `1640x1232@30`, 출력은 `nvvidconv`에서 `640x480`으로 축소
- 21 fps 이하 입력: `3280x2464@21`
- 전달된 `flip` 값을 실제 `nvvidconv flip-method`에 사용하고 0–7 범위 검증
- `sensor_id`, `capture_width`, `capture_height` 선택 인자 추가
- 지연 누적 방지를 위해 `appsink drop=true max-buffers=1 sync=false` 사용

기존 수업 코드는 변경 없이 사용할 수 있다.

```python
cam = Util.gstrmer(width=640, height=480, fps=30, flip=0)
cap = cv2.VideoCapture(cam, cv2.CAP_GSTREAMER)
```

실제 선택된 모드는 `Camera mode = 3`, 입력 `1640x1232`, 출력 프레임 `(480, 640, 3)`이었다.

## 패키지 및 시스템 적용

- 설치 패키지: `gong-rc-pop 0.2.1+20260715`
- DEB SHA-256: `62b989b18ca080aba9c3d87fded7d1d8ec7b931a312a6f7fe69eff64f3662c81`
- 활성 ISP 파일: `/var/nvidia/nvcam/settings/camera_overrides.isp`
- JetPack 5 호환 ISP SHA-256: `b6bcafec4e9cc2226d7c23e51e14c9d9ee40192000a1be8588b6ec6f7e9c20e1`
- 이전 설정 백업: `/var/backups/gong-rc-camera-20260715_132259`, `/var/backups/gong-rc-camera-20260715_132649`
- Argus 최종 로그: `Found override file` 확인, `Invalid isp config attribute` 없음

## 캡처 검증

동일 장소와 동일 파이프라인에서 워밍업 포함 30프레임을 읽었다.

| 상태 | 30프레임 시간 | 평균 B/G/R | R-G 차이 |
|---|---:|---:|---:|
| ISP 없음 | 0.937초 | 136.68 / 127.38 / 154.89 | 27.51 |
| JetPack 4 원본 ISP | 0.927초 | 127.82 / 137.12 / 143.73 | 6.61 |
| JetPack 5 호환 ISP | 0.936초 | 126.79 / 136.19 / 142.03 | 5.84 |

적색 편향이 크게 줄었고 육안으로도 분홍색 캐스트가 사라졌다. `Cannot query video position` 경고는 세 캡처 모두에서 나타났지만 모든 프레임이 정상 반환됐다.

## 남아 있는 비치명적 로그

- 두 번째 카메라 모듈이 실제로 없어서 발생하는 `ModuleNotPresent` 메시지
- `nvphsd` 서비스가 없어 발생하는 power hint 메시지
- GUI 디스플레이가 없는 SSH 실행에서 발생하는 `No protocol specified`

이 메시지들은 CSI 카메라 0번의 30프레임 캡처 성공에는 영향을 주지 않았다.

## 재현 및 복원 파일

- `migration_data/scripts/install_camera_isp_override.sh`: 기존 ISP/cache 백업 후 호환 ISP 설치 및 Argus 재시작
- `migration_data/tests/capture_camera_frame.py`: 헤드리스 캡처와 프레임 통계 검증
- `migration_data/raw/camera_compare/camera_overrides_jetpack5.isp`: 현재 적용한 호환 ISP
- `migration_data/raw/camera_compare/migrated_before_isp.jpg`: 적용 전 화면
- `migration_data/raw/camera_compare/migrated_after_isp_jetpack5.jpg`: 최종 화면
