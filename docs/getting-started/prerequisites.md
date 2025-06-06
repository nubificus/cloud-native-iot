# Prerequisites

Before you begin with the Cloud-Native IoT platform, make sure you have the following in place:

---

## 1. Hardware Requirements

## IoT Device

**ESP32 / ESP32-S2 / ESP32-S3**  
We have tested the following device types:

- ESP32-C6
- ESP32-S2R2
- ESP32-S3
- ESP32-D0WD-V3

_Note: Use of other compatible boards is supported but not formally validated._

- **Control Plane Node**
  - x86_64 VM or bare-metal
  - 2 vCPU, 4 GB RAM (min)
- **Worker Nodes (optional, recommended ×2)**
  - x86_64 VM or bare-metal each
  - 2 vCPU, 4 GB RAM (min)
  - _Note: For minimal testing, a single node (control plane only) is sufficient. For production or realistic scenarios, at least two worker nodes are recommended._

## 2. Host Machine Software

| Tool                                  | Version Requirement | Install Guide                                                                                 |
| ------------------------------------- | ------------------- | --------------------------------------------------------------------------------------------- |
| Git                                   | ≥ 2.30              | [Git Downloads](https://git-scm.com/downloads)                                                |
| Docker or Podman                      | Latest stable       | [Docker Installation](https://docs.docker.com/get-docker/)                                    |
| Python                                | ≥ 3.8               | [Python Downloads](https://www.python.org/downloads/)                                         |
| Go                                    | ≥ 1.20              | [Go Installation](https://go.dev/doc/install)                                                 |
| ESP-IDF                               | Latest              | [ESP-IDF Getting Started](https://docs.espressif.com/projects/esp-idf/en/latest/get-started/) |
| CMake, Ninja, build-essential (Linux) | –                   | `sudo apt install cmake ninja-build build-essential`                                          |

---

## 3. Kubernetes Cluster

- **k3s** version ≥ 1.25

  - [Quickstart Guide](https://rancher.com/docs/k3s/latest/en/quick-start/)

- **kubectl**

  - [Install kubectl](https://kubernetes.io/docs/tasks/tools/)

- **Helm**
  - [Install Helm](https://helm.sh/docs/intro/install/)

## Reference Docs

- [Architecture Overview](../architecture/index.md)
- [ESP32 Firmware Build](../tutorials/esp32-initial.md)
- [End-to-End Scenario](../tutorials/e2e.md)

---

Ready? Move on to the [Quickstart Guide](quickstart.md).
