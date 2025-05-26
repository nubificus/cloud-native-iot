# Cloud-native IoT Project Components Overview

This document provides a high-level overview of the key components that make up
the Cloud-native IoT project. 

## Secure Onboarding & Device Registration

- [DICE-based Attestation server](attestation-server.md): Simple entity deployed in a secure enclave that validates DICE certificates generated from leaf devices.
- [Onboarding and OTA update Service](esp32-akri.md): Component that integrates with the user application and provides endpoints to propagate general and attestation information to the rest of the system.
- [Enhanced Akri Discovery Handler](akri-dh.md): Facilitates dynamic discovery and inventory of IoT devices within Kubernetes clusters, based on Akri.

  <!-- [:octicons-arrow-right-24: Read More](onboarding/overview.md) -->

## OTA (Over-The-Air) Update Framework

- [OTA Agent](ota-agent.md): Manages firmware fetch and provides the update endpoint for devices.
- [OTA Service](ota-service.md): Runs on devices to securely receive, verify, and apply firmware updates.
- [TLS Security](mbedtls.md): Ensures encrypted communication and integrity of update payloads.

  <!-- [:octicons-arrow-right-24: Read More](ota-updates/overview.md) -->

## Cloud-Native Infrastructure

- [Kubernetes & Operators](flasjob.md): All components are deployed and managed using Kubernetes primitives, custom resource definitions (CRDs), and operators.
- [Application building & packaging](cloud-native-build.md): All components are built and packaged using standard cloud-native tooling.

<!---- Observability: Metrics, logs, and tracing are integrated to monitor device health, OTA progress, and offload performance. -->


  <!-- [:octicons-arrow-right-24: Read More](../flashjob-operator/overview.md) -->
<!-- 
# Onboarding Overview

Secure device onboarding is a cornerstone of our platform, enabling zero-touch, verifiable registration of edge devices. The onboarding workflow is anchored on the **DICE (Device Identifier Composition Engine)** standard and integrated with Akri to register and expose trusted devices within Kubernetes.

## Goals

- Ensure only trusted devices can join the system
- Automate device inventory creation
- Map discovered and authenticated devices as Kubernetes resources

## Core Components

- **DICE Auth Service**: Verifies attestation certificates from devices.
- **Submit Service**: Lightweight device-side tool to initiate onboarding.
- **Akri Integration**: Extends Akri discovery to perform security checks before admission.

## High-Level Flow

1. Device generates a DICE-based attestation report.
2. Device sends attestation + metadata via the Submit client.
3. DICE Auth Service verifies identity and signs onboarding token.
4. Akri registers device as a Kubernetes resource.

Trusted onboarding is a prerequisite for OTA updates and resource offloading.

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

# Resource Offloading

Edge devices often have limited compute resources. To support demanding workloads like ML inference or real-time data processing, we enable **secure and dynamic offloading** of compute tasks to neighboring or cloud-based accelerators.

## Key Concepts

- **vAccel**: Abstraction for heterogeneous acceleration (e.g., GPU, TPU).
- **Neighbor Offloading**: Offloading to nearby nodes in a federated edge setup.
- **Secure Channel**: All offloading happens over mutually authenticated, encrypted channels.

## Benefits

- Reduced on-device compute load
- Accelerated inference and analytics
- Seamless fallback to cloud if no neighbor is available

Offloading decisions are policy-driven and workload-aware.
-->
