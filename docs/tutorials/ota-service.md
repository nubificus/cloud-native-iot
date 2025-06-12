# ESP32 OTA Component

This is the installation tutorial page for the [ESP32 OTA Component](/components/ota-service).

`ota-service` is an ESP32 Component for performing Over the Air updates. The component contains only the handlers. To setup the functions as akri-endpoints handlers, see [ESP32 Akri Component](/components/esp32-akri).

## How to use

```bash
cd <path-to-your-esp-idf-project>
mkdir -p components
cd components
git clone https://github.com/nubificus/ota-service.git
```

Add the component to your project by simply adding the following line inside `idf_component_register()` of `<path-to-your-esp-idf-project>/main/CMakeLists.txt`:

```cmake
REQUIRES ota-service
```

E.g:

```cmake
idf_component_register(SRCS "test.c"
                       INCLUDE_DIRS "."
                       REQUIRES ota-service)
```

You may also have to add the following configuration to resolve some `mbedtls` issues:

```bash
idf.py menuconfig
```

and enable `Component config -> mbedTLS -> HKDF Algorithm (RFC 6859)`

Afterwards, you can include the component's header file:

```c
#include "ota-service.h"
```

The component follows the secure OTA workflow when `OTA_SECURE` macro is defined. Otherwise, the update is non-secure.
