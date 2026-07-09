from pop import Pilot, AI
import numpy as np
import time
import math


# ============================================================
# AutoCar 객체 생성
# ============================================================

Car = Pilot.AutoCar()


# ============================================================
# 기본 설정값
# ============================================================

SPEED = 70
MOVE_TIME = 0.7
BACK_TIME = 0.7
STABLE_TIME = 0.2
GYRO_DELAY = 0.03

CALIB_STEERS = np.linspace(-1.0, 1.0, 11)


# ============================================================
# gyro -> 조향각 추정 설정값
# ============================================================

# getGyro("z")가 raw 값이면 보통 1/131 사용
# getGyro("z")가 이미 deg/s라면 1.0으로 변경
GYRO_SCALE = 1.0 / 131.0

# 차량 앞뒤 바퀴 사이 거리, 실제 차량에 맞게 수정
WHEEL_BASE_CM = 18.0

# MOVE_TIME 동안 실제 이동한 거리
# 직접 자로 재서 넣으면 더 정확하다.
# 예: speed=70, move_time=0.7 동안 35cm 이동하면 35.0
MOVE_DISTANCE_CM = 35.0

# 조향각 표시용 최대 바퀴 각도
# AutoCar.steering = 1.0 일 때 앞바퀴가 대략 몇 도 꺾이는지
MAX_WHEEL_ANGLE_DEG = 30.0


# ============================================================
# 조향 범위 보정 설정
# ============================================================

RANGE_GAIN = 1.6

LEFT_GAIN = RANGE_GAIN
RIGHT_GAIN = RANGE_GAIN

STEER_MIN = -1.0
STEER_MAX = 1.0


# ============================================================
# AutoCar 호환 함수
# ============================================================

def car_forward(car, speed):
    try:
        car.forward(speed)
    except TypeError:
        car.forward()


def car_backward(car, speed):
    try:
        car.backward(speed)
    except TypeError:
        car.backward()


# ============================================================
# Linear Regression 관련 함수
# ============================================================

def train_lr(lr, times=1000):
    if hasattr(lr, "train"):
        try:
            lr.train(times=times)
        except TypeError:
            lr.train()
    elif hasattr(lr, "fit"):
        try:
            lr.fit(times=times)
        except TypeError:
            lr.fit()
    else:
        raise RuntimeError("Linear_Regression 객체에 train 또는 fit 메서드가 없습니다.")


def lr_value(lr, x):
    result = lr.run([float(x)])

    try:
        return float(result[0][0])
    except Exception:
        try:
            return float(result[0])
        except Exception:
            return float(result)


# ============================================================
# gyro 값으로 차체 회전각 / 바퀴 조향각 계산
# ============================================================

def calc_angle_from_gyro_samples(gyro_samples, dt_samples):
    """
    gyro_samples:
        getGyro("z")에서 읽은 값들

    dt_samples:
        각 gyro 샘플 사이의 시간 간격들

    반환:
        gyro_avg_raw
        gyro_avg_dps
        yaw_angle_deg
        wheel_angle_deg
    """

    if len(gyro_samples) == 0:
        return {
            "gyro_avg_raw": 0.0,
            "gyro_avg_dps": 0.0,
            "yaw_angle_deg": 0.0,
            "wheel_angle_deg": 0.0
        }

    gyro_raw_arr = np.array(gyro_samples, dtype=float)
    dt_arr = np.array(dt_samples, dtype=float)

    gyro_avg_raw = float(np.mean(gyro_raw_arr))

    # raw gyro 값을 deg/s로 변환
    gyro_dps_arr = gyro_raw_arr * GYRO_SCALE
    gyro_avg_dps = float(np.mean(gyro_dps_arr))

    # yaw angle = gyro_z 각속도를 시간 적분
    if len(dt_arr) == len(gyro_dps_arr):
        yaw_angle_deg = float(np.sum(gyro_dps_arr * dt_arr))
    else:
        yaw_angle_deg = float(gyro_avg_dps * MOVE_TIME)

    # 차체 회전각 yaw로부터 조향각 추정
    # bicycle model 근사:
    # radius = distance / yaw_rad
    # steering_angle = atan(wheel_base / radius)
    yaw_rad = math.radians(yaw_angle_deg)

    if abs(MOVE_DISTANCE_CM) < 1e-6:
        wheel_angle_deg = 0.0
    else:
        wheel_angle_rad = math.atan2(WHEEL_BASE_CM * yaw_rad, MOVE_DISTANCE_CM)
        wheel_angle_deg = math.degrees(wheel_angle_rad)

    return {
        "gyro_avg_raw": gyro_avg_raw,
        "gyro_avg_dps": gyro_avg_dps,
        "yaw_angle_deg": yaw_angle_deg,
        "wheel_angle_deg": wheel_angle_deg
    }


