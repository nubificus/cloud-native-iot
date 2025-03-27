# Cloud Native IoT Project User's guide

Placeholder document for the end to end scenario

## End to end scenario 

### Steps
- Create script to assign unique and known names to USB devices (based on serialId, vendorId, mac, etc)
- Create minimal firmware containing OTA functionality and `/info` endpoint for onboarding
- Build it with Action (update action to have 2 modes)
- Flash N devices with minimal firmware (document partition table/secure boot/build settings etc)
- Create a fresh k3s with latest Akri
- Deploy our custom operator
- Deploy our DICE auth server (with Redis)
- Deploy an onboarding Discovery Handler
- Post their MAC addresses to DICE auth  (automate proccess)
- Wait for onboarding Discovery Handler to discover them
- Deploy 2 additional Discovery Handlers (based on 2 different application types)
- Use operator to flash X devices with application A and Y devices with application B (leveraging panos' script)
- Use operator to repurpose 1 or more Devices for application A to B
- Use operator to upgrade 1 or more Devices to newest fimrware version

### Future tasks
- Implement Dice authentication for the Devices at the onboarding DH step
