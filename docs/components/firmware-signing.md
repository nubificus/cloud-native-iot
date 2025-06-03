# Firmware Signing

Firmware authenticity and integrity are essential to prevent malicious updates and bricking attacks.

## Signing Workflow

1. Firmware is signed using an offline private key.
2. OTA Service embeds signature in metadata descriptor.
3. OTA Agent verifies the signature before applying the update.

## Cryptographic Tools

- **ed25519** or **ECDSA** for digital signatures
- **SHA-256** checksum for integrity verification
- **mbedTLS** used for TLS and crypto on-device (ESP32)

## Example Signing Script

```bash
openssl dgst -sha256 -sign fw-private.pem -out firmware.sig firmware.bin
```

```json
{
  "version": "1.3.2",
  "signature": "base64:MEUCIQD...",
  "checksum": "sha256:...",
  "public_key_hint": "esp32_ca"
}
```


