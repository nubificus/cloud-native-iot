# Linux-Akri

Linux-Akri is an onboarding and updating system for Linux. 

## Build

### Requirements
Python 3.5.2+

### Usage
To run the server, please execute the following from the root directory:

```
pip3 install -r requirements.txt
python3 -m openapi_server
```

To launch the integration tests, use tox:
```
sudo pip install tox
tox
```

### Running with Docker

To run the server on a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t openapi_server .

# starting up a container
docker run -p 8080:8080 openapi_server
```

## Endpoints

The API Specification is described below:

- `/info`: a GET request on this endpoint will return useful information about the device, like device type, version etc. For example:
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

- `/onboard`: The `/onboard` endpoint returns a DICE Attestation Certificate, used to prove the device's identity. The certificate can be verified against an Attestation Server, like [Dice-Auth](https://github.com/nubificus/dice-auth). Example:
```bash
$ curl 192.168.122.67/onboard
-----BEGIN CERTIFICATE-----
MIIC0jCCAnigAwIBAgIUfcRQ6Y/ZwvPtXF58PF0pZRQo4gAwCgYIKoZIzj0EAwQw
MzExMC8GA1UEBRMoN2RjNDUwZTk4ZmQ5YzJmM2VkNWM1ZTdjM2M1ZDI5NjUxNDI4
ZTIwMDAgFw0xODAzMjIyMzU5NTlaGA85OTk5MTIzMTIzNTk1OVowMzExMC8GA1UE
BRMoN2RjNDUwZTk4ZmQ5YzJmM2VkNWM1ZTdjM2M1ZDI5NjUxNDI4ZTIwMDBZMBMG
ByqGSM49AgEGCCqGSM49AwEHA0IABFF+Vw/AqiUxPM7jYqovKuiwYb8MAiGR0Tbc
yH4vEO2uSd8RNpKz03bkoWGfuZaH/uf8amoW94rwuIz6ve0c/bSjggFmMIIBYjAf
BgNVHSMEGDAWgBR9xFDpj9nC8+1cXnw8XSllFCjiADAdBgNVHQ4EFgQUfcRQ6Y/Z
wvPtXF58PF0pZRQo4gAwDgYDVR0PAQH/BAQDAgIEMA8GA1UdEwEB/wQFMAMBAf8w
gf4GCisGAQQB1nkCARgBAf8EgewwgemgQgRAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKNCBEAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAApEIEQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACmAwoBAKcWDBRvcGVu
c3NsLmV4YW1wbGUucDI1NjAKBggqhkjOPQQDBANIADBFAiEAkTn8A6XUpDW6V+xY
jvYU4HhoB0UlK3ErOGJwJm76lDMCIH4bPrAt5QT+bddhskfGG9cZT1D1wnzB0kPH
fbLzfaQf
-----END CERTIFICATE-----
```
Correspondingly, we see the following output on device's console:
```console
52:54:00:24:7d:77
192.168.122.67 - - [03/Jul/2025 08:20:20] "GET /onboard HTTP/1.1" 200 -
```
The first line shows the MAC address, which is used as the Unique Device Secret during certificate generation.

- `/update`: The `/update` endpoint handles POST requests to switch the currently running container image with a new one, provided in the request. Now, there are two options to update the current container image: The non-secure and the secure. In the non-secure case, the update proceeds without authentication. In the secure case, end-to-end device authentication is required before the image is provided. A non-secure example, where the container image is given directly:

```bash
$ curl -H 'Content-Type: application/json' -d '{ "docker_image": "hello-world" }' -X POST 192.168.122.67/update
"Container was initiated with the provided image!"
```
The following messages appear on the device console:
```console
Docker image to use:  hello-world
Deleting the container..
workload
192.168.122.67 - - [03/Jul/2025 09:21:11] "POST /update HTTP/1.1" 200 -
```
which means that the current container was deleted before running a new one with the given "hello-world" image.

Of course, the secure case is a bit more complex. Instead of directly passing the "docker-image" argument in the POST request, we leave that attribute empty. However, additional arguments must be provided. The secure update process redirects `linux-akri` to a secure agent, which authenticates the device using its DICE Attestation certificate and then delivers the new container image.

```bash
$ export AGENT_IP=...
$ curl -H 'Content-Type: application/json' -d '{ "args": ["--ip", "$AGENT_IP"], "docker_image" : "" }' -X POST 192.168.122.67/update
```
Now the agent here is an [updated version of the ESP32 OTA Agent](https://github.com/nubificus/ota-agent/tree/feat_linux_akri) which, instead of transmitting firmware to verified devices, supplies `linux-akri` with the new container image to deploy.

The agent I used (after having built it by following the instructions of the aforementioned repository):
```bash
$ export CONTAINER_IMG=hello-world
$ export DICE_AUTH_URL=http://localhost:8000
$ export SERVER_KEY_PATH=crt/key.pem
$ export SERVER_CRT_PATH=crt/cert.pem
$ ./ota-agent
```

Furthermore, a Dice-Auth Attestation server is required to work along the Agent. See the [instructions](https://github.com/nubificus/dice-auth).

The output on the device console:
```console
Agent IP:  localhost
52:54:00:24:7d:77
Docker image to use:  hello-world
Deleting the container..
workload
192.168.122.67 - - [03/Jul/2025 10:15:38] "POST /update HTTP/1.1" 200 -

```
