# 21번 DQN Gymnasium 마이그레이션 (2026-07-15)

## 발생 오류

- `ModuleNotFoundError: No module named 'gym'`
- `ModuleNotFoundError: No module named 'pyvirtualdisplay'`
- `FileNotFoundError: glxinfo`

## 버전 결정

기존 정상 기체에는 Gym 0.17.2, pyglet 1.5.0, PyVirtualDisplay 3.0이 있었지만,
21번 노트북을 구형 API에 묶지 않고 유지보수되는 공식 후속 프로젝트 Gymnasium으로
이전했다.

2026-07-15 기준 최신 Gymnasium 1.3.0은 Python 3.10 이상이 필요하다. 현재
JetPack 5 환경은 Python 3.8이므로 Python 3.8을 공식 지원하는 마지막 최신 버전
`Gymnasium 0.29.1`을 선택했다.

- Gymnasium 0.29.1: Python `>=3.8`
- Gymnasium 1.3.0: Python `>=3.10`
- CartPole 최신 API는 환경 생성 시 `render_mode="rgb_array"`를 지정한다.

공식 근거:

- https://pypi.org/project/gymnasium/0.29.1/
- https://pypi.org/project/gymnasium/
- https://gymnasium.farama.org/environments/classic_control/cart_pole/

## 설치 항목

Python 가상환경 `/home/soda/venvs/gong-rc`:

- gymnasium 0.29.1
- pygame 2.6.1 (classic-control extra)
- PyVirtualDisplay 3.0
- cloudpickle 3.1.2
- farama-notifications 0.0.6

시스템 패키지:

- xvfb
- xauth
- mesa-utils (`glxinfo`)

NVIDIA GL/CUDA 라이브러리를 Mesa로 교체하지 않았다. `mesa-utils`는 진단 명령만
추가하며, `rgb_array` 렌더링은 `SDL_VIDEODRIVER=dummy`로 headless 실행한다.

재설치 스크립트:

```bash
sudo TARGET_USER=soda \
  /home/soda/gong_rc_2026/migration_data/scripts/install_dqn_gymnasium.sh
```

## 노트북 API 변경

수정 파일:

- `autocar/jupyter_source/a21_dqn.ipynb`
- Jupyter 실제 파일: `/home/soda/Project/python/notebook/gong_rc_2026/a21_dqn.ipynb`

주요 변경:

```python
import gymnasium as gym

env = gym.make("CartPole-v1", render_mode="rgb_array")
obs, info = env.reset(seed=42)

frame = env.render()
obs, reward, terminated, truncated, info = env.step(action)

if terminated or truncated:
    obs, info = env.reset()
```

- `env.render(mode="rgb_array")`를 환경 생성 시 `render_mode` 지정 방식으로 변경
- `reset()` 반환값을 `(observation, info)`로 변경
- `step()` 반환값을 5개로 변경
- `done`을 `terminated or truncated`로 변경
- Pygame headless 환경에 `SDL_VIDEODRIVER=dummy`, `SDL_AUDIODRIVER=dummy` 적용
- 기존 오류 traceback과 실행 결과 제거
- POP DQN CPU 저메모리 생성·학습 셀 추가

변환 스크립트:

- `migration_data/scripts/update_a21_dqn_gymnasium.py`

원본 백업:

- 로컬: `migration_data/raw/backups/a21_dqn_pre_gymnasium_20260715.ipynb`
- 기체: `/home/soda/venvs/gong-rc/.migration_backups/a21_dqn_20260715/`

## 실기 검증

`migration_data/tests/test_dqn_gymnasium.py`:

```text
GYMNASIUM=0.29.1
DISPLAY=:1
GLXINFO_RETURN=0
FRAME_SHAPE=(400, 600, 3)
GYMNASIUM_CARTPOLE_RENDER=PASS
DQN_DEVICE={'requested': 'cpu', 'effective': 'cpu', 'loaded': True}
POP_DQN_GYMNASIUM=PASS
```

`migration_data/tests/test_dqn_notebook_import_order.py`로 실제 노트북과 같은
`Util -> AI -> DQN` 순서도 검증했다.

```text
VISIBLE_GPUS=0
DQN_NOTEBOOK_IMPORT_ORDER=PASS
```

## 수업 운용

21번 DQN은 작은 네트워크이므로 CPU 저메모리 정책을 사용한다.

```python
from pop import AI

AI.configure("cpu")
dqn = AI.DQN(state_size=4, hidden_size=8, output_size=1)
```

Gymnasium 셀을 다시 실행하기 전에 이전 `env`는 `env.close()`하고, 가상 화면을
다시 만들기 전에는 이전 `display.stop()`을 호출한다.
