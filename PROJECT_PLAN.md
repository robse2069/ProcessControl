# ProcessControl Rework Plan

## 1. Project Goal

This project is a CAN-based actor/sensor system with a centralized control and logging unit. The original design targets a common hardware platform for sensors and optional actors, with the node configuration differentiating instance behavior rather than hardware differences.

The primary goals of the rework are:

- refactor the codebase to support modular testing and continuous improvement
- separate configuration, communication, and control logic cleanly
- support identical sensor hardware/software with per-instance configuration
- provide a test strategy covering unit, integration, and system validation
- validate the timing requirement for at least 10 sensors on one bus
- keep a strong focus on deterministic measurement and publish timing

This plan is based on the current legacy project intent described in [README.md](README.md), [NodeConfigurator/SystemDesignConsiderations.txt](NodeConfigurator/SystemDesignConsiderations.txt), and the existing GUI and node structure.

---

## 2. Current Baseline and Legacy Constraints

### Existing architecture

- Centralized GUI/configuration tool for node setup and validation
- CAN bus used as the communication backbone
- Sensor node family intended to be hardware-identical and software-identical
- Configuration decides node role and behavior
- Logging and monitoring are handled centrally
- Actors were intentionally postponed and are not part of the current first-use case

### Legacy observations

- The system was originally designed around a central control and logging view
- Configuration and runtime monitoring are already conceptually separated
- The codebase contains a GUI layer, configuration concepts, and communication access but was not structured for modular testing
- The original design mentions periodic reading and update cycles, which is a strong indicator that timing and deterministic scheduling must be made explicit

### Rework principle

The rework should preserve the functional intent while turning the system into a testable, layered architecture.

---

## 3. Target System Architecture

### 3.1 Functional decomposition

The final system should be organized in layers:

1. Configuration Layer
   - node configuration data model
   - sensor instance definitions
   - parameter validation
   - GUI-based configuration workflow

2. Communication Layer
   - CAN message definitions
   - bus abstraction
   - message encoding/decoding
   - timeout and retry handling
   - logging of raw frames and protocol events

3. Control and Coordination Layer
   - central orchestration of the measurement cycle
   - sensor registry and discovery
   - health monitoring and error tracking
   - logging and time-stamping of acquired data

4. Sensor Node Application Layer
   - measurement acquisition
   - local filtering, calibration, and conversion
   - periodic publish cycle
   - response to configuration and diagnostics commands

5. Test and Validation Layer
   - unit tests for isolated logic
   - integration tests for message/data interfaces
   - system tests with real hardware
   - timing validation under load

### 3.2 Responsibility split

#### Central control and logging unit

- manages the list of known sensor nodes
- stores configuration and runtime status
- provides a central log and diagnostics stream
- receives published sensor values and validates their freshness
- tracks network health, missed packets, and timing drift

#### Sensor nodes

- same hardware and same firmware base
- object identity is determined by configuration
- measure according to configured parameters and update rate
- publish values on the CAN network in a deterministic and repeatable cycle
- answer configuration and diagnostic requests

#### Configuration application

- provides a GUI to select a node, inspect parameters, change settings, and verify the result
- validates ranges, units, and update rates before sending a configuration
- keeps configuration files explicit and versioned
- supports reproducible test environments

---

## 4. Refactoring Plan

### Phase 1: Baseline and architecture documentation

Objectives:

- define the high-level system model
- document message semantics and command vocabulary
- define node states and configuration lifecycle
- identify current hardware assumptions and dependencies

Deliverables:

- system context description
- CAN message map
- node and sensor configuration schema
- architecture decision record for the rework

### Phase 2: Isolate system boundaries

Objectives:

- separate GUI logic from protocol logic
- isolate bus communication from application logic
- separate configuration model from runtime state
- create clear interfaces for measurement, logging, and control

Key design decisions:

- protocol layer owns CAN frame encoding/decoding
- sensor logic owns measurement and publish decisions
- control unit owns orchestration and monitoring
- GUI remains presentation-oriented and should consume stable data models