def estimate_wheel_angle_from_steer(steer):
    """
    steering 명령값 기준의 단순 바퀴 각도 추정.
    실제 측정값이 아니라 명령값 기반 표시용이다.
    """
    return float(steer) * MAX_WHEEL_ANGLE_DEG


# ============================================================
# 앞으로 움직이면서 gyro, yaw angle, wheel angle 측정
# ============================================================

def move_forward_and_measure(car, steer, speed, move_time):
    """
    지정한 steer 값으로 앞으로 움직이면서
    gyro 평균, 차체 회전각, 추정 바퀴 조향각을 함께 계산한다.
    """

    car.steering = steer
    car_forward(car, speed)

    start = time.time()
    last = start

    gyro_samples = []
    dt_samples = []

    while time.time() - start < move_time:
        now = time.time()
        dt = now - last
        last = now

        z = car.getGyro("z")

        gyro_samples.append(float(z))
        dt_samples.append(float(dt))

        time.sleep(GYRO_DELAY)

    car.stop()
    time.sleep(STABLE_TIME)

    angle_info = calc_angle_from_gyro_samples(
        gyro_samples=gyro_samples,
        dt_samples=dt_samples
    )

    result = {
        "steer": float(steer),
        "command_wheel_angle_deg": estimate_wheel_angle_from_steer(steer),
        "gyro": angle_info["gyro_avg_raw"],
        "gyro_dps": angle_info["gyro_avg_dps"],
        "yaw_angle_deg": angle_info["yaw_angle_deg"],
        "wheel_angle_deg": angle_info["wheel_angle_deg"]
    }

    return result


def move_backward_return(car, steer, speed, back_time):
    car.steering = steer
    car_backward(car, speed)

    time.sleep(back_time)

    car.stop()
    time.sleep(STABLE_TIME)


# ============================================================
# 1. steer -> gyro / angle 반응 데이터 수집
# ============================================================

def collect_response_data(car):
    dataset = {
        "steer": [],
        "gyro": [],
        "gyro_dps": [],
        "yaw_angle_deg": [],
        "wheel_angle_deg": [],
        "command_wheel_angle_deg": []
    }

    car.setSpeed(SPEED)

    try:
        for steer in CALIB_STEERS:
            steer = round(float(steer), 1)

            print("측정 steer:", steer)

            measured = move_forward_and_measure(
                car=car,
                steer=steer,
                speed=SPEED,
                move_time=MOVE_TIME
            )

            move_backward_return(
                car=car,
                steer=steer,
                speed=SPEED,
                back_time=BACK_TIME
            )

            dataset["steer"].append(measured["steer"])
            dataset["gyro"].append(measured["gyro"])
            dataset["gyro_dps"].append(measured["gyro_dps"])
            dataset["yaw_angle_deg"].append(measured["yaw_angle_deg"])
            dataset["wheel_angle_deg"].append(measured["wheel_angle_deg"])
            dataset["command_wheel_angle_deg"].append(measured["command_wheel_angle_deg"])

            print({
                "steer": measured["steer"],
                "command_wheel_angle_deg": measured["command_wheel_angle_deg"],
                "gyro_raw": measured["gyro"],
                "gyro_dps": measured["gyro_dps"],
                "yaw_angle_deg": measured["yaw_angle_deg"],
                "estimated_wheel_angle_deg": measured["wheel_angle_deg"]
            })

            time.sleep(0.3)

    finally:
        car.stop()

    return dataset


# ============================================================
# gyro=0이 되는 실제 직진 조향값 찾기
# ============================================================

def find_zero_steer(steer_arr, gyro_arr):
    for i in range(len(steer_arr) - 1):
        s1 = steer_arr[i]
        s2 = steer_arr[i + 1]

        g1 = gyro_arr[i]
        g2 = gyro_arr[i + 1]

        if g1 == 0:
            return float(s1)

        if g1 * g2 < 0:
            zero_steer = s1 + (0 - g1) * (s2 - s1) / (g2 - g1)
            return float(zero_steer)

    idx = np.argmin(np.abs(gyro_arr))
    return float(steer_arr[idx])


# ============================================================
# 2. 측정 데이터로 AI 학습 데이터 만들기
# ============================================================

