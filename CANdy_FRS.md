# **Functional Requirements Specification (FRS)**

**Project:** Unified Automotive Engineering & Competitor Analysis Platform

**Version:** 1.0 (Comprehensive Master)

**Status:** Approved for Development

## **1\. Introduction**

### **1.1 Purpose**

The purpose of this software is to serve as a comprehensive engineering tool for vehicle diagnostics, electronic control unit (ECU) integration, and test automation. a "multi-tool" for automotive engineers. It is designed to unify two critical workflows into a single platform:

1. **OEM Engineering:** Validating, updating, and automating tests for internal Electronic Control Units (ECUs) using robust, production-grade standards.  
2. **Competitor Analysis:** Reverse engineering, data collection, and network topology mapping of third-party vehicles.

Enabling both a high quality interface to enable updating and testing their own ECUs, but also to support data collection and analysis of competitor vehicles.

It is designed to be the universal open-source automotive engineering tool to compete with Vector and ETAS, and provide robust support for modern automotive communication protocols as well as complex software download (SWDL) procedures.

The system must allow engineers to communicate with vehicle networks, perform diagnostics, flash software, automate test sequences, and reverse engineer and debug vehicle networks.

### **1.2 Scope**

The system shall replace legacy tools by supporting modern automotive protocols (e.g., DoIP, CAN-FD) and complex update procedures (Software Download/SWDL). It must be modular, allowing for optimized sub-packages (UIs) for specific tasks such as vehicle snapshots or deep-dive diagnostics.

---

## **2\. General System Capabilities & Architecture**

### **2.1 Workspace & Project Management**

* **Workspace Persistence:** The system shall allow users to save the entire application state (Hardware settings, Channel mappings, Loaded ECUs) into a "Workspace" file for rapid restoration of test environments.  
* **Granular Save/Load:** Users must be able to save and import different elements separately. For example, user settings (themes, fonts, layout) must be savable independently from network configurations.  
* **Portable Vehicle Configs:** Users must be able to export specific vehicle configurations (Protocol parameters, Timing settings, ECU IDs) into portable files to be shared and modified by other engineers.  
* **Project Files:** The system shall support a specific file format for storing project-specific settings, including channel definitions and protocol parameters.

### **2.2 Hardware Abstraction Layer (HAL)**

* **Vendor Independence:** The system shall utilize a Hardware Abstraction Layer to interface with Vehicle Communication Interfaces (VCIs) from various vendors (e.g., Vector, ETAS, Intrepid, NI) without requiring specific vendor-locked software versions.  
* **J2534 Support:** The system must support the SAE J2534 Pass-Thru standard to ensure compatibility with compliant third-party hardware.  
* **Multi-Channel Support:** The system must support simultaneous connections to multiple hardware channels across different protocols.



## **3\. Communication Protocol Specifications**

The software must support configuration, transmission, and reception on the following vehicle network protocols:

### **3.1 CAN & CAN-FD (Controller Area Network)**

* **Configuration:** Users shall be able to configure Baud Rate, Sample Point, and Bit Timing for both Nominal and Data phases (for CAN-FD).  
* **Arbitration:** The system must handle message arbitration IDs (11-bit and 29-bit).  
* **Transmission/Reception:** The system shall be capable of sending and receiving raw CAN frames, supporting "Mixed Mode" addressing, and interpreting signals based on loaded database files (e.g., DBC).

### **3.2 LIN (Local Interconnect Network)**

* **Master/Slave Simulation:** The system shall be capable of acting as a LIN Master or a LIN Slave.  
* **LDF Support:** The system must support importing LIN Description Files (LDF) to configure the network.  
* **Schedule Tables:** The system shall allow the definition and execution of Schedule Tables to orchestrate frame transmission timing.

### **3.3 FlexRay**

* **Network Configuration:** The system must support complex FlexRay parameters, including Cycle Time, Slot configurations, and Cluster parameters.  
* **Fibex Support:** The system shall support parsing FIBEX (Field Bus Exchange Format) files to automatically configure network parameters.  
* **Cold Start:** The system must be capable of performing "Cold Start" procedures to wake up and synchronize the FlexRay cluster independent of other nodes.

### **3.4 DoIP (Diagnostics over IP) & DoIP-EVA2**

