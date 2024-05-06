import time
import RPi.GPIO as GPIO


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

    def step(self, steps=1, invert_direction=False):
        try:
            self.enable()
            if invert_direction:
                GPIO.output(self.dir_pin, GPIO.HIGH if steps < 0 else GPIO.LOW)
            else:
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


def rotate_motor(horizontal=False, invert_direction=False):
    if not horizontal:
        step_pin = 6,
        dir_pin = 5,
        enable_pin = 23
    else:
        step_pin = 11,
        dir_pin = 9,
        enable_pin = 22

    current_motor = StepperMotor(
        step_pin=step_pin,
        dir_pin=dir_pin,
        enable_pin=enable_pin,
        steps_per_rev=40000,
        step_time=0.0001,
        step_delay=0.00005,
    )
    current_motor.initialize()

    start_angle = 0
    end_angle = 1
    angle_steps = 1

    for next_angle in range(start_angle, end_angle + 1, angle_steps):
        current_motor.step(1, invert_direction=invert_direction)

    current_motor.cleanup()
