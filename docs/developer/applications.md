# Application development

## Introduction

Developing IoT applications using ESP32 typically begins with flashing firmware to a single device via USB during development. This is suitable for initial prototyping or testing.

```bash
idf.py build
idf.py --port /dev/ttyUSB0 flash monitor
```

However, as systems scale, this manual approach becomes infeasible and introduces operational challenges.

## The Challenge of Scalability

Consider an application such as a **smart air quality sensor** deployed across a whole city. You might start with a handful of devices but eventually grow to manage hundreds or thousands.

Challenges emerge when:
- A **critical firmware update** needs to be pushed to all devices.
- You want **centralized monitoring and lifecycle management** of each sensor node.

In such cases, physically accessing and flashing each device is impractical and unscalable.

## Our Approach to Scalable Management

To address these limitations, we have developed the following two components as part of our Cloud-Native IoT Platform, which users can integrate into their ESP32 applications:

| Component | Purpose |
|----------|---------|
| [`esp32-akri`](https://github.com/nubificus/esp32-akri) | Enables ESP32 devices to register with Kubernetes clusters via Akri, facilitating automated discovery and management. |
| [`ota-service`](https://github.com/nubificus/ota-service) | Provides secure over-the-air (OTA) firmware updates for ESP32, eliminating the need for manual reflashing. |

Together, they enable ESP32 devices to become manageable, cloud-native compute nodes.

## Integration Guide

### 1. Setting Up the ESP32 Project Structure

Assume your project has the following structure:

```
your-project/
├── components/
├── main/
│   ├── main.cc
│   └── CMakeLists.txt
├── CMakeLists.txt
└── ...
```

Clone the required components:

```bash
mkdir -p components && cd components
git clone https://github.com/nubificus/ota-service
git clone https://github.com/nubificus/esp32-akri
```

### 2. Registering the Components in CMake

Modify `main/CMakeLists.txt`:

```cmake
idf_component_register(SRCS "main.cc"
                       INCLUDE_DIRS "."
                       REQUIRES esp32-akri ota-service)
```

### 3. Including Required Headers

In `main.cc`:

```cpp
extern "C" {
  #include "esp32-akri.h"
  #include "ota-service.h"
}
```

### 4. Providing Device Metadata to the System

This function provides metadata for Akri and OTA usage:

```cpp
esp_err_t info_get_handler(httpd_req_t *req)
{
    char json_response[128];
    snprintf(json_response, sizeof(json_response),
             "{"device":"%s","application":"%s","version":"%s"}",
             DEVICE_TYPE, APPLICATION_TYPE, FIRMWARE_VERSION);
    httpd_resp_set_type(req, "application/json");
    httpd_resp_send(req, json_response, strlen(json_response));
    return ESP_OK;
}
```

### 5. Handling Configuration via Root CMake

Those two components require the following environment variables:
* `FIRMWARE_VERSION`: A unique version identifier for the application you are working on.
* `DEVICE_TYPE`: The specific ESP32 target for which you will build this application.
* `APPLICATION_TYPE`: The type of application you are developing (e.g. image_classification, etc.).
* `OTA_SECURE`: Set this variable when you want to use secure OTA update services.

Edit your root `CMakeLists.txt` to handle environment configuration by adding the code below:

```cmake
if(NOT DEFINED ENV{FIRMWARE_VERSION})
    add_compile_definitions(FIRMWARE_VERSION="0.1.0")
else()
    add_compile_definitions(FIRMWARE_VERSION=\"$ENV{FIRMWARE_VERSION}\")
endif()

if(NOT DEFINED ENV{DEVICE_TYPE})
    add_compile_definitions(DEVICE_TYPE="esp32")
else()
    add_compile_definitions(DEVICE_TYPE=\"$ENV{DEVICE_TYPE}\")
endif()

if(NOT DEFINED ENV{APPLICATION_TYPE})
    add_compile_definitions(APPLICATION_TYPE="generic")
else()
    add_compile_definitions(APPLICATION_TYPE=\"$ENV{APPLICATION_TYPE}\")
endif()

if(DEFINED ENV{OTA_SECURE})
    add_compile_definitions(OTA_SECURE=1)
endif()
```

### 6. Initializing Akri and OTA in the Application

In `app_main()`:

```cpp
void app_main(void)
{
    int ret;

    ret = akri_server_start();
    if (ret) {
        ESP_LOGE("main", "Cannot start Akri server");
        abort();
    }

    ret = akri_set_info_handler(info_get_handler);
    if (ret) {
        ESP_LOGE("main", "Cannot set info handler");
        abort();
    }
}
```

### 7. Setting Environment Variables Before Build

Before building, export the following:

```bash
export FIRMWARE_VERSION="0.0.1"
export DEVICE_TYPE="esp32s3"
export APPLICATION_TYPE="thermo"
export OTA_SECURE=1
```

### 8. Building and Flashing the Application

```bash
idf.py build
idf.py --port /dev/ttyUSB0 flash monitor
```

Once deployed, your device will be:
- Discoverable through Akri.
- OTA-ready for firmware updates.
- Exposing device metadata via HTTP.

## Conclusion

Integrating Akri and OTA-Service into your ESP32 firmware empowers you with production-grade capabilities, including:

- Scalable remote firmware management.
- Dynamic discovery and orchestration through Kubernetes.

When combined with the advanced CI/CD pipeline outlined in the [Build Automation](build_automation.md) section, you can achieve a streamlined development process that enhances efficiency, reduces deployment times, and ensures consistent application performance across your IoT devices.
