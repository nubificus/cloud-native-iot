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

