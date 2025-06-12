# ESP32 Akri Component

ESP32 Component for managing the akri-related HTTP endpoints of the device.
The component does not contain the handlers, only the functions to setup
handlers for the akri-specific endpoints. The corresponding handler functions
are contained into the `ota-service` component. Furthermore, it enables us to
start (prerequisite to setup endpoint) and stop the HTTP server, as well as
define handlers for generic methods and endpoints.

## Responsibilities

- Provide functions that enable the user to set handlers for various events, like information request, onboarding request and update request.
- Manage all the rest HTTP endpoints by letting the user set handlers for any endpoint, start and stop the HTTP server.

## Deployment Notes

- Packaged as an `ESP-IDF` component.

## API Reference

```c
int akri_server_start();
```

The function can be used to initialize an underlying HTTP
server, on which later one can define handler functions for
any endpoint.

**Returns:** `ESP_OK` on success, an error code otherwise.

```c
int akri_server_end();
```

Correspondingly, `akri_server_end()` can be used to stop the
HTTP server.

**Returns:** `ESP_OK` on success, an error code otherwise.

```c
int akri_set_update_handler(esp_err_t (*handler)(httpd_req_t *req));
```

Define a function to handle POST requests on `/update` endpoint.
Keep in mind the body of the request, which should contain an IP
in the following form: "ip: X.X.X.X"

**Parameters:**

- `handler`: a pointer to the function that will handle POST requests on `/update`

**Returns:** `ESP_OK` on success, an error code otherwise.

```c
int akri_set_info_handler(esp_err_t (*handler)(httpd_req_t *req));
```

Define a function to handle GET requests on `/info` endpoint.

**Parameters:**

- `handler`: a pointer to the function that will handle GET requests on `/info`

**Returns:** `ESP_OK` on success, an error code otherwise.

```c
int akri_set_onboard_handler(esp_err_t (*handler)(httpd_req_t *req));
```

Define a function to handle GET requests on `/onboard` endpoint.

**Parameters:**

- `handler`: a pointer to the function that will handle GET requests on `/onboard`

**Returns:** `ESP_OK` on success, an error code otherwise.

```c
int akri_set_handler_generic(const char *uri,
                             httpd_method_t method,
                             esp_err_t (*handler)(httpd_req_t *req));
```

The generic define-handler function: You may use it to define
functions to handle any endpoint of any method.

**Parameters:**

- `uri`: the endpoint uri to configure
- `method`: the HTTP method that will be handled. See [esp-idf](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/protocols/esp_http_server.html).
- `handler`: a pointer to the function that will handle `method` requests on `/<uri>`

**Returns:** `ESP_OK` on success, an error code otherwise.

Make sure you have connected the device on the internet previously.

## Endpoints

The exported endpoints from esp32-akri are:

- `/info`
- `/onboard`
- `/update`

### `/info`

By sending a GET request to `/info`, one should retrieve information about the
device (device type, firmware version, firmware type etc) in JSON format.

### `/update`

On the other side, the update should be initialized through a POST request.
More specifically, the body of the request should include the IP address of the
OTA agent in the form: "ip: A.B.C.D". The handler then will extract the IP from
the request and initialize a TLS (secure) connection between the device and the
[Agent](/components/ota-agent). If the authentication succeeds, the device will receive the new
firmware.

### `/onboard`

Currently, the `/onboard` endpoint waits for GET requests, and responds with
the Attestation Certificate in PEM format. The purpose of this endpoint is to
enable the onboarding process of the device. **Important!!** However, the
current state is not secure at all, since the certificate is not transferred
over a TLS connection, thus it could get stolen by a malicious user with the
upper goal to impersonate a trusted device. Saying that, this endpoint should
probably receive POST requests, containing the IP address of an external TLS
server that could communicate securely with the IoT.
For installation instructions see the [tutorial](/tutorials/akri-esp32).