def make_training_data(dataset):
    steer_arr = np.array(dataset["steer"], dtype=float)
    gyro_arr = np.array(dataset["gyro"], dtype=float)

    order = np.argsort(steer_arr)
    steer_arr = steer_arr[order]
    gyro_arr = gyro_arr[order]

    print("===== 정렬된 측정 데이터 =====")

    for i in range(len(steer_arr)):
        print({
            "steer": float(steer_arr[i]),
            "gyro": float(gyro_arr[i])
        })

    zero_steer = find_zero_steer(steer_arr, gyro_arr)

    print("실제 직진 보정 steer:", zero_steer)
    print("실제 직진 명령 기준 바퀴각 추정:", estimate_wheel_angle_from_steer(zero_steer))

    left_mask = gyro_arr > 0
    right_mask = gyro_arr < 0

    left_steer = steer_arr[left_mask]
    left_gyro_abs = np.abs(gyro_arr[left_mask])

    right_steer = steer_arr[right_mask]
    right_gyro_abs = np.abs(gyro_arr[right_mask])

    left_steer = np.append(left_steer, zero_steer)
    left_gyro_abs = np.append(left_gyro_abs, 0.0)

    right_steer = np.append(right_steer, zero_steer)
    right_gyro_abs = np.append(right_gyro_abs, 0.0)

    left_order = np.argsort(left_gyro_abs)
    right_order = np.argsort(right_gyro_abs)

    left_gyro_abs = left_gyro_abs[left_order]
    left_steer = left_steer[left_order]

    right_gyro_abs = right_gyro_abs[right_order]
    right_steer = right_steer[right_order]

    left_max = np.max(left_gyro_abs)
    right_max = np.max(right_gyro_abs)

    usable_gyro = min(left_max, right_max)

    print("left_max_gyro :", left_max)
    print("right_max_gyro:", right_max)
    print("usable_gyro   :", usable_gyro)

    desired_values = np.linspace(-1.0, 1.0, 11)

    X_data = []
    Y_data = []

    print("===== 보정 테이블 =====")

    for desired in desired_values:
        desired = round(float(desired), 1)

        if desired < 0:
            target_gyro = abs(desired) * usable_gyro

            corrected = np.interp(
                target_gyro,
                left_gyro_abs,
                left_steer
            )

        elif desired > 0:
            target_gyro = abs(desired) * usable_gyro

            corrected = np.interp(
                target_gyro,
                right_gyro_abs,
                right_steer
            )

        else:
            corrected = zero_steer

        corrected = float(corrected)
        corrected = max(STEER_MIN, min(STEER_MAX, corrected))

        X_data.append([desired])
        Y_data.append([corrected])

        print({
            "desired_steer": desired,
            "corrected_steer": corrected,
            "corrected_command_wheel_angle_deg": estimate_wheel_angle_from_steer(corrected)
        })

    return zero_steer, X_data, Y_data


# ============================================================
# 3. AI Linear Regression 학습
# ============================================================

def train_alignment_model(X_data, Y_data):
    LR = AI.Linear_Regression()

    try:
        LR.restore = False
    except Exception:
        pass

    try:
        LR.ckpt_name = "wheel_alignment_" + str(int(time.time()))
    except Exception:
        pass

    LR.X_data = X_data
    LR.Y_data = Y_data

    train_lr(LR, times=1000)

    return LR


# ============================================================
# 4. 보정 조향값 계산
# ============================================================

def calibrated_steering(LR, desired_steer, zero_steer):
    desired_steer = float(desired_steer)
    desired_steer = max(-1.0, min(1.0, desired_steer))

    lr_corrected = lr_value(LR, desired_steer)

    if desired_steer < 0:
        gain = LEFT_GAIN
    elif desired_steer > 0:
        gain = RIGHT_GAIN
    else:
        gain = 1.0

    corrected = zero_steer + gain * (lr_corrected - zero_steer)
    corrected = max(STEER_MIN, min(STEER_MAX, corrected))

    return corrected


# ============================================================
# 5. AI 보정 결과 확인
# ============================================================

def print_ai_result(LR, zero_steer):
    print("===== AI 보정 결과 확인 =====")

    for desired in np.linspace(-1.0, 1.0, 11):
        desired = round(float(desired), 1)

        lr_corrected = lr_value(LR, desired)

        final_corrected = calibrated_steering(
            LR=LR,
            desired_steer=desired,
            zero_steer=zero_steer
        )

        print({
            "desired": desired,
            "LR_corrected": lr_corrected,
            "final_corrected": final_corrected,
            "command_wheel_angle_deg": estimate_wheel_angle_from_steer(final_corrected)
        })


# ============================================================
# 6. 보정된 조향값으로 gyro / 조향각 검증
# ============================================================

