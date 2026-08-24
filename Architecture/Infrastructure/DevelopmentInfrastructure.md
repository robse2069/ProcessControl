# Recommended Development Infrastructure

## 1. Purpose

This document defines the recommended infrastructure for developing and validating the Process Control software and STM32 SensorNode firmware.

The constraints are:

- Most development is performed on a Windows laptop.
- The Windows user does not have administrator rights.
- WSL cannot be used.
- The final Python product must run on Linux PCs, laptops, and Raspberry Pi systems.
- STM32 firmware must be built, flashed, and debugged against physical hardware.

The recommendation is a Windows-first development workflow with a Linux hardware and release station. The Windows laptop remains the primary editing and test environment; Linux provides native SocketCAN and embedded hardware access.

## 2. Recommended Topology

```mermaid
flowchart LR
    WIN[Windows laptop\nno admin rights]
    GIT[Git repository\nshared source of truth]
    SIM[Local Python simulation\nvirtual CAN backend]
    LINUX[Linux PC or Raspberry Pi\nmanaged test station]
    CAN[SocketCAN\ncan0 / vcan0]
    STM32[STM32 SensorNode\nCAN + ST-LINK]
    PROD[Linux PC / laptop / Raspberry Pi\nproduction target]

    WIN <--> GIT
    WIN --> SIM
    GIT <--> LINUX
    LINUX --> CAN
    CAN <--> STM32
    GIT --> PROD
    PROD --> CAN
```

### Windows laptop

Used for the majority of daily work:

- Python GUI and NodeConfigurator development
- Firmware C and header editing
- Unit tests and protocol tests
- Local simulated-CAN integration tests
- Documentation and Git operations

The Windows environment must not require system-wide installation or administrator privileges for normal development.

### Linux test station

A Linux PC, laptop, or Raspberry Pi is used for operations that require native Linux or physical hardware:

- SocketCAN and `can-utils`
- USB-CAN adapter or CAN HAT
- STM32 flashing and debugging
- Hardware-in-the-loop tests
- Final Linux packaging and smoke tests

This station may be local to the lab or accessed remotely over SSH or remote desktop.

### Production target

The production target may be an x86-64 Linux PC/laptop or an ARM Raspberry Pi. The Python application should use configuration to select the CAN interface and must not configure network interfaces from inside application code.

## 2.1 HIL Test Deployment

The hardware-in-the-loop (HIL) station consists of two Raspberry Pis. The Raspberry Pi 1, named `testberry.local`, is dedicated to automated test execution. The Raspberry Pi 3B, named `pcberry.local`, is the operator and CAN station: it runs the Process Control GUI with its test interface and the Node Configurator with its test interface, and connects to the real CSN through the CAN adapter.

The Arduino Nano is the electrical test stimulator. It is controlled by the Raspberry Pi 1 and must be connected to the CSN through suitable relay contacts, level protection, filtering, current limiting, and common-ground or isolation circuitry as required by the CSN electrical design.

```mermaid
flowchart LR
  subgraph RPI1[ Raspberry Pi 1 - testberry.local - HIL test controller ]
    RF[Robot Framework]
    SU[Test suite]
    LIB[Test libraries\nPython / GPIO / remote control]
    RF --> SU
    SU --> LIB
  end

  subgraph NANO[Arduino Nano - test stimulator]
    DIO[5 GPIO switching outputs]
    PWM[PWM output]
    PULSE[Software-controlled pulse output]
  end

  subgraph SIG[Stimulus and protection hardware]
    RELAY[5 relays\none resistor per relay]
    RC[RC filter\nPWM to 0 V to 5 V]
    PDRV[Pulse conditioning\nlevel and protection]
  end

  subgraph RPI3[ Raspberry Pi 3B - pcberry.local - Linux test station ]
    GUI[Process Control GUI\nwith test interface]
    CFG[Node Configurator\nwith test interface]
    ADAPTER[CAN adapter\nSocketCAN can0]
  end

  subgraph DUT[Device under test]
    CSN[Real CSN\nSTM32 SensorNode]
    RIN[Resistance input]
    VIN[Voltage input]
    PIN[Pulse input]
    CSNCAN[CAN interface]
    RIN --- CSN
    VIN --- CSN
    PIN --- CSN
    CSN --- CSNCAN
  end

  LIB -->|USB serial or network command| NANO
  DIO --> RELAY
  RELAY -->|select resistor| RIN
  PWM --> RC
  RC -->|analog signal: 0 V to 5 V| VIN
  PULSE --> PDRV
  PDRV --> PIN
  GUI --> ADAPTER
  CFG --> ADAPTER
  ADAPTER <--> CSNCAN
  RF -.->|start, monitor, collect results| GUI
  RF -.->|configure and verify| CFG
```

