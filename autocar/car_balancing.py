import time

from pop import Pilot

# ============================================================
# AutoCar 객체 생성
# ============================================================

Car = Pilot.AutoCar()


# ============================================================
# 설정값
# ============================================================

SPEED = 60

# 전체 주행 시간
RUN_TIME = 5.0

# 제어 주기
CONTROL_DT = 0.05

# getGyro("z")가 raw 값이면 MPU6050 기준 보통 1 / 131
# getGyro("z")가 이미 deg/s라면 1.0으로 변경
GYRO_SCALE = 1.0 / 131.0

# 정지 상태에서 gyro bias 측정 시간
BIAS_CALIB_TIME = 2.0

# 자세 제어 게인
K_YAW = 0.035
K_GYRO = 0.015

# 중요:
# 조향 방향이 반대로 걸리면 -1.0
# 조향 방향이 정상이라면 1.0
STEER_SIGN = -1.0

# 조향 제한
STEER_MIN = -1.0
STEER_MAX = 1.0

# 노이즈 무시 범위
GYRO_DEADBAND = 0.3
YAW_DEADBAND = 0.5

# 전체 제어 출력 크기
CONTROL_GAIN = 1.0


# ============================================================
# 기본 함수
# ============================================================

def clip(value, min_value, max_value):
    return max(min_value, min(max_value, float(value)))


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


def get_gyro_z_raw(car):
    return float(car.getGyro("z"))


def get_gyro_z_dps(car, gyro_bias_raw):
    raw = get_gyro_z_raw(car)

    corrected_raw = raw - gyro_bias_raw
    gyro_dps = corrected_raw * GYRO_SCALE

    if abs(gyro_dps) < GYRO_DEADBAND:
        gyro_dps = 0.0

    return raw, corrected_raw, gyro_dps


# ============================================================
# gyro bias 측정
# ============================================================

def calibrate_gyro_bias(car, sec=2.0):
    print("===== gyro bias 측정 시작 =====")
    print("차량을 움직이지 말고 기다리세요.")

    values = []
    start = time.time()

    while time.time() - start < sec:
        z = get_gyro_z_raw(car)
        values.append(z)
        time.sleep(0.02)

    bias = sum(values) / len(values)

    print({
        "gyro_bias_raw": bias,
        "sample_count": len(values)
    })

    print("===== gyro bias 측정 완료 =====")

    return bias


# ============================================================
# 초기 방향 유지 제어
# ============================================================

def hold_initial_heading(car, speed=60, run_time=5.0):
    gyro_bias_raw = calibrate_gyro_bias(
        car=car,
        sec=BIAS_CALIB_TIME
    )

    yaw_angle = 0.0
    target_yaw = 0.0

    print("===== 초기 방향 유지 주행 시작 =====")
    print("target_yaw:", target_yaw)

    car.steering = 0.0
    car_forward(car, speed)

    start_time = time.time()
    last_time = start_time

    log = {
        "time": [],
        "gyro_raw": [],
        "gyro_dps": [],
        "yaw_angle": [],
        "yaw_error": [],
        "steer_cmd": []
    }

    try:
        while True:
            now = time.time()
            dt = now - last_time
            last_time = now

            if dt <= 0:
                dt = CONTROL_DT

            gyro_raw, gyro_corrected_raw, gyro_dps = get_gyro_z_dps(
                car=car,
                gyro_bias_raw=gyro_bias_raw
            )

            # gyro 적분으로 현재 방향 추정
            yaw_angle += gyro_dps * dt

            # 출발 방향을 유지해야 하므로 목표 yaw는 0
            yaw_error = target_yaw - yaw_angle

            if abs(yaw_error) < YAW_DEADBAND:
                yaw_error_for_control = 0.0
            else:
                yaw_error_for_control = yaw_error

            # ==================================================
            # 수정된 제어식
            # ==================================================
            # base_cmd는 이론적인 보정값
            # STEER_SIGN으로 실제 차량의 조향 방향을 맞춘다.
            # 지금 테스트 결과에서는 반대로 걸렸으므로 STEER_SIGN = -1.0
            # ==================================================

            base_cmd = (
                K_YAW * yaw_error_for_control
                - K_GYRO * gyro_dps
            )

            steer_cmd = STEER_SIGN * base_cmd
            steer_cmd = steer_cmd * CONTROL_GAIN
            steer_cmd = clip(steer_cmd, STEER_MIN, STEER_MAX)

            car.steering = steer_cmd

            t = now - start_time

            log["time"].append(t)
            log["gyro_raw"].append(gyro_raw)
            log["gyro_dps"].append(gyro_dps)
            log["yaw_angle"].append(yaw_angle)
            log["yaw_error"].append(yaw_error)
            log["steer_cmd"].append(steer_cmd)

            print({
                "time": round(t, 2),
                "gyro_raw": round(gyro_raw, 3),
                "gyro_dps": round(gyro_dps, 3),
                "yaw_angle_deg": round(yaw_angle, 3),
                "yaw_error_deg": round(yaw_error, 3),
                "base_cmd": round(base_cmd, 3),
                "steer_cmd": round(steer_cmd, 3)
            })

            time.sleep(CONTROL_DT)

            if t >= run_time:
                break

    finally:
        car.stop()
        print("===== 주행 종료 =====")

    return log


# ============================================================
# 전진 후 후진 복귀 테스트
# ============================================================

def hold_initial_heading_forward_backward(car):
    log = hold_initial_heading(
        car=car,
        speed=SPEED,
        run_time=RUN_TIME
    )

    time.sleep(0.5)

    print("===== 후진 복귀 =====")

    car.steering = 0.0
    car_backward(car, SPEED)
    time.sleep(RUN_TIME)
    car.stop()

    return log


# ============================================================
# 실행
# ============================================================

if __name__ == "__main__":
    hold_initial_heading_forward_backward(Car)