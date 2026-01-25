# Network Option Categorization

## Primary (Visible in Main UI)
These are the minimal settings required to establish a connection in 90% of cases.
1.  **Gateway IP** (Target IP)
2.  **Logical Tester ID** (My Address)
3.  **Target Node ID** (ECU Address)

## Advanced (Hidden in Settings Dialog)
These are for power users, specific OEM quirks, or complex network setups.

### Application / Transport
*   **Protocol Version**: (Default: 2012/ISO)
*   **TCPStack**: (Default / Custom Pcap)
*   **ConnectOption**: (TCP / UDP)
*   **ServerPort**: (Local listening port)
*   **Source IP**: (Interface binding)
*   **EnablePCapLogging** & **Filter**

### Timings & Retries
*   **ResponseTimeout** / **ExtendedResponseTimeout**
*   **AckWaitTime**
*   **Command Retries**: NRC21RetryCount, ReconnectionRetryCount, VehicleDiscoveryRetryCount.
*   **Delays**: SocketActivationDelay, NRC21RetryDelay.

### Routing & Activation
*   **Activation Type**: SendRoutineActivationRequest (Default/WWH-OBD/OEM).
*   **OEM Specifics**: OEMBytes, SendOEMBytesRoutineActivationRequest.
*   **Padding**: Status & Value.

### VLAN & Ethernet (Layer 2/3)
*   **VLAN IDs**: VLAN_ID, Priorities (Diag, ARP, CnC).
*   **Subnet Mask** & **Multicast IP**.