### Deployment responsibilities

| Component | Responsibility | Connection |
| --- | --- | --- |
| Raspberry Pi 1 (`testberry.local`) | Runs Robot Framework, test suites, sequencing, assertions, and result storage. | Controls the Arduino Nano through USB serial or a network command interface. |
| Robot Framework | Coordinates stimulus actions and test-interface actions, then evaluates observed CSN behavior. | Test libraries connect to GPIO/serial control and the Pi 3B interfaces. |
| Arduino Nano | Generates the electrical input conditions for the CSN. | Five GPIOs drive five relay controls; one PWM output drives the filtered voltage path; one software-controlled output drives the pulse path. |
| Relay/protection board | Selects one of five resistance values and protects the Nano and CSN interfaces. | Relay contacts connect the selected resistor to the CSN resistance input. |
| PWM/RC circuit | Converts the Nano PWM signal into an adjustable analog stimulus. | Provides an analog signal from 0 V to 5 V to the CSN voltage input. |
| Pulse conditioning circuit | Shapes and protects the Nano pulse output. | Provides the required pulse levels and timing to the CSN pulse input. |
| Raspberry Pi 3B (`pcberry.local`) | Runs the GUI and Configurator test interfaces and hosts the CAN connection to the DUT. | CAN adapter to the CSN CAN bus; network or test-control link to the Pi 1. |
| CAN adapter | Provides the Linux CAN interface used by GUI and Configurator. | `can0` on the Raspberry Pi 3B to the CSN CAN bus. |
| Real CSN | Device under test; executes the actual STM32 firmware and produces CAN measurements/status. | Receives resistance, voltage, and pulse stimuli plus CAN configuration/control. |

### Test-control relationship

Robot Framework should treat the Pi 3B applications as externally controlled test interfaces rather than directly importing their internal Python modules. The test suite should:

1. Command the Pi 1/Arduino Nano to apply a defined stimulus.
2. Use the GUI test interface or Configurator test interface to configure or observe the CSN.
3. Read the resulting measurement, state, error, and control values through the Pi 3B CAN path.
4. Compare the observed result with the expected value and store the test evidence on the Pi 1.

The Pi 1 and Pi 3B should use a defined network protocol or SSH-based command interface. The test suite must identify which Pi owns each operation so that test execution, GUI interaction, CAN access, and stimulus generation do not become implicit dependencies.

### Stimulus channels

- **Resistance input:** Five Arduino GPIO outputs operate five relay channels. Each relay connects a different resistor to the CSN resistance input. The test suite should define whether relay combinations are forbidden, allowed, or interpreted as additional resistance values.
- **Voltage input:** One Arduino PWM output passes through the RC filter and protection stage to produce an analog signal from 0 V to 5 V. The test suite should allow settling time after each duty-cycle change before sampling the CSN.
- **Pulse input:** One Arduino output generates the software-controlled pulse signal. The required frequency, duty cycle, pulse count, and start/stop behavior should be specified per test case. Timing-critical pulse generation should use Arduino hardware timers where the required accuracy exceeds what a software loop can provide.

### HIL safety and startup requirements

- Default all Arduino stimulus outputs to an inactive and electrically safe state during reset and boot.
- Prevent relay changes while a measurement is being sampled unless the test explicitly requires a transition.
- Confirm the selected resistor and voltage output before connecting stimulus to the CSN.
- Keep the CSN actor outputs disabled or connected to safe loads during sensor-input tests.
- Record stimulus values, relay states, PWM duty cycle, pulse parameters, CAN frames, firmware state, and error code with each test result.
- Keep HIL configuration separate from production configuration on both Raspberry Pis.

## 2.2 Development and HIL Deployment Diagram

This deployment view combines the Windows development environment with the HIL installation. The Windows laptop is the primary development workstation. SSH is used to operate the Raspberry Pi 1 test controller and the Raspberry Pi 3B Linux station without requiring the Windows laptop to have CAN or STM32 USB drivers.

The Raspberry Pi 3B (`pcberry.local`) hosts the Linux Python applications and the CAN adapter. The Raspberry Pi 1 (`testberry.local`) hosts Robot Framework, the Arduino stimulus control, the ARM STM32 buildchain, and the STM32 debugger. The ST-LINK debugger is physically attached to `testberry.local` and provides the programming and debugging connection to the real CSN.

