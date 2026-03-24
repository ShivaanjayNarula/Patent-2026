# Modular Software Architecture (ESP32/STM32, MicroPython)

## Layering
- Hardware Abstraction Layer (HAL) for GPIO, SPI/Parallel camera, I2C IMU, ADC/Depth, PWM/Servo, Stepper drivers, Flash, Acoustic modem UART.
- Perception layer for event camera ISR, event buffering, and SNN inference.
- Control layer for navigation PID and thruster mixing.
- Decision layer for restoration gating and treated-location memory.
- Actuation layer for gantry indexing and pod release.
- System layer for workflow state machine and telemetry/logging.

## Modules
- `pins.py`: Pin map for ESP32/STM32.
- `hal.py`: Peripheral wrappers for SPI, I2C, UART, PWM, GPIO, Flash.
- `vision.py`: Event camera ISR, event ring buffer, SNN interface.
- `navigation.py`: PID controllers, depth hold, attitude hold, thruster mixing.
- `restoration.py`: Confidence gating, depth limit checks, treated-location memory.
- `deployment.py`: X-Y gantry indexing, limit switches, pod release counter.
- `telemetry.py`: Flash logging and acoustic modem packet preparation.
- `state_machine.py`: Scan-Detect-Deploy-Log workflow.
- `main.py`: System init loop.

## State Machine
- `SCAN`: collect events, run SNN periodically.
- `DETECT`: evaluate classification + confidence.
- `DEPLOY`: index gantry, release pods, confirm count.
- `LOG`: persist data and prep telemetry.
- `FAILSAFE`: halt actuators and wait for manual reset.

