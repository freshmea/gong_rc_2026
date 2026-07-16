# TensorFlow softmax NvMap/cuDNN 오류 수정 (2026-07-15)

## 증상

수업용 softmax 모델의 `model.fit()`에서 다음 오류가 연속 발생했다.

- `NvMapMemAllocInternalTagged: 1074810371 error 12`
- `CUDNN_STATUS_NOT_INITIALIZED`
- XLA `RET_CHECK failure ... dnn != nullptr`
- `Error retrieving driver version ... /proc/driver/nvidia/version`

## 확인한 원인

오류 커널 PID 8464가 RSS 약 4.54 GB를 사용하고 있었고, 시스템의 사용 가능
메모리는 약 1.4 GB였다. Jetson은 CPU와 GPU가 RAM을 공유하므로 약 1.0 GB의
추가 NvMap 할당이 `ENOMEM`(error 12)으로 실패했고 cuDNN/XLA 오류가 뒤따랐다.

`/proc/driver/nvidia/version`은 이 Jetson L4T R35.6.4 시스템에 존재하지 않았다.
따라서 해당 메시지는 핵심 원인이 아니라 cuDNN 초기화 실패 중 나온 부수 오류다.

문제 커널만 종료한 뒤 사용 가능 메모리는 약 4.8 GB로 회복됐다.

## 적용한 수정

새 IPython/Jupyter 커널이 TensorFlow import 전에 다음 값을 설정하도록 설치했다.

```text
TF_FORCE_GPU_ALLOW_GROWTH=true
TF_CPP_MIN_LOG_LEVEL=2
MPLBACKEND=Agg
```

- 사용자 시작 파일: `/home/soda/.ipython/profile_default/startup/20-tensorflow-jetson.py`
- 서비스 drop-in: `/etc/systemd/system/jupyter-gong-rc.service.d/tensorflow.conf`
- 원본: `migration_data/system/20-tensorflow-jetson.py`
- 원본: `migration_data/system/jupyter-gong-rc-tensorflow.conf`

오류가 발생한 커널 ID `b00caa4e-44af-4c9e-887a-2f15bb08f6a4`도 새 PID
9557로 재시작했다. Jupyter 서비스 전체는 재시작하지 않아 다른 커널은 유지했다.

## 수업 코드 권장형

환경 설정은 반드시 `import tensorflow`보다 먼저 실행한다. 보드에 설치된 Jupyter
시작 파일이 자동 처리하지만, 노트북을 다른 기체로 복사해도 안전하도록 코드에도
넣어 둘 수 있다.

```python
import os
os.environ.setdefault("TF_FORCE_GPU_ALLOW_GROWTH", "true")
os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")

import numpy as np
import tensorflow as tf

a1 = [73, 62, 83, 110, 139, 123, 177, 159, 182]
a2 = [1,1,1,0,0,0,0,0,0]
a3 = [0,0,0,1,1,1,0,0,0]
a4 = [0,0,0,0,0,0,1,1,1]

X = np.array(a1, dtype=np.float32).reshape(-1, 1)
Y = np.array([a2, a3, a4], dtype=np.float32).T
X_scaled = (X - X.mean()) / X.std()

model = tf.keras.Sequential([
    tf.keras.layers.Dense(3, input_shape=[1], activation="softmax")
])
model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.05),
    loss="categorical_crossentropy",
    metrics=["accuracy"],
    jit_compile=False,
)
model.fit(X_scaled, Y, epochs=10, verbose=0)
```

`jit_compile=False`는 이 작은 모델에 불필요한 XLA 컴파일을 피하는 방어 설정이다.
영구 메모리 설정을 적용한 비교 시험에서는 이 옵션을 생략한 원문도 통과했다.

## 실기 검증 결과

`migration_data/tests/test_tensorflow_softmax_jetson.py`를 새 프로세스에서 실행했다.

```text
TENSORFLOW=2.12.0
GPU_COUNT=1
SOFTMAX_ROW_SUMS=[1. 1. 1. 1. 1. 1. 1. 1. 1.]
SOFTMAX_JETSON=PASS
```

`jit_compile=False`를 제거한 원문 compile 형태도 다음과 같이 통과했다.

```text
TENSORFLOW=2.12.0
GPU_COUNT=1
FINAL_ACCURACY=0.777778
SOFTMAX_JETSON=PASS
```

IPython 시작 설정 자체도
`migration_data/tests/check_tensorflow_kernel_defaults.py`로 검증했다.

```text
TF_FORCE_GPU_ALLOW_GROWTH=true
TF_CPP_MIN_LOG_LEVEL=2
MPLBACKEND=Agg
TENSORFLOW_KERNEL_DEFAULTS=PASS
```

10 epoch의 정확도는 무작위 초기값 때문에 실행마다 달라질 수 있다. 이는 NvMap
오류와 무관하다. 분류 결과를 안정적으로 보여 주려면 epoch를 늘리고 학습 전
`tf.keras.utils.set_random_seed(...)`를 지정한다.

## 재발 시 복구

1. Jupyter에서 `Kernel > Restart Kernel`을 실행한다.
2. 첫 셀부터 순서대로 다시 실행한다.
3. 여러 TensorFlow 커널을 동시에 오래 유지하지 않는다.
4. `free -h`와 `ps -eo pid,rss,cmd --sort=-rss | head`로 대용량 커널을 찾는다.

이미 TensorFlow를 import한 커널에서는 GPU 초기화 정책을 완전히 바꿀 수 없으므로
환경 변수를 뒤늦게 설정하는 대신 반드시 커널을 재시작해야 한다.
