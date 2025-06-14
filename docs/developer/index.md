# Overview

The Developer section is intended for contributors and advanced users who want to extend, customize, or integrate with the Cloud-Native IoT platform. It provides the internal architecture details, code structure, and tooling guidance necessary to build and maintain platform components.

Whether you're developing new plugins, modifying the onboarding logic, or integrating with third-party systems, this guide will help you understand how the platform works under the hood.

What you'll find here:

- [Application bootstrap](applications.md): How to structure and code in the logic for your application.
- [Application building](build_automation.md): How to build and package ESP32 applications using our automated CI/CD workflows.
- [Firmware packaging](firmware_packaging.md): How the workflows package app binaries for multiple ESP32 targets as OCI images and manifests.
- [Initial flash packaging](initial_flash_packaging.md): How the workflows prepare multi-arch OCI manifests for flashing devices for the first time.
- [High-level Architecture](architecture.md) as a basis to extend the platform: Guidelines for adding new device types, API endpoints, or custom discovery mechanisms.

This section is the go-to resource for anyone looking to contribute to the platform or build custom integrations atop its core functionality.