* **Discovery:** The system must automatically discover DoIP entities (Vehicle/ECU) on the network via UDP broadcasts.  
* **Routing Activation:** The system shall handle Routing Activation requests to establish a logical connection with the target ECU.  
* **VLAN Support (EVA2):** The system must support tagging traffic with VLAN IDs for network segregation. This includes implementing a **Custom TCP Stack** (e.g., via WinPCap) to handle VLAN-tagged traffic.  
* **Connection Management:** Support for TCP and UDP data transmission, maintaining "Tester Present" messages to keep sessions alive.

### **3.5 Network Services**

* **Integrated DHCP Server:** The system shall include an internal DHCP server capability to assign IP addresses to connected ECUs if required.  
* **Static IP Override:** Users shall be able to manually configure static IP addresses and subnet masks where dynamic assignment is not possible.

---

## **4\. Module A: Core Engineering & Diagnostics**

*Designed for reliable interaction with known/internal ECUs.*

### **4.1 Diagnostic Services (UDS \- ISO 14229\)**

The system must support standard UDS services including:

* Diagnostic Session Control ($10)  
* ECU Reset ($11)  
* DTC Read/Clear ($19/$14)  
* Read/Write Data by Identifier ($22/$2E)  
* Security Access ($27) \- including Seed/Key handling.  
* Routine Control ($31)  
* Request Download/Upload ($34/$35)  
* **Transport Layer (ISO 15765):** The system must handle multi-frame message segmentation and reassembly (ISO-TP) automatically.

### **4.2 Diagnostic Operation**

* **Manual Command Entry:** Users shall be able to manually construct and send raw diagnostic hex strings.  
* **Response Interpretation:** The system must capture positive and negative responses (NRCs) and display them in a human-readable format.  
* **Gateway Routing:** The system shall support routing diagnostic requests through a Gateway ECU to reach sub-networks (e.g., diagnosing a LIN ECU via a Central Gateway).  
* **Tester Present:** Configurable "Heartbeat" messaging to maintain sessions, with adjustable intervals.

### **4.3 Logging & Analysis**

* **Real-Time Trace:** The system shall provide a trace window displaying all transmitted and received messages with timestamps, channel IDs, and data payloads.  
* **Decoding:** The trace shall automatically decode raw hex data into human-readable signal names if a database (DBC/LDF/Fibex) is loaded.  
* **File Logging:** The system must log network traffic to industry-standard formats (e.g., PCAP for Ethernet, ASC/BLF for CAN/FlexRay).  
* **Wireshark Integration:** The system shall support integration with packet analyzers like Wireshark for deep inspection of DoIP/Ethernet traffic.  
* **Filtering:** Users shall be able to configure filters to log only specific message IDs or protocols.

### 5.4 Community Protocol Repository (`opendbc` Compatible)

*   **Three-Tier Architecture:** The system shall support a tiered lookup strategy for protocol definitions:
    1.  **Local Overrides:** User's local modifications (Highest Priority).
    2.  **Enterprise/Team Repo:** A private Git repository for internal sharing.
    3.  **Upstream `opendbc`:** A cached clone of the public `commaai/opendbc` repository.
*   **Format:** The system must natively support the **DBC file format** used by `opendbc`.
*   **Export:** Any reverse-engineered data (decoded signals) must be exportable as valid `.dbc` files to allow upstream contribution.

---

## **5\. Module B: Advanced Software Download (SWDL) Engine**

*A professional-grade engine for updating ECU firmware via complex, scripted flows.*

### **5.1 Download Sequencing & Logic**

* **Specification Files:** The engine shall execute downloads based on structured specification files (e.g., SDS) that define the sequence of operations, file paths, and logic.  
* **Flow Control:** The specification format must support:  
  * Conditional Branching: on\_success\_jump\_to\_node / on\_failure\_jump\_to\_node.  
  * Loops (While/For) and Jumps (GoTo).  
  * Global Variables to pass data between steps.  
  * Error Handling: Flags for terminate\_on\_error vs. continue.  
  * Retry Logic: Configurable retry\_count and retry\_wait times.

### **5.2 Supported Download Modes**

