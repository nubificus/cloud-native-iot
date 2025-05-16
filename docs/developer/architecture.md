# System Architecture

Our platform spans cloud, edge, and device layers with secure orchestration, discovery, and task delegation built into each layer.

## High-Level Architecture

```text
+-----------------+
| Cloud Platform  |
+-----------------+
         ^
         |
+----------------+   +------------------+    +------------------+
| Edge Node(s)   |<--| Akri + Offloader |<-->| Neighbor Devices |
+----------------+   +------------------+    +------------------+
         ^
         |
+----------------+     +-------------------+
| IoT Devices    |<--->| Onboarding Agent  |
+----------------+     +-------------------+
```

## Key Components

- Onboarding Service: Securely verifies device identity (DICE-based)

- Akri: Dynamically discovers and exposes verified devices

- OTA Service & Agent: Secure firmware update management

- vAccel Offloader: Enables remote compute delegation

## Technology Stack

- Kubernetes
- Akri + CRDs
- mbedTLS
- Rust, Go, C, Python
