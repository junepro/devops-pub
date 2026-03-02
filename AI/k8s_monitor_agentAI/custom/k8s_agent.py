#!/usr/bin/env python3
"""
K8s AI Agent
OpenAI SDK + MCP 클라이언트를 이용해 클러스터 문제를 분석하고
Slack에 해결 방법과 인터랙티브 버튼을 전송합니다
"""

import asyncio
import json
import os
import logging
from typing import Any, Optional
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import httpx

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_CHANNEL_ID = os.environ["SLACK_CHANNEL_ID"]
MCP_SERVER_CMD = ["python", "mcp_server/server.py"]

openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


# ─────────────────────────────────────────────────────────────
# MCP 세션 헬퍼
# ─────────────────────────────────────────────────────────────

async def get_mcp_tools(session: ClientSession) -> list[dict]:
    """MCP 도구 목록을 OpenAI Tool 형식으로 변환"""
    tools_result = await session.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema or {"type": "object", "properties": {}}
            }
        }
        for tool in tools_result.tools
    ]


async def call_mcp_tool(session: ClientSession, name: str, args: dict) -> str:
    """MCP 도구 호출"""
    result = await session.call_tool(name, args)
    return result.content[0].text if result.content else "{}"


# ─────────────────────────────────────────────────────────────
# OpenAI Agent - 문제 분석
# ─────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """당신은 Kubernetes DevOps 전문가입니다.
kind 클러스터를 모니터링하고 문제를 분석합니다.

분석 순서:
1. get_events (Warning 이벤트 먼저)
2. get_pods (비정상 Pod 확인)
3. get_deployments (배포 상태 확인)
4. 필요시 get_pod_logs / describe_pod로 상세 조사

문제 발견 시 반드시 JSON 형식으로 응답하세요:
{
  "problems": [
    {
      "severity": "critical|warning|info",
      "title": "문제 제목",
      "description": "상세 설명",
      "affected": "영향받는 리소스",
      "root_cause": "추정 원인",
      "solutions": [
        {
          "label": "버튼에 표시될 짧은 라벨 (20자 이내)",
          "description": "해결 방법 설명",
          "action": "mcp_tool_name",
          "params": {"tool": "도구명", "args": {}}
        }
      ]
    }
  ],
  "summary": "전체 클러스터 상태 요약"
}

