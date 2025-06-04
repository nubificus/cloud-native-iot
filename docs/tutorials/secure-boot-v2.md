# Secure Boot V2

[Official Documentation](https://docs.espressif.com/projects/esp-idf/en/v5.3.1/esp32/security/secure-boot-v2.html)

This guide provides information on how to enable secure boot V2 on esp32
devices, how to generate V2 keys and how to sign images (or partition tables)
based on the V2 security mechanism of esp32 devices and esp-idf framework.

Not every esp32 device supports V2 Secure Boot. It's supported by ECO 3
onwards. Furthermore, devices that support V2 Secure Boot, probably support V1,
too (see Secure-Boot.md). However, the official documentation mentions that "It
is recommended that users use Secure Boot V2 if they have a chip version that
supports it. Secure Boot V2 is safer and more flexible than Secure Boot V1."

## Guide

### Step 1

First of all, we need an ESP32 Project to use. From the esp-idf repository, you
could use `examples/get-started/hello_world`. Of course, you must have
installed esp-idf previously - the repository contains docs. Afterwards, to
view some information about the device you are working on, run:

```
esptool.py flash_id
```

In the next steps, you will have to set the flash size in menuconfig, as long as the target device.

### Step 2

Set the target device by running:

```
idf.py set-target <dev-target>
```

### Step 3

Set the flash size in your sdkconfig file by using

```
idf.py menuconfig
```

And set the right value in `Serial flasher config -> Flash size`

### Step 4

Generate a secure boot signing key v2.

**Important**
The keys used to sign binary images (bootloader, application, partition table)
in Secure Boot V1 are different than those in V2. This means you **can't** just
use `espsecure.py generate_signing_key` or use an existing V1 key. The command
used to generate V2 keys is the following:

```
espsecure.py generate_signing_key --version 2 --scheme rsa3072 <output-file.pem>
```

or

```
openssl genrsa -out <output-file.pem> 3072
```

Afterwards, we use use this file for signing images.

### Step 5

Enable Secure Boot V2 in menuconfig: Run

```
idf.py menuconfig
```

and select the following options:

```
1. [*] Security features -> Enable hardware Secure Boot in bootloader

2. [*] Security features -> Enable hardware Secure Boot in bootloader -> Select
   secure boot version -> Enable Secure Boot version 2

3. [*] Sign binaries during build

4. Secure boot private signing key: <key-path.pem>

5. UART ROM download mode: "Enabled (not recommended)"
```

Regarding the last option, enabling UART ROM download mode lets us flash the
board using tools like `esptool.py` or `idf.py flash`. However, in production
environments where we would like to protect our boards from **physical
attacks**, we should probably set this option to `Permanently disabled
(recommended)`.

Furthermore, bootloader binaries are usually larger when secure boot is enabled
and partition table default offset `0x8000` is not enough. You can change that
to `0x10000` in `Partition Table -> Offset of partition table`

Before moving forward, I would recommend you to cleanup the directory from
previous builds by running:

```
idf.py fullclean
```

### Step 6

Now, to build the bootloader, application image and partition table (and sign
them, too), run:

```
idf.py build
```

If you would like to build only the bootloader, you could also run:

```
idf.py bootloader
```

Those commands will also print instructions on how to flash the bootloader. For
example, in my system, the printed message is:

```
==============================================================================
Bootloader built. Secure boot enabled, so bootloader not flashed automatically.
To sign the bootloader with additional private keys.
    /home/ilias/.espressif/python_env/idf5.4_py3.8_env/bin/python /home/ilias/esp-idf/components/esptool_py/esptool/espsecure.py sign_data -k secure_boot_signing_key2.pem -v 2 --append_signatures -o signed_bootloader.bin build/bootloader/bootloader.bin
Secure boot enabled, so bootloader not flashed automatically.
    /home/ilias/.espressif/python_env/idf5.4_py3.8_env/bin/python  /home/ilias/esp-idf/components/esptool_py/esptool/esptool.py --chip esp32s2 --port=(PORT) --baud=(BAUD) --before=default_reset --after=no_reset write_flash --flash_mode dio --flash_freq 80m --flash_size keep 0x1000 /home/ilias/esp-idf/examples/get-started/blink/build/bootloader/bootloader.bin
==============================================================================
```

As you can see, esp-idf tells us that **Secure boot enabled, so bootloader not
flashed automatically**. Therefore, we could use recommended command to flash
the bootloader. In a more generic form:

```
esptool.py --before=default_reset --after=no_reset write_flash --flash_mode dio --flash_freq 80m --flash_size keep 0x1000 build/bootloader/bootloader.bin
```

You may have to define explicitly `--chip` or `--port` options. In my case,
they were `--chip esp32s2` and `--port=/dev/ttyUSB0`.

### Step 7

Now, we can flash the application by using the `idf.py flash` command. If you
have previously built the application using `idf.py build`, the application
binary has been automatically signed and saved in `build` directory. For the
hello-world example, the file is called `hello_world.bin`. However, if you
previously built the bootloader with `idf.py bootloader`, you now have to run
`idf.py build` to create and sign the application and the partition table.
After that, go ahead and run:

```
idf.py flash
```

### Step 8

Finally, we can execute our application by running:

```
idf.py monitor
```

and you will see the output of the application on the terminal. Secure Boot is
now enabled and works fine if the output is the expected.

**It's necessary not to lose your private key**. Otherwise, you won't be able
to reflash your board with new applications, bootloaders or partition tables.

## Sign other images

Sometimes, we may have some already built binaries but they are unsigned. For
example, you may have ran `idf.py build` to a project which is not configured
with the secure boot options. This project contains an unsigned application
binary file located in `build` directory (say, app.bin), as well as an unsigned
partition table binary file in `build/partition_table/` (say,
partition-table.bin). Saying that, it is possible to sign these files without
having to re-build your application. That is possible with the `espsecure.py
sign_data` command. More specifically, you can run:

```
espsecure.py sign_data --version 2 --keyfile PRIVATE_SIGNING_KEY --output build/app-signed.bin build/app.bin
```

to sign your application and

```
espsecure.py sign_data --version 2 --keyfile PRIVATE_SIGNING_KEY --output build/partition_table/partition-table.bin build/partition_table/partition-table-signed.bin
```

to sign your partition table.

Now, based on the offsets configured on the partition table (say, `0x10000` for
the partition table and `0x20000` for the factory app), you can use
`esptool.py` to flash the signed binaries:

```
esptool.py --before default_reset --after no_reset write_flash --flash_mode dio --flash_size keep --flash_freq 80m 0x10000 build/partition_table/partition-table-signed.bin 0x20000 build/app-signed.bin
```

As before, you may have to configure `--chip` and `--port`.
