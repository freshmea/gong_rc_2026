import json
import time

import numpy as np
from pop import Pilot

Car = Pilot.AutoCar()


# =========================
# 안전 설정값
# =========================

SPEED = 70          # 기존 70보다 낮게 시작 권장
MOVE_TIME = 0.70    # 앞으로 움직이는 시간
BACK_TIME = 0.70    # 뒤로 복귀하는 시간
STABLE_TIME = 0.15  # 정지 후 안정 시간

GYRO_COUNT = 8
GYRO_DELAY = 0.03


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


def get_gyro_avg(car, count=8, delay=0.03):
    values = []

    for _ in range(count):
        z = car.getGyro("z")
        values.append(float(z))
        time.sleep(delay)

    return sum(values) / len(values)


def move_forward_and_measure(car, steer, speed, move_time):
    """
    짧게 앞으로 이동하면서 gyro 평균을 측정
    """
    car.steering = steer
    car_forward(car, speed)

    start_time = time.time()
    gyro_values = []

    while time.time() - start_time < move_time:
        z = car.getGyro("z")
        gyro_values.append(float(z))
        time.sleep(GYRO_DELAY)

    car.stop()
    time.sleep(STABLE_TIME)

    if len(gyro_values) == 0:
        return 0.0

    return sum(gyro_values) / len(gyro_values)


def move_backward_return(car, steer, speed, back_time):
    """
    같은 steering 값으로 뒤로 복귀
    같은 steering을 유지해야 앞으로 간 곡선 경로를 되돌아오기 쉽다.
    """
    car.steering = steer
    car_backward(car, speed)

    time.sleep(back_time)

    car.stop()
    time.sleep(STABLE_TIME)


def collect_steering_data(car):
    dataset = {
        "steer": [],
        "gyro": []
    }

    car.setSpeed(SPEED)

    steer_values = np.linspace(-1.0, 1.0, 11)

    try:
        for steer in steer_values:
            steer = round(float(steer), 1)

            print("test steer:", steer)

            # 1. 앞으로 짧게 이동하면서 gyro 측정
            gyro_avg = move_forward_and_measure(
                car=car,
                steer=steer,
                speed=SPEED,
                move_time=MOVE_TIME
            )

            # 2. 같은 steering으로 뒤로 복귀
            move_backward_return(
                car=car,
                steer=steer,
                speed=SPEED,
                back_time=BACK_TIME
            )

            dataset["steer"].append(steer)
            dataset["gyro"].append(gyro_avg)

            print({
                "steer": steer,
                "gyro": gyro_avg
            })

            time.sleep(0.3)

    finally:
        car.stop()

    return dataset