```mermaid
flowchart LR
  subgraph DEV[Windows laptop - developer workstation]
    VSC[VS Code]
    PY[Python source\nGUI and Configurator]
    C[STM32 C source]
    TEST[Local unit and virtual-CAN tests]
    VSC --> PY
    VSC --> C
    VSC --> TEST
  end

  REPO[Git repository\nsource and test artifacts]

  subgraph PI1[Raspberry Pi 1 - testberry.local - HIL test controller]
    RF[Robot Framework]
    SU[HIL test suite]
    RFLIB[Test libraries]
    BUILD[STM32 buildchain\nARM GCC + linker + scripts]
    DEBUG[STM32 debugger\nST-LINK tools]
    RF --> SU
    SU --> RFLIB
    BUILD --> DEBUG
  end

  subgraph PI3[Raspberry Pi 3B - pcberry.local - Linux test station]
    GUI[Process Control GUI\ntest interface]
    CFG[Node Configurator\ntest interface]
    CAN[CAN adapter\nSocketCAN can0]
    GUI --> CAN
    CFG --> CAN
  end

  subgraph STIM[Arduino Nano HIL stimulator]
    NANO[5 relay GPIOs\nPWM 0 V to 5 V\npulse output]
    CONDITION[Relay, RC, pulse\nprotection circuitry]
    NANO --> CONDITION
  end

  subgraph DUT[Real device under test]
    CSN[CSN STM32]
    INPUTS[Resistance, voltage,\nand pulse inputs]
    CSNCAN[CAN interface]
    CSN --- INPUTS
    CSN --- CSNCAN
  end

  DEV <--> |Git / file synchronization| REPO
  REPO <--> |pull source, push results| PI1
  REPO <--> |pull source, publish artifacts| PI3
  DEV -.-> |SSH| PI1
  DEV -.-> |SSH| PI3
  RFLIB --> |USB serial or network command| NANO
  CONDITION --> INPUTS
  CAN <--> CSNCAN
  DEBUG <--> |SWD| CSN
  RF -.-> |coordinate test interfaces| GUI
  RF -.-> |configure and verify| CFG
```

### Deployment node responsibilities

| Deployment node | Deployed components | Main responsibility |
| --- | --- | --- |
| Windows laptop | VS Code, Python source, STM32 source, local tests | Daily implementation, review, documentation, and fast software-only validation without administrator rights. |
| Raspberry Pi 1 (`testberry.local`) | Robot Framework, HIL tests, test libraries, ARM GCC buildchain, STM32 debugger tools | Test sequencing, assertions, result storage, Arduino Nano control, firmware compilation, flashing, and debugging. |
| Raspberry Pi 3B (`pcberry.local`) | GUI, Configurator, `python-can`, SocketCAN, CAN adapter | Operator/test interfaces and CAN communication with the real CSN. |
| Arduino Nano | Relay GPIO control, PWM generator, pulse generator | Electrical stimulation of the real CSN through the protection and conditioning circuits. |
| Real CSN | STM32 firmware, CAN, sensor inputs | Device under test. Receives HIL stimuli, executes firmware, and reports measurements/status over CAN. |

### Connections

- **Windows to `testberry.local`:** SSH for starting Robot Framework, invoking firmware builds, flashing, debugging, retrieving firmware artifacts, and maintenance.
- **Windows to `pcberry.local`:** SSH for starting the GUI/Configurator, retrieving test observations, and maintaining the CAN station.
- **Repository to both Pis:** Git-based source and test synchronization. Generated logs and firmware artifacts should be identified and retained separately from source files.
- **Pi 1 to Arduino Nano:** USB serial is preferred for explicit stimulus commands; a network command service may be used if the Nano is physically remote from Pi 1.
- **Pi 1 to Pi 3B:** Test-library calls over the network or SSH control the GUI and Configurator test interfaces and retrieve observations.
- **Pi 3B to CSN:** The CAN adapter exposes `can0` through SocketCAN for GUI, Configurator, and test-interface operations.
- **Pi 1 to CSN debugger:** ST-LINK uses SWD for flashing and source-level debugging. SWD is a separate connection from CAN and must not be treated as the runtime communication path.
- **Arduino Nano to CSN:** The relay, RC, and pulse-conditioning circuits provide the resistance, 0 V to 5 V analog, and pulse stimuli. The Nano must not be connected directly to unprotected CSN inputs.

## 3. Windows Python Development

### 3.1 User-level installation

Use a Python installation available to the user, either an existing corporate installation or a user-local installation. Create the environment inside the repository:

```text
ProcessControl/
  .venv/
  GUI/
  NodeConfigurator/
  SensorNode/
```

Create and activate it from PowerShell or Command Prompt:

