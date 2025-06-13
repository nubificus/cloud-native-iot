# Frequently Asked Questions

## How does the FlashJob Operator ensure the security of firmware updates?

The FlashJob Operator prioritizes security by integrating with the Attestation Server to verify device identity using DICE certificates,  
ensuring only trusted devices are updated. It employs mbedTLS for encrypted communication between the FlashPod and devices,  
and leverages Firmware Signing to cryptographically secure firmware images.  
Additionally, the OTA Service and Agent monitor the process, while Akri’s metadata validation prevents unauthorized access,  
creating a robust, end-to-end secure workflow.

## How can I use the `filter_uuid.py` script to manage device updates?

The `filter_uuid.py` script helps you select Akri-discovered devices for firmware updates.  
Install Python 3.x and the `kubernetes` and `pyyaml` packages, then run the script with `python3 filter_uuid.py`.  
Follow prompts to filter by device type, application type, or UUID, select devices interactively, specify the firmware image,  
and configure batch sizes and delays for gradual rollouts.  
The script generates a FlashJob CR, which the Operator applies, as detailed in the [tutorial](/docs/tutorials/filter_uuid.md).
