# vAccel Offloading

[vAccel](https://github.com/nubificus/vaccel) provides a lightweight abstraction for offloading compute-intensive functions like ML inference to available hardware accelerators, either locally or remotely.

## Features

- Unified API for various backends (CUDA, TVM, Torch)
- Runtime plugin system with support for RDMA, gRPC, vsock
- Can be embedded in devices or run as a remote service

## Deployment Architecture

```text
[ESP32 / Linux Device]
     |
     |  [vAccel Client Plugin]
     v
[RDMA/gRPC Transport]
     v
[vAccel Agent with Torch Plugin on Neighbor Node]
```

## Example Workflows

- Image classification offload from ESP32 to Jetson node
- Video frame preprocessing pushed to nearby GPU node

## Sample API

```C
vaccel_noop();
vaccel_image_classification(model, image_data, &result);
```
