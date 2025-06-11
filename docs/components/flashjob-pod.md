# FlashJob Pod

The FlashJob Pod is a custom Pod deployed by the [FlashJob Operator](./flashjob.md)
in order to perform the OTA update of a specific ESP32 device.

It contains two components:

- the [esp32-flashjob](https://github.com/nubificus/esp32-flashjob/tree/main/cmd/esp32-flashjob)
  component
- the [ota-agent](./ota-agent.md)

## esp32-flashjob

The `esp32-flashjob` component is responsible for downloading and extracting
the firmware from an OCI image registry, setting up the environment
and executing the [ota-agent](./ota-agent.md).

### Platform-specific OCI images

We take advantage of multi-platform OCI manifest to help us build and distribute
firmware for a number of supported devices and platforms (eg `esp32`, `esp32s2`,
`esp32s3` and more).

Using our [automated build workflow](https://github.com/nubificus/esp32-build/blob/main/.github/workflows/build.yml)
we are able to build and package firmware built for each device type
under a single OCI manifest.

That way we can have the same version of a firmware built and packaged under the
same OCI image tag:

```console
$ docker buildx imagetools inspect harbor.nbfc.io/cloud-iot/nubificus/fmnist-esp-ota:resnet-4.4.4-ESP32_KEY3
Name:      harbor.nbfc.io/cloud-iot/nubificus/fmnist-esp-ota:resnet-4.4.4-ESP32_KEY3
MediaType: application/vnd.docker.distribution.manifest.list.v2+json
Digest:    sha256:fee40c0d537d1ac83ef003784db3ec586be25f618f5717dc4a482d558310d9d7

Manifests:
  Name:      harbor.nbfc.io/cloud-iot/nubificus/fmnist-esp-ota:resnet-4.4.4-ESP32_KEY3@sha256:1a567013c7245a9cfe44b4015ef3fd805713fbf6017026d907b699c80f7c012f
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  custom/esp32s2r2

  Name:      harbor.nbfc.io/cloud-iot/nubificus/fmnist-esp-ota:resnet-4.4.4-ESP32_KEY3@sha256:f4040645c64786b86fc5b5f7d90703d071126093d3311329acf01492492d599b
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  custom/esp32s3

  Name:      harbor.nbfc.io/cloud-iot/nubificus/fmnist-esp-ota:resnet-4.4.4-ESP32_KEY3@sha256:a082451cc409a41e601ce08213eee1a817952a612394a08820979ac567dd0273
  MediaType: application/vnd.docker.distribution.manifest.v2+json
  Platform:  custom/esp32s3r8
```

### esp32-flashjob workflow

The lifecycle of the `esp32-flashjob` is the following:

- spawns and loads any information for the device and the OTA update from the
  environment
- downloads and extracts the firmware package in the OCI image based on the
  requested platform
- sends a request to the esp32 device to enable OTA flash mode
- executes the [ota-agent](./ota-agent.md) capturing all logs

### Environment variables

In order to properly download the firmware and setup the environment for [ota-agent](./ota-agent.md)
with the correct parameters, `eps32-flashjob` requires the following environment
variables to be set by the [flashjob operator](./flashjob.md) or Akri:

- `DEVICE`: The device type (eg esp32s3/esp32s2)
- `HOST` or `HOST_ENDPOINT_*`: The IP address of the device
- `FIRMWARE`: The OCI image with the tag
- `DICE_AUTH_SERVICE_SERVICE_HOST`: The IP address of the [attestation server](./attestation-server.md)

<!-- TODO: Add logs from a running FlashJob Por -->
