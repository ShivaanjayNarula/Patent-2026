# Autonomous Neuromorphic Underwater Coral Restoration System

## Overview
An autonomous underwater platform that detects coral degradation in real time using event-based vision and neuromorphic processing, then performs immediate, localized restoration via an indexed X–Y pod deployment mechanism. The system minimizes latency, bandwidth, and energy use by processing event streams on-device, eliminating dependence on remote analysis or human intervention.

## Goals
- Real-time detection and classification of coral health (Healthy/Damaged/Decomposed).
- Immediate, precise deployment of restoration pods at detected locations.
- Energy-efficient, long-duration underwater operation with minimal bandwidth.
- Avoid redundant deployment using location memory and confidence-based logic.

## Non-Goals
- Full reef mapping at survey-grade resolution.
- Continuous live video streaming to surface in all conditions.
- Manual diver-operated restoration workflows.

## System Architecture (High Level)
- Mobility subsystem for navigation and station-keeping.
- Perception subsystem using event-based camera and optional spawning/egg sensing.
- Neuromorphic compute subsystem (SNN processor + MCU) for classification and control.
- Deployment subsystem with indexed X–Y gantry and controlled multi-pod release.
- Logging and comms subsystem for storage and surface reporting.

## Subsystems and Components

### 1) Mobility and Housing
**Purpose:** Underwater navigation, stability, and protection of electronics.
- Waterproof pressure-sealed enclosure.
- Vectored thrusters + ESC drivers.
- IMU for orientation and tilt.
- Depth/pressure sensor for depth holding.
- Battery pack + power management.

### 2) Perception (Event-Driven Vision)
**Purpose:** Low-latency, low-power coral surface scanning.
- Event-based camera module.
- Dual fixed LED illumination.
- Optical lens and mounting frame.

### 3) Optional Spawning/Egg Detection Module
**Purpose:** Detect gamete/larvae presence for logging and restoration planning.
- Macro optical sensor / micro-camera + LED.
- Turbidity/particle sensor (flow-through).
- Micro-pump + micro-filter sampling chamber (optional).

### 4) Neuromorphic Processing
**Purpose:** On-device classification from event streams.
- SNN processor (neuromorphic AI chip).
- Embedded MCU (e.g., ESP32/STM32) for control logic.
- Local storage (Flash/SSD).

### 5) Decision Logic and Safety
**Purpose:** Gate deployment with confidence, stability, and safety checks.
- Confidence threshold check.
- Stable hovering verification (IMU + depth).
- Obstacle/jam detection feedback.
- Treated-location memory to prevent duplicate release.

### 6) X–Y Indexed Deployment
**Purpose:** Precise pod selection and positioning in a 10x10 grid.
- X-axis stepper motor + linear rail.
- Y-axis stepper motor + linear rail.
- Encoders or limit switches.
- Pod storage grid (100 pods).

### 7) Multi-Pod Release
**Purpose:** Controlled dispensing of exactly 10 pods per treatment.
- Servo-actuated release gate.
- Pod counter sensor (IR/limit/hall).
- Discharge chute/outlet port.

### 8) Logging and Communication
**Purpose:** Record actions and transmit summaries when possible.
- Storage module (SSD/Flash).
- Communication module (acoustic modem / RF at surface).
- GPS at surface + underwater localization (as available).

## Data Flow
1. Event-based camera produces event stream (ON/OFF pixel changes).
2. SNN processes events and classifies coral health with confidence score.
3. MCU applies decision logic (confidence, stability, location memory, jam check).
4. X–Y gantry indexes to target pod coordinates.
5. Release gate dispenses exactly 10 pods; counter validates count.
6. Log events, classification, deployment count, and location.
7. Resume scanning for next target.

## Control Flow (Stepwise)
1. Deploy underwater; stabilize at target depth.
2. Scan coral surface using event-driven vision.
3. (Optional) Spawn/egg detection and logging.
4. SNN classification: Healthy/Damaged/Decomposed + confidence.
5. Safety checks and location memory verification.
6. Index gantry to selected pod coordinate.
7. Release 10 pods; confirm via counter sensor.
8. Log and optionally transmit summary.
9. Continue scanning.

## Interfaces and Signals
- Event camera -> SNN input (event stream).
- SNN -> MCU (classification + confidence score).
- MCU -> Thrusters (position hold commands).
- MCU -> Gantry motors (indexing commands).
- MCU -> Release gate (actuation signal).
- Sensors -> MCU (IMU, depth, jam, pod counter).

## Safety and Reliability Considerations
- Confidence thresholding to reduce false deployments.
- Station-keeping validation prior to release.
- Jam detection and recovery sequence.
- Treated-location memory to avoid redundant release.
- Electric indexing mechanism to reduce hydraulic leakage risk.

## Deployment Logic (Pseudo)
- If classification == Damaged/Decomposed AND confidence >= threshold:
  - If stable_hover == true AND location_not_treated == true AND no_jam == true:
    - Index gantry to target pod coordinates.
    - Release 10 pods and validate count.
    - Log deployment and mark location as treated.

## Key Innovations
- Event-based sensing with on-device SNN processing for real-time reef assessment.
- Closed-loop detection-to-restoration architecture with minimal latency.
- Indexed X–Y gantry for precise multi-pod deployment.
- Confidence-based and location-aware deployment logic.

