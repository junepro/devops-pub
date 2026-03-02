"""
K8s MCP Slack Bot — EKS 버전
- MCP Client : Flux159/mcp-server-kubernetes
- LLM        : Google Gemini 2.0 Flash
- 클러스터   : AWS EKS (EC2 Bastion IAM Role 인증)
- 실행 환경  : EC2 Bastion

병렬 실행:
  1. run_monitor_loop  — EKS 클러스터 주기적 분석 + Slack 알림
  2. start_slack_app   — @멘션 / DM 자연어 명령 처리
  3. kubeconfig_refresh_loop — EKS 토큰 10분마다 자동 갱신
"""

import asyncio
import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
log = logging.getLogger(__name__)


def _check_env():
    required = [
        "GOOGLE_API_KEY",
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN",
        "SLACK_SIGNING_SECRET",
        "SLACK_CHANNEL_ID",
        "AWS_REGION",
        "EKS_CLUSTER_NAME",
    ]
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"❌ 필수 환경변수 누락: {', '.join(missing)}")
        print("   .env 파일을 확인하세요.")
        sys.exit(1)


async def main():
    _check_env()

    region   = os.environ["AWS_REGION"]
    cluster  = os.environ["EKS_CLUSTER_NAME"]
    interval = int(os.environ.get("MONITOR_INTERVAL_SECONDS", "60"))

    # ── 시작 시 EKS kubeconfig 갱신 ──────────────────────────────
    from agent.eks_auth import refresh_kubeconfig, verify_kubectl, kubeconfig_refresh_loop

    log.info("EKS kubeconfig 초기 설정 중...")
    ok = await asyncio.get_event_loop().run_in_executor(None, refresh_kubeconfig)
    if not ok:
        print("❌ EKS kubeconfig 갱신 실패. AWS CLI / IAM Role 설정을 확인하세요.")
        sys.exit(1)

    ok = await asyncio.get_event_loop().run_in_executor(None, verify_kubectl)
    if not ok:
        print("❌ EKS 연결 실패. kubeconfig 및 클러스터 상태를 확인하세요.")
        sys.exit(1)

    print("=" * 56)
    print("🚀 K8s MCP Slack Bot — EKS")
    print(f"   MCP Server  : Flux159/mcp-server-kubernetes (npx)")
    print(f"   LLM         : Gemini 2.0 Flash")
    print(f"   EKS 클러스터: {cluster} ({region})")
    print(f"   모니터링    : {interval}초 간격")
    print(f"   Slack 채널  : {os.environ['SLACK_CHANNEL_ID']}")
    print("=" * 56)
    print()
    print("💬 Slack 사용법")
    print(f"   채널 @멘션 또는 봇 DM 으로 자연어 입력")
    print(f"   예) @k8s-bot nginx deployment 만들어줘 replicas 2")
    print(f"   예) @k8s-bot CrashLoopBackOff pod 정리해줘")
    print(f"   예) @k8s-bot 도움말")
    print()

    from agent.monitor import run_monitor_loop
    from slack_app.app import start_slack_app

    # 세 루프 동시 실행
    await asyncio.gather(
        run_monitor_loop(interval=interval),   # EKS 모니터링
        start_slack_app(),                      # Slack 자연어 명령
        kubeconfig_refresh_loop(),              # EKS 토큰 자동 갱신
    )


if __name__ == "__main__":
    asyncio.run(main())
