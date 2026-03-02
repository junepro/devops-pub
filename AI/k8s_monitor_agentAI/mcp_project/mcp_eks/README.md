# 🚀 K8s MCP Slack Bot — EKS

## 아키텍처

```
EC2 Bastion (python main.py — systemd 상시 실행)
│
│  IAM Role (Access Key 불필요)
│
├─ [루프 1] EKS 모니터링 (60초 주기)
│     │
│     ▼
│  MCPGeminiClient (MCP Client)
│     │  1. list_tools()     MCP Protocol (stdio)
│     │  2. Gemini → tool_use ──────────────────────┐
│     │  3. call_tool()                              │
│     └──────────────────────────────────────────────┤
│                                                    │
│  mcp-server-kubernetes (Flux159, npx)              │
│     │  ~/.kube/config (EKS kubeconfig)             │
│     ▼                                              │
│  AWS EKS 클러스터 ◄───────────────────────────────┘
│
├─ [루프 2] Slack 자연어 명령
│     @멘션 / DM → MCPGeminiClient → EKS → 답변
│     Fix 버튼   → MCP call_tool   → EKS → 결과
│
└─ [루프 3] kubeconfig 10분마다 자동 갱신
      aws eks update-kubeconfig
      (EKS STS 토큰 15분 만료 대응)
```

## 파일 구조

```
k8s-mcp-eks/
├── main.py                      # 진입점 — 세 루프 병렬 실행
├── requirements.txt
├── .env                         # 환경변수
├── agent/
│   ├── eks_auth.py              # EKS kubeconfig 갱신 / 연결 확인
│   ├── mcp_gemini_client.py     # ★ 표준 MCP Client + Gemini 연동
│   ├── monitor.py               # 모니터링 에이전트 + Slack 알림
│   └── commander.py             # 자연어 명령 에이전트
└── slack_app/
    └── app.py                   # Slack Bolt (@멘션, DM, 버튼)
```

## EC2 Bastion 실행 순서

### 1. 사전 요구사항
```bash
python3.11 --version   # 3.11 이상
node --version         # 18 이상
aws --version          # AWS CLI v2
kubectl version        # kubectl
```

### 2. 설치
```bash
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. .env 작성
```bash
vi .env   # 각 항목 입력
```

### 4. EKS 연결 확인
```bash
# IAM Role 이 올바르게 설정되어 있으면 자동 인증
aws eks update-kubeconfig --region us-east-1 --name k8s-mcp-dev-eks
kubectl get nodes
```

### 5. 실행
```bash
source venv/bin/activate
export $(grep -v '^#' .env | xargs)
python main.py
```

### 6. systemd 서비스 등록 (상시 실행)
```bash
# /etc/systemd/system/k8s-bot.service
[Unit]
Description=K8s MCP Slack Bot (EKS)
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/k8s-mcp-eks
EnvironmentFile=/home/ubuntu/k8s-mcp-eks/.env
ExecStart=/home/ubuntu/k8s-mcp-eks/venv/bin/python main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# 등록 및 시작
sudo systemctl daemon-reload
sudo systemctl enable k8s-bot
sudo systemctl start k8s-bot
sudo journalctl -u k8s-bot -f
```

## Slack 사용 예시
```
@k8s-bot 도움말
@k8s-bot pod 목록 보여줘
@k8s-bot nginx deployment 만들어줘 replicas 2
@k8s-bot my-app 5개로 스케일 업
@k8s-bot my-app 재시작해줘
@k8s-bot CrashLoopBackOff pod 전부 정리해줘
```



## 추가 설정 슬랙

Event Subscriptions -> on

Subscribe to bot events -> app_mention , message.im 설정

## bot oauth
app_mentions:read
앱이 있는 대화에서 @monitor_bot을(를) 직접 멘션하는 메시지 보기

channels:history
"monitor_bot" 앱이 추가된 공개 채널에서 메시지와 다른 콘텐츠 보기

chat:write
@monitor_bot(으)로 메시지 보내기

chat:write.public
@monitor_bot이(가) 멤버가 아닌 채널로 메시지 보내기

im:history
"monitor_bot" 앱이 추가된 다이렉트 메시지에서 메시지와 다른 콘텐츠 보기

im:read
"monitor_bot" 앱이 추가된 다이렉트 메시지에 관한 기본 정보 보기

im:write
사람들과 다이렉트 메시지 시작


## sudo npm install -g mcp-server-kubernetes
## pip install google-genai aiohttp "slack-bolt[async]"