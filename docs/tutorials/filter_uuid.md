# FlashJob Operator: `filter_uuid.py` Tutorial

This tutorial provides a detailed guide on using the `filter_uuid.py` script to interact with Akri instances in a Kubernetes cluster, filter devices, and generate a FlashJob YAML for firmware updates using the FlashJob Operator. For instructions on deploying the FlashJob Operator, refer to the [installation guide](/docs/getting-started/installation.md).

## Overview

The `filter_uuid.py` script is a Python utility designed to simplify the process of selecting Akri-discovered IoT devices in a Kubernetes cluster and generating a FlashJob YAML file for firmware flashing. It supports filtering devices by UUID, device type, and application type, allows user selection of devices, and enables gradual rollout of firmware updates in batches.

## Prerequisites

Before using the `filter_uuid.py` script, ensure the following are in place:

- **Python 3.x**: Installed on your system.
- **Required Python Packages**:
  ```bash
  pip install kubernetes pyyaml
  ```
- **Kubernetes Cluster**: A running Kubernetes (e.g., k3s) cluster with Akri instances configured.
- **kubectl**: Configured with access to the cluster (ensure the correct context is set).
- **FlashJob Operator**: Deployed in the cluster. Refer to [installation](/docs/getting-started/installation.md) for deployment instructions.
- **Akri Instances**: Configured in the `default` namespace (or modify the script for other namespaces).

## Script Overview

The `filter_uuid.py` script performs the following tasks:

1. **Fetch Akri Instances**: Retrieves Akri instances from the Kubernetes API server.
2. **Filter Instances**: Filters devices based on user-provided criteria (UUID, device type, application type).
3. **User Selection**: Allows interactive selection of specific or all Akri instances.
4. **Firmware Specification**: Prompts for firmware image details.
5. **Gradual Rollout**: Supports batch-based firmware updates with configurable batch sizes and delays.
6. **YAML Generation**: Saves selected UUIDs and firmware details to a FlashJob YAML file.
7. **Apply YAML**: Applies the generated YAML to the cluster using `kubectl`.

## Step-by-Step Usage

### 1. Run the Script

To use the `filter_uuid.py` script, first clone the FlashJob Operator repository:

```bash
git clone https://github.com/nubificus/flashjob_operator
cd flashjob_operator
```

Execute the script in a terminal:

```bash
python3 filter_uuid.py
```

The script will guide you through an interactive process to filter devices, select instances, and configure firmware updates.

### 2. Filter Akri Instances

The script prompts you to filter Akri instances based on the following criteria:

- **Device Type**: Filter devices by their type (e.g., `esp32`). Press Enter to skip.
- **Application Type**: Filter by application type (e.g., `thermo`). Press Enter to skip.
- **UUID**: Filter by a specific UUID. Press Enter to skip.

Example prompt:

```text
Enter device type to filter (or press Enter to skip): esp32
Enter application type to filter (or press Enter to skip): thermo
Enter UUID to filter (or press Enter to skip):
```

The script queries the Kubernetes API and lists matching Akri instances.

### 3. Select Devices

After filtering, the script displays a list of available Akri instances, each with an index, UUID, device type, and application type. For example:

```text
Available Akri Instances:
[0] UUID: d95c7c2d-7dc5-427b-9bf7-51a5d299c99e, Device Type: esp32, Application Type: thermo
[1] UUID: 44606d10-7c29-4098-9d6a-dc16f95090d1, Device Type: esp32, Application Type: thermo
```

You are prompted to select devices:

- **Select All**: Enter `y` to select all listed UUIDs.
- **Select Specific Devices**: Enter `n` and provide a comma-separated list of indices (e.g., `0,1`).

Example:

```text
Do you want to select all UUIDs? (y/n): y
```

### 4. Enter Firmware Details

Next, specify the firmware image to use for flashing the selected devices. Provide the full image path, including the repository and tag. For example:

```text
Enter the firmware to use: harbor.nbfc.io/nubificus/esp32:x.x.xxxxxxx
```

### 5. Configure Gradual Rollout (Optional)

To manage large-scale updates, the script supports gradual rollout in batches:

- **Batch Size**: Specify the number of devices per batch (default: `5`).
- **Delay Between Batches**: Specify the delay in seconds between batches (default: `60`).

Example:

```text
Enter the number of UUIDs per batch (default is 5): 2
Enter the delay between batches in seconds (default is 60): 30
```

### 6. Apply the FlashJob

The script generates a FlashJob YAML file (e.g., `flashjob_operator/config/samples/application_v1alpha1_flashjob.yaml`) with the selected UUIDs and firmware details. It then applies the YAML to the cluster using `kubectl`.

Example output:

```text
Applying batch 1 with UUIDs: ['d95c7c2d-7dc5-427b-9bf7-51a5d299c99e', '44606d10-7c29-4098-9d6a-dc16f95090d1']
UUIDs saved to flashjob_operator/config/samples/application_v1alpha1_flashjob.yaml
Successfully applied flashjob_operator/config/samples/application_v1alpha1_flashjob.yaml
Waiting for 30 seconds before the next batch...
```

For each batch, the script updates the YAML with the next set of UUIDs and applies it after the specified delay.

## Example Workflow

Here’s a complete example of running the script:

```text
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

## Generated FlashJob YAML

The script generates a YAML file like the following, which is used by the FlashJob Operator to manage firmware updates:

```yaml
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

## Script Functions

The `filter_uuid.py` script includes the following key functions:

- **get_akri_instances()**: Queries the Kubernetes API to retrieve Akri instances.
- **filter_instances()**: Filters instances based on user-provided UUID, device type, and application type.
- **user_select_instances()**: Handles interactive selection of Akri instances.
- **save_uuids_to_yaml()**: Generates and saves the FlashJob YAML file with selected UUIDs and firmware details.
- **apply_yaml()**: Applies the generated YAML file to the cluster using `kubectl`.
- **gradual_rollout()**: Manages batch-based application of the YAML file with specified delays.

## Tips & Notes

- **Namespace**: The script assumes Akri instances are in the `default` namespace. If your instances are in a different namespace, modify the script or specify the namespace in the YAML.
- **kubectl Context**: Ensure the `kubectl` context is set to the correct cluster before running the script.
- **Troubleshooting**: If the script or FlashJob application fails, check the FlashJob Operator logs:
  ```bash
  kubectl logs -n operator-system deployment/flashjob-operator
  ```
- **Batch Configuration**: Adjust batch size and delay for gradual rollout based on your cluster’s capacity and device requirements.

## Troubleshooting Common Issues

- **Error: Kubernetes API Unreachable**: Verify that `kubectl` is configured correctly and the cluster is accessible.
- **No Akri Instances Found**: Ensure Akri is deployed and instances are registered in the `default` namespace.
- **YAML Application Fails**: Check the operator logs (`kubectl logs -n operator-system deployment/flashjob-operator`) and verify the firmware image is valid.
- **Script Fails to Save YAML**: Ensure the script has write permissions in the target directory (`flashjob_operator/config/samples/`).

This tutorial should help you effectively use the `filter_uuid.py` script to manage firmware updates for IoT devices with the FlashJob Operator. For further details on deploying the operator, see [installation](/docs/getting-started/installation.md).
