# POP AI 다중 커널 메모리 수정 (2026-07-15)

## 결론

사용자 지적대로 `import AI`만으로 수 GB가 되는 상태는 정상적인 수업 운용 상태가
아니었다. 마이그레이션 전후를 같은 코드로 측정한 결과, POP 소스의 작은 변경보다
TensorFlow/CUDA 런타임 세대 차이와 POP의 즉시 로딩·optimizer 공유 구조가 원인이었다.

현재 기체에는 lazy loading, CPU 기본 정책, 명시적 GPU 정책, 인스턴스별 optimizer를
적용한 `gong-rc-pop 0.3.2+20260715`를 설치했다.

## 두 기체의 차이

| 항목 | 정상 기체 192.168.0.46 | 마이그레이션 기체 192.168.0.34 |
|---|---:|---:|
| Jetson Linux | R32.4.3 | R35.6.4 |
| CUDA / cuDNN | 10.2 / 8.0 | 11.4 / 8.6 |
| TensorFlow | 2.2.0+nv20.6 | 2.12.0+nv23.6 |
| Python | 3.6.9 | 3.8 |
| 기존 `import pop.AI` RSS | 약 378 MB | 약 1,235 MB |
| 기존 작은 모델 1 epoch RSS | 약 1,486 MB | 약 1,933 MB |

정상 기체도 작은 모델을 처음 만들 때 TensorFlow 로그상 GPU 메모리 4,309 MB를
예약했다. 따라서 과거에 10개 이상 활성화한 커널은 모두 GPU 모델을 학습한 상태가
아니라, 대부분 아직 TensorFlow GPU 컨텍스트를 만들지 않은 커널이었던 것으로
실측 결과상 판단된다.

## 원인

1. TensorFlow 2.12 NVIDIA wheel은 2.2보다 import와 CUDA 컨텍스트 비용이 크다.
2. 기존 `pop.AI`는 모듈 import와 동시에 TensorFlow/Keras 및 모든 AI 클래스를
   로드했다.
3. `Linear_Regression`, `DNN`, `CNN`, `RNN` 등의 Adam optimizer가 클래스 전역
   객체였다. TensorFlow 2.12 optimizer는 학습 변수와 slot 상태를 보관하므로 여러
   모델이 같은 optimizer를 재사용하면 이전 모델 참조와 상태가 누적될 수 있다.
4. GPU memory growth는 초기 전체 예약을 막지만 TensorFlow import 비용, CUDA/cuDNN
   컨텍스트, XLA tracing cache 자체를 없애지는 않는다.

## 적용한 구조

### Lazy AI facade

`autocar/pop/AI.py`는 가벼운 facade이며, 기존 구현은
`autocar/pop/_AI_tensorflow.py`에 보존했다.

```python
from pop import AI

print(AI.is_loaded())       # False
print(AI.device_policy())   # 아직 TensorFlow 미로드
```

위 코드만 실행하면 TensorFlow를 import하지 않는다. `AI.DNN`, `AI.CNN` 등 실제
클래스를 처음 조회할 때만 TensorFlow 구현을 로드한다.

### CPU 기본 정책

작은 회귀, softmax, DNN 실습은 별도 설정 없이 CPU를 사용한다.

```python
from pop import AI

model = AI.DNN(input_size=1, hidden_size=10, output_size=3)
```

CPU 모드는 OpenCV/카메라 로딩을 깨뜨리는 전역 `CUDA_VISIBLE_DEVICES=-1`을 쓰지
않는다. POP 패키지 로드 후 TensorFlow API로만 GPU 가시성을 제한한다.

### 명시적 GPU 정책

CNN, 큰 영상 모델 등 GPU가 실제로 필요한 커널에서 클래스 접근 전에 지정한다.

```python
from pop import AI

AI.configure("gpu")
model = AI.CNN(input_size=[28, 28], output_size=10)
```

GPU 모드에는 memory growth가 적용된다. CPU/GPU 정책은 TensorFlow 초기화 뒤 바꿀
수 없으므로 변경하려면 Jupyter 커널을 재시작해야 한다.

