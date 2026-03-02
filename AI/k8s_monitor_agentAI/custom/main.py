#!/usr/bin/env python3
"""
메인 진입점
K8s 모니터링 에이전트 + Slack 인터랙티브 앱을 동시에 실행
"""

import asyncio
import logging
import os
import sys

log = logging.getLogger(__name__)


async def main():
    # 환경 변수 검증
    required_envs = [
        "OPENAI_API_KEY",
        "SLACK_BOT_TOKEN",
        "SLACK_APP_TOKEN",
        "SLACK_SIGNING_SECRET",
        "SLACK_CHANNEL_ID"
    ]
    missing = [e for e in required_envs if not os.environ.get(e)]
    if missing:
        print(f"❌ 필수 환경변수 누락: {', '.join(missing)}")
        print("   .env 파일을 설정하고 다시 실행하세요.")
        sys.exit(1)

    interval = int(os.environ.get("MONITOR_INTERVAL_SECONDS", "60"))

    print("🚀 K8s MCP Slack DevOps Bot 시작")
    print(f"   모니터링 간격: {interval}초")
    print(f"   Slack 채널: {os.environ['SLACK_CHANNEL_ID']}")

    # 에이전트 루프 + Slack 앱 병렬 실행
    from agent.k8s_agent import run_analysis_loop
    from slack_app.app import start_slack_app

    await asyncio.gather(
        run_analysis_loop(interval_seconds=interval),
        start_slack_app()
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    asyncio.run(main())
