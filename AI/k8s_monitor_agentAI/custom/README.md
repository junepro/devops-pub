# 🚀 K8s MCP + OpenAI + Slack DevOps Bot

kind 클러스터 문제를 자동 감지하고, AI가 분석 후 Slack으로 해결 방법을 제안합니다.
버튼 클릭 한 번으로 실제 수정 작업이 실행됩니다.

## 📐 아키텍처

```
┌─────────────┐     kubectl      ┌──────────────┐     MCP      ┌───────────────┐
│  kind       │◄────────────────►│  MCP Server  │◄────────────►│  AI Agent     │
│  Cluster    │                  │  (Python)    │              │  (OpenAI GPT) │
└─────────────┘                  └──────────────┘              └───────┬───────┘
                                                                        │ Slack API
                                                               ┌────────▼───────┐
                                                               │  Slack Channel │
                                                               │  [Fix] [Ignore]│
                                                               └────────┬───────┘
                                                                        │ Button Click
                                                               ┌────────▼───────┐
                                                               │  Slack Bolt    │
                                                               │  (Action Handler)│
                                                               └────────┬───────┘
                                                                        │ MCP Call
                                                               ┌────────▼───────┐
                                                               │  Execute Fix   │
                                                               │  (restart/scale)│
                                                               └────────────────┘
```

## 🗂️ 프로젝트 구조

```
k8s-mcp-slack/
├── main.py                    # 진입점 (에이전트 + Slack 앱 동시 실행)
├── requirements.txt
├── .env.example               # 환경변수 템플릿
├── mcp_server/
│   └── server.py             # K8s MCP 서버 (9가지 도구)
├── agent/
│   └── k8s_agent.py          # OpenAI Agent + MCP 클라이언트
└── slack_app/
    └── app.py                # Slack Bolt (버튼 인터랙션 처리)
```

## 🔧 MCP 서버 도구 목록

| 도구 | 설명 |
|------|------|
| `get_pods` | 네임스페이스별 Pod 상태 조회 |
| `get_events` | K8s 이벤트 (Warning 위주) |
| `get_pod_logs` | Pod 로그 조회 |
| `get_nodes` | 노드 상태 및 리소스 |
| `get_deployments` | Deployment 상태 |
| `restart_deployment` | 롤링 재시작 |
| `scale_deployment` | 레플리카 수 조정 |
| `delete_pod` | Pod 삭제 (재생성 트리거) |
| `describe_pod` | Pod 상세 정보 + 이벤트 |

## 🚀 실행 방법

### 1. 사전 준비

```bash
# kind 클러스터 실행 확인
kubectl get nodes

# Python 패키지 설치
pip install -r requirements.txt
```

### 2. Slack 앱 설정

1. https://api.slack.com/apps 에서 새 앱 생성
2. **OAuth & Permissions** → Bot Token Scopes 추가:
   - `chat:write`, `chat:write.public`
3. **Socket Mode** 활성화 → App-Level Token 발급 (xapp-...)
4. **Event Subscriptions** → Socket Mode로 설정
5. 앱을 채널에 초대: `/invite @앱이름`

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일을 편집기로 열어 값 입력
```

### 4. 실행

```bash
# 환경변수 로드 후 실행
source .env
python main.py

# 또는 dotenv 사용
python -c "from dotenv import load_dotenv; load_dotenv()" && python main.py
```

## 💬 Slack 메시지 예시

```
🔍 K8s 클러스터 상태 리포트

요약: 2개 문제 감지됨

────────────────────────────────
🔴 [CRITICAL] Pod CrashLoopBackOff 감지
📌 영향 리소스: `default/my-app-7d9f8b-xkz2p`
📋 설명: Pod가 반복적으로 재시작 중 (재시작 횟수: 15)
🔍 원인: OOMKilled - 메모리 한도 초과

[🔄 Pod 재시작] [📈 레플리카 축소] [🙈 무시]

💡 제안 해결책:
  • 🔄 Pod 재시작: my-app Deployment 롤링 재시작
  • 📈 레플리카 축소: 레플리카를 1로 줄여 부하 감소
```

## ⚙️ 주요 설정

```python
# agent/k8s_agent.py
interval_seconds=60   # 모니터링 주기 (기본 60초)
model="gpt-4o"        # 사용 모델
```

## 🧪 단독 테스트

```bash
# MCP 서버 직접 테스트
python mcp_server/server.py

# 에이전트 단발 분석 테스트 (Slack 전송 없음)
python agent/k8s_agent.py

# Slack 앱만 실행
python slack_app/app.py
```
