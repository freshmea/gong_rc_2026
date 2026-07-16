# 22번 CartPole 후속 수정 (2026-07-15)

21번 DQN의 Gymnasium 전환 뒤 같은 구형 Gym API를 사용하는 노트북을 검색했다.
대상은 `a21_dqn.ipynb`, `a22_cartpole.ipynb` 두 개뿐이었다.

22번도 다음과 같이 변경했다.

- `import gym` -> `import gymnasium as gym`
- `reset()` -> `(state, info)`
- `step()` -> `(state, reward, terminated, truncated, info)`
- `done` -> `terminated or truncated`
- POP DQN에 `AI.configure("cpu")` 저메모리 정책 적용
- deprecated `np.bool` 경로 대신 예측 확률을 `int` 행동으로 명시 변환
- 상태는 행동 전 값을 저장하고 action label은 `(N, 1)` 형태로 저장
- 기존 실행 결과 제거

수정 파일:

- `autocar/jupyter_source/a22_cartpole.ipynb`
- `/home/soda/Project/python/notebook/gong_rc_2026/a22_cartpole.ipynb`

백업:

- `migration_data/raw/backups/a22_cartpole_pre_gymnasium_20260715.ipynb`
- `/home/soda/venvs/gong-rc/.migration_backups/a22_cartpole_20260715/`

검증 `migration_data/tests/test_a22_cartpole_episode.py`:

```text
EPISODE_STEPS=36
DQN_LOSS=8.005361557006836
A22_CARTPOLE_EPISODE=PASS
```

episode 길이와 loss는 초기 가중치 및 샘플 행동에 따라 실행마다 달라진다. 유한한
loss로 episode 수집과 DQN 학습이 정상 종료되는지가 회귀 검사 기준이다.