* **Standard VBF:** Conventional Erase-Program-Verify sequences using Volvo Binary Format (VBF) files (containing header info, addresses, checksums).  
* **Signed Download (Secure):** A secure flow requiring:  
  * Certificate Exchange (signing\_certificate).  
  * Hash Validation (Root Hashes and Hash Tables).  
  * Signature Verification (SBL and Application signatures).  
* **Unsigned Download:** Support for Package XML-based downloads where security is explicitly disabled.  
* **Dual-Bank / Background Download:** Updating ECUs while operational.  
  * Downloading to a memory buffer for activation at restart.  
  * Execution of "Switch Bank" ($DF00) and "Commit/Rollback" ($022A) routines.  
* **Infotainment (NGI/PIVI):** File-system based updates using RPM/IMG files.  
  * Routine-Based Transfer: Triggering routines to pull files rather than direct memory writes.  
  * External Media: Handling files stored on USB/External media.  
* **File Transfer (REST):** 
    *   **Repository Sync:**  REST API client to sync PIDs, Protocol Definitions, and Firmware files from the central repository.
    *   **Local Download:** Capability to download update packages for local flashing.
    *   *(Note: Live telemetry streaming is NOT required).*

### **5.3 Specialized Features**

* **Spike Mode:** Capability to send a high-frequency physical wake-up message (e.g., $10 02$ every 10ms) to initialize unresponsive ECUs before flashing.  
* **Security Integration:** Integration with external DLLs or Security Files (.sfg) to handle proprietary seed/key unlock algorithms.  
* **Secure Boot/Authentication:** Support for modern authentication mechanisms (e.g., certificate-based) prior to connecting.

---

## **6\. Module C: Reverse Engineering & Competitor Analysis**

*A distinct suite of tools optimized for discovery and data collection on unknown vehicles.*

### **6.1 Network Identification**

* **Topology Scanner:** The system shall automatically scan supported physical interfaces to identify active nodes, broadcast IDs, and protocol types (Baud Rate detection).  
* **Traffic Analysis:** Real-time monitoring of raw bus traffic to identify periodic message IDs and communication patterns.

### 6.2 Automated Decoding & DBC Generation

*   **PID Decoder:** A built-in automated tool to query (brute-force or smart-fuzz) PIDs.
*   **DBC Export:** The system shall allow users to map discovered signals to names and **export the result as a `.dbc` file** compatible with `opendbc` and Vector tools.
*   **Live Interpretation:** The system shall parse incoming traffic using loaded DBC files.

### **6.3 Vehicle "Snapshot" Module**

* **Optimized UI:** A simplified, purpose-built sub-package/UI designed for rapid data capture.  
* **One-Click Parsing:** The module shall iterate through detected nodes to query and parse Identification DIDs (typically $F1xx) to extract:  
  * Hardware & Software Part Numbers.  
  * Calibration IDs.  
  * VIN & Config Data.  
* **Report Generation:** The snapshot must be exportable as a portable file format (JSON, HTML, CSV, or XML) for benchmarking.

---

## **7\. Automation & Integration**

### **7.1 External API**

* **COM / REST Interface:** The system must expose a comprehensive API to allow external applications (Python, C\#, TestStand) to control the software.  
* **Capabilities:** External scripts must be able to:  
  * Load Workspaces and Configurations.  
  * Connect/Disconnect Channels.  
  * Execute SWDL Sequences.  
  * Send Diagnostic Requests and Read Responses.  
  * Access logging data.

### **7.2 Internal Sequencing**

* **Logic Engine:** An internal scripting environment allowing users to chain diagnostic commands, add delays, and create simple loops (If/Else, While) without requiring an external compiler.

---

## **8\. Performance & System Requirements**

### **8.1 High-Load Optimization**

* **CPU Optimization:** The system must be optimized to handle high-load scenarios (e.g., full bus load on FlexRay) without dropping frames.  
* **Performance Mode:** The system must include a feature (e.g., disable\_ui\_log) that suppresses real-time UI updates to prevent CPU bottlenecks and buffer overflows during critical high-speed operations like CAN flashing.

### **8.2 Reliability**

* **Process Priority:** SWDL operations over CAN/DoIP must be prioritized to ensure process reliability.

### **8.3 System Requirements**

* **OS Compatibility:** The software must be compatible with Windows 10 and later operating systems.

