# ESP32 Akri Component

This is the installation tutorial page for the [ESP32 Akri Component](/components/esp32-akri).

## Tutorial

```bash
cd <path-to-your-esp-idf-project>
mkdir -p components
cd components
git clone https://github.com/nubificus/esp32-akri.git
```

Add the component to your project by simply adding the following line inside `idf_component_register()` of `<path-to-your-esp-idf-project>/main/CMakeLists.txt`:

```cmake
REQUIRES esp32-akri
```

E.g:

```cmake
idf_component_register(SRCS "test.c"
                       INCLUDE_DIRS "."
                       REQUIRES esp32-akri)
```

Afterwards, you can include the component's header file:

```c
#include "esp32-akri.h"
```
