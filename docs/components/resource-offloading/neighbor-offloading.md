# Neighbor Node Offloading

In addition to centralized cloud offloading, our framework supports peer-to-peer offloading across trusted edge nodes.

## Discovery & Matching

- Neighbor nodes advertise capabilities (e.g., "GPU", "AI-accelerator")
- Devices query available nodes based on workload needs
- Matching is done using Kubernetes labels and Akri resource metadata

## Offload Policy Engine

Policies determine:

- Whether offloading is allowed
- Preferred nodes (e.g., same rack, region)
- Resource thresholds

## Secure Offload Channels

All offloads are done via:

- **Mutual TLS** (mbedTLS + x509 certs)
- Or **RDMA over trusted LAN segments**
- Device attestation verified before accepting remote compute

## Use Case Example

```text
[ESP32 Camera] --> [Jetson Node w/ Torch Inference] --> [Result Streamed Back]
```
