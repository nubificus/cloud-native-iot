# Installation

This document will guide you through the process of configuring a k3s cluster
with all the necessary components to run our Cloud Native IoT framework, namely:

- [Akri](https://github.com/project-akri/akri)
- [Attestation Server](./../components/attestation-server.md)
- [FlashJob Operator](./../components/flashjob.md)
- [Longhorn](https://github.com/longhorn/longhorn)
- [MetalLB](https://github.com/metallb/metallb)

The cluster used while writing this document was a [k3s](https://k3s.io/)
installation on a Ubuntu 22.04 machine. The k3s cluster was configured with
[Calico CNI](https://github.com/projectcalico/calico) to provide networking.

## Install MetalLB in the cluster

To ensure the IoT devices can talk to the [OTA agent](./../components/ota-agent.md),
we need to provide the [flashjob pod](./../components/flashjob-pod.md) with a
routeable IP. We use metallb to do that.

First, we need to apply the manifest:

```bash
VERSION=v0.13.12
kubectl apply -f https://raw.githubusercontent.com/metallb/metallb/$VERSION/config/manifests/metallb-native.yaml
```

Next, we will create an IP pool:

```bash
cat <<EOF | tee ip-pool.yaml
apiVersion: metallb.io/v1beta1
kind: IPAddressPool
metadata:
  name: first-pool
  namespace: metallb-system
spec:
  addresses:
  - 192.168.5.201-192.168.5.230
EOF
kubectl apply -f ip-pool.yaml
```

> **Note**: This must be a unique range in our subnet. For our e2e example,
> we use 192.168.5.221-230 (max 9 concurrent flashjobs).

Finally, we will enable l2 advertisement (this will populate ARP entries
across the cluster):

```bash
cat <<EOF | tee l2add.yaml
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: example
  namespace: metallb-system
spec:
  ipAddressPools:
  - first-pool
EOF
kubectl apply -f l2add.yaml
```

> **Note**: This is not needed most probably for this setup, but it's good to
> have it in case an ARP request does not reach the cluster correctly.

## Install longhorn in the cluster

The DICE auth server uses Redis as a storage backend. To ensure Redis has
persistent storage across reboots an additional storage system for Kubernetes must
be installed. In this case, we use Longhorn since it is suggested by the k3s maintainers.

First, we need to install `open-iscsi` in all k3s nodes:

```bash
sudo apt update
sudo apt install open-iscsi -y
```

Once `open-iscsi` is properly installed, we can go ahead and install `longhorn`:

```bash
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/deploy/longhorn.yaml
```

## Install Akri in the cluster

To install Akri we will use Helm:

```bash
helm repo add akri-helm-charts https://project-akri.github.io/akri/
helm repo update
KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm install akri akri-helm-charts/akri
```

And now, we can verify the Akri Pods are properly deployed:

```bash
$ kubectl get pods -A | grep akri
default            akri-agent-daemonset-4p249                    1/1     Running     0          43s
default            akri-agent-daemonset-h87nf                    1/1     Running     0          43s
default            akri-controller-deployment-745f4bfc4c-hkg84   1/1     Running     0          43s
default            akri-webhook-configuration-78666f968d-lf875   1/1     Running     0          43s
```

## Deploy DICE auth server and Redis

To deploy the DICE auth server, we need to also deploy a Redis pod as well
as a persistent volume for the Redis pod:

```bash
cat <<EOF | sudo tee deployment.yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: redis-data
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: longhorn
  resources:
    requests:
      storage: 2Gi
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis-deployment
  labels:
    app: redis
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: redis:latest
          ports:
            - containerPort: 6379
          volumeMounts:
            - mountPath: /data
              name: redis-storage
          resources:
            limits:
              memory: "256Mi"
              cpu: "500m"
          command: ["redis-server", "--appendonly", "yes"]
      volumes:
        - name: redis-storage
          persistentVolumeClaim:
            claimName: redis-data
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
    - protocol: TCP
      port: 6379  # Service port
      targetPort: 6379  # Pod container port
  type: ClusterIP  # Change to NodePort or LoadBalancer if external access is needed
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dice-auth-deployment
  labels:
    app: dice-auth
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dice-auth
  template:
    metadata:
      labels:
        app: dice-auth
    spec:
      containers:
        - name: dice-auth
          image: harbor.nbfc.io/nubificus/iot/dice-auth-server:e2e
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
---
apiVersion: v1
kind: Service
metadata:
  name: dice-auth-service
spec:
  selector:
    app: dice-auth
  ports:
    - protocol: TCP
      port: 8000  # Service port
      targetPort: 8000  # Pod container port
  type: ClusterIP  # Change to NodePort or LoadBalancer if external access is needed
EOF
kubectl apply -f deployment.yaml
```

We should see the Dice auth and Redis Pod running:

```bash
$ kubectl get pods
NAME                                          READY   STATUS    RESTARTS   AGE
...
dice-auth-deployment-5cfd8b6dc4-qhzg8         1/1     Running   0          107s
redis-deployment-64dd9d7478-t4rmd             1/1     Running   0          39s
```

### Build the DICE auth server container image

In case you need to build DICE auth server container image, there is
a Dockerfile in the `dice-auth` repo:

```bash
git clone https://github.com/nubificus/dice-auth.git
cd dice-auth
sudo podman build -t harbor.nbfc.io/nubificus/iot/dice-auth-server:latest .
sudo podman push harbor.nbfc.io/nubificus/iot/dice-auth-server:latest
```

## Install Flashjob Operator in the cluster

### Method 1: One-Click Installation via YAML

We can install the operator using the official release YAML:

```bash
kubectl apply -f https://github.com/nubificus/flashjob_operator/releases/download/v1.20.1/inst  all.yaml
```

### Method 2: Helm Installation

Add the FlashJob Operator Helm repository:

```bash
helm repo add flashjob https://nubificus.github.io/flashjob_operator
helm repo update
```

Install the Operator using Helm:

```bash
helm install my-flashjob-operator flashjob/operator \
--version 1.20.1 \
--namespace operator-system --create-namespace \
--set image.repository=harbor.nbfc.io/cloud-iot/akri_operator \
--set image.tag=1.20.1
```

## Wrapping up

Now, we have a fully functional cluster with all the necessary components
to run our Cloud Native IoT framework. You can continue this journey by
preparing an ESP32-device to [be onboarded in the cluster](./../tutorials/esp32-initial.md)
and [deploying a Discovery Handler to onboard the device](./../components/akri-dh.md#deploying-the-discovery-handler)!
