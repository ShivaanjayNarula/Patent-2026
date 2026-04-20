"""MicroPython-style firmware skeleton for ESP32/STM32.
This is a hardware-lean reference architecture with explicit pin definitions,
ISRs, and a Scan-Detect-Deploy-Log state machine.
"""

from machine import Pin, SPI, I2C, UART, PWM, ADC
import time


# =========================
# Pin Definitions
# =========================
class Pins:
    # Event camera (SPI or Parallel). Example uses SPI + IRQ.
    CAM_SPI_SCK = 18
    CAM_SPI_MOSI = 23
    CAM_SPI_MISO = 19
    CAM_SPI_CS = 5
    CAM_IRQ = 4

    # IMU (I2C)
    IMU_SDA = 21
    IMU_SCL = 22

    # Depth sensor (ADC example)
    DEPTH_ADC = 34

    # Thrusters (PWM)
    THRUSTER_FL = 25
    THRUSTER_FR = 26
    THRUSTER_RL = 27
    THRUSTER_RR = 14

    # Gantry steppers (step/dir)
    GANTRY_X_STEP = 32
    GANTRY_X_DIR = 33
    GANTRY_Y_STEP = 12
    GANTRY_Y_DIR = 13

    # Limit switches
    LIM_X_MIN = 15
    LIM_X_MAX = 2
    LIM_Y_MIN = 0
    LIM_Y_MAX = 16

    # Servo gate
    SERVO_GATE = 17

    # Pod counter (digital input)
    POD_COUNTER = 35

    # Acoustic modem (UART)
    MODEM_TX = 1
    MODEM_RX = 3


# =========================
# HAL
# =========================
class EventBuffer:
    def __init__(self, size=1024):
        self.size = size
        self.buf = [0] * size
        self.head = 0
        self.count = 0

    def push(self, val):
        self.buf[self.head] = val
        self.head = (self.head + 1) % self.size
        self.count = min(self.count + 1, self.size)

    def read_all(self):
        # Simple snapshot read
        return self.buf[: self.count]


class EventCameraHAL:
    def __init__(self):
        self.spi = SPI(
            1,
            baudrate=10_000_000,
            polarity=0,
            phase=0,
            sck=Pin(Pins.CAM_SPI_SCK),
            mosi=Pin(Pins.CAM_SPI_MOSI),
            miso=Pin(Pins.CAM_SPI_MISO),
        )
        self.cs = Pin(Pins.CAM_SPI_CS, Pin.OUT, value=1)
        self.irq_pin = Pin(Pins.CAM_IRQ, Pin.IN)
        self.buffer = EventBuffer(size=2048)
        self.irq_pin.irq(trigger=Pin.IRQ_RISING, handler=self._irq_handler)

    def _irq_handler(self, pin):
        # Interrupt handler reads a burst of event bytes
        self.cs.off()
        raw = self.spi.read(16)  # fixed burst; tune as needed
        self.cs.on()
        for b in raw:
            self.buffer.push(b)

    def read_events(self):
        return self.buffer.read_all()


class IMUHAL:
    def __init__(self):
        self.i2c = I2C(0, sda=Pin(Pins.IMU_SDA), scl=Pin(Pins.IMU_SCL), freq=400_000)

    def read_orientation(self):
        # Replace with real IMU registers
        return 0.0, 0.0, 0.0  # roll, pitch, yaw


class DepthSensorHAL:
    def __init__(self):
        self.adc = ADC(Pin(Pins.DEPTH_ADC))
        self.adc.atten(ADC.ATTN_11DB)

    def read_depth_m(self):
        raw = self.adc.read()
        return (raw / 4095.0) * 40.0  # scale to 40m range


class ThrusterHAL:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin), freq=50)

    def set_thrust(self, us):
        # Map microseconds to duty (ESP32: 0-1023)
        duty = int((us / 2000.0) * 1023)
        self.pwm.duty(duty)


class StepperHAL:
    def __init__(self, step_pin, dir_pin):
        self.step = Pin(step_pin, Pin.OUT)
        self.dir = Pin(dir_pin, Pin.OUT)

    def step_n(self, steps, direction):
        self.dir.value(1 if direction > 0 else 0)
        for _ in range(steps):
            self.step.on()
            time.sleep_us(400)
            self.step.off()
            time.sleep_us(400)


class ServoHAL:
    def __init__(self, pin):
        self.pwm = PWM(Pin(pin), freq=50)

    def set_angle(self, angle):
        us = 500 + int((angle / 180.0) * 2000)
        duty = int((us / 2000.0) * 1023)
        self.pwm.duty(duty)


class FlashLogger:
    def __init__(self):
        self.records = []

    def append(self, record):
        self.records.append(record)