def verify_alignment_with_gyro(car, LR, zero_steer):
    print("===== Gyro 기반 얼라인먼트 검증 =====")

    test_values = [-1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0]

    result = {
        "desired": [],
        "corrected": [],
        "gyro": [],
        "gyro_dps": [],
        "yaw_angle_deg": [],
        "wheel_angle_deg": [],
        "command_wheel_angle_deg": []
    }

    try:
        for desired in test_values:
            desired = round(float(desired), 1)

            corrected = calibrated_steering(
                LR=LR,
                desired_steer=desired,
                zero_steer=zero_steer
            )

            measured = move_forward_and_measure(
                car=car,
                steer=corrected,
                speed=SPEED,
                move_time=MOVE_TIME
            )

            move_backward_return(
                car=car,
                steer=corrected,
                speed=SPEED,
                back_time=BACK_TIME
            )

            result["desired"].append(desired)
            result["corrected"].append(corrected)
            result["gyro"].append(measured["gyro"])
            result["gyro_dps"].append(measured["gyro_dps"])
            result["yaw_angle_deg"].append(measured["yaw_angle_deg"])
            result["wheel_angle_deg"].append(measured["wheel_angle_deg"])
            result["command_wheel_angle_deg"].append(measured["command_wheel_angle_deg"])

            print({
                "desired": desired,
                "corrected": corrected,
                "command_wheel_angle_deg": measured["command_wheel_angle_deg"],
                "gyro_raw": measured["gyro"],
                "gyro_dps": measured["gyro_dps"],
                "yaw_angle_deg": measured["yaw_angle_deg"],
                "estimated_wheel_angle_deg": measured["wheel_angle_deg"]
            })

            time.sleep(0.3)

    finally:
        car.stop()

    print("===== 좌우 대칭성 확인 =====")

    for level in [0.2, 0.4, 0.6, 0.8, 1.0]:
        left_desired = round(-level, 1)
        right_desired = round(level, 1)

        if left_desired not in result["desired"]:
            continue

        if right_desired not in result["desired"]:
            continue

        left_idx = result["desired"].index(left_desired)
        right_idx = result["desired"].index(right_desired)

        left_gyro = result["gyro"][left_idx]
        right_gyro = result["gyro"][right_idx]

        left_yaw = result["yaw_angle_deg"][left_idx]
        right_yaw = result["yaw_angle_deg"][right_idx]

        left_wheel_angle = result["wheel_angle_deg"][left_idx]
        right_wheel_angle = result["wheel_angle_deg"][right_idx]

        left_abs = abs(left_gyro)
        right_abs = abs(right_gyro)

        diff = abs(left_abs - right_abs)
        avg = (left_abs + right_abs) / 2

        if avg == 0:
            error_rate = 0.0
        else:
            error_rate = diff / avg * 100

        print({
            "level": level,
            "left_gyro": left_gyro,
            "right_gyro": right_gyro,
            "left_yaw_angle_deg": left_yaw,
            "right_yaw_angle_deg": right_yaw,
            "left_estimated_wheel_angle_deg": left_wheel_angle,
            "right_estimated_wheel_angle_deg": right_wheel_angle,
            "gyro_error_rate_percent": error_rate
        })

    return result


# ============================================================
# 7. 실제 주행 테스트
# ============================================================

def run_test(car, LR, zero_steer):
    print("===== 실제 주행 테스트 =====")

    try:
        for desired in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            corrected = calibrated_steering(
                LR=LR,
                desired_steer=desired,
                zero_steer=zero_steer
            )

            print({
                "desired": desired,
                "corrected": corrected,
                "command_wheel_angle_deg": estimate_wheel_angle_from_steer(corrected)
            })

            car.steering = corrected
            car_forward(car, SPEED)
            time.sleep(MOVE_TIME)

            car.stop()
            time.sleep(0.2)

            car.steering = corrected
            car_backward(car, SPEED)
            time.sleep(BACK_TIME)

            car.stop()
            time.sleep(0.5)

    finally:
        car.stop()


# ============================================================
# 전체 실행
# ============================================================

def main():
    dataset = collect_response_data(Car)

    print("===== 측정 데이터 =====")
    print(dataset)

    zero_steer, X_data, Y_data = make_training_data(dataset)

    print("===== AI 학습 데이터 =====")
    print("X_data:", X_data)
    print("Y_data:", Y_data)

    LR = train_alignment_model(X_data, Y_data)

    print_ai_result(LR, zero_steer)

    verify_result = verify_alignment_with_gyro(
        car=Car,
        LR=LR,
        zero_steer=zero_steer
    )

    run_test(Car, LR, zero_steer)


if __name__ == "__main__":
    main()