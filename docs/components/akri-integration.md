# Akri Integration for Onboarding

We extend Akri's discovery handler mechanism to incorporate device verification before exposing devices as Kubernetes resources.

Except for the [OTA Agent](/components/ota-agent/), which utilizes the attestation server
to verify whether an incoming connection is authorized or not, we now incorporated this
rationale into the Discovery handler. Therefore, a device verification is required before
exposing a device as a Kubernetes resource. This enhancement ensures that only verified
devices are discoverable and managed within the cluster, strengthening the overall security
and preventing unauthorized devices from being represented in Kubernetes.

![Figure 1](../assets/images/extend-akri.png){width="1000"}
