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

After building and pushing the Discovery Handler image to a registry, we are ready
to create an Akri Configuration that uses this Discovery Handler to discover
compatible devices.

### Create Akri configuration

The easiest way to achieve this is by using Helm template to create the
a YAML file containing all the required resources based on a minimal YAML definition
file.

In this file, we can specify the name of our Akri Configuration,
which Discovery Handler we will use, the discovery details that
the DH will use the perform the device discovery, as well as
which Broker Pod should be deployed for every discovered device:

```yaml
# onboarding-config-template.yaml

controller:
  enabled: false
agent:
  enabled: false
cleanupHook:
  enabled: false
rbac:
  enabled: false
webhookConfiguration:
  enabled: false
useLatestContainers: false
custom:
  configuration:
    enabled: true
    name: http-range-onboard # The name of akric
    capacity: 2
    discoveryHandlerName: http-discovery-onboard # name of discovery handler, must be unique and matching discovery.name. will be used for socket creation
    discoveryDetails: | # make sure this is valid YAML
      ipStart: 192.168.11.20
      ipEnd: 192.168.11.100
      applicationType: initial
      secure: true
    brokerPod:
      image:
        repository: docker.io/gntouts/pause
        tag: latest
  discovery:
    enabled: true
    image:
      repository: harbor.nbfc.io/nubificus/iot/akri-discovery-handler-go
      tag: latest
    name: http-discovery-onboard # name of discovery handler, must be unique and matching custom.configuration.discoveryHandlerName
```

> **Note:** The name of the Akri configuration (`.custom.configuration.name`) must
> be unique.
> Similarly, the Discovery Handler name defined in the configuration section
> (`.custom.configuration.discoveryHandlerName`) and the name defined in the
> discovery section (`.custom.discovery.name`) must both be
> unique **and** identical.
> It is not possible for Discovery Handlers from different Akri Configurations
> to share the same name,
> as the name is used to create the socket that the Discovery service listens on.

Now, let's create the actual YAML file that will be applied to Kubernetes using Helm:

```bash
helm template akri akri-helm-charts/akri -f onboarding-config-template.yaml > onboarding-config.yaml
```

Finally, let's apply it to create the Akri Configuration:

```bash
kubectl apply -f ./onboarding-config.yaml
```

We should now be able to see the deployed Pods of our Discovery Handler:

```console
$ kubectl get pods | grep http-onboard
http-discovery-onboard-daemonset-8r9nl                1/1     Running   0          1m
http-discovery-onboard-daemonset-d5frl                1/1     Running   0          1m
http-discovery-onboard-daemonset-htlbd                1/1     Running   0          1m
```

### Delete Akri configuration

If we want to delete the Akri Configuration, we need to either use the
generated YAML file:

```bash
kubectl delete -f ./onboarding-config.yaml
```

Or delete the Akri Configuration and DaemonSet manually:

```bash
kubectl delete akric http-range-onboard
kubectl delete daemonset http-discovery-onboard-daemonset
```
