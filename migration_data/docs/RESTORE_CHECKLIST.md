# 복원 체크리스트

## 플래시 전

- [ ] `migration_data` 전체를 두 곳 이상에 복사
- [ ] `sha256sum -c SHA256SUMS` 확인
- [ ] microSD/eMMC/NVMe와 board SKU 확인
- [ ] 배선·커넥터·I2C 주소 사진 기록
- [ ] 추가 사용자 파일, 모델, ROS bag 별도 백업
- [ ] JetPack 5 최초 설치 여부와 QSPI 갱신 절차 확인

## 첫 부팅

- [ ] `soda` 사용자와 SSH 구성
- [ ] `cat /etc/nv_tegra_release`
- [ ] `cat /etc/os-release`
- [ ] `uname -a`
- [ ] `dpkg-query -W nvidia-jetpack`
- [ ] 저장장치와 여유 공간 확인
- [ ] 모든 boot media가 같은 JetPack major인지 확인

## 사용자와 권한

```bash
sudo usermod -aG dialout,audio,video,i2c,gpio soda
```

- [ ] 재로그인 후 `id soda` 확인
- [ ] udev rule은 `MODE="0660", GROUP="dialout"` 우선
- [ ] `sudo udevadm control --reload-rules && sudo udevadm trigger`
- [ ] 재부팅 후 `/dev/rplidar` 확인

## 개발 환경

- [ ] Python virtual environment 생성
- [ ] Python 3.6 wheel/바이너리를 복사하지 않고 재설치
- [ ] JetPack 제공 CUDA/cuDNN/TensorRT 사용
- [ ] TensorRT engine 재생성
- [ ] ROS Noetic 설치와 `rosdep` 실행
- [ ] catkin의 기존 build/devel/log를 제외하고 source만 복원
- [ ] `.zshrc`의 Melodic source를 Noetic으로 변경
- [ ] tmux TPM/plugin 재설치
- [ ] Jupyter password/token 새로 발급
- [ ] Jupyter service 경로와 User/Group 검토

## 하드웨어 검증

- [ ] health check FAIL 0
- [ ] I2C 주소/버스 매핑 기록
- [ ] ALSA playback/capture 열거
- [ ] 현장에서 1초 녹음과 샘플 재생
- [ ] LiDAR info/health Good
- [ ] 카메라 단일 프레임
- [ ] ROS rplidar topic과 scan rate
- [ ] Hector SLAM map 생성
- [ ] GPIO 출력은 부하 제거 후 시험
- [ ] 조향은 바퀴를 띄우고 중앙값부터 시험
- [ ] 모터는 비상 정지 준비 후 저출력 시험

## 수업 검증

- [ ] a01~a10: 카메라/오디오/기초 기능
- [ ] a11: LiDAR
- [ ] a12~a13: LED
- [ ] a14~a28: ML/DL 코드
- [ ] a29: wheel alignment
- [ ] a30: car balancing
- [ ] a31: collision avoidance/tracking
- [ ] 기존 출력과 새 출력 차이를 보고서에 기록