class SteeringCalibrator:
    def __init__(self):
        self.steer_table = []
        self.gyro_table = []

        self.base_gyro = 0.0
        self.zero_correction = 0.0

        self.usable_gyro = 0.0

        self.left_steer = []
        self.left_delta = []

        self.right_steer = []
        self.right_delta = []

    def fit(self, steer_list, gyro_list):
        steer_arr = np.array(steer_list, dtype=float)
        gyro_arr = np.array(gyro_list, dtype=float)

        order = np.argsort(steer_arr)
        steer_arr = steer_arr[order]
        gyro_arr = gyro_arr[order]

        self.steer_table = steer_arr.tolist()
        self.gyro_table = gyro_arr.tolist()

        # steer=0에 가장 가까운 값의 gyro를 직진 기준으로 사용
        zero_idx = np.argmin(np.abs(steer_arr))
        self.base_gyro = float(gyro_arr[zero_idx])

        # 기준 gyro 대비 변화량
        delta_arr = gyro_arr - self.base_gyro

        # 실제로 가장 직진에 가까운 steering 값
        zero_correction_idx = np.argmin(np.abs(delta_arr))
        self.zero_correction = float(steer_arr[zero_correction_idx])

        left_mask = steer_arr < self.zero_correction
        right_mask = steer_arr > self.zero_correction

        left_steer = steer_arr[left_mask]
        left_delta = delta_arr[left_mask]

        right_steer = steer_arr[right_mask]
        right_delta = delta_arr[right_mask]

        if len(left_steer) < 2 or len(right_steer) < 2:
            raise ValueError("왼쪽/오른쪽 조향 데이터가 부족합니다.")

        self.left_steer = left_steer.tolist()
        self.left_delta = left_delta.tolist()

        self.right_steer = right_steer.tolist()
        self.right_delta = right_delta.tolist()

        left_max = max(abs(v) for v in self.left_delta)
        right_max = max(abs(v) for v in self.right_delta)

        # 좌우 모두 표현 가능한 공통 회전량
        self.usable_gyro = float(min(left_max, right_max))

        print("===== Calibration Result =====")
        print("base_gyro       :", self.base_gyro)
        print("zero_correction :", self.zero_correction)
        print("left_max_delta  :", left_max)
        print("right_max_delta :", right_max)
        print("usable_gyro     :", self.usable_gyro)

    def steering(self, desired_steer):
        """
        사용자가 원하는 steer -1.0 ~ 1.0을 넣으면
        실제 Car.steering에 넣을 보정값을 반환한다.
        """

        desired_steer = float(desired_steer)
        desired_steer = max(-1.0, min(1.0, desired_steer))

        if abs(desired_steer) < 1e-6:
            return self.zero_correction

        target_delta_abs = abs(desired_steer) * self.usable_gyro

        if desired_steer > 0:
            corrected = self._inverse_interpolate(
                target_delta_abs,
                self.right_steer,
                self.right_delta
            )
        else:
            corrected = self._inverse_interpolate(
                target_delta_abs,
                self.left_steer,
                self.left_delta
            )

        return max(-1.0, min(1.0, corrected))

    def _inverse_interpolate(self, target_delta_abs, steer_list, delta_list):
        steer_arr = np.array(steer_list, dtype=float)
        delta_abs_arr = np.abs(np.array(delta_list, dtype=float))

        order = np.argsort(delta_abs_arr)
        delta_abs_arr = delta_abs_arr[order]
        steer_arr = steer_arr[order]

        unique_delta = []
        unique_steer = []

        for d, s in zip(delta_abs_arr, steer_arr):
            if len(unique_delta) == 0 or abs(d - unique_delta[-1]) > 1e-6:
                unique_delta.append(d)
                unique_steer.append(s)

        if len(unique_delta) < 2:
            idx = np.argmin(np.abs(delta_abs_arr - target_delta_abs))
            return float(steer_arr[idx])

        return float(np.interp(
            target_delta_abs,
            unique_delta,
            unique_steer
        ))

    def save(self, path="steering_calibration.json"):
        data = {
            "steer_table": self.steer_table,
            "gyro_table": self.gyro_table,
            "base_gyro": self.base_gyro,
            "zero_correction": self.zero_correction,
            "usable_gyro": self.usable_gyro
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self, path="steering_calibration.json"):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.fit(data["steer_table"], data["gyro_table"])


def main():
    dataset = collect_steering_data(Car)

    print("===== Raw Dataset =====")
    print(dataset)

    calib = SteeringCalibrator()
    calib.fit(dataset["steer"], dataset["gyro"])
    calib.save()

    print("===== Calibrated Steering Table =====")

    for desired in np.linspace(-1.0, 1.0, 11):
        desired = round(float(desired), 1)
        corrected = calib.steering(desired)

        print({
            "desired": desired,
            "corrected": corrected
        })

    # 테스트 주행
    try:
        for desired in [-1.0, -0.5, 0.0, 0.5, 1.0]:
            corrected = calib.steering(desired)

            print("run:", {
                "desired": desired,
                "corrected": corrected
            })

            Car.steering = corrected
            car_forward(Car, SPEED)
            time.sleep(0.4)
            Car.stop()
            time.sleep(0.2)

            Car.steering = corrected
            car_backward(Car, SPEED)
            time.sleep(0.4)
            Car.stop()
            time.sleep(0.5)

    finally:
        Car.stop()


if __name__ == "__main__":
    main()