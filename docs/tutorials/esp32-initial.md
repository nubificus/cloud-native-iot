# ESP32: Over the air update (OTA)

esp32-ota-update is a vanilla-type firmware for esp32 devices. It doesn't include any actual real world application, however, it can be used to load the necessary tools to perform an OTA update later. 
## Build

The following commands will build the project.

**Download esp-idf source**
```bash
cd ~
git clone --recursive https://github.com/espressif/esp-idf.git
```
**Install and set the environment variables**
```bash
cd esp-idf
./install.sh
. ./export.sh
# You have to run the last command every time the environment variables are lost.
```
**Download the project**
```bash
mkdir projects && cd projects
git clone https://github.com/nubificus/esp32-ota-update.git --recursive
cd esp32-ota-update
```
**Security Configuration**
If you want to use the secure implementation, set the `OTA_SECURE` environment variable before building. Otherwise, the default configuration is the non-secure.
```bash
export OTA_SECURE=1
```
**Build and Flash**
```bash
export FIRMWARE_VERSION="0.1.0"
export DEVICE_TYPE="esp32s2"
export APPLICATION_TYPE="thermo"
export WIFI_SSID=...
export WIFI_PASS=...
idf.py build
idf.py flash monitor
```

**Create Docker image**

```bash
export FIRMWARE_VERSION="0.1.0"
export DEVICE_TYPE="esp32s2"
export APPLICATION_TYPE="thermo"
tee Dockerfile > /dev/null << 'EOT'
FROM scratch
COPY ./build/ota.bin /firmware/ota.bin
LABEL "com.urunc.iot.path"="/firmware/ota.bin"
EOT
docker build --push -t harbor.nbfc.io/nubificus/$APPLICATION_TYPE-$DEVICE_TYPE-firmware:$FIRMWARE_VERSION .
rm -f Dockerfile
```

**You may have to define the port explicitly**
```bash
idf.py -p <PORT> flash monitor
# example: -p /dev/ttyUSB0
```

**Additionally, you may have to change user's rights**
```bash
sudo adduser <USER> dialout
sudo chmod a+rw <PORT>
```
**To exit ESP32 monitor**
```
Ctr + ]
```
## Firmware Provider App
### Non-secure implementation
In the case of the non-secure implementation, the microcontroller operates as a server, after receiving the post request. Therefore, we need a tcp client to operate as the firmware provider for the microcontroller. The following C program can do this job.
```C
/* tcp_client.c */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define SERVER_IP "192.168.8.62"
#define SERVER_PORT 3333
#define CHUNK_SIZE  1024

void send_file(const char *filename) {
    int sock;
    struct sockaddr_in server_address;
    FILE *file;
    char buffer[CHUNK_SIZE];
    size_t bytes_read;

    /* Create socket */
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) {
        perror("Error: Socket creation failed");
        exit(EXIT_FAILURE);
    }

    /* Define the server address */
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(SERVER_PORT);
    server_address.sin_addr.s_addr = inet_addr(SERVER_IP);

    /* Connect to the server */
    if (connect(sock, (struct sockaddr *)&server_address, sizeof(server_address)) < 0) {
        perror("Error: Connection failed");
        close(sock);
        exit(EXIT_FAILURE);
    }

    /* Open the file */
    file = fopen(filename, "rb");
    if (!file) {
        perror("Error: File opening failed");
        close(sock);
        exit(EXIT_FAILURE);
    }

    /* Read from the file and send it to the server in chunks */
    while ((bytes_read = fread(buffer, 1, CHUNK_SIZE, file)) > 0) {
    if (send(sock, buffer, bytes_read, 0) < 0) {
            perror("Error: Failed to send data");
            break;
        }
    }

    printf("File %s sent successfully\n", filename);

    /* Close file and socket */
    fclose(file);
    close(sock);
}


int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Usage: %s <file_path>\n", argv[0]);
        exit(EXIT_FAILURE);
    }

    send_file(argv[1]);
    return 0;
}
```
Don't forget to change **SERVER_IP**. Then, you can build and run the program using the following commands:

```bash
gcc -o client tcp_client.c
./client /path/to/file.bin
```
### Secure implementation
If you build with `OTA_SECURE`, you will need to check the more advanced OTA Agent implementation, which works with DICE certificates and TLS connection. For more information, view the [repository](https://github.com/nubificus/ota-agent) or the [documentation](../components/ota-agent.md).

## Simple Firmware to use for Update

Now we also need to create a simple firmware image, which will be sent by the server to update ESP32. You can use the `hello-world` example, located in `~/esp-idf/examples/get-started/hello_world/`. Build with the following commands:

```bash
cd ~/esp-idf/examples/get-started/hello_world/
idf.py build
```
The new firmware image is located in `~/esp-idf/examples/get-started/hello_world/build/hello_world.bin`.
You can use that file for the ota update by providing the path when running the client.

## Multi-platform image building

```bash
git clone -b feat_http_server git@github.com:nubificus/esp32-ota-update.git
cd esp32-ota-update
mkdir -p dist/esp32s2
tee env.list > /dev/null << 'EOT'
FIRMWARE_VERSION=0.2.0
DEVICE_TYPE=esp32s2
APPLICATION_TYPE=thermo
EOT
docker run --rm -v $PWD:/project -w /project espressif/idf:latest idf.py set-target esp32s2
docker run --rm -v $PWD:/project -w /project --env-file ./env.list espressif/idf:latest idf.py build
sudo mv build/ota.bin dist/esp32s2/ota.bin

mkdir -p dist/esp32s3
tee env.list > /dev/null << 'EOT'
FIRMWARE_VERSION=0.2.0
DEVICE_TYPE=esp32s3
APPLICATION_TYPE=thermo
EOT
docker run --rm -v $PWD:/project -w /project espressif/idf:latest idf.py set-target esp32s3
docker run --rm -v $PWD:/project -w /project --env-file ./env.list espressif/idf:latest idf.py build
sudo mv build/ota.bin dist/esp32s3/ota.bin

mkdir -p dist/esp32
tee env.list > /dev/null << 'EOT'
FIRMWARE_VERSION=0.2.0
DEVICE_TYPE=esp32
APPLICATION_TYPE=thermo
EOT
docker run --rm -v $PWD:/project -w /project espressif/idf:latest idf.py set-target esp32
docker run --rm -v $PWD:/project -w /project --env-file ./env.list espressif/idf:latest idf.py build
sudo mv build/ota.bin dist/esp32/ota.bin

sudo chown -R $USER dist

tee Dockerfile > /dev/null << 'EOT'
FROM scratch
ARG DEVICE
COPY dist/${DEVICE}/ota.bin /firmware/ota.bin
LABEL "com.urunc.iot.path"="/firmware/ota.bin"
EOT

docker buildx build --platform custom/esp32 -t harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0-esp32 --build-arg DEVICE=esp32 . --push --provenance false
docker buildx build --platform custom/esp32s2 -t harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0-esp32s2 --build-arg DEVICE=esp32s2 . --push --provenance false
docker buildx build --platform custom/esp32s3 -t harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0-esp32s3 --build-arg DEVICE=esp32s3 . --push --provenance false

docker manifest create harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0 \
  --amend harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0-esp32 \
  --amend harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0-esp32s2 \
  --amend harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0-esp32s3

docker manifest push harbor.nbfc.io/nubificus/iot/esp32-thermo-firmware:0.2.0
```
