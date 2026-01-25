# User Story

- As an automotive competitor analysis engineer, I shall be able to access a vehicle, and start mapping its network topology with the click of a button.
- As an Automotive Data Engineer, I shall be able to use this tool to export and import the topology of the vehicle,so it does not have to be mapped every time.
- As an automotive competitor analysis engineer, I shall be able to use this tool and it's CANdecoder Wizard to start to build openDBC files for the vehicle.
- As an Automotive Data Engineer, I shall be able to use this tool to export and import the DBC files of the vehicle,so it does not have to be built every time.
- As an Automotive Competitor Analysis Engineer or Benchmarking Engineer, i shall be able to use this tool to log the telemetry data from the whole vehicle, this should extend to all signals, from all network on the vehicle
- As an Automotive Tools Manager, I shall be able to retain a central repository of vehicle data, so it can be accessed from any device, and it should be able to be shared with other users, and have a mechanism to retrieve the data from the repository.
- As an Automotive Open-source Developer, I shall be able to push and pull open-source vehicle data to and from the repository, and have a mechanism to retrieve the data from the repository to central repo such as opendbc.
- As an Automotive Software Engineer, I shall be able to use this tool to analyse all the hardware and software data from the vehicle's Electrical Architecture.
- As an Automotive Software Engineer, I shall be able to (with the right security files), use this tool to flash software updates to the vehicle. (SWDL)
- As an Automotive Test Engineer, I shall be able to use this tool to perform tests on the vehicle, such as ECU identification, signal decoding, and more.
- As an Automotive Test Engineer, I shall be able to use this tool to perform tests on the vehicle, such as ECU resiliance, Penetration Testing (not planned yet).

## Core Engineering
Features:
- Vehicle Identification
- Vehicle Electrical Architecture Analysis
- Vehicle Topology Mapping
- ECU Identification
- Signal Identification
- Signal Decoding
- Vehicle Telemetry Logging
- Software Analysis
- ECU Software Update
- ECU Resiliance
- Penetration Testing (not planned yet)

### Multi-Protocol Support
- CAN, CAN-FD, LIN, FlexRay, DoIP (UDS via Ethernet)

### Hardware Abstraction Layer (HAL)
- Vendor-neutral support for J2534 Pass-Thru, ELM327, and DoIP interfaces, also include proprietary devices from ETAS and Vector.

### Diagnostic Services
- ISO-14229 (UDS) support including Session Control, DTC reading, and Security Access

### Workspace Management
- Save and restore complete testing environments (Hardware config + Loaded Projects)

## Competitor Analysis

### Topology Scanner
- Automatic network discovery

### Snapshot Module
- Rapid ECU identification (VIN, Hardware/Software IDs)

## High-Performance

### Python 3.13 Ready
- Optimized for the latest Python JIT compiler for high-speed signal decoding

### Efficient UI
- PyQt5-based interface designed for responsiveness

## Installation

### Prerequisites
- Python 3.13+ (Recommended for JIT performance) or Python 3.8+
- Windows 10/11

### Setup
1. Clone the repository:
    ```bash
    git clone https://github.com/your-org/CANdy_Diag_Pro.git
    cd CANdy_Diag_Pro
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. **Launch the Application**:
    ```bash
    python main.py
    ```
    *To enable JIT (Python 3.13+):* `python -X jit main.py`

2. **Connect Hardware**:
    * Select your adapter type (ELM327 / DoIP)
    * Configure connection parameters (Port / IP)
    * Click **Connect**

3. **Workspaces**:
    * Use **File > Save Workspace** to persist your current setup
    * Use **File > Open Workspace** to restore a previous session

## Documentation
* [Developer Guide](docs/DEVELOPER_GUIDE.md): Architecture and contribution details.
* [Performance Guide](docs/PERFORMANCE.md): JIT optimization instructions.
* [Requirements](CANdy_Diag_Pro.md): Functional Requirements Specification.