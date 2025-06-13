# Installation

## Install FlashJob Operator

The FlashJob Operator is a Kubernetes operator designed to automate the process of flashing firmware to devices using Akri instances. It manages the lifecycle of FlashJob custom resources, which define the parameters for firmware updates, and orchestrates the necessary Kubernetes resources such as Pods and Services to perform the flashing operations.

### Deploying the Controller

The FlashJob Operator can be deployed to a Kubernetes cluster using one of the following methods:

#### Method 1: One-Click Installation via YAML

1. Apply the Installer YAML:

   - Install the operator using the official release YAML:

   ```
   kubectl apply -f https://github.com/nubificus/flashjob_operator/releases/download/v1.20.1/install.yaml
   ```

2. Apply the Custom Resource:

   - Apply a FlashJob resource manually or use the filter_uuid.py script (see below):

   ```
   kubectl apply -f config/samples/application_v1alpha1_flashjob.yaml
   ```

#### Method 2: Helm Installation

1. Add the Helm Repository:

   - Add the FlashJob Operator Helm repository:

   ```
   helm repo add flashjob https://nubificus.github.io/flashjob_operator
   helm repo update
   ```

2. Install the Operator:

   - Install the operator using Helm:

   ```
   helm install my-flashjob-operator flashjob/operator \
   --version 1.20.1 \
   --namespace operator-system --create-namespace \
   --set image.repository=harbor.nbfc.io/cloud-iot/akri_operator \
   --set image.tag=1.20.1
   ```

3. Uninstall (if needed):

   - Remove the operator and namespace:

   ```
   helm uninstall my-flashjob-operator --namespace operator-system
   kubectl delete namespace operator-system
   ```

For more information and advanced usage, please refer to the [FlashJob Components](../components/flashjob.md) and the [FlashJob tutorial](../tutorials/flashjob.md).