### Phase 3: Introduce modular test seams

Objectives:

- avoid direct hardware dependencies in core logic
- allow protocol and scheduler logic to be exercised with fake bus objects and mock timing sources
- make timing logic and state management deterministic and testable

Examples of seams:

- bus adapter interface
- clock/timer abstraction
- message serializer/deserializer
- sensor drivers behind a common measurement interface
- logger backend abstraction

### Phase 4: Reorganize the configuration model

Objectives:

- define a single canonical configuration format
- allow same firmware to be instantiated differently via configuration
- enforce validation and defaults
- ensure all sensor instances are configured according to the same state machine

This includes:

- configuration schema for node ID, update period, measurement scaling, calibration, and status fields
- explicit validation for minimum/maximum values and allowed ranges
- versioning for configuration compatibility

### Phase 5: Timing and determinism hardening

Objectives:

- enforce a schedule that satisfies the required 10 ms measurement/publish cycle
- verify bus load and CPU load under 10 sensors and future expansion
- define clear failure behavior for missed deadlines

This phase is mandatory because the real-time behavior is a system-level requirement, not just a software preference.

### Phase 6: Validation and release readiness

Objectives:

- run the full test suite for unit, integration, and hardware system validation
- verify reliability and timing under realistic conditions
- produce release criteria for the sensor network

---

## 5. Test Strategy

### 5.1 Unit tests

Unit tests should target individual logic blocks without hardware access.

Focus areas:

- configuration validation and parsing
- measurement conversion and scaling
- CAN payload encoding/decoding
- scheduler logic for periodic publish tasks
- timeout and error-state handling
- logger formatting and storage logic

Goal:

- cover each decision path and edge case
- keep tests deterministic and fast
- fail clearly when protocol or configuration rules are violated

### 5.2 Integration tests

Integration tests exercise multiple components working together while using controlled interfaces or a simulated bus.

Examples:

- sensor node publishes a valid message on the bus
- control unit decodes and stores the value
- configuration application writes a new node state and verifies the node accepts it
- timed publish cycle keeps a sensor alive and consistent under repeated updates

Recommended environment:

- local bus simulation or CAN loopback or virtual bus
- fixture-based node instances
- deterministic message logs
- time assertions with a controllable clock or measured timestamps

### 5.3 System tests with real hardware

System tests must use the actual hardware stack and real CAN communication.

Validation scenarios:

- single sensor on the bus
- 10 sensors simultaneously on the bus
- sensor start-up and restart behavior
- configuration update while running
- missed message detection and recovery
- timing jitter measurement under load
- central log verification and consistency checks

Required system outputs:

- publish period per sensor
- message loss count
- jitter and latency statistics
- detection of deadlines missed by the system

### 5.4 Acceptance criteria for tests

The project should not be considered ready unless:

- all unit tests pass reliably
- integration tests verify full message flow
- system tests confirm stable operation with at least 10 sensors
- timing checks prove the 10 ms publish requirement is satisfied under the target bus load

---

## 6. Timing Analysis: 10 Sensors at 10 ms Publish Rate

### Requirement

At least 10 sensors are connected to the same CAN bus. Each sensor shall measure and publish its value every 10 ms.

### Derived load

For one sensor:

- 1 measurement per 10 ms
- equivalent to 100 measurements per second

For 10 sensors:

- 10 x 100 = 1000 published sensor values per second

This means the system must support a sustained publish rate of roughly 1000 CAN messages per second, assuming one message per sensor update.

### CAN bus capacity check

A standard CAN frame has non-trivial overhead but still remains compact. Even with message overhead, a 500 kbps CAN bus can handle a traffic load far above the required 1000 frames/s without approaching the practical bus limit under normal conditions.

The design should still treat this as a real-time requirement and not just as an average throughput estimate.

### Timing design constraints

The system must ensure:

- each sensor executes measurement within a bounded time window
- each sensor publishes no later than the 10 ms target period
- bus scheduling does not create arbitration starvation or unpredictable delay spikes
- central logging does not block the measurement publish path
- message processing can handle 10 sensors plus control, health, and diagnostics traffic

