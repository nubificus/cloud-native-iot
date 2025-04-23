# OTA Agent

OTA-agent is resposible for communicating with the device and authenticate it. Actually, the program operates as a TLS server (thus, the communication is secure) and waits for an upcoming connection from the microcontroller that has been requested to update its firmware. As being described in the graphs of `docs/design/ota_process.md`, when it's about to update, the microcontroller will receive a POST request to its `/update` endpoint. The request will contain an IP address on its body, like `ip: A.B.C.D`. This IP belongs to the agent, which should have been executed earlier. The agent requires the following arguments to run, which are given as environment variables:

- `NEW_FIRMWARE_PATH`: The path to the firmware that will be sent to the microcontroller (on successs)
- `DICE_AUTH_URL`: The URL to connect to Dice-Auth HTTP server, to authenticate the connected microcontroller. Under the hood, the agent will send the received Attestation Certificate, while Dice-Auth will verify it against the saved Root certificates.
- `SERVER_CRT_PATH`: The certificate to be used by the TLS server. It can be generated using commands like `openssl genpkey -algorithm RSA -out key.pem` and `openssl req -new -x509 -key key.pem -out cert.pem -days 365`.
- `SERVER_KEY_PATH`: The private key to be used by the TLS server. Can be generated as shown above.

# Build

```bash
git submodule update --init
cd  mbedtls && git submodule update --init && make -j$(nproc) && cd -
make
```
