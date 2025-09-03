# Gemini OBD-II Diagnostic Tool

A multi-adapter vehicle diagnostic tool with a graphical user interface, built with Python and PyQt5. This tool allows users to connect to vehicles using different communication protocols like ELM327 (Serial) and DoIP (Ethernet) to read diagnostic data.

## Features

*   **Multi-Adapter Support:** Connect to vehicles using ELM327 or DoIP adapters.
*   **Real-time Data:** View real-time vehicle data such as RPM, speed, and coolant temperature.
*   **Diagnostic Trouble Codes (DTCs):** Read and clear diagnostic trouble codes.
*   **Custom Commands:** Send custom UDS commands for advanced diagnostics.
*   **User-Friendly Interface:** A simple and intuitive GUI for easy operation.
*   **Extensible:** Easily add new commands by editing the `commands.json` file.

## Requirements

*   Python 3.6+
*   PyQt5
*   python-obd
*   pyserial
*   pydoipclient
*   udsoncan

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-directory>
    ```

2.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```

2.  **Select the connection type:**
    *   For **ELM327 (Serial)**, select the correct serial port from the dropdown menu.
    *   For **DoIP (Ethernet)**, enter the vehicle's IP address and the ECU's logical address.

3.  **Click "Connect"** to establish a connection with the vehicle.

4.  **Send commands:**
    *   Click on the predefined command buttons to send requests to the vehicle.
    *   Use the "Add New Command" button to send custom UDS commands.

5.  **View data:**
    *   The "Data Viewer" will display the responses from the vehicle.
    *   The "Log" panel will show the communication logs and any errors.

6.  **Click "Disconnect"** to close the connection.

## How it Works

The application uses a modular architecture with a core communication manager and pluggable adapters for different protocols. The GUI is built with PyQt5 and runs the communication logic in a separate thread to prevent it from freezing.

Commands are loaded from the `commands.json` file, which can be easily edited to add new commands without modifying the source code.