### Recommended scheduling strategy

For deterministic behavior:

- each sensor runs on a fixed periodic task or timer
- the publish period is a strict 10 ms cycle
- a single master scheduler or central coordinator can validate timing and trigger periodic checks
- bus traffic should be planned so that measurement frames are not emitted in bursts by all sensors at exactly the same instant unless the system intentionally schedules them in a staggered pattern

A practical approach is:

- keep one 10 ms measurement cycle
- each sensor is assigned a fixed time slot or offset within the cycle
- the offset pattern reduces simultaneous bus contention and improves timing consistency

### Timing budget

A recommended budget should reserve margin for:

- sensor acquisition time
- filtering/calibration time
- message creation and serialization
- CAN bus arbitration and transmission latency
- control-unit processing time
- logging cost and diagnostics handling

Recommended target:

- measurement and publish deadline: 10 ms maximum
- timing jitter: keep below a conservative percentage of the period
- reserve at least 20% headroom for future extension and additional traffic

### Timing validation method

The project should include formal timing checks:

- record timestamps at measurement start and publish completion
- record central receive timestamps for each message
- compare sensor publish period against the target 10 ms
- collect jitter statistics over a representative time window
- test under 10-sensor load and under startup/recovery conditions

---

## 7. Test and Validation Matrix

| Layer | Scope | Main goal | Typical evidence |
| --- | --- | --- | --- |
| Unit | config parsing, scaling, payload logic | verify logic correctness | deterministic tests |
| Integration | bus + application interaction | verify protocol flow | message logs and state transitions |
| System | real hardware with 10 sensors | verify real-time behavior | timing logs and network health data |

---

## 8. Delivery Roadmap

### Milestone 1: Architecture freeze

- define the sensor node and central control roles
- define CAN message and configuration semantics
- define the testable layer boundaries

### Milestone 2: Modular refactor

- split logic into testable modules
- isolate protocol, configuration, and task orchestration
- add interfaces and seam points for fake devices

### Milestone 3: Validation harness ready

- create unit and integration test setup
- create communication fixtures and logs
- define hardware test process

### Milestone 4: Timing proof

- validate 10 sensors at 10 ms publish cadence
- measure jitter, bus load, and missed deadlines
- tune periodic scheduling before final release

### Milestone 5: Release readiness

- all tests pass
- system behavior proven on real hardware
- configuration workflow and logging are stable and repeatable

---

## 9. Explicit Risks and Mitigations

### Risk: timing drift

Mitigation:

- fixed cadence scheduler
- timestamping at sensor and control side
- measurement of jitter and deadline misses

### Risk: bus congestion

Mitigation:

- deterministic publish timing
- cap message count per cycle
- monitor load and reject nonessential traffic

### Risk: configuration mismatches

Mitigation:

- strict validation
- clear schema/version checks
- explicit verify-and-ack workflow

### Risk: test gaps due to hardware dependency

Mitigation:

- keep hardware-dependent code isolated
- test protocol and logic separately from hardware access

---

## 10. Recommended Work Order

1. Freeze the node model and message specification.
2. Separate configuration, protocol, and runtime logic.
3. Add unit tests for validation and conversion logic.
4. Add integration tests around CAN message flow and node state.
5. Validate timing with at least 10 sensors.
6. Perform a final hardware system test using the real bus and sensor setup.
7. Only then consider the refactor complete and release-ready.

---

## 11. Final Project Position

This rework is not a broad rewrite for its own sake. It is a controlled modernization of the original concept: a uniform sensor node architecture, a central control and logging unit, a GUI-driven configuration flow, and a testable, deterministic communication model.

The most important technical focus is simple and explicit:

- same hardware and same software
- different sensor instances via configuration
- central monitoring and logging
- periodic measurement publication every 10 ms per sensor
- validation of system timing with at least 10 sensors on one bus

This is the foundation on which the project should be rebuilt.