문제가 없으면:
{"problems": [], "summary": "클러스터 정상 운영 중"}"""


async def analyze_cluster(session: ClientSession) -> dict:
    """클러스터 분석 실행"""
    tools = await get_mcp_tools(session)
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "현재 kind 클러스터 상태를 종합 분석하고 문제를 JSON으로 보고해주세요."}
    ]

    log.info("클러스터 분석 시작...")

    # ReAct loop
    for iteration in range(10):
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto",
            temperature=0
        )

        msg = response.choices[0].message
        messages.append({"role": "assistant", "content": msg.content, "tool_calls": msg.tool_calls})

        # 도구 호출
        if msg.tool_calls:
            for tc in msg.tool_calls:
                fn_name = tc.function.name
                fn_args = json.loads(tc.function.arguments)
                log.info(f"  Tool: {fn_name}({fn_args})")

                result = await call_mcp_tool(session, fn_name, fn_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result
                })
        else:
            # 최종 응답 파싱
            content = msg.content or "{}"
            # JSON 블록 추출
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            try:
                return json.loads(content)
            except json.JSONDecodeError:
                log.warning(f"JSON 파싱 실패: {content[:200]}")
                return {"problems": [], "summary": content}

    return {"problems": [], "summary": "분석 완료 (반복 제한 도달)"}


# ─────────────────────────────────────────────────────────────
# MCP 도구 실행 (버튼 액션용)
# ─────────────────────────────────────────────────────────────

async def execute_fix(action: dict) -> str:
    """버튼 클릭 시 실제 MCP 도구 실행"""
    server_params = StdioServerParameters(command=MCP_SERVER_CMD[0], args=MCP_SERVER_CMD[1:])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tool_name = action["params"]["tool"]
            tool_args = action["params"]["args"]
            log.info(f"Fix 실행: {tool_name}({tool_args})")
            result = await call_mcp_tool(session, tool_name, tool_args)
            return result


# ─────────────────────────────────────────────────────────────
# Slack Block Kit 메시지 빌더
# ─────────────────────────────────────────────────────────────

SEVERITY_EMOJI = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵"
}


def build_slack_blocks(analysis: dict) -> list[dict]:
    """분석 결과를 Slack Block Kit 형식으로 변환"""
    blocks = []

    # 헤더
    blocks.append({
        "type": "header",
        "text": {"type": "plain_text", "text": "🔍 K8s 클러스터 상태 리포트", "emoji": True}
    })

    # 요약
    blocks.append({
        "type": "section",
        "text": {"type": "mrkdwn", "text": f"*요약:* {analysis.get('summary', '')}"}
    })

    if not analysis.get("problems"):
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": "✅ 감지된 문제 없음"}
        })
        return blocks

    blocks.append({"type": "divider"})

    for i, problem in enumerate(analysis["problems"]):
        emoji = SEVERITY_EMOJI.get(problem.get("severity", "info"), "⚪")

        # 문제 설명
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"{emoji} *[{problem['severity'].upper()}] {problem['title']}*\n"
                    f"📌 *영향 리소스:* `{problem.get('affected', 'N/A')}`\n"
                    f"📋 *설명:* {problem.get('description', '')}\n"
                    f"🔍 *원인:* {problem.get('root_cause', '')}"
                )
            }
        })

        # 해결 방법 버튼들
        solutions = problem.get("solutions", [])
        if solutions:
            action_elements = []
            for j, sol in enumerate(solutions[:4]):  # 최대 4개 버튼
                action_id = f"fix_{i}_{j}"
                # 액션 데이터를 value에 인코딩
                value = json.dumps({
                    "problem_title": problem["title"],
                    "solution_label": sol["label"],
                    "solution_description": sol["description"],
                    "action": sol.get("action", ""),
                    "params": sol.get("params", {})
                })

                style = "danger" if problem.get("severity") == "critical" else "primary"

                action_elements.append({
                    "type": "button",
                    "text": {"type": "plain_text", "text": sol["label"], "emoji": True},
                    "style": style,
                    "action_id": action_id,
                    "value": value,
                    "confirm": {
                        "title": {"type": "plain_text", "text": "실행 확인"},
                        "text": {"type": "mrkdwn", "text": f"*{sol['description']}*\n\n정말 실행하시겠습니까?"},
                        "confirm": {"type": "plain_text", "text": "실행"},
                        "deny": {"type": "plain_text", "text": "취소"}
                    }
                })

            # Ignore 버튼 추가
            action_elements.append({
                "type": "button",
                "text": {"type": "plain_text", "text": "🙈 무시", "emoji": True},
                "action_id": f"ignore_{i}",
                "value": json.dumps({"problem_title": problem["title"], "ignore": True})
            })

            blocks.append({
                "type": "actions",
                "elements": action_elements
            })

        # 해결 방법 설명 (별도 텍스트)
        if solutions:
            sol_text = "\n".join(
                f"  • *{s['label']}:* {s['description']}"
                for s in solutions
            )
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"💡 *제안 해결책:*\n{sol_text}"}
            })

        blocks.append({"type": "divider"})

    return blocks


# ─────────────────────────────────────────────────────────────
# Slack 메시지 전송
# ─────────────────────────────────────────────────────────────

async def send_slack_message(blocks: list[dict], text: str = "K8s 클러스터 알림") -> Optional[str]:
    """Slack 메시지 전송, ts(타임스탬프) 반환"""
    async with httpx.AsyncClient() as http:
        resp = await http.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={
                "channel": SLACK_CHANNEL_ID,
                "text": text,
                "blocks": blocks
            }
        )
        data = resp.json()
        if data.get("ok"):
            log.info(f"Slack 메시지 전송 완료: ts={data['ts']}")
            return data["ts"]
        else:
            log.error(f"Slack 전송 실패: {data}")
            return None


async def update_slack_message(ts: str, blocks: list[dict], text: str = "") -> None:
    """기존 Slack 메시지 업데이트"""
    async with httpx.AsyncClient() as http:
        await http.post(
            "https://slack.com/api/chat.update",
            headers={"Authorization": f"Bearer {SLACK_BOT_TOKEN}"},
            json={
                "channel": SLACK_CHANNEL_ID,
                "ts": ts,
                "text": text,
                "blocks": blocks
            }
        )


# ─────────────────────────────────────────────────────────────
# 메인 워커 - 주기적 클러스터 분석
# ─────────────────────────────────────────────────────────────

async def run_analysis_loop(interval_seconds: int = 60):
    """주기적으로 클러스터 분석 실행"""
    log.info(f"K8s 모니터링 시작 (간격: {interval_seconds}초)")
    server_params = StdioServerParameters(
        command=MCP_SERVER_CMD[0],
        args=MCP_SERVER_CMD[1:]
    )

    while True:
        try:
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    analysis = await analyze_cluster(session)

            log.info(f"분석 완료: 문제 {len(analysis.get('problems', []))}개 발견")

            # 문제가 있을 때만 Slack 전송
            if analysis.get("problems"):
                blocks = build_slack_blocks(analysis)
                await send_slack_message(blocks, f"⚠️ K8s 클러스터 이상 감지: {len(analysis['problems'])}개 문제")
            else:
                log.info("문제 없음 - Slack 전송 스킵")

        except Exception as e:
            log.error(f"분석 중 오류: {e}", exc_info=True)

        await asyncio.sleep(interval_seconds)


if __name__ == "__main__":
    # 단발 분석 테스트
    async def test():
        server_params = StdioServerParameters(
            command=MCP_SERVER_CMD[0], args=MCP_SERVER_CMD[1:]
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                analysis = await analyze_cluster(session)

        print(json.dumps(analysis, ensure_ascii=False, indent=2))
        blocks = build_slack_blocks(analysis)
        print("\n--- Slack Blocks ---")
        print(json.dumps(blocks, ensure_ascii=False, indent=2))

    asyncio.run(test())
