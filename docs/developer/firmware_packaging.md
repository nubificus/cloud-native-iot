# Firmware Packaging

## Overview

Our [automated build workflow](https://github.com/nubificus/esp32-build),
handles the entire process of building, tagging, and packaging firmware for
multiple ESP32 targets. The key steps are:

1. Building firmware images for each target using the same base image name
   `harbor.nbfc.io/cloud-iot/<repo>`.
2. Tagging each target's firmware image with a unique identifier that includes
   the target, application type, version, and commit SHA.
3. Combining all target-specific images into a single OCI manifest and pushing
   it to our image registry.
4. Storing all artifacts in S3 buckets for easy access and backup.

## Rationale

In IoT deployents, especially when dealing with a large number of versatile
ESP32 devices, it is crucial to optimize OTA firmware updates. Creating
monlithic firmware images for each device target that include all binaries
(bootloader, partition table, application) is inefficient. Obtaining only the
updated application binaries and combining them into a single OCI manifest
image allows for:

- **Reduced bandwidth usage**: Only the changed binaries are downloaded.
- **Faster updates**: Devices can quickly fetch and apply only the necessary
  changes.
- **Simplified management**: All target-specific images are aggregated under a
  single manifest, making it easier to manage and deploy updates.

In order to exploit these benefits, we have also designed the
[`esp32-flashjob`](https://github.com/nubificus/esp32-flashjob) component for
performing secure OTA updates. This component uses the manifest to determine
which application binary to download and apply, ensuring that devices only
fetch the necessary updates without needing to reflash the entire firmware.
Further information about the flashjob can be found
[here](../components/flashjob.md).

## Example: Bug Fix Rollout

Imagine an app has a bug in version `1.0.0`.

1. You fix the bug and build a new firmware `1.0.1`.
2. `esp32-build` creates:

a. New firmware images per target.
b. Updated manifest at:

```
harbor.nbfc.io/cloud-iot/<repo>:<app_type>-1.0.1-<key>
```

3. Devices running `esp32-flashjob` detect the update and self-upgrade.
