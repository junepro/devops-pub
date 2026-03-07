# install
helm dependency update
helm install argocd-stack . -n argocd --create-namespace
# 로컬 8080 포트를 argocd-server 서비스의 443 포트로 연결
kubectl port-forward svc/argocd-server -n argocd 8080:443
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Argo CD 서버 포트를 로컬 8080으로 전달
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Step 1: 리소스 생성
    kubectl apply -f test-app.yaml

# Step 2: 상태 모니터링 (터미널)

    kubectl argo rollouts get rollout canary-demo --watch

# Step 3: 버전 업데이트 (이미지 변경)

    이미지를 yellow로 변경하여 Canary 배포를 시작합니다.

    kubectl argo rollouts set image canary-demo canary-demo=argoproj/rollouts-demo:yellow
    결과: Pod 4개 중 1개만 yellow로 바뀌고 Paused 상태가 됩니다.

    확인: 브라우저에서 localhost:8080 접속 시 간혹 노란색 화면이 나옵니다.

# Step 4: 수동 승인 (UI 또는 CLI)

    ArgoCD UI에서 해당 App의 Rollout 리소스를 클릭하고 "Promote" 버튼을 누르거나 아래 명령어를 입력하세요.

    kubectl argo rollouts promote canary-demo