```text
py -m venv .venv
.venv\\Scripts\\activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
```

If the Python launcher is unavailable, use the approved user-level Python executable in its place. Dependency installation must stay inside `.venv` and must not use a system-wide package directory.

### 3.2 Local CAN simulation

Windows development should use a simulated CAN backend rather than Linux-specific SocketCAN commands. `python-can` provides a virtual bus suitable for protocol and application tests.

Recommended backend selection:

```text
CAN_BACKEND=virtual     Windows development and automated tests
CAN_BACKEND=socketcan   Linux hardware or vcan tests
CAN_INTERFACE=can0      Physical Linux CAN interface
CAN_INTERFACE=vcan0     Linux virtual CAN interface
```

The application should expose one CAN interface abstraction. The GUI and Configurator should depend on that abstraction, not directly on `os.system`, `sudo`, `ip`, `ifconfig`, or a concrete `can.interface.Bus` constructor.

A simulated SensorNode should implement the relevant protocol behavior:

- Runtime data frames
- Setup request on `0x7F0`
- Configuration frames `0x7F1` through `0x7F4`
- Setup termination and persistent configuration behavior
- Runtime set-value handling
- State transitions needed by the tests

This permits most Python development without a CAN adapter or physical STM32 board.

### 3.3 Windows responsibilities and limitations

Supported locally without administrator rights:

- GUI layout and behavior
- Configurator workflows
- XML/configuration parsing
- CAN frame encoding and decoding through the virtual backend
- Logging and file output
- Firmware-independent logic tests
- Firmware source editing and review

Normally dependent on administrator-installed drivers or a managed station:

- Physical USB-CAN communication
- ST-LINK USB access
- Hardware-in-the-loop testing
- Direct SocketCAN testing

## 4. Linux and Raspberry Pi Infrastructure

Use Debian, Ubuntu, or Raspberry Pi OS. The Linux station should have:

- Python 3 and `venv`
- `python-can`
- `can-utils`
- ARM GNU toolchain for STM32
- A supported STM32 flashing/debugging tool
- Git
- Optional CMake or Make
- Optional pytest and coverage tools

The physical CAN interface should be configured outside the Python application. A typical Linux setup is conceptually:

```text
CAN bitrate: 500000
Physical interface: can0
Virtual test interface: vcan0
```

The exact interface setup requires administrator privileges on the Linux station and should be performed by the station owner or administrator. The application should only open the already-configured interface.

### Raspberry Pi considerations

For a Raspberry Pi deployment:

- Prefer a supported CAN HAT or USB-CAN adapter.
- Use a reliable power supply.
- Use a read-only or industrial-grade storage strategy where possible.
- Run the application as a dedicated non-root user.
- Store logs outside the source tree.
- Configure automatic startup with a `systemd` service prepared by the administrator.
- Keep development, production, and hardware-test configuration files separate.

## 5. STM32 Development Workflow

STM32 development is split into source work on Windows and hardware operations on the Linux test station.

### 5.1 Source development on Windows

The Windows laptop is suitable for:

- Editing `SensorNode/Firmware/Inc/` and `SensorNode/Firmware/Src/`
- Reviewing HAL and application boundaries
- Implementing state, configuration, CAN, scheduling, and sensor logic
- Writing host-side tests for portable logic
- Reviewing compiler output produced by the Linux station
- Git commits and documentation

The firmware source does not need to execute on Windows.

### 5.2 Build on Linux

The Linux test station should provide an ARM embedded toolchain, normally `arm-none-eabi-gcc`, together with the project linker script, startup code, STM32 HAL sources, and build configuration.

The build should produce at least:

```text
SensorNode firmware artifacts:
  .elf  debugging symbols and debugger input
  .hex  programming/distribution format
  .bin  optional raw binary
```

The build must be scripted so the same command can be run manually, remotely, and later by CI. The existing System Workbench project can be used initially if it remains the only known-good build, but a command-line build should be introduced as soon as practical.

Conceptual workflow:

```text
Windows edit -> Git push/commit -> Linux checkout -> build -> artifact
```

### 5.3 Flash and debug on Linux

Connect the STM32 board and ST-LINK programmer to the Linux test station. The station owns:

- ST-LINK USB access and drivers
- Firmware flashing
- Reset and device identification
- Breakpoint debugging
- Firmware log or diagnostic capture
- CAN hardware connection
- Sensor and actor verification

The Windows laptop can control the station through SSH or remote desktop, but physical USB access remains on the station.

### 5.4 Firmware test layers

Use progressively more hardware-specific tests:

