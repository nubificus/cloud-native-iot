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
