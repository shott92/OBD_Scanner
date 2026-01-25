# Developer Guide

Welcome to the **CANdy_Diag_Pro** development team! This guide covers the system architecture, setup, and coding standards.

## 🏗️ Architecture Overview

The system follows a modular, domain-driven architecture to separate UI logic from Core engineering logic.

### Directory Structure
```text
CANdy_Diag_Pro/
├── core/                   # Business Logic & backend
│   ├── hal/                # Hardware Abstraction Layer (VCIInterface, J2534)
│   ├── session/            # State Persistence (Workspace/Project)
│   ├── adapters/           # Protocol implementations (DoIP, ELM327)
│   ├── processing/         # JIT-optimized algorithms (Signal, Checksum)
│   └── communication_manager.py # Bridge between GUI and Adapters
├── gui/                    # User Interface (PyQt5)
│   ├── widgets/            # Reusable UI components
│   └── main_window.py      # Main Application Window
├── docs/                   # Documentation
└── main.py                 # Entry Point
```

### Key Components

#### 1. Hardware Abstraction Layer (HAL)
Located in `core/hal/`, the `VCIInterface` class defines the contract for all hardware adapters.
*   **Goal**: Allow swapping hardware (e.g., swapping an ELM327 for a Vector VN1630) without changing the UI code.
*   **Adding a New Adapter**: Inherit from `VCIInterface` and implement `connect()`, `disconnect()`, `send_frame()`, and `read_frame()`.

#### 2. Session Management
Located in `core/session/`.
*   **Workspace**: Stores application-wide settings (Theme, Last used Adapter) and references to loaded Projects.
*   **Project**: Stores specific vehicle configurations (Protocol Baud Rates, Channel Mappings).
*   **Persistence**: Data is serialized to JSON.

#### 3. Communication Manager
`core/communication_manager.py` acts as the Controller.
*   Runs in a background thread (via Qt).
*   Manages the active Adapter instance.
*   Emits signals (`connection_status`, `data_received`) to update the GUI safely.

## 🚀 Setting Up the Development Environment

1.  **Python Version**: We target **Python 3.13**. Please ensure you have it installed to test JIT optimizations.
2.  **Virtual Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🧪 Testing & Verification

*   **Integration Tests**: We currently rely on manual verification using the "Simulated" or "ELM327" adapters.
*   **Performance (JIT)**:
    *   Test CPU-bound logic (decoders in `core/processing`) using the `timeit` module.
    *   Refer to `docs/PERFORMANCE.md` for details.

## 🤝 Contribution Guidelines

1.  **Code Style**: Follow PEP 8.
2.  **Architecture**: Do NOT import `PyQt5` inside `core/` modules (except for Signal definitions in Managers) to keep the backend testable without a UI.
3.  **Async/Threading**: Long-running hardware operations must run in the `CommunicationManager` thread, never blocking the Main GUI thread.

## 📅 Roadmap (Phase 2)
*   Implement `DiagnosticService` for handling complex UDS flows.
*   Integrate the SWDL (Software Download) Engine.
*   Add DBC File Parsing.
