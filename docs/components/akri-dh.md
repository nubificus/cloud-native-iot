# Secure HTTP Discovery Handler

## Overview

To securely integrate esp32-based devices with Akri and our project, we had to
develop a [custom Discovery Handler in Go](https://github.com/nubificus/secure-http-discovery-handler/tree/main).
To achieve that, we developed a [new Go package](https://github.com/nubificus/go-akri).
You can find more about the package in the [Go Akri doc](./go-akri.md).
Since `esp32` devices are WiFi enabled and require connection to the internet
for most use-cases, we implemented an HTTP Discovery Handler that scans a given
IP range to detect which IPs belong to compatible `esp32` devices.
The Discovery Handler performs a GET request for each IP in that range
(at the `/info` endpoint) and verifies that the device matches
a given application type, as defined in the Discovery Details of the Akri configuration.

After that, the matching devices are also tested against our [attestation server](./attestation-server.md)
to ensure that they are indeed secure and trusted.
Then, the Discovery Handler sends the list of the devices
that match the desired application type and are trusted to the agent and
the devices are onboarded in our Akri installation as `akrii` (Akri instances).

## Discovery Details parsing

The Discovery Details is a single string defined when creating a new Akri Configuration.
Our Discovery Handler expects this string to be a valid YAML string that will be
parsed into the following Go struct:

<!-- markdownlint-disable -->

```go
type DiscoveryDetails struct {
  IPStart     string `yaml:"ipStart"` // The first IP of the IP range to scan
  IPEnd       string `yaml:"ipEnd"` // The last IP of the IP range to scan
  Application string `yaml:"applicationType"` // The application type to match devices
  Secure      bool   `yaml:"secure"` // Whether to ensure the devices are secure with the attestation server
}
```

<!-- markdownlint-enable -->

An example configuration including DiscoveryDetails:

```yaml
custom:
  configuration:
    ...
    discoveryDetails: |
      ipStart: 192.168.11.36
      ipEnd: 192.168.11.45
      applicationType: fmnist
      secure: true
```

## Expected device response

The Discovery Handler expects a JSON response to the GET request that send to
each IP in the given IP range. That JSON response is unmarshalled into
the following Go struct. The application field is used to match the devices,
while all the fields are propagated to the Akri agent if the device is properly
"discovered".

```go
type DeviceInfo struct {
  Device      string `json:"device"`
  Application string `json:"application"`
  Version     string `json:"version"`
}
```

An example esp32 device response:

```console
$ curl http://192.168.11.131/info
{"device":"esp32c6","application":"vanilla","version":"0.0.0"}
```

## Packaging the Discovery Handler

In order to deploy our Discovery Handler, we need to package it in a Docker image.
A sample Dockerfile can be found in the [DH repo](https://github.com/nubificus/secure-http-discovery-handler/blob/main/Dockerfile).

<!-- markdownlint-disable -->

```dockerfile
FROM docker.io/library/golang:1.24.2-alpine3.21 AS builder
WORKDIR /app
COPY . .
RUN go mod tidy && \
    go mod vendor && \
    go mod verify

RUN CGO_ENABLED=0 GOOS=linux go build -ldflags "-s -w" -ldflags "-extldflags '-static'" -o discovery-handler ./cmd/secure-http-discovery-handler

FROM docker.io/library/alpine:3.21

COPY --from=builder /app/discovery-handler /discovery-handler
ENTRYPOINT ["/discovery-handler"]
```

<!-- markdownlint-enable -->

## Deploying the Discovery Handler

After building the Discovery Handler, we need to push the Docker image into a registry.
Then we can create an Akri Configuration that uses this Discovery Handler
to discover compatible devices, as shown in the [instructions](./../getting-started/installation.md#installation)

<!-- TODO: Change link to point to actual instructions! -->
