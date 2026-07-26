# a21 DQN Gymnasium 32GB 적용 결과

날짜: 2026-07-17  
대상: `gong-rc-32gb`, Python 3.8 teaching venv

64GB 마이그레이션 설정과 동일하게 다음 버전을 설치했다.

- `gymnasium[classic-control]==0.29.1`
- `PyVirtualDisplay==3.0`
- `pygame==2.6.1` (classic-control 의존성)
- Ubuntu `xvfb`, `xauth`, `mesa-utils`

Python 3.8에서 사용할 수 있는 64GB 기준 버전은 Gymnasium 0.29.1이다.
설치는 기존 `migration_data/scripts/install_dqn_gymnasium.sh`를 사용했다.

통합 검증 결과:

```text
GYMNASIUM=0.29.1
DISPLAY=:1
GLXINFO_RETURN=0
FRAME_SHAPE=(400, 600, 3)
GYMNASIUM_CARTPOLE_RENDER=PASS
DQN_DEVICE={'requested': 'cpu', 'effective': 'cpu', 'loaded': True}
POP_DQN_GYMNASIUM=PASS
```

`test_dqn_gymnasium.py`는 CartPole reset/step, 600x400 RGB 렌더링,
Xvfb/GLX, POP `AI.DQN` 1회 학습과 예측을 실제로 수행한다.

`validate_a21_notebook_smoke.py`는 Jupyter에 배포된 실제
`a21_dqn.ipynb`를 `/tmp`에 복사한 후 두 개의 `range(1000)`만 5회로
줄여 모든 셀을 실행한다. 원본 노트북은 변경하지 않는다.

```text
A21_NOTEBOOK_SMOKE=PASS cells=8 errors=0 loops=5
```

`setup_python_jupyter.sh`가 이후 `install_dqn_gymnasium.sh`를 자동으로
호출하므로 다음 20대 기체에서는 이 설치 단계가 누락되지 않는다.

Jupyter에서 이전에 실패한 커널이 열려 있다면 커널을 재시작한 뒤 a21 첫
셀부터 실행한다.
