# Akri Integration for Onboarding

We extend Akri's discovery handler mechanism to incorporate device verification before exposing devices as Kubernetes resources.

## How It Works

1. Custom Akri Discovery Handler scans the network for candidate devices.
2. For each detected device, it queries the DICE Auth Service.
3. If the device is verified, it's registered as a Kubernetes `Device` resource.
4. The resource can now be scheduled for OTA, workloads, or monitoring.

## Benefits

- Transparent to the device — no manual K8s interaction
- Enables policy-based resource allocation using standard Kubernetes primitives
- Prevents rogue or untrusted devices from joining the cluster

## Sample CRD Snippet

```yaml
apiVersion: akri.sh/v0
kind: Configuration
metadata:
  name: verified-esp32
spec:
  discoveryHandler:
    name: secure-http
    secureMode: true
    allowedDeviceTypes:
      - esp32
```
