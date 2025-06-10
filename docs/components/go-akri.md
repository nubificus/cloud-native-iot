# Akri Discovery Handler package for Go

## Overview

As stated in Akri documentation, a Discovery Handler is anything that implements
the DiscoveryHandler service and Registration client defined in the [Akri's
discovery gRPC proto file](https://github.com/project-akri/akri/blob/cc14ba6bd326d62b4388efbed499148c50bf007d/discovery-utils/proto/discovery.proto).
To enable the discovery of resources (aka devices),
we need to implement a Discovery Handler (DH), which performs the actual
discovery on behalf of the Agent.

The Discovery Handler component has the following lifecycle:

- **Register with the agent**
  Upon starting, creates a Registration client and registers itself
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

To develop a custom Discovery Handler in Go, we created a [new Go package](https://github.com/nubificus/go-akri)
(similar to Akri's template) that streamlines the Discovery Handler's lifecycle.
This approach requires users to only define the custom device discovery logic
and discovery details parsing.

## Usage

The only logic we need to implement is the actual discovery process. The rest is
taken care of by the package.

### Discovery Function

The Discovery logic must be implemented in a `DiscoverFunc` as shown below
and must be passed to a new DiscoveryApp instance.

```go
type DiscoverFunc func(string) ([]*pb.Device, error)
```

The input string is the raw discovery details. The developer is responsible to parse
them (and set them at deploy time). This function should return a list containing
the discovered devices and an error, if any occurred.

A sample discovery function can be found in the [go-akri](https://github.com/nubificus/go-akri/blob/main/cmd/example-discovery-handler/main.go)
repo:

```go
func discovery(_ string) ([]*pb.Device, error) {
    device := &pb.Device{
        Id: "dummy-device",
        Properties: map[string]string{
            "AKRI_HTTP":        "http",
            "VERSION":          "0.0.1",
        },
        Mounts:      []*pb.Mount{},
        DeviceSpecs: []*pb.DeviceSpec{},
    }
    devices := []*pb.Device{device}
    return devices, nil
}
```

### Running the App

To run the app, we need to define a minimal new DiscoveryApp instance, configure
it with the desired discovery function and options and run it:

```go
package main

import (
    akri "github.com/nubificus/go-akri/pkg/discovery-handler"
    "github.com/nubificus/go-akri/pkg/pb"
)

func discovery(_ string) ([]*pb.Device, error) {
    return nil, nil
}

func main() {
    app := akri.NewApp(discovery, akri.WithLogLevel(akri.DebugLevel))
    app.Run()
}
```

### Configuration options

The available configuration options are the following:

#### WithRegisterRetries

`WithRegisterRetries` sets the amount of retries for registering the
discovery handler with the Akri agent. (Default is 10)

#### WithgRPCShutdownDelay

`WithgRPCShutdownDelay` sets the forced shutdown delay for the gRPC server. Normally
the gRPC server will shutdown gracefully, but if that takes longer than the
forcedGRPCShutdownDelay, the server will stop immediately. (Default is 5 seconds)

#### WithDiscoverSleep

`WithDiscoverSleep` sets the sleep duration between discovery scans.
(Default is 30 seconds)

#### WithLogLevel

`WithLogLevel` sets the log level for the discovery handler app.
(Default is INFO)

#### WithShared

`WithShared` sets whether the discovered devices could be used by multiple nodes
or can only be ever be discovered by a single node. (Default is false)

## gRPC code generation

> Note: If you are not intending to dig deeper into the package internals
> (eg. to bring the package up to date with the latest Akri release the package),
> feel free to skip this section.

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

<!-- markdownlint-disable -->

```bash
$ mkdir -p $PWD/pkg/pb
$ docker run --rm --user $(id -u):$(id -g) -v $PWD/pkg/pb:/out harbor.nbfc.io/nubificus/akri-protobuf:latest v0.12.20
Akri target tag: v0.12.20
Downloading protobuf file from https://raw.githubusercontent.com/project-akri/akri/v0.12.20/discovery-utils/proto/discovery.proto
Modifying protobuf file...
Generating Go code from protobuf file...
Go code generated successfully
```

<!-- markdownlint-enable -->

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
