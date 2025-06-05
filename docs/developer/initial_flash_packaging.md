# Initial Flash Packaging

## Overview

This guide explains how we prepare and publish OCI images for flashing devices
for the first time. After the firmware artifacts are built, the `esp32-build`
workflow proceeds with the generation of the initial flash images that is
comprised of the following steps:
1. Creation of platform-specific flash images for each requested architecture
   (e.g., `amd64`, `arm64`) by copying all necessary firmware artifacts into a
   container image. All images use the same base name
   `harbor.nbfc.io/cloud-iot/<repo>-flash`.
2. Tagging each platform's flash image with a unique identifier that includes
   the platform architecture, application type, version, and commit SHA.
3. Creation of a multi-arch manifest that allows `docker run` to automatically
   select the correct architecture for the host platform.

## Rationale
Flashing a blank or factory-reset ESP32 device should be as seamless and
platform-independent as possible especially when onboarding devices at scale.
Traditionally, this requires knowing the exact ESP32 variant (e.g., `esp32s2`,
`esp32s3`), having the correct bootloader, partition table, and app binary on
hand, and running vendor-specific flashing tools per operating system or
architecture. This process is not only error-prone but slows down
manufacturing, debugging and deployment workflows. Our approach solves this by
packaging all necessary flashing artifacts into OCI images, and combining them
in a multi-architecture Docker manifest. The required files are:

- `bootloader.bin`
- `partition-table.bin`
- `ota_data_initial.bin`
- `sdkconfig`
- `partitions.csv`
- `app binary`

## Example: Onboarding a New Device

Imagine you have a new ESP32 device that needs to be flashed for the first
time. The steps are as follows:
1. **Build the Firmware**: Use the `esp32-build` workflow to build the firmware
   for your device. This will generate the necessary artifacts including the
   bootloader, partition table, and application binary and bundle them into a
   multi-arch OCI flash manifest.
2. **Obtain the Flash Image**: After the build completes, you can pull the
   appropriate flash image for your device type and architecture from our
   registry:
   ```
   harbor.nbfc.io/cloud-iot/<repo>-flash:<app_type>-<version>
   ```
3. **Run the Flash Job**: Use the provided Docker image to flash your device.
   The command will look like this:

```shell
docker run --rm -it --device=<PORT> harbor.nbfc.io/cloud-iot/<repo>-flash:<app_type>-<version> \
--port <PORT> --chip <DEVICE_TYPE> --flash_size <FLASH_SIZE> \
[--baud <BAUD>] [--override_pt [normal|normal_with_model|no_factory|no_factory_with_model]]
```

The `--device` argument is a Docker option that grants the container access to
the specified hardware port. The other custom arguments used in that command
are explained as follows:

* `--port`: Specifies the port through which the firmware will be flashed,
* `--chip`: indicates the device type, which may include the suffixes `r2` and `r8`,
* `--flash_size`: defines the flash size of the device being flashed,
* `[--baud]`: sets the baud rate (frequency) for flashing the board and
* `[--override_pt]`: allows the explicit replacement of the current partition
  table (generated during the build process) with a new one based on user
  preferences, expanded across the entire flash of the device. The available
  options are:
  * `normal`: Creates three app partitions (one factory and two OTA).
  * `normal_with_model`: Creates three app partitions (one factory and two OTA)
    along with a custom tflite model partition.
  * `no_factory`: Creates two app partitions (two OTA), with the app placed in
    `ota_0`.
  * `no_factory_with_model`: Creates two app partitions (two OTA) with the app
    placed in `ota_0`, along with a custom tflite model partition.
