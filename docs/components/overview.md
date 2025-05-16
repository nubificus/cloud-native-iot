# Cloud-native IoT Project Components Overview

This document provides a high-level overview of the key components that make up the Cloud-native IoT project. 

---

## Secure Onboarding & Device Registration

- DICE-based Attestation: Devices use DICE evidence to prove their identity securely during onboarding.
- Onboarding Service: Verifies device attestation certificates and registers devices into the system.
- Akri Integration: Facilitates dynamic discovery and inventory of IoT devices within Kubernetes clusters.

  [:octicons-arrow-right-24: Read More](onboarding/overview.md)

---

## OTA (Over-The-Air) Update Framework

- OTA Agent: Manages firmware fetch and provides the update endpoint for devices.
- OTA Service: Runs on devices to securely receive, verify, and apply firmware updates.
- TLS Security: Ensures encrypted communication and integrity of update payloads.

  [:octicons-arrow-right-24: Read More](ota-updates/overview.md)

---

## Application & Device Management APIs

- Expose REST endpoints to query device and application info.
- Provide APIs for triggering OTA updates and retrieving attestation certificates.
- Enable remote management actions via secure and authenticated HTTP interfaces.

---

## Compute Offloading with vAccel

- vAccel: Allows lightweight, scalable offloading of compute-intensive tasks from edge devices to nearby accelerators or cloud resources.
- Custom Transport: Supports TCP sockets for communication.
- Integrates seamlessly with Kubernetes-native mechanisms.

  [:octicons-arrow-right-24: Read More](resource-offloading/overview.md)

---

## Cloud-Native Infrastructure

- Kubernetes & Operators: All components are deployed and managed using Kubernetes primitives, custom resource definitions (CRDs), and operators.
- Secure Identity & Communication: Mutual TLS, certificate management, and token-based authentication ensure system-wide security.
<!---- Observability: Metrics, logs, and tracing are integrated to monitor device health, OTA progress, and offload performance. -->


  [:octicons-arrow-right-24: Read More](../flashjob-operator/overview.md)