1. **Host-side unit tests:** state transitions, calibration arithmetic, CAN packing/unpacking, configuration validation.
2. **Cross-build checks:** compile the firmware with the ARM toolchain and treat warnings as review items.
3. **Protocol simulation:** connect the Windows Python tools to the simulated SensorNode.
4. **Hardware-in-the-loop:** connect the Linux test station, real CAN bus, STM32 node, and sensors/actors.
5. **Release smoke test:** flash the release artifact and verify startup, setup, runtime frames, and error handling.

## 6. Repository and Configuration Structure

The infrastructure should evolve toward the following structure:

```text
ProcessControl/
  .venv/                         local Windows environment, ignored by Git
  requirements.txt               runtime Python dependencies
  requirements-dev.txt           test and development dependencies
  pyproject.toml                 Python tooling configuration
  tests/
    python/
    protocol/
    simulated_node/
  tools/
    run_virtual_can_tests.py
    build_firmware.sh
    flash_firmware.sh
  config/
    development-windows.toml
    test-virtual-can.toml
    production-linux.toml
    production-raspberry-pi.toml
  GUI/
  NodeConfigurator/
  SensorNode/
  Architecture/
```

The current source tree may not contain all of these files yet. They describe the intended infrastructure boundary, not a claim that the files already exist.

Configuration should define at least:

- CAN backend
- CAN interface name
- CAN bitrate where applicable
- GUI update period
- Logging directory
- Firmware artifact path for test scripts
- Target node ID

Secrets, machine-local paths, and generated logs must not be committed.

## 7. Development and Release Flow

```mermaid
sequenceDiagram
    actor Developer
    participant Win as Windows laptop
    participant Git as Git repository
    participant Linux as Linux test station
    participant FW as STM32 board
    participant Pi as Production Linux target

    Developer->>Win: Edit Python and C source
    Developer->>Win: Run unit and virtual-CAN tests
    Developer->>Git: Commit and push changes
    Git-->>Linux: Checkout or pull source
    Linux->>Linux: Build Python package and STM32 firmware
    Linux->>FW: Flash firmware artifact
    Linux->>FW: Run CAN hardware-in-the-loop tests
    Linux-->>Developer: Report test results and artifacts
    Developer->>Git: Tag approved release
    Git-->>Pi: Deploy source/package and configuration
    Pi->>FW: Operate over configured CAN interface
```

## 8. Responsibilities by Environment

| Activity | Windows laptop | Linux test station | Production Linux/Pi |
| --- | --- | --- | --- |
| Edit Python | Primary | Optional | No |
| Edit STM32 C | Primary | Optional | No |
| Python unit tests | Primary | Yes | Smoke tests |
| Virtual CAN tests | Primary | Yes | Optional |
| SocketCAN tests | No | Primary | Yes |
| Physical CAN | Only if drivers already exist | Primary | Yes |
| STM32 compilation | Optional if toolchain is portable | Primary | Usually no |
| STM32 flashing/debugging | Usually no | Primary | No |
| GUI validation | Primary | Yes | Yes |
| Release packaging | Optional | Primary | No |
| Field operation | No | Optional | Primary |

## 9. Required Architectural Changes

The current code contains Linux-specific setup and direct CAN construction in the Python applications. Before this infrastructure can be used reliably, make these changes:

1. Introduce a small CAN transport interface used by both GUI and Configurator.
2. Select `virtual` or `socketcan` through configuration or command-line arguments.
3. Move bitrate and interface setup into Linux deployment scripts.
4. Remove `sudo`, `ip`, and `ifconfig` calls from application startup.
5. Add a simulated SensorNode for Windows protocol tests.
6. Add protocol tests for setup frames, runtime frames, signed values, and byte order.
7. Add a scripted firmware build on the Linux station.
8. Keep flashing as an explicit hardware-station operation.
9. Add separate development, test, and production configuration files.
10. Document the exact Linux/Pi service and CAN setup for the station administrator.

These changes preserve the existing CAN integration boundary while making the application portable across Windows development, Linux desktop deployment, and Raspberry Pi deployment.

## 10. Infrastructure Decision

Adopt **Windows-first development with a managed Linux/Raspberry Pi hardware station**.

This is the best fit for the constraints because it keeps the bulk of development local and administrator-independent, while reserving Linux for the capabilities that cannot be reproduced faithfully on the Windows laptop: SocketCAN, physical CAN, STM32 flashing, and hardware debugging.

The Linux station should be treated as a required validation environment, not as a prerequisite for every source edit. The virtual CAN backend and simulated SensorNode provide the fast feedback loop; hardware-in-the-loop testing provides final confidence.
