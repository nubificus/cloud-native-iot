# Device API

**Version:** 0.1.0  
**Base path:** _(Device-local address, e.g., `http://{device-ip}`)_

---

## 📋 Endpoints

### `GET /manage/info`

**Summary:** Get device information  
**Description:** Retrieve static information about the IoT device.

**Responses:**

- `200 OK`: JSON representation of the device

```json
{
  "device": "generic-iot-device",
  "application": "example-app",
  "version": "1.0.0"
}
```

---

### `GET /manage/onboard`

**Summary:** Retrieve attestation certificate  
**Description:** Obtain the device’s attestation certificate in PEM format.

**Responses:**

- `200 OK`: PEM-encoded certificate (Content-Type: `application/x-pem-file`)
- `500 Internal Server Error`: Certificate retrieval error

Example Error:

```json
{
  "error": "Internal error",
  "details": "Stack trace or detailed error info"
}
```

---

### `POST /manage/update`

**Summary:** Start OTA firmware update  
**Description:** Initiates an Over-the-Air update using the provided image and optional arguments.

**Request Body (application/json):**

```json
{
  "image": "harbor.nbfc.io/drop/temp-sensor-capture:v0.1.0",
  "params": ["server", "192.168.1.100"]
}
```

**Responses:**

- `200 OK`: Update initiated
- `400 Bad Request`: Invalid update request
- `500 Internal Server Error`: Update process failed

Error Example:

```json
{
  "error": "Internal error",
  "details": "Stack trace or detailed error info"
}
```

---

### `GET /app/info`

**Summary:** Get app information  
**Description:** Retrieve static information about the deployed application on the IoT device.

**Responses:**

- `200 OK`: JSON representation of the app

```json
{
  "device": "temp-sensor",
  "application": "temp-sensor-capture",
  "image": "harbor.nbfc.io/drop/temp-sensor-capture:v0.1.0",
  "version": "1.0.0"
}
```
