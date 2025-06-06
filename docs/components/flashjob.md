# FlashJob Operator


The FlashJob Operator is a Kubernetes operator designed to automate the process of flashing firmware to devices using Akri instances. It manages the lifecycle of FlashJob custom resources, which define the parameters for firmware updates, and orchestrates the necessary Kubernetes resources such as Pods and Services to perform the flashing operations.

## Deploying the Controller
The FlashJob Operator can be deployed to a Kubernetes cluster using one of the following methods:

### Method 1: One-Click Installation via YAML 
1) Apply the Installer YAML:
    - Install the operator using the official release YAML:

    ~~~
    kubectl apply -f https://github.com/nubificus/flashjob_operator/releases/download/v1.20.1/install.yaml
    ~~~
2) Apply the Custom Resource:
    - Apply a FlashJob resource manually or use the filter_uuid.py script (see below):

    ~~~
    kubectl apply -f config/samples/application_v1alpha1_flashjob.yaml
    ~~~
### Method 2: Helm Installation
1) Add the Helm Repository:
    - Add the FlashJob Operator Helm repository:

    ~~~
    helm repo add flashjob https://nubificus.github.io/flashjob_operator
    helm repo update
    ~~~
2) Install the Operator:
    - Install the operator using Helm:

    ~~~
    helm install my-flashjob-operator flashjob/operator \
    --version 1.20.1 \
    --namespace operator-system --create-namespace \
    --set image.repository=harbor.nbfc.io/cloud-iot/akri_operator \
    --set image.tag=1.20.1
    ~~~

3) Uninstall (if needed): 
    - Remove the operator and namespace:

    ~~~
    helm uninstall my-flashjob-operator --namespace operator-system
    kubectl delete namespace operator-system
    ~~~
 
##  Python Script: filter_uuid.py
The **filter_uuid.py** script is a utility designed to interact with Akri instances in a Kubernetes cluster. It allows users to filter Akri instances based on UUID, device type, and application type, and then save the selected UUIDs into a YAML file for use with the FlashJob operator. Additionally, it supports gradual roll-out of firmware updates to selected devices.

#### Prerequisites
- Python 3.x
- kubernetes Python package (pip install kubernetes)
- pyyaml Python package (pip install pyyaml)
- Access to a Kubernetes cluster with Akri instances configured.

####  Script Overview

1) **Fetch Akri Instances:**  Retrieves Akri instances from the Kubernetes API server.

2) **Filter Instances:**  Filters instances based on UUID, device type, and application type.

3) **User Selection:**  Allows the user to select specific instances or all instances.

4) **Save UUIDs to YAML:** Saves the selected UUIDs into a YAML file for use with the FlashJob operator.

5) **Gradual Rollout:**  Applies the YAML file in batches for gradual firmware roll-out.

#### Usage

1) **Run the Script:**

```
python3 filter_uuid.py
```
2) **Filter Instances:**

- The script will prompt to enter filters for device type, application type, and UUID.

3) **Select Instances:**

- After filtering, the script will display the available Akri instances and the use cat select all or specific instances.

4) **Enter Firmware Details:**

- Provide the firmware to be used for the selected devices.

5) **Gradual Rollout:**

- Specify the number of UUIDs per batch and the delay between batches (in seconds).

#### Example Workflow
```
$ python3 filter_uuid.py
Enter device type to filter (or press Enter to skip): esp32
Enter application type to filter (or press Enter to skip): thermo
Enter UUID to filter (or press Enter to skip):

Available Akri Instances:
[0] UUID: d95c7c2d-7dc5-427b-9bf7-51a5d299c99e, Device Type: esp32, Application Type: thermo
[1] UUID: 44606d10-7c29-4098-9d6a-dc16f95090d1, Device Type: esp32, Application Type: thermo

Do you want to select all UUIDs? (y/n): y
Enter the firmware to use: harbor.nbfc.io/nubificus/esp32:x.x.xxxxxxx
Enter the number of UUIDs per batch (default is 5): 2
Enter the delay between batches in seconds (default is 60): 30

Applying batch 1 with UUIDs: ['d95c7c2d-7dc5-427b-9bf7-51a5d299c99e', '44606d10-7c29-4098-9d6a-dc16f95090d1']
UUIDs saved to flashjob_operator/config/samples/application_v1alpha1_flashjob.yaml
Successfully applied flashjob_operator/config/samples/application_v1alpha1_flashjob.yaml
Waiting for 30 seconds before the next batch...
```

#### Script Functions

1) **get_akri_instances():** Fetches Akri instances from the Kubernetes API server.

2) **filter_instances():**  Filters instances based on UUID, device type, and application type.

3) **save_uuids_to_yaml():**  Saves the selected UUIDs into a YAML file.

4) **user_select_instances():**  Allows the user to select instances interactively.

5) **apply_yaml():** Applies the YAML file using kubectl.

6) **gradual_rollout():** Applies the YAML file in batches for gradual roll-out.


