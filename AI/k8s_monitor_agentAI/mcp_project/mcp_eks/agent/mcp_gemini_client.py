"""
표준 MCP Client + Gemini 연동 (EKS 버전)

표준 MCP 흐름:
  1. stdio_client 로 mcp-server-kubernetes 프로세스 실행
  2. ClientSession.initialize() 로 MCP 프로토콜 초기화
  3. list_tools() 로 사용 가능한 도구 목록 조회
  4. Gemini 에게 도구 목록 + 사용자 메시지 전달
  5. Gemini → tool_use 선택
  6. call_tool() 로 MCP 서버(→ EKS)에 실행 요청
  7. 결과를 tool_result 로 Gemini 에게 반환
  8. 반복 → Gemini 최종 텍스트 응답
"""

import json
import logging
import os
from typing import Any
import asyncio

import google.generativeai as genai
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.types import Tool as MCPTool
from contextlib import AsyncExitStack  # <── [이 줄을 반드시 추가하세요]
log = logging.getLogger(__name__)

# ── mcp-server-kubernetes 서버 파라미터 ─────────────────────────
# Flux159/mcp-server-kubernetes
# ~/.kube/config (EKS kubeconfig, aws eks update-kubeconfig 로 갱신)
# EC2 Bastion IAM Role 로 EKS 인증 → Access Key 불필요
MCP_SERVER_PARAMS = StdioServerParameters(
    command="mcp-server-kubernetes",  # npx 대신 직접 실행 파일명 사용
    args=[],                          # npx 관련 인자 제거
    env={
        **os.environ,
        "KUBECONFIG": os.environ.get(
            "KUBECONFIG",
            os.path.expanduser("~/.kube/config"),
        ),
    },
)

def _mcp_tool_to_gemini(mcp_tool: MCPTool) -> genai.protos.FunctionDeclaration:
    """
    MCP list_tools() 결과 하나를 Gemini FunctionDeclaration 으로 변환
    Gemini 가 어떤 MCP 도구를 쓸지 이해할 수 있도록 스키마 변환
    """

    def _clean(schema: dict) -> dict:
        """Gemini 미지원 JSON Schema 필드 제거"""
        drop = {"additionalProperties", "$schema", "default", "examples", "$defs"}
        if not isinstance(schema, dict):
            return schema
        return {
            k: (
                _clean(v) if isinstance(v, dict)
                else [_clean(i) if isinstance(i, dict) else i for i in v]
                if isinstance(v, list)
                else v
            )
            for k, v in schema.items()
            if k not in drop
        }

    def _to_schema(s: dict) -> genai.protos.Schema:
        """JSON Schema dict → Gemini protos.Schema"""
        type_map = {
            "string":  "STRING",
            "integer": "INTEGER",
            "number":  "NUMBER",
            "boolean": "BOOLEAN",
            "array":   "ARRAY",
            "object":  "OBJECT",
        }
        result: dict[str, Any] = {
            "type_": type_map.get(s.get("type", "object"), "OBJECT"),
        }
        if "description" in s:
            result["description"] = s["description"]
        if "properties" in s:
            result["properties"] = {
                k: _to_schema(v) for k, v in s["properties"].items()
            }
        if "required" in s:
            result["required"] = s["required"]
        if "items" in s:
            result["items"] = _to_schema(s["items"])
        if "enum" in s:
            result["enum"] = s["enum"]
        return genai.protos.Schema(**result)

    schema = _clean(mcp_tool.inputSchema or {"type": "object", "properties": {}})
    return genai.protos.FunctionDeclaration(
        name=mcp_tool.name,
        description=mcp_tool.description or "",
        parameters=_to_schema(schema) if schema.get("properties") else None,
    )

# ── MCPGeminiClient (Persistent Session 버전) ──
class MCPGeminiClient:
    def __init__(self, system_prompt: str, model_name: str = "gemini-2.5-flash"):
        genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
        self.model = genai.GenerativeModel(model_name=model_name, system_instruction=system_prompt)
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._lock = asyncio.Lock()
        self.cached_tools = None  # <── [추가] 도구 목록 캐싱 변수

    async def _ensure_connected(self):
        """세션이 없으면 연결하고 초기화합니다."""
        if self.session:
            return
        
        log.info("MCP 서버 영구 세션 연결 시작...")
        read, write = await self.exit_stack.enter_async_context(stdio_client(MCP_SERVER_PARAMS))
        self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
        await self.session.initialize()
        log.info("MCP 영구 세션 초기화 완료.")

    async def run(self, user_message: str, max_iter: int = 15) -> str:
        """연결된 단일 세션을 사용하여 명령을 처리합니다."""
        async with self._lock: # 동시 호출 방지
            try:
                await self._ensure_connected()
                
                # 도구 목록 로드 (캐싱 가능하지만 안전을 z위해 매번 조회)
                tools_resp = await self.session.list_tools()
                gemini_tools = [genai.prWotos.Tool(function_declarations=[_mcp_tool_to_gemini(t) for t in tools_resp.tools])]

                chat = self.model.start_chat()
                response = chat.send_message(user_message, tools=gemini_tools)

                for _ in range(max_iter):
                    parts = response.candidates[0].content.parts
                    tool_result_parts = []

                    for part in parts:
                        if hasattr(part, "function_call") and part.function_call.name:
                            fn_name = part.function_call.name
                            fn_args = dict(part.function_call.args or {})
                            log.info(f"  [MCP Persistent Call] {fn_name}")
                            
                            mcp_result = await self.session.call_tool(fn_name, fn_args)
                            result_text = mcp_result.content[0].text if mcp_result.content else "{}"
                            
                            tool_result_parts.append(genai.protos.Part(
                                function_response=genai.protos.FunctionResponse(name=fn_name, response={"content": result_text})
                            ))

                    if tool_result_parts:
                        response = chat.send_message(genai.protos.Content(parts=tool_result_parts, role="function"), tools=gemini_tools)
                        continue
                    
                    texts = [p.text for p in parts if hasattr(p, "text") and p.text]
                    return "".join(texts) if texts else "결과가 없습니다."

            except Exception as e:
                log.error(f"실행 중 오류: {e}")
                self.session = None # 에러 발생 시 세션 초기화 (다음 호출 때 재연결)
                return f"❌ 오류 발생: {str(e)}"

    async def close(self):
        """앱 종료 시 자원 해제"""
        await self.exit_stack.aclose