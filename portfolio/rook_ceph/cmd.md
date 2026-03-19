## Rook operator install
git clone --single-branch --branch master https://github.com/rook/rook.git
cd rook/deploy/examples

kubectl create -f crds.yaml -f common.yaml -f operator.yaml
kubectl -n rook-ceph get pods

## cluster install
kubectl apply -f cluster.yaml
kubectl -n rook-ceph get pods -w


## tool install
kubectl create -f toolbox.yaml
kubectl -n rook-ceph rollout status deploy/rook-ceph-tools
kubectl -n rook-ceph exec -it deploy/rook-ceph-tools -- bash

ceph status
ceph osd status
ceph osd tree
ceph df

## test
kubectl apply -f blockpool-test.yaml

kubectl apply -f rook-rbd-sc-test.yaml

kubectl apply -f pvc-test.yaml
kubectl get pvc

kubectl apply -f pod-test.yaml
kubectl exec -it rook-test-pod -- sh

## dashboard
kubectl -n rook-ceph port-forward svc/rook-ceph-mgr-dashboard 8443:8443


## delete

k delete -f ebs-sc.yaml