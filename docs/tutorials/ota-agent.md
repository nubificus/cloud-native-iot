# OTA Agent

This is the installation tutorial page for the [OTA Agent](/components/ota-agent).

## TLS

The OTA Agent requires secure communication with the microcontroller device, therefore we utilize the OpenSSL tool to generate a private key and the corresponding certificate, which can be used afterwards to run our TLS server.

```bash
openssl genpkey -algorithm RSA -out key.pem
openssl req -new -x509 -key key.pem -out cert.pem -days 365
```

## Build

```bash
git clone https://github.com/nubificus/ota-agent.git --recursive
cd ota-agent
cd  mbedtls && git submodule update --init && make -j$(nproc) && cd -
make

export DICE_AUTH_URL=...     #Attestaion Server URL
export NEW_FIRMWARE_PATH=... #Path to binary artifact to be used in OTA
export SERVER_CRT_PATH=...   #Path to TLS Server certificate
export SERVER_KEY_PATH=...   #Path to TLS Server private key
./ota-agent
```
