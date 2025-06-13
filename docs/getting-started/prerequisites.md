# Prerequisites

Before you begin with the Cloud-Native IoT platform, make sure you have the following in place:

---

## 1. Hardware Requirements

- **IoT Device**  
  - ESP32 / ESP32-S2 / ESP32-S3 dev board  
  - We have tested the following devices: [Supported Microcontroller List](https://github.com/nubificus/wiki/blob/main/infrastructure/microcontroller_nodes.md).   
  - *Note: - *Note: Use of other compatible  boards is supported but not formally validated.*
- **Control Plane Node**  
  - x86_64 VM or bare-metal  
  - 2 vCPU, 4 GB RAM (min)  
- **Worker Nodes (optional, recommended ×2)**  
  - x86_64 VM or bare-metal each  
  - 2 vCPU, 4 GB RAM (min)  
  - *Note: For minimal testing, a single node (control plane only) is sufficient. For production or realistic scenarios, at least two worker nodes are recommended.*

---

## 2. Host Machine Software

| Tool                   | Version Requirement         | Install Guide                                                 |
| ---------------------- | --------------------------- | ------------------------------------------------------------- |
| Git                    | ≥ 2.30                      | https://git-scm.com/downloads                                 |
| Docker or Podman       | Latest stable               | https://docs.docker.com/get-docker/                           |
| Python                 | ≥ 3.8                       | https://www.python.org/downloads/                             |
| Go                     | ≥ 1.20                      | https://go.dev/doc/install                                    |
| ESP-IDF                | Latest                      | https://docs.espressif.com/projects/esp-idf/en/latest/get-started/ |
| CMake, Ninja, build-essential (Linux) | –           | `sudo apt install cmake ninja-build build-essential`          |

---

## 3. Kubernetes Cluster

- **k3s** version ≥ 1.25  
  - Quickstart: https://rancher.com/docs/k3s/latest/en/quick-start/  
- **kubectl**  
  - Install: https://kubernetes.io/docs/tasks/tools/  
- **Helm**  
  - Install: https://helm.sh/docs/intro/install/  

---

## Reference Docs

- [Architecture Overview](../architecture/index.md)
- [ESP32 Firmware Build](../tutorials/esp32-initial.md)
- [End-to-End Scenario](../tutorials/e2e.md) 

---

Ready? Move on to the [Quickstart Guide](quickstart.md).