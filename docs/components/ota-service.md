# OTA Service

The OTA Service is an ESP32 Component for performing Over the Air updates. The component contains only the handlers. To setup the functions as akri-endpoints handlers, use the `esp32-akri` component.

## Responsibilities

- Prepare the board for an OTA firmware update
- Provide the handler functions to perform the OTA update
- Handle errors if the OTA update is incomplete

## Endpoints

- Setup by `esp32-akri`.

## Deployment Notes

- Packaged as an `ESP-IDF` component.

## How to use

```bash
cd <path-to-your-esp-idf-project>
mkdir -p components
cd components
git clone https://github.com/nubificus/ota-service.git
```

Add the component to your project by simply adding the following line inside `idf_component_register()` of `<path-to-your-esp-idf-project>/main/CMakeLists.txt`:

```cmake
REQUIRES ota-service
```

E.g:

```cmake
idf_component_register(SRCS "test.c"
                       INCLUDE_DIRS "."
                       REQUIRES ota-service)
```

You may also have to add the following configuration to resolve some `mbedtls` issues:

```bash
idf.py menuconfig
```

and enable `Component config -> mbedTLS -> HKDF Algorithm (RFC 6859)`

Afterwards, you can include the component's header file:

```c
#include "ota-service.h"
```

## API Reference

```c
/*
 * this function can be passed as an
 * argument in `akri_set_update_handler()`
 * so that it (only) runs when we receive a
 * POST request at `/update` endpoint.
 * */
esp_err_t ota_request_handler(httpd_req_t *req);
```

The component follows the secure OTA workflow when `OTA_SECURE` macro is defined. Otherwise, the update is non-secure.