class ModemHAL:
    def __init__(self):
        self.uart = UART(1, baudrate=9600, tx=Pin(Pins.MODEM_TX), rx=Pin(Pins.MODEM_RX))

    def prepare_packet(self, data):
        return str(data).encode("utf-8")

    def transmit(self, data):
        self.uart.write(data)


# =========================
# Vision & SNN
# =========================
class TinyMLRunner:
    \"\"\"Thin wrapper around TFLite Micro or tflite_runtime interpreter.
    Expects a model with a single input vector and 3-class output.
    \"\"\"

    def __init__(self, model_path=\"/flash/snn_model.tflite\", input_len=64):
        self.model_path = model_path
        self.input_len = input_len
        self.interpreter = None
        self.input_index = None
        self.output_index = None
        self._init_interpreter()

    def _init_interpreter(self):
        # Prefer MicroPython TFLM module when available.
        try:
            from tflite_micro import Interpreter  # type: ignore
        except Exception:
            Interpreter = None

        if Interpreter is None:
            try:
                from tflite_runtime.interpreter import Interpreter  # type: ignore
            except Exception:
                Interpreter = None

        if Interpreter is None:
            raise RuntimeError(\"No TFLite interpreter available on this build.\")

        self.interpreter = Interpreter(model_path=self.model_path)
        self.interpreter.allocate_tensors()
        in_details = self.interpreter.get_input_details()
        out_details = self.interpreter.get_output_details()
        self.input_index = in_details[0][\"index\"]
        self.output_index = out_details[0][\"index\"]

    def infer(self, features):
        self.interpreter.set_tensor(self.input_index, features)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_index)


def extract_features(events, feature_len=64):
    \"\"\"Convert raw event bytes into a fixed-length feature vector.\n+    Uses a simple modulo histogram for deterministic, low-cost features.\n+    \"\"\"\n+    feats = [0] * feature_len\n+    if not events:\n+        return [0] * feature_len\n+    for b in events:\n+        feats[b % feature_len] += 1\n+    # Normalize to [0,1]\n+    total = len(events)\n+    return [[f / total for f in feats]]  # 2D batch\n+\n+\n+class SNNModel:\n+    def __init__(self, model_path=\"/flash/snn_model.tflite\"):\n+        self.runner = TinyMLRunner(model_path=model_path)\n+\n+    def infer(self, events):\n+        if not events:\n+            return \"healthy\", 0.5\n+        features = extract_features(events)\n+        logits = self.runner.infer(features)[0]\n+        # Argmax over 3 classes\n+        idx = 0\n+        best = logits[0]\n+        for i in range(1, 3):\n+            if logits[i] > best:\n+                best = logits[i]\n+                idx = i\n+        labels = [\"healthy\", \"damaged\", \"decomposed\"]\n+        confidence = float(best)\n+        return labels[idx], confidence


class VisionModule:
    def __init__(self, cam):
        self.cam = cam
        self.snn = SNNModel()

    def classify(self):
        events = self.cam.read_events()
        label, conf = self.snn.infer(events)
        return label, conf


# =========================
# Navigation
# =========================
class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.integral = 0.0
        self.prev = 0.0

    def update(self, error, dt):
        self.integral += error * dt
        derivative = (error - self.prev) / dt if dt > 0 else 0.0
        self.prev = error
        return self.kp * error + self.ki * self.integral + self.kd * derivative


class NavigationModule:
    def __init__(self, imu, depth, thrusters):
        self.imu = imu
        self.depth = depth
        self.thrusters = thrusters
        self.pid_depth = PID(1.2, 0.05, 0.2)

    def hold_depth(self, target_depth, dt):
        depth_m = self.depth.read_depth_m()
        error = target_depth - depth_m
        thrust = self.pid_depth.update(error, dt)
        for t in self.thrusters:
            t.set_thrust(1500 + int(thrust))
        return depth_m


# =========================
# Restoration Logic
# =========================
class RestorationLogic:
    def __init__(self, confidence_threshold=0.85, min_depth=2.0, max_depth=40.0):
        self.threshold = confidence_threshold
        self.min_depth = min_depth
        self.max_depth = max_depth
        self.treated = []

    def is_treated(self, x, y, radius=0.75):
        for tx, ty in self.treated:
            dx = x - tx
            dy = y - ty
            if (dx * dx + dy * dy) ** 0.5 <= radius:
                return True
        return False

    def mark_treated(self, x, y):
        self.treated.append((x, y))

    def should_deploy(self, label, confidence, depth_m, x, y):
        if confidence < self.threshold:
            return False
        if not (self.min_depth <= depth_m <= self.max_depth):
            return False
        if self.is_treated(x, y):
            return False
        return label in ("damaged", "decomposed")


# =========================
# Deployment Control
# =========================
class GantryControl:
    def __init__(self, x_stepper, y_stepper, lim_x_min, lim_x_max, lim_y_min, lim_y_max):
        self.x = x_stepper
        self.y = y_stepper
        self.lim_x_min = lim_x_min
        self.lim_x_max = lim_x_max
        self.lim_y_min = lim_y_min
        self.lim_y_max = lim_y_max
        self.grid = 10

    def home(self):
        # Simple homing
        while self.lim_x_min.value() == 1:
            self.x.step_n(1, -1)
        while self.lim_y_min.value() == 1:
            self.y.step_n(1, -1)

    def index_to(self, gx, gy):
        # Minimal stepper moves; replace with calibrated steps-per-cell
        self.x.step_n(gx * 50, 1)
        self.y.step_n(gy * 50, 1)


class PodRelease:
    def __init__(self, servo, counter_pin):
        self.servo = servo
        self.counter = Pin(counter_pin, Pin.IN)

    def release(self, count=10):
        released = 0
        for _ in range(count):
            self.servo.set_angle(90)
            time.sleep_ms(200)
            self.servo.set_angle(0)
            time.sleep_ms(200)
            released += 1
        return released


# =========================
# Telemetry
# =========================
class Telemetry:
    def __init__(self, flash, modem):
        self.flash = flash
        self.modem = modem

    def log(self, record):
        self.flash.append(record)

    def transmit_latest(self):
        if not self.flash.records:
            return
        packet = self.modem.prepare_packet(self.flash.records[-1])
        self.modem.transmit(packet)


# =========================
# State Machine
# =========================
class StateMachine:
    SCAN = 0
    DETECT = 1
    DEPLOY = 2
    LOG = 3
    FAILSAFE = 4

    def __init__(self, vision, nav, logic, gantry, release, telemetry):
        self.state = self.SCAN
        self.vision = vision
        self.nav = nav
        self.logic = logic
        self.gantry = gantry
        self.release = release
        self.telemetry = telemetry
        self.last_label = "healthy"
        self.last_conf = 0.0
        self.last_depth = 0.0
        self.pose_x = 0.0
        self.pose_y = 0.0

    def tick(self, dt):
        if self.state == self.SCAN:
            self.last_depth = self.nav.hold_depth(10.0, dt)
            self.state = self.DETECT

        elif self.state == self.DETECT:
            label, conf = self.vision.classify()
            self.last_label = label
            self.last_conf = conf
            self.state = self.DEPLOY

        elif self.state == self.DEPLOY:
            if self.logic.should_deploy(
                self.last_label, self.last_conf, self.last_depth, self.pose_x, self.pose_y
            ):
                self.gantry.index_to(3, 4)
                released = self.release.release(10)
                self.logic.mark_treated(self.pose_x, self.pose_y)
                self.telemetry.log(
                    {
                        "label": self.last_label,
                        "conf": self.last_conf,
                        "depth": self.last_depth,
                        "released": released,
                    }
                )
            self.state = self.LOG

        elif self.state == self.LOG:
            self.telemetry.transmit_latest()
            self.state = self.SCAN

        else:
            # FAILSAFE
            pass


# =========================
# Main
# =========================
def main():
    cam = EventCameraHAL()
    imu = IMUHAL()
    depth = DepthSensorHAL()

    thrusters = [
        ThrusterHAL(Pins.THRUSTER_FL),
        ThrusterHAL(Pins.THRUSTER_FR),
        ThrusterHAL(Pins.THRUSTER_RL),
        ThrusterHAL(Pins.THRUSTER_RR),
    ]

    vision = VisionModule(cam)
    nav = NavigationModule(imu, depth, thrusters)
    logic = RestorationLogic()

    gantry = GantryControl(
        StepperHAL(Pins.GANTRY_X_STEP, Pins.GANTRY_X_DIR),
        StepperHAL(Pins.GANTRY_Y_STEP, Pins.GANTRY_Y_DIR),
        Pin(Pins.LIM_X_MIN, Pin.IN),
        Pin(Pins.LIM_X_MAX, Pin.IN),
        Pin(Pins.LIM_Y_MIN, Pin.IN),
        Pin(Pins.LIM_Y_MAX, Pin.IN),
    )

    release = PodRelease(ServoHAL(Pins.SERVO_GATE), Pins.POD_COUNTER)
    telemetry = Telemetry(FlashLogger(), ModemHAL())

    sm = StateMachine(vision, nav, logic, gantry, release, telemetry)

    last = time.ticks_ms()
    while True:
        now = time.ticks_ms()
        dt = time.ticks_diff(now, last) / 1000.0
        last = now
        sm.tick(dt)
        time.sleep_ms(50)


# Uncomment for direct execution in MicroPython
# main()
