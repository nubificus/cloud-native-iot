# OTA Update Framework

Our OTA framework enables secure and modular delivery of firmware and software updates to both ESP32 and Linux-based devices. The design separates update orchestration, delivery, and verification, ensuring robustness and extensibility.

## Key Goals

- Secure firmware delivery (TLS + attestation validation)
- Minimal downtime for device updates
- Support for heterogeneous targets (ESP32, Linux-class devices)
- CRD-based update management

## Core Components

- **OTA Agent**: Server-side control plane and proxy to firmware registry.
- **OTA Service**: Runs on devices; receives and applies updates.
- **Firmware Signing and Verification**: Ensures authenticity and integrity.

Only devices that pass onboarding can receive OTA updates.