환경변수 방식도 지원한다.

```bash
POP_AI_DEVICE=gpu python3 lesson.py
```

### 직접 TensorFlow softmax 코드

POP을 거치지 않고 TensorFlow를 직접 사용하는 작은 예제는 모델 생성 전에 GPU를
숨기면 약 500 MB 수준의 CPU 경로를 사용할 수 있다.

```python
import tensorflow as tf
tf.config.set_visible_devices([], "GPU")

# 이 아래에서 Sequential/model.compile/model.fit 실행
```

GPU가 필요한 직접 TensorFlow 코드는 기존 Jupyter startup의
`TF_FORCE_GPU_ALLOW_GROWTH=true`를 사용한다.

### 인스턴스별 optimizer

각 POP AI 모델 생성 시 독립 `tf.keras.optimizers.Adam`을 만든다. 두 개의 살아 있는
DNN을 각각 학습해도 optimizer와 variable slot을 공유하지 않는다.

## 검증 결과

### import만 수행

| 조건 | RSS |
|---|---:|
| 수정 전 현재 기체 | 약 1,235 MB |
| 수정 후 현재 기체 | 약 151 MB |

결과: `TENSORFLOW_LAZY_IMPORT=PASS`

### 실제 DNN 1 epoch

| 정책 | RSS | 결과 |
|---|---:|---|
| CPU 기본 | 약 694 MB | `POP_AI_CPU=PASS` |
| GPU 명시 | 약 1,991 MB | `POP_AI_GPU=PASS`, GPU 1개 |

### 같은 프로세스에서 모델 10회 반복 생성·학습

- 두 동시 DNN의 optimizer가 서로 다름: PASS
- 1회차 RSS: 709.8 MB
- 10회차 RSS: 732.0 MB
- 첫 학습 뒤 추가 증가: 22.1 MB
- 결과: `POP_AI_REPEATED_MODELS=PASS`

반복 모델 생성 자체는 TensorFlow retracing 경고를 낼 수 있다. 수업에서는 가능한 한
모델을 한 번 만들고 반복 학습하며, 모델을 교체할 때는 이전 참조를 지우고
`tf.keras.backend.clear_session()`을 호출한다.

### import 커널 10개 동시 실행

- 개별 RSS: 약 149~152 MB
- 10개 총 RSS: 1,498.4 MB
- 모든 프로세스에서 TensorFlow 미로드 확인
- 결과: `POP_AI_TEN_IMPORTS=PASS`

## 설치 산출물

- 패키지: `migration_data/packages/gong-rc-pop_0.3.2+20260715_arm64.deb`
- SHA-256: `39c1324643e36ab2036da0b9793785b6481dbeb19a773e3980761dc7ad7382d2`
- 설치 상태: `gong-rc-pop 0.3.2+20260715`
- `dpkg -V gong-rc-pop`: 변경 파일 없음
- 이전 AI 백업: `/home/soda/venvs/gong-rc/.migration_backups/pop_ai_20260715_1627/AI.py.pre_lazy`

## 테스트 파일

- `migration_data/tests/profile_pop_ai_memory.py`
- `migration_data/tests/profile_pop_ai_direct_memory.py`
- `migration_data/tests/test_pop_ai_lazy_device.py`
- `migration_data/tests/test_pop_ai_repeated_models.py`
- `migration_data/tests/test_pop_ai_ten_imports.py`

## 운용 기준

1. 단순 `from pop import AI` 커널은 여러 개 유지 가능하다.
2. 작은 회귀/softmax/DNN은 기본 CPU 정책을 사용한다.
3. CNN/YOLO 등 GPU가 필요한 커널만 `AI.configure("gpu")`를 사용한다.
4. GPU 학습 커널은 현재 실측 약 2 GB이므로 동시에 여러 개 유지하지 않는다.
5. CPU/GPU를 바꿀 때는 커널을 재시작한다.
