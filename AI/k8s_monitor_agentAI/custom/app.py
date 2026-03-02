#!/usr/bin/env python3
"""
Slack Bolt App
인터랙티브 버튼 클릭을 처리하고 MCP 도구를 실행합니다
"""

import asyncio
import json
import logging
import os
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from agent.k8s_agent import execute_fix, update_slack_message

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_APP_TOKEN = os.environ["SLACK_APP_TOKEN"]        # Socket Mode용 xapp- 토큰
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]

app = AsyncApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)


# ─────────────────────────────────────────────────────────────
# Fix 버튼 핸들러 (action_id: fix_*)
# ─────────────────────────────────────────────────────────────

@app.action({"action_id": lambda id: id.startswith("fix_")})
async def handle_fix_action(ack, body, client):
    await ack()

    action = body["actions"][0]
    user = body["user"]["name"]
    message_ts = body["message"]["ts"]
    channel = body["channel"]["id"]

    try:
        payload = json.loads(action["value"])
    except (json.JSONDecodeError, KeyError):
        log.error(f"Invalid action value: {action.get('value')}")
        return

    problem_title = payload.get("problem_title", "알 수 없음")
    solution_label = payload.get("solution_label", "")
    solution_desc = payload.get("solution_description", "")
    action_params = payload.get("params", {})

    log.info(f"Fix 요청: user={user}, problem={problem_title}, solution={solution_label}")

    # 메시지를 "진행 중" 상태로 업데이트
    await client.chat_update(
        channel=channel,
        ts=message_ts,
        text=f"⏳ `{solution_label}` 실행 중...",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"⏳ *실행 중...*\n"
                        f"👤 *실행자:* @{user}\n"
                        f"🔧 *작업:* {solution_label}\n"
                        f"📋 *대상 문제:* {problem_title}\n"
                        f"💬 *내용:* {solution_desc}"
                    )
                }
            }
        ]
    )

    # 실제 MCP 도구 실행
    try:
        result_json = await execute_fix(payload)
        result = json.loads(result_json) if result_json else {}
        success = result.get("success", True)
        message = result.get("message", "실행 완료")

        status_emoji = "✅" if success else "❌"
        status_text = "성공" if success else "실패"

        # 결과 메시지로 업데이트
        await client.chat_update(
            channel=channel,
            ts=message_ts,
            text=f"{status_emoji} 작업 {status_text}",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"{status_emoji} *작업 {status_text}*\n"
                            f"👤 *실행자:* @{user}\n"
                            f"🔧 *작업:* {solution_label}\n"
                            f"📋 *대상 문제:* {problem_title}\n"
                            f"💬 *결과:* {message}"
                        )
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {"type": "mrkdwn", "text": f"🕐 처리 완료 | `{action_params.get('tool', 'N/A')}`"}
                    ]
                }
            ]
        )

        # 결과를 스레드에 추가
        await client.chat_postMessage(
            channel=channel,
            thread_ts=message_ts,
            text=f"✅ *{solution_label}* 실행 결과:\n```{json.dumps(result, ensure_ascii=False, indent=2)}```"
        )

    except Exception as e:
        log.error(f"Fix 실행 오류: {e}", exc_info=True)
        await client.chat_update(
            channel=channel,
            ts=message_ts,
            text="❌ 실행 실패",
            blocks=[
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"❌ *실행 실패*\n"
                            f"👤 *실행자:* @{user}\n"
                            f"🔧 *작업:* {solution_label}\n"
                            f"💬 *오류:* {str(e)}"
                        )
                    }
                }
            ]
        )


# ─────────────────────────────────────────────────────────────
# Ignore 버튼 핸들러 (action_id: ignore_*)
# ─────────────────────────────────────────────────────────────

@app.action({"action_id": lambda id: id.startswith("ignore_")})
async def handle_ignore_action(ack, body, client):
    await ack()

    action = body["actions"][0]
    user = body["user"]["name"]
    message_ts = body["message"]["ts"]
    channel = body["channel"]["id"]

    try:
        payload = json.loads(action["value"])
    except:
        payload = {}

    problem_title = payload.get("problem_title", "알 수 없음")
    log.info(f"무시 처리: user={user}, problem={problem_title}")

    await client.chat_update(
        channel=channel,
        ts=message_ts,
        text="🙈 무시됨",
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": (
                        f"🙈 *무시됨*\n"
                        f"👤 *처리자:* @{user}\n"
                        f"📋 *문제:* {problem_title}"
                    )
                }
            }
        ]
    )


# ─────────────────────────────────────────────────────────────
# 시작
# ─────────────────────────────────────────────────────────────

async def start_slack_app():
    handler = AsyncSocketModeHandler(app, SLACK_APP_TOKEN)
    await handler.start_async()


if __name__ == "__main__":
    asyncio.run(start_slack_app())
