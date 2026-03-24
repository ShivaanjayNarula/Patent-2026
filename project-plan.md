# Project Plan: Autonomous Neuromorphic Underwater Coral Restoration System

## Objectives
- Build a prototype platform that autonomously detects coral degradation and deploys restoration pods.
- Validate energy efficiency, deployment accuracy, and real-time performance in controlled tests.
- Prepare documentation and evidence for patent submission and demonstration.

## Scope
**In Scope**
- Event-based vision integration.
- SNN-based classification on-device.
- Indexed X–Y gantry pod deployment (10x10 grid).
- Basic navigation and station-keeping.
- Logging and optional surface communication.

**Out of Scope (initial prototype)**
- Full reef-scale mapping.
- Long-duration field trials in open ocean.
- Advanced swarm coordination of multiple robots.

## Milestones and Deliverables

### 1) Requirements and Architecture (Week 1)
- Define functional requirements and performance targets.
- Finalize system architecture and interfaces.
- Deliverable: Architecture spec + component list.

### 2) Subsystem Prototyping (Weeks 2-4)
- Mobility subsystem prototype (thrusters, IMU, depth control).
- Event camera integration and LED illumination tests.
- SNN inference pipeline on embedded hardware.
- Deliverable: Subsystem test reports + integration checklist.

### 3) Deployment Mechanism Build (Weeks 5-6)
- X–Y gantry assembly (rails, motors, encoders).
- Pod storage grid design (10x10).
- Release gate + pod counter sensor integration.
- Deliverable: Gantry + release mechanism functional demo.

### 4) Control Logic and Integration (Weeks 7-8)
- Implement decision logic (confidence threshold, stability, location memory, jam checks).
- Integrate perception -> decision -> deployment pipeline.
- Deliverable: End-to-end bench test with simulated inputs.

### 5) Tank Testing and Calibration (Weeks 9-10)
- Underwater stability, depth holding, and scanning tests.
- Validate detection accuracy and false deployment rate.
- Calibrate gantry positioning and pod count accuracy.
- Deliverable: Test report with metrics and tuning parameters.

### 6) Field-Ready Demo Prep (Week 11)
- Hardening, waterproofing validation, and endurance checks.
- Documentation: system design, operating procedure, and patent figures.
- Deliverable: Final demo package + documentation bundle.

## Task Breakdown

### Hardware
- Select event-based camera and lens.
- Design enclosure and mounting points.
- Choose thrusters, ESCs, and battery capacity.
- Build X–Y gantry with stepper motors and rails.
- Integrate pod release gate and counter sensor.

### Software/Firmware
- Event stream ingestion and preprocessing.
- SNN model training/inference pipeline.
- MCU control firmware (movement, safety checks, deployment).
- Data logging and summary reporting.

### Integration and Test
- Electrical power distribution and safety.
- Waterproof sealing and pressure testing.
- Calibration of gantry coordinates and pod counts.
- End-to-end detection-to-deployment flow.

## Risks and Mitigations
- **Underwater visibility/lighting variability** -> use dual LEDs and adaptive thresholds.
- **False positives in classification** -> confidence gating and training refinement.
- **Gantry misalignment** -> limit switches/encoders and calibration routine.
- **Jam or failed release** -> jam detection + retry/abort logic.
- **Power constraints** -> event-based sensing and low-power inference.

## Metrics of Success
- Detection latency: near real time (sub-second classification).
- Deployment accuracy: 10 pods released per target, <5% error rate.
- False deployment rate: below defined threshold in tank tests.
- Endurance: minimum target runtime under battery constraints.

## Documentation Outputs
- System design document (architecture + component roles).
- Operating procedure and safety checklist.
- Test reports with measured metrics.
- Patent-ready figures and diagrams.

