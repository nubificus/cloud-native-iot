# Cloud Native IoT Project User's guide

Placeholder document for the end to end scenario

## End to end scenario

### Steps

- Create script to assign unique and known names to USB devices (based on serialId, vendorId, mac, etc)
- Create minimal firmware containing OTA functionality and `/info` endpoint for onboarding
- Build it with Action (update action to have 2 modes)
- Flash N devices with minimal firmware (document partition table/secure boot/build settings etc)
- [Create a fresh k3s with latest Akri](#install-akri)
- [Deploy our custom operator](#deploy-flashjob-operator)
- [Deploy our DICE auth server](#deploy-dice-auth-server)
- Deploy an onboarding Discovery Handler
- Post their MAC addresses to DICE auth  (automate proccess)
- Wait for onboarding Discovery Handler to discover them
- Deploy 2 additional Discovery Handlers (based on 2 different application types)
- Use operator to flash X devices with application A and Y devices with application B (leveraging panos' script)
- Use operator to repurpose 1 or more Devices for application A to B
- Use operator to upgrade 1 or more Devices to newest fimrware version

### Future tasks

- Implement Dice authentication for the Devices at the onboarding DH step

### Install Akri

#### Provision VMs

```bash
incus launch images:ubuntu/22.04/cloud cniot01 --project NBFC-long-running-infra --description "Control plane VM for Akri k3s" -p default --target @amd64 --vm -c limits.cpu=3 -c limits.memory=4GiB -d root,size=30GiB --vm
incus launch images:ubuntu/22.04/cloud cniot02 --project NBFC-long-running-infra --description "Worker VM for Akri k3s" -p default --target @amd64 --vm -c limits.cpu=2 -c limits.memory=2GiB -d root,size=20GiB --vm
```

#### Install k3s cluster

In the control-plane node:

```bash
POD_CIDR="10.240.32.0/19"
SERVICE_CIDR="10.240.0.0/19"
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC='--flannel-backend=none' sh -s - --disable-network-policy --disable "servicelb" --disable "metrics-server" --cluster-cidr $POD_CIDR --service-cidr $SERVICE_CIDR

sudo addgroup k3s-admin
sudo adduser $USER k3s-admin
sudo usermod -a -G k3s-admin $USER
sudo chgrp k3s-admin /etc/rancher/k3s/k3s.yaml
sudo chmod g+r /etc/rancher/k3s/k3s.yaml
newgrp k3s-admin

POD_CIDR="10.240.32.0/19"
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/tigera-operator.yaml
wget https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/custom-resources.yaml
sed -i "s|192\.168\.0\.0/16|${POD_CIDR}|g" custom-resources.yaml
kubectl apply -f custom-resources.yaml
rm custom-resources.yaml

sudo cat /var/lib/rancher/k3s/server/node-token
```

In the worker node:

```bash
TOKEN="mynodetoken"
TOKEN="K10cb1aec2eaef0b96931b5523fc8bdc11f398a544cd239a8defb7a0b5d837daec4::server:6e958b911ddbdf5670f1042e761ebd1a"
curl -sfL https://get.k3s.io | K3S_URL=https://cniot01:6443 K3S_TOKEN=$TOKEN sh -
```

#### Install Akri in the cluster

To install Akri we will need Helm:

```bash
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

Once Helm is installed:

```bash
helm repo add akri-helm-charts https://project-akri.github.io/akri/
helm repo update
KUBECONFIG=/etc/rancher/k3s/k3s.yaml helm install akri akri-helm-charts/akri
```

Verify the Akri Pods are properly deployed:

```bash
$ kubectl get pods -A | grep akri
default            akri-agent-daemonset-4p249                    1/1     Running     0          43s
default            akri-agent-daemonset-h87nf                    1/1     Running     0          43s
default            akri-controller-deployment-745f4bfc4c-hkg84   1/1     Running     0          43s
default            akri-webhook-configuration-78666f968d-lf875   1/1     Running     0          43s
```

### Deploy Flashjob Operator

```bash
cd ~
sudo apt-get install make -y
curl -fsSL https://scripts.gntouts.com/go.sh | bash -s go1.24.2
git clone -b uuid_array git@github.com:nubificus/flashjob_operator.git
cd flashjob_operator

GOPATH=$(go env GOPATH):$PWD make manifests
GOPATH=$(go env GOPATH):$PWD make install

sudo apt-get install podman -y
sudo podman login --username gntouts --password <REDACTED> harbor.nbfc.io
cat <<EOF | sudo tee -a /etc/containers/registries.conf
[registries.search]
registries = ['docker.io']
EOF
sudo CONTAINER_TOOL=podman IMG=harbor.nbfc.io/nubificus/iot/flashjob-operator:e2e make docker-build docker-push
IMG=harbor.nbfc.io/nubificus/iot/flashjob-operator:e2e make deploy
```

You should see the Operator Pod running:

```bash

$ kubectl get pods -A | grep manager
operator-system    operator-controller-manager-c75bcc686-6lsk2   1/1     Running     0          23s
```

### Deploy DICE auth server

#### Build the DICE auth server container image

```bash
cd ~
git clone -b feat_submit_mac git@github.com:nubificus/dice-auth.git
cd dice-auth
sudo podman build -t harbor.nbfc.io/nubificus/iot/dice-auth-server:e2e .
sudo podman push harbor.nbfc.io/nubificus/iot/dice-auth-server:e2e
```

#### Deploy DICE auth server and Redis

The DICE auth server uses Redis as a storage backend. To ensure Redis has persistent storage across reboots an additional storage
system for Kubernetes must be installed. In this case, we use Longhorn since it is suggested by the k3s maintainers.

```bash
sudo apt update
sudo apt install open-iscsi -y # required by longhorn, make sure to install in both nodes
kubectl apply -f https://raw.githubusercontent.com/longhorn/longhorn/v1.6.0/deploy/longhorn.yaml
```

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

### Deploy Onboarding Discovery Handler

Next, we need to deploy a new Discovery Handler to onboard any devices.

To create the new DH we need apply a new Akri Config:

```yaml
controller:
  enabled: false
agent:
  enabled: false
useLatestContainers: false
rbac:
  enabled: false
webhookConfiguration:
  enabled: false
custom:
  configuration:
    enabled: true
    name: http-range-onboard # The name of akric
    capacity: 2
    discoveryHandlerName: http-discovery-onboard # name of discovery handler, must be unique and matching discovery.name. will be used for socket creation
    discoveryDetails: | # make sure this is valid YAML
      ipStart: 192.168.11.20
      ipEnd: 192.168.11.100
      applicationType: initial
      secure: true
    brokerPod:
      image:
        repository: gntouts/akri-example-broker
        tag: aba58b6
  discovery:
    enabled: true
    image:
      repository: harbor.nbfc.io/nubificus/iot/akri-discovery-handler-go
      tag: 61d23fb
    name: http-discovery-onboard # name of discovery handler, must be unique and matching custom.configuration.discoveryHandlerName
```

```bash
helm template akri akri-helm-charts/akri -f onboardingConfig.yaml > template.yaml
kubectl apply -f ./template.yaml
```
