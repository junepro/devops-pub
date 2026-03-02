# Clone Repo
git clone https://github.com/kubernetes/autoscaler.git
  
# Navigate to VPA
cd autoscaler/vertical-pod-autoscaler/
  
# Uninstall VPA (if we are using old one)
./hack/vpa-down.sh
  
# Install new version of VPA
./hack/vpa-up.sh
  
# Verify VPA Pods
kubectl get pods -n kube-system

# Terminal 1 - List and watch pods
kubectl get pods -w
  
# Terminal 2 - Generate Load
kubectl run --generator=run-pod/v1 apache-bench -i --tty --rm --image=httpd -- ab -n 500000 -c 1000 http://vpa-demo-service-nginx.default.svc.cluster.local/
  
# Terminal 3 - Generate Load
kubectl run --generator=run-pod/v1 apache-bench2 -i --tty --rm --image=httpd -- ab -n 500000 -c 1000 http://vpa-demo-service-nginx.default.svc.cluster.local/
  
# Terminal 4 - Generate Load
kubectl run --generator=run-pod/v1 apache-bench3 -i --tty --rm --image=httpd -- ab -n 500000 -c 1000 http://vpa-demo-service-nginx.default.svc.cluster.local/