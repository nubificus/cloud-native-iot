# ESP32 Akri Component

ESP32 Component for managing the akri-related HTTP endpoints of the device.
The component does not contain the handlers, only the functions to setup
handlers for the akri-specific endpoints. The corresponding handler functions
are contained into the `ota-service` component. Furthermore, it enables us to
start (prerequisite to setup endpoint) and stop the HTTP server, as well as
define handlers for generic methods and endpoints.

## Responsibilities

- Provide functions that enable the user to set handlers for various events,
  like information request, onboarding request and update request.
- Manage all the rest HTTP endpoints by letting the user set handlers for any
  endpoint, start and stop the HTTP server.

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
[Agent](/components/ota-agent). If the authentication succeeds, the device will
receive the new firmware.

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

## Note: Linux-Akri

Except for ESP32 devices there's also support for OTA updates on Linux devices.
Linux-Akri is an onboarding and updating system for Linux, not in terms of
firmware updates, but for updating currently running containers by providing a
new container image.

### Requirements

Python 3.5.2+

### Usage

To run the server, please execute the following from the root directory:

```bash
pip3 install -r requirements.txt
python3 -m openapi_server
```

To launch the integration tests, use tox:

```bash
sudo pip install tox
tox
```

### Running with Docker

To run the server on a Docker container, please execute the following from the
root directory:

```bash
# building the image
docker build -t openapi_server .

# starting up a container
docker run -p 8080:8080 openapi_server
```

### Endpoints

The API Specification is described below:

- `/info`: a GET request on this endpoint will return useful information about
  the device, like device type, version etc. For example:

```bash
$ curl 192.168.122.67/info
{
  "application": "generic",
  "device": "rpi5-5",
  "version": "0.0.10"
}
```

Meanwhile, the device console shows:

```console
192.168.122.67 - - [03/Jul/2025 08:14:32] "GET /info HTTP/1.1" 200 -
```

- `/onboard`: The `/onboard` endpoint returns a DICE Attestation Certificate,
  used to prove the device's identity. The certificate can be verified against
  an Attestation Server, like [Dice-Auth](https://github.com/nubificus/dice-auth).
  Example:

```bash
$ curl 192.168.122.67/onboard
-----BEGIN CERTIFICATE-----
[...]
-----END CERTIFICATE-----
```

Correspondingly, we see the following output on device's console:

```console
52:54:00:24:7d:77
192.168.122.67 - - [03/Jul/2025 08:20:20] "GET /onboard HTTP/1.1" 200 -
```

The first line shows the MAC address, which is used as the Unique Device Secret
during certificate generation.

- `/update`: The `/update` endpoint handles POST requests to switch the
  currently running container image with a new one, provided in the request.
  Now, there are two options to update the current container image: The non
  secure and the secure. In the non-secure case, the update proceeds without
  authentication. In the secure case, end-to-end device authentication is
  required before the image is provided. A non-secure example, where the
  container image is given directly:

```bash
$ curl -H 'Content-Type: application/json' \
  -d '{ "docker_image": "hello-world" }' \
  -X POST 192.168.122.67/update
"Container was initiated with the provided image!"
```

The following messages appear on the device console:

```console
Docker image to use:  hello-world
Deleting the container..
workload
192.168.122.67 - - [03/Jul/2025 09:21:11] "POST /update HTTP/1.1" 200 -
```

which means that the current container was deleted before running a new one
with the given "hello-world" image.

Of course, the secure case is a bit more complex. Instead of directly passing
the "docker-image" argument in the POST request, we leave that attribute empty.
However, additional arguments must be provided. The secure update process
redirects `linux-akri` to a secure agent, which authenticates the device using
its DICE Attestation certificate and then delivers the new container image.

```bash
export AGENT_IP=...
curl -H 'Content-Type: application/json' \
  -d '{ "args": ["--ip", "$AGENT_IP"], "docker_image" : "" }' \
  -X POST 192.168.122.67/update
```

Now the agent here is the same as the
[ESP32 OTA Agent](https://github.com/nubificus/ota-agent), except for the
different environment variable we use to define the content to be sent. Instead
of defining `NEW_FIRMWARE_PATH`, as we do in ESP32 OTA updates, we now define
`CONTAINER_IMG` to transmit the new image descriptor.

After having built the agent by following the instructions of the aforementioned
repository:

```bash
export CONTAINER_IMG=hello-world
export DICE_AUTH_URL=http://localhost:8000
export SERVER_KEY_PATH=crt/key.pem
export SERVER_CRT_PATH=crt/cert.pem
./ota-agent
```

Furthermore, a Dice-Auth Attestation server is required to work along the Agent.
See the [instructions](https://github.com/nubificus/dice-auth).

The output on the device console:

```console
Agent IP:  localhost
52:54:00:24:7d:77
Docker image to use:  hello-world
Deleting the container..
workload
192.168.122.67 - - [03/Jul/2025 10:15:38] "POST /update HTTP/1.1" 200 -
```
