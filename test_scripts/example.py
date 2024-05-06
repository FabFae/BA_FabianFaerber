from argparse import ArgumentParser

import RPi.GPIO as GPIO
import time


class GpioDevice:
    def initialize(self):
        GPIO.setmode(GPIO.BCM)

    def cleanup(self):
        pass

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


class StepperMotor(GpioDevice):
    def __init__(
        self,
        step_pin,
        dir_pin,
        enable_pin,
        steps_per_rev,
        step_time=0.001,
        step_delay=0.001,
        auto_disable: bool = True,
    ):
        self.step_pin = step_pin
        self.dir_pin = dir_pin
        self.enable_pin = enable_pin
        self.steps_per_rev = steps_per_rev
        self.step_time = step_time
        self.step_delay = step_delay
        self.auto_disable = auto_disable

    def initialize(self):
        super().initialize()
        GPIO.setup(self.enable_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.step_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.dir_pin, GPIO.OUT, initial=GPIO.LOW)
        if self.auto_disable:
            self.disable()

    def cleanup(self):
        super().cleanup()
        GPIO.cleanup(self.enable_pin)
        GPIO.cleanup(self.step_pin)
        GPIO.cleanup(self.dir_pin)

    def enable(self):
        GPIO.output(self.enable_pin, GPIO.LOW)

    def disable(self):
        GPIO.output(self.enable_pin, GPIO.HIGH)

    def step(self, steps=1):
        try:
            self.enable()
            GPIO.output(self.dir_pin, GPIO.HIGH if steps > 0 else GPIO.LOW)
            for _ in range(abs(steps)):
                GPIO.output(self.step_pin, GPIO.HIGH)
                time.sleep(self.step_time)
                GPIO.output(self.step_pin, GPIO.LOW)
                time.sleep(self.step_delay)
        finally:
            if self.auto_disable:
                self.disable()

    def rotate(self, *, angle: float):
        self.step(steps=int(angle / 360 * self.steps_per_rev))


class CameraTrigger(GpioDevice):
    def __init__(self, trigger_pin: int = 10, trigger_time=0.1):
        self.trigger_pin = trigger_pin
        self.trigger_time = trigger_time

    def initialize(self):
        super().initialize()
        GPIO.setup(self.trigger_pin, GPIO.OUT, initial=GPIO.LOW)

    def cleanup(self):
        super().cleanup()
        GPIO.cleanup(self.trigger_pin)

    def __call__(self):
        GPIO.output(self.trigger_pin, GPIO.HIGH)
        time.sleep(self.trigger_time)
        GPIO.output(self.trigger_pin, GPIO.LOW)


class RingLight(GpioDevice):
    def __init__(self, pin_1: int = 17, pin_2: int = 27):
        self.pin_1 = pin_1
        self.pin_2 = pin_2

    def __call__(self, led_set_1: bool = False, led_set_2: bool = False):
        GPIO.output(self.pin_1, GPIO.HIGH if led_set_1 else GPIO.LOW)
        GPIO.output(self.pin_2, GPIO.HIGH if led_set_2 else GPIO.LOW)

    def initialize(self):
        super().initialize()
        GPIO.setup(self.pin_1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(self.pin_2, GPIO.OUT, initial=GPIO.LOW)
        return self

    def cleanup(self):
        super().cleanup()
        GPIO.output(self.pin_1, GPIO.LOW)
        GPIO.cleanup(self.pin_1)
        GPIO.output(self.pin_2, GPIO.LOW)
        # GPIO.cleanup(self.pin_2)


class OpenScanClassic:
    parser = ArgumentParser(
        description="Capture photos with turntable and angle control."
    )
    parser.add_argument(
        "--photos-per-row", type=int, help="Number of photos per rotation", required=True
    )
    parser.add_argument(
        "--angle-step", type=int, help="Angle step for the arm control", required=True
    )
    parser.add_argument(
        "--camera-trigger-time", type=int, help="Time to wait after camera is triggered", required=True
    )

    def __init__(
        self, photos_per_row: int, angle_step: int, camera_trigger_time: float
    ):
        self.photos_per_row = photos_per_row
        self.angle_step = angle_step

        self.arm = StepperMotor(
            step_pin=6,
            dir_pin=5,
            enable_pin=23,
            # 40000 = 200 steps per revolution of the stepper * 16 (micro stepping mode from my drivers)
            # * 15 (gear ratio between small and large gear).
            steps_per_rev=40000,
            step_time=0.0001,
            step_delay=0.00005,
        )
        self.turntable = StepperMotor(
            step_pin=11,
            dir_pin=9,
            enable_pin=22,
            steps_per_rev=3200,
            step_time=0.0001,
            step_delay=0.00005,
        )
        self.trigger = CameraTrigger(trigger_time=camera_trigger_time)

    def run(self):
        start_angle = 45
        end_angle = 180

        with self.arm as arm, self.turntable as turntable, self.trigger as trigger:
            row_angle = 360 / self.photos_per_row
            previous_angle = start_angle
            for next_angle in range(start_angle, end_angle + 1, self.angle_step):
                print(f"Angle: {next_angle} started")
                arm.rotate(angle=next_angle - previous_angle)
                previous_angle = next_angle
                for j in range(0, self.photos_per_row):
                    print(f"\tCapturing {j}/{self.photos_per_row}: {j * row_angle} deg")
                    trigger()
                    turntable.rotate(angle=row_angle)
                print(f"Angle: {next_angle} completed\n")


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Capture photos with turntable and angle control."
    )
    parser.add_argument(
        "--device",
        type=str,
        help="Mini|Classic",
        choices=["Mini", "Classic"],
        required=True,
    )
    device_cls = {"Mini": OpenScanClassic, "Classic": OpenScanClassic}[
        vars(parser.parse_known_args()[0])["device"]
    ]

    kwargs = vars(device_cls.parser.parse_known_args()[0])
    input("Reset position to starting one then <enter>")
    device_cls(**kwargs).run()
