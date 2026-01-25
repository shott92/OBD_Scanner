# CANdy_Diag_Pro
**Unified Automotive Engineering & Competitor Analysis Platform**

CANdy_Diag_Pro is a professional-grade automotive diagnostic tool designed to compete with industry standards like Vector CANoe and ETAS. It unifies internal ECU validation (Engineering Mode) and competitor analysis (Reverse Engineering Mode) into a single, modular platform.

## Key Features

### 🛠️ Core Engineering
*   **Multi-Protocol Support**: CAN, CAN-FD, LIN, FlexRay, DoIP (UDS via Ethernet).
*   **Hardware Abstraction Layer (HAL)**: Vendor-neutral support for J2534 Pass-Thru, ELM327, and DoIP interfaces.
*   **Diagnostic Services**: ISO-14229 (UDS) support including Session Control, DTC reading, and Security Access.
*   **Workspace Management**: Save and restore complete testing environments (Hardware config + Loaded Projects).

### 🔍 Competitor Analysis & Reverse Engineering
*   **Topology Scanner**: Automatic network discovery (Passive & Active Intrusion).
*   **Architecture Mapping**: Visual tree view of ECUs, DIDs, and Signals.
*   **Snapshot Module**: rapid data extraction ("Gleaning") from mapped architectures.
*   **Universal Configs**: 3-Layer Repository (Local/Internal/Public) for vehicle definitions.

### ⚡ High-Performance
*   **Python 3.13 Ready**: Optimized for the latest Python JIT compiler for high-speed signal decoding.
*   **Efficient UI**: PyQt5-based interface designed for responsiveness.

## Installation

### Prerequisites
*   **Python 3.13+** (Recommended for JIT performance) or Python 3.8+
*   Windows 10/11

### Setup
1.  Clone the repository:
    ```bash
    git clone https://github.com/your-org/CANdy_Diag_Pro.git
    cd CANdy_Diag_Pro
    ```

2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Launch the Application**:
    ```bash
    python main.py
    ```
    *To enable JIT (Python 3.13+):* `python -X jit main.py`

2.  **Connect Hardware**:
    *   Select your adapter type (ELM327 / DoIP).
    *   Configure connection parameters (Port / IP).
    *   Click **Connect**.

3.  **Workspaces**:
    *   Use **File > Save Workspace** to persist your current setup.
    *   Use **File > Open Workspace** to restore a previous session.

## Documentation
*   [Developer Guide](docs/DEVELOPER_GUIDE.md): Architecture and contribution details.
*   [Performance Guide](docs/PERFORMANCE.md): JIT optimization instructions.
*   [Requirements](CANdy_Diag_Pro.md): Functional Requirements Specification.
