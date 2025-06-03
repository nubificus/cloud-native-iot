# esp32-akri
ESP32 Component for managing the akri-related http endpoints of the device. The component does not contain the handlers, only the functions to setup handlers for the akri-specific endpoints. The corresponding handler functions are contained into the `ota-service` component.

## How to use

```bash
cd <path-to-your-esp-idf-project>
mkdir -p components
cd components
git clone https://github.com/nubificus/esp32-akri.git
```

Add the component to your project by simply adding the following line inside `idf_component_register()` of `<path-to-your-esp-idf-project>/main/CMakeLists.txt`:

```cmake
REQUIRES esp32-akri
```

E.g:

```cmake
idf_component_register(SRCS "test.c"
                       INCLUDE_DIRS "."
                       REQUIRES esp32-akri)
```

Afterwards, you can include the component's header file:
```c
#include "esp32-akri.h"
```

## API Reference
```c
int akri_server_start();

int akri_server_end();

int akri_set_update_handler(esp_err_t (*handler)(httpd_req_t *req));

int akri_set_info_handler(esp_err_t (*handler)(httpd_req_t *req));

int akri_set_onboard_handler(esp_err_t (*handler)(httpd_req_t *req));

int akri_set_temp_handler(esp_err_t (*handler)(httpd_req_t *req));

int akri_set_handler_generic(const char *uri,
                             httpd_method_t method,
                             esp_err_t (*handler)(httpd_req_t *req));
```
Make sure you have connected the device on the internet previously.

## Endpoints

The exported endpoints from esp32-akri are:

- `/info`
- `/onboard`
- `/update`

### `/info`
By sending a GET request to `/info`, one can retrieve information about the
device (device type, firmware version, firmware type etc) in JSON format.

### `/update`
On the other side, the update should be initialized through a POST request.
More specifically, the body of the request should include the IP address of the
OTA agent in the form: "ip: A.B.C.D". The handler then will extract the IP from
the request and initialize a TLS (secure) connection between the device and the
Agent. If the authentication succeeds, the device will receive the new
firmware.

### `/onboard` (FIXME)
Currently, the `/onboard` endpoint waits for GET requests, and responds with
the Attestation Certificate in PEM format. The purpose of this endpoint is to
enable the onboarding process of the device. **Important!!** However, the
current state is not secure at all, since the certificate is not transferred
over a TLS connection, thus it could get stolen by a malicious user with the
upper goal to impersonate a trusted device. Saying that, this endpoint should
probably receive POST requests, containing the IP address of an external TLS
server that could communicate securely with the IoT.
