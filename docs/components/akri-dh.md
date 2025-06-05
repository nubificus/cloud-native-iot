# Akri Discovery Handler

## Overview

As stated in Akri documentation, a Discovery Handler is anything that implements
the DiscoveryHandler service and Registration client defined in the [Akri's
discovery gRPC proto file](https://github.com/project-akri/akri/blob/cc14ba6bd326d62b4388efbed499148c50bf007d/discovery-utils/proto/discovery.proto).
To enable the discovery of resources (aka devices),
we need to implement a Discovery Handler (DH), which performs the actual
discovery on behalf of the Agent.

The Discovery Handler component has the following lifecycle:

- **Register with the agent**
Upon starting, creates a Registration client and register itself
with the agent
- **Start DiscoveryHandler service**
After registering, creates a DiscoveryHandler service and listens
for Discovery requests
- **Perform discovery**
Upon receiving a Discovery request from the agent, parses the Discovery details,
performs the relevant discovery based on said details and returns
a streaming Response containing discovered devices. This is then repeated in a loop
to ensure that the Akri agent is updated with the latest devices.

Akri provides a [Discovery Handler template](https://github.com/project-akri/akri-discovery-handler-template)
as well as a [walk-through](https://docs.akri.sh/development/development-walkthrough)
on how to implement a custom Discovery Handler.
This is very helpful if you are looking to build a Discovery Handler in Rust.

## Go implementation

To develop a custom Discovery Handler in Go, we created a [new Go package](https://github.com/nubificus/go-akri)
(similar to Akri's template) that streamlines the Discovery Handler's lifecycle.
This approach allows users to define only the custom discovery details parsing
and device discovery logic.

### gRPC code generation

> Note: If you are not intending to dig deeper into the package internals
(eg. to bring the package up to date with the latest Akri release the package),
feel free to skip this section.

The first step to build or update this package is to generate the gRPC Client/Service
code in Go based on the [Akri proto file](https://github.com/project-akri/akri/blob/cc14ba6bd326d62b4388efbed499148c50bf007d/discovery-utils/proto/discovery.proto).
The easiest way to achieve this is by using our [protobuf generator tool](https://github.com/nubificus/go-akri/tree/main/tools/protobuf-gen),
which is packaged in a Docker image.

You can list the latest [Akri tags](https://github.com/project-akri/akri/tags):

```bash
$ docker run --rm harbor.nbfc.io/nubificus/akri-protobuf:latest --list
📦 Latest tags (sorted, limited to 5):
v0.13.8
v0.12.20
v0.12.9
v0.10.4
v0.8.23
```

You can generate the Go code under `/pkg/pb` from a specific Akri tag:

```bash
$ mkdir -p $PWD/pkg/pb
$ docker run --rm --user $(id -u):$(id -g) -v $PWD/pkg/pb:/out harbor.nbfc.io/nubificus/akri-protobuf:latest v0.12.20
Akri target tag: v0.12.20
Downloading protobuf file from https://raw.githubusercontent.com/project-akri/akri/v0.12.20/discovery-utils/proto/discovery.proto
Modifying protobuf file...
Generating Go code from protobuf file...
Go code generated successfully
```

Or you can use the latest release by omitting the tag parameter:

```bash
$ mkdir -p $PWD/pkg/pb
$ docker run --rm --user $(id -u):$(id -g) -v $PWD/pkg/pb:/out harbor.nbfc.io/nubificus/akri-protobuf:latest
Warning: No target tag provided.
Using latest tag as default.
Akri target tag: v0.13.8
Downloading protobuf file from https://raw.githubusercontent.com/project-akri/akri/v0.13.8/discovery-utils/proto/discovery.proto
Modifying protobuf file...
Generating Go code from protobuf file...
Go code generated successfully
```

### Creating a Discovery Handler

It is fairly simple to use the package with the [go-akri](https://github.com/nubificus/go-akri/tree/main/pkg/discovery-handler)
package. All you have to do is define a Discover function, that will
be responsible to parse the discovery details and perform the discovery
steps required by your use case.

A very simple example can be found at [our repo](https://github.com/nubificus/go-akri/blob/main/cmd/example-discovery-handler/main.go):

```go
func discoveryFunc(_ string) ([]*pb.Device, error) {
	device := &pb.Device{
		Id: "dummy-device",
		Properties: map[string]string{
			"AKRI_HTTP":        "http",
			"HOST_ENDPOINT":    "127.0.0.1",
			"APPLICATION_TYPE": "example",
			"DEVICE":           "dummy",
			"VERSION":          "0.0.1",
		},
		Mounts:      []*pb.Mount{},
		DeviceSpecs: []*pb.DeviceSpec{},
	}
	devices := []*pb.Device{device}
	return devices, nil
}

func main() {
	app := akri.NewApp(discoveryFunc, akri.WithLogLevel(zerolog.TraceLevel))
	app.Run()
}
```

### Packaging the Discovery Handler

In order to deploy our Discovery Handler, we need to package it in a Docker image.
A sample Dockerfile can be found in the [go-akri repo](https://github.com/nubificus/go-akri/blob/main/Dockerfile).

```dockerfile
FROM docker.io/library/golang:1.24.2-alpine3.21 AS builder
WORKDIR /app
COPY . .
RUN go mod tidy && \
    go mod vendor && \
    go mod verify
    
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags "-s -w" -ldflags "-extldflags '-static'" -o discovery-handler ./cmd/http-discovery-handler
    
FROM docker.io/library/alpine:3.21

COPY --from=builder /app/discovery-handler /discovery-handler
ENTRYPOINT ["/discovery-handler"]
```

## HTTP Secure Discovery Handler

Short description (what were the goals behind this, how it works in short)

Detailed list of lifecycle (how it expects to receive discovery details,
what steps it performs when
discovering a device, how it authenticates the device before onboarding,
how it handles unauthorized devices, how it handles shutdown)

### Deploying the Discovery Handler

Instructions on how to deploy.

### Deploy Onboarding Discovery Handler

Next, we need to deploy a new Discovery Handler to onboard any devices.

To create the new DH we need apply a new Akri Config:

```yaml
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
      tag: 61d23fb
    name: http-discovery-onboard # name of discovery handler, must be unique and matching custom.configuration.discoveryHandlerName
```

```bash
helm template akri akri-helm-charts/akri -f onboardingConfig.yaml > template.yaml
kubectl apply -f ./template.yaml
```



Example logs of DH while working