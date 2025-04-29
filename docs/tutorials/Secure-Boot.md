We worked on enabling secure boot on devices supporting secure boot v1. The following steps summarize the process:

## 1. Create a private signing key
`espsecure.py generate_signing_key secure_boot_signing_key.pem`

**IMPORTANT!!! Make sure to save that key. If the key is lost, the device can't be used again after secure boot is enabled!**

## 2. Menuconfig

- Security Features
  - Enable hardware Secure Boot in bootloader
  - Secure bootloader mode (Reflashable)
  - Secure boot private signing key -> Path to key
- Partition Table
  - Offset -> 0x10000

## 3. Build the bootloader
Better build in a new directory, so the following command prints instructions

`idf.py -B build-secure bootloader`

This command should print some similar instructions as the following ones:

```
Bootloader built and secure digest generated.
Secure boot enabled, so bootloader not flashed automatically.
Burn secure boot key to efuse using:
	$HOME/.espressif/python_env/idf5.4_py3.8_env/bin/python $HOME/esp-idf/components/esptool_py/esptool/espefuse.py burn_key secure_boot_v1 $HOME/ilias/esp-idf/examples/get-started/hello_world/build-secure/bootloader/secure-bootloader-key-256.bin
First time flash command is:
	$HOME/.espressif/python_env/idf5.4_py3.8_env/bin/python  $HOME/esp-idf/components/esptool_py/esptool/esptool.py --chip esp32 --before=default_reset --after=no_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 2MB 0x1000 $HOME/esp-idf/examples/get-started/hello_world/build-secure/bootloader/bootloader.bin
==============================================================================
To reflash the bootloader after initial flash:
	$HOME/.espressif/python_env/idf5.4_py3.8_env/bin/python  $HOME/esp-idf/components/esptool_py/esptool/esptool.py --chip esp32 --before=default_reset --after=no_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 2MB 0x0 $HOME/esp-idf/examples/get-started/hello_world/build-secure/bootloader/bootloader-reflash-digest.bin
==============================================================================
```

## 4. Burn the secure key on the device (Can only be written once)

Using the first provided command, we burn the secure key on the device's eFuse:
```
$HOME/.espressif/python_env/idf5.4_py3.8_env/bin/python $HOME/esp-idf/components/esptool_py/esptool/espefuse.py  burn_key secure_boot_v1 $HOME/esp-idf/examples/get-started/hello_world/build-secure/bootloader/secure-bootloader-key-256.bin
```
It will print among others:
`Type 'BURN' (all capitals) to continue.`

## 5. Flash the bootloader:
You may add the `--port` argument 
```
$HOME/.espressif/python_env/idf5.4_py3.8_env/bin/python  $HOME/esp-idf/components/esptool_py/esptool/esptool.py --chip esp32 --before=default_reset --after=no_reset write_flash --flash_mode dio --flash_freq 40m --flash_size 2MB 0x1000 $HOME/esp-idf/examples/get-started/hello_world/build-secure/bootloader/bootloader.bin
```

## 6. Build and flash the app
It will automatically sign the firmware image
`idf.py -B build-secure flash monitor`

The signed firmware is now running.

## 7. Sign another image
If we want to sign an already built firmware image, we can do so by using the following command:
```
espsecure.py sign_data --version 1 --keyfile ./my_signing_key.pem --output ./image_signed.bin image-unsigned.bin
``` 

## 8. Flash the signed image
Afterwards, we can flash the signed app:
```
export BUILD_DIR=/path/to/build_dir/

python3 $HOME/esp-idf/components/esptool_py/esptool/esptool.py --chip esp32 --before default_reset --after hard_reset write_flash --flash_mode dio --flash_size detect 0x10000 $BUILD_DIR/partition_table/partition-table.bin 0x20000 /path/to/image_signed.bin
```
