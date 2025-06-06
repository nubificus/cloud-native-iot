# Flashjob Operator

The FlashJob Operator is a Kubernetes operator designed to automate the process of flashing firmware to devices using Akri instances. It manages the lifecycle of FlashJob custom resources, which define the parameters for firmware updates, and orchestrates the necessary Kubernetes resources such as Pods and Services to perform the flashing operations.

FlashJob is composed of a CRD, a controller, and CR.
Below, each of these components is described in detail.

## Custom Resource Definition (CRD)

The FlashJob CRD defines the schema for the custom resource managed by the operator. It is located at `config/crd/bases/application.flashjob.nbfc.io_flashjobs.yaml`.

### Spec

- **UUID**: Unique identifier for the device.
- **Firmware**: The firmware image to be flashed.
- **Version**: The version of the firmware.
- **HostEndpoint**: The endpoint of the host where the device is connected.
- **Device**: The type of device (e.g., `esp32s2`).
- **ApplicationType**: The type of application (e.g., `thermo`).
- **ExternalIP**: The external IP address of the service.
- **FlashjobPodImage**: The container image used from the flash pod.

### Status

- **Conditions**: A list of conditions representing the current state of the FlashJob.
- **Message**: A human-readable message describing the current state.
- **HostEndpoint**: The endpoint of the host where the device is connected.
- **Phase**: Current phase (InProgress, Completed, Failed).
- **CompletedUUIDs**:List of UUIDs for devices that have completed flashing

### FlashJob Controller

The controller, implemented in `internal/controller/flashjob_controller.go`, manages the lifecycle of FlashJob resources through a reconciliation loop. It ensures the desired state specified in the FlashJob resource is achieved by handling the creation, updating, and deletion of associated Pods and Services.

### Key Functions

- **Reconcile:**

  - **Reconciliation Loop**
  - The main reconciliation loop that handles the creation and updating of FlashJob resources.
  - Ensures that the desired state (defined in the `FlashJobSpec`) matches the observed state.
  - Manages the lifecycle of associated Pods and Services.

- **getAkriInstanceDetails**

  - Retrieves details about the Akri instance associated with the device UUID.

- **handleFlashingPod**

  - Manages the creation and updating of the flashing Pod.
  - Creates a Pod using the `FlashjobPodImage` and configures it with environment variables such as `FIRMWARE`, `UUID`, `HOST_ENDPOINT`, and `DEVICE`.

- **createService**

  - Creates a `LoadBalancer` Service per Pod with a unique external IP.

- **waitForServiceIP**

  - Waits for the Service to acquire an external IP.
  - Updates the `FlashJob` resource with the external IP once it is available.

- **updateFlashJobStatus**

  - Updates the `FlashJob` status based on Pod phase and deletes completed resources.

- **handleDeletion**
  - Handles the deletion of `FlashJob` resources.
  - Cleans up associated resources such as Pods and Services.
  - Removes the finalizer to allow the resource to be deleted from the cluster.

### Example FlashJob Resource

Below is an example FlashJob resource definition, located at `config/samples/application_v1alpha1_flashjob.yaml`:

```yaml
apiVersion: application.flashjob.nbfc.io/v1alpha1
kind: FlashJob
metadata:
  name: flashjob
  namespace: default
spec:
  uuid:
    - d95c7c2d-7dc5-427b-9bf7-51a5d299c99e
    - 44606d10-7c29-4098-9d6a-dc16f95090d1
  device: esp32
  hostEndpoint:
  firmware: harbor.nbfc.io/nubificus/esp32:x.x.xxxxxxx
  version: 0.2.0
  applicationType: thermo
  externalIP:
  flashjobPodImage: harbor.nbfc.io/nubificus/iot/esp32-sota:xxx.x-debug
```

### Fields

- **uuid:** The unique identifier for the device.

- **device:** The type of device (e.g., esp32).

- **firmware:** The firmware image to be flashed.

- **version:** The version of the firmware.

- **applicationType:** The type of application (e.g., thermo).

- **flashjobPodImage:** The container image used from the pod.

## How It Works

For a detailed step-by-step explanation of the FlashJob Operator workflow, including all involved components and lifecycle diagrams, see [FlashJob Operator Workflow](../architecture/flashjobworkflow.md).

For implementation details and the full source code, see the [FlashJob Operator GitHub repository](https://github.com/nubificus/flashjob_operator).