#### Integration with FlashJob Operator

The script generates a YAML file (application_v1alpha1_flashjob.yaml) that can be directly used by the FlashJob operator to manage firmware updates for the selected devices. The YAML file includes the UUIDs of the selected devices, the firmware to be used, and other necessary configurations.

#### Example YAML Output

```
apiVersion: application.flashjob.nbfc.io/v1alpha1
kind: FlashJob
metadata:
  name: flashjob
  namespace: default
spec:
  applicationType: thermo
  device: esp32
  externalIP:
  firmware: harbor.nbfc.io/nubificus/esp32:x.x.xxxxxxx
  flashjobPodImage: harbor.nbfc.io/nubificus/iot/x.x.xxxxxxx
  hostEndpoint:
  uuid:
    - d95c7c2d-7dc5-427b-9bf7-51a5d299c99e
    - 44606d10-7c29-4098-9d6a-dc16f95090d1
  version: "0.2.0"
```

> **_NOTE:_**
> - Ensure that the Kubernetes cluster is accessible and that the kubectl configuration is correctly set up.
> - The script assumes that the Akri instances are in the default namespace. Modify the script if your instances are in a different namespace.


## Components

#### Custom Resource Definition (CRD)

The FlashJob CRD defines the schema for the custom resource managed by the operator. It is located at `config/crd/bases/application.flashjob.nbfc.io_flashjobs.yaml`.

### Spec
- **UUID**: Unique identifier for the device.
- **Firmware**: The firmware image to be flashed.
- **Version**: The version of the firmware.
- **HostEndpoint**: The endpoint of the host where the device is connected.
- **Device**: The type of device (e.g., `esp32s2`).
- **ApplicationType**: The type of application (e.g., `thermo`).
- **ExternalIP**: The external IP address of the service.
- **FlashjobPodImage**: The container image used from the  flash pod.

### Status
- **Conditions**: A list of conditions representing the current state of the FlashJob.
- **Message**: A human-readable message describing the current state.
- **HostEndpoint**: The endpoint of the host where the device is connected.
- **Phase**: Current phase (InProgress, Completed, Failed).
- **CompletedUUIDs**:List of UUIDs for devices that have completed flashing

#### FlashJob Controller

The controller, implemented in `internal/controller/flashjob_controller.go`, manages the lifecycle of FlashJob resources through a reconciliation loop. It ensures the desired state specified in the FlashJob resource is achieved by handling the creation, updating, and deletion of associated Pods and Services.

### Key Functions:

- **Reconcile:**
    - The main reconciliation loop that handles the creation and updating of FlashJob resources.

    - Ensures that the desired state (defined in the FlashJobSpec) matches the observed state.

    - Manages the lifecycle of associated Pods and Services.

- **getAkriInstanceDetails:**
    - Retrieves details about the Akri instance associated with the device UUID.

- **handleFlashingPod:**
    - Manages the creation and updating of the flashing Pod.
    - Creates a Pod using the FlashjobPodImage and configures it with environment variables such as FIRMWARE, UUID, HOST_ENDPOINT, and DEVICE.

- **createService:**
    - Creates a LoadBalancer Service per Pod with a unique external IP.

- **waitForServiceIP:**
    - Waits for the Service to acquire an external IP.

    - Updates the FlashJob resource with the external IP once it is available.

- **updateFlashJobStatus:**
    - Updates the FlashJob status based on Pod phase and deletes completed resources.

- **handleDeletion:**
    - Handles the deletion of FlashJob resources.

    - Cleans up associated resources such as Pods and Services.

    - Removes the finalizer to allow the resource to be deleted from the cluster.

### Example FlashJob Resource
Below is an example FlashJob resource definition, located at `config/samples/application_v1alpha1_flashjob.yaml`:
```
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
The FlashJob Operator continuously reconciles the desired state of FlashJob resources with the actual state in the Kubernetes cluster. Here’s an overview of the process:

1) Reconciliation Loop:
    - The controller monitors FlashJob resources for changes.
    - When a FlashJob is created or updated, the Reconcile function triggers resource management.
2) Firmware Flashing:
    - For each device UUID, a pod is created using the specified FlashjobPodImage.
    - The pod is configured with environment variables such as FIRMWARE, UUID, HOST_ENDPOINT, and DEVICE.
    - The pod executes the firmware flashing operation.
3) Service Management:
    - A LoadBalancer service is created for each flashing pod to provide external access.
    - The controller waits for an external IP to be assigned and updates the FlashJob resource accordingly.
4) Status Updates:
    - The controller tracks the status of flashing pods and updates the FlashJob status (InProgress, Completed, or Failed).
    - Upon successful completion, the pod and its service are deleted, and the UUID is added to CompletedUUIDs.
5) Resource Cleanup:
    - When a FlashJob is deleted, the controller removes all associated pods and services.
    - The finalizer is cleared to allow complete resource deletion.