#!/usr/bin/env python3
"""
K8s MCP Server
kind 클러스터를 모니터링하고 조작하는 MCP 도구 모음
"""

import json
import subprocess
import asyncio
from typing import Any
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool, TextContent, CallToolResult, ListToolsResult
)
from kubernetes import client, config
from kubernetes.client.rest import ApiException

# K8s 클라이언트 초기화
try:
    config.load_kube_config()  # ~/.kube/config 사용
except:
    config.load_incluster_config()

v1 = client.CoreV1Api()
apps_v1 = client.AppsV1Api()

app = Server("k8s-mcp-server")


@app.list_tools()
async def list_tools() -> ListToolsResult:
    return ListToolsResult(tools=[
        Tool(
            name="get_pods",
            description="네임스페이스의 Pod 목록과 상태를 가져옵니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {
                        "type": "string",
                        "description": "네임스페이스 (기본값: all)",
                        "default": "all"
                    }
                }
            }
        ),
        Tool(
            name="get_events",
            description="K8s 이벤트를 가져옵니다. Warning 이벤트 위주로 확인",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "default": "all"},
                    "event_type": {
                        "type": "string",
                        "description": "Warning 또는 Normal",
                        "default": "Warning"
                    },
                    "limit": {"type": "integer", "default": 20}
                }
            }
        ),
        Tool(
            name="get_pod_logs",
            description="특정 Pod의 로그를 가져옵니다",
            inputSchema={
                "type": "object",
                "required": ["pod_name", "namespace"],
                "properties": {
                    "pod_name": {"type": "string"},
                    "namespace": {"type": "string"},
                    "lines": {"type": "integer", "default": 50},
                    "container": {"type": "string", "default": ""}
                }
            }
        ),
        Tool(
            name="get_nodes",
            description="노드 상태와 리소스 정보를 가져옵니다",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_deployments",
            description="Deployment 상태를 가져옵니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "namespace": {"type": "string", "default": "all"}
                }
            }
        ),
        Tool(
            name="restart_deployment",
            description="Deployment를 롤링 재시작합니다",
            inputSchema={
                "type": "object",
                "required": ["name", "namespace"],
                "properties": {
                    "name": {"type": "string", "description": "Deployment 이름"},
                    "namespace": {"type": "string"}
                }
            }
        ),
        Tool(
            name="scale_deployment",
            description="Deployment의 레플리카 수를 조정합니다",
            inputSchema={
                "type": "object",
                "required": ["name", "namespace", "replicas"],
                "properties": {
                    "name": {"type": "string"},
                    "namespace": {"type": "string"},
                    "replicas": {"type": "integer"}
                }
            }
        ),
        Tool(
            name="delete_pod",
            description="Pod를 삭제합니다 (자동 재생성 트리거)",
            inputSchema={
                "type": "object",
                "required": ["pod_name", "namespace"],
                "properties": {
                    "pod_name": {"type": "string"},
                    "namespace": {"type": "string"}
                }
            }
        ),
        Tool(
            name="describe_pod",
            description="Pod 상세 정보 (이벤트 포함)를 가져옵니다",
            inputSchema={
                "type": "object",
                "required": ["pod_name", "namespace"],
                "properties": {
                    "pod_name": {"type": "string"},
                    "namespace": {"type": "string"}
                }
            }
        ),
    ])


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> CallToolResult:
    try:
        if name == "get_pods":
            result = await _get_pods(arguments)
        elif name == "get_events":
            result = await _get_events(arguments)
        elif name == "get_pod_logs":
            result = await _get_pod_logs(arguments)
        elif name == "get_nodes":
            result = await _get_nodes(arguments)
        elif name == "get_deployments":
            result = await _get_deployments(arguments)
        elif name == "restart_deployment":
            result = await _restart_deployment(arguments)
        elif name == "scale_deployment":
            result = await _scale_deployment(arguments)
        elif name == "delete_pod":
            result = await _delete_pod(arguments)
        elif name == "describe_pod":
            result = await _describe_pod(arguments)
        else:
            result = {"error": f"Unknown tool: {name}"}

        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        )
    except Exception as e:
        return CallToolResult(
            content=[TextContent(type="text", text=json.dumps({"error": str(e)}))]
        )


async def _get_pods(args: dict) -> dict:
    namespace = args.get("namespace", "all")
    pods = []

    if namespace == "all":
        pod_list = v1.list_pod_for_all_namespaces()
    else:
        pod_list = v1.list_namespaced_pod(namespace)

    for pod in pod_list.items:
        containers = []
        if pod.status.container_statuses:
            for cs in pod.status.container_statuses:
                containers.append({
                    "name": cs.name,
                    "ready": cs.ready,
                    "restart_count": cs.restart_count,
                    "state": _get_container_state(cs.state)
                })

        pods.append({
            "name": pod.metadata.name,
            "namespace": pod.metadata.namespace,
            "phase": pod.status.phase,
            "containers": containers,
            "node": pod.spec.node_name,
            "age": str(pod.metadata.creation_timestamp)
        })

    # 문제 있는 Pod 먼저
    pods.sort(key=lambda x: (
        0 if x["phase"] in ["Failed", "Unknown", "Pending"] else 1
    ))
    return {"pods": pods, "total": len(pods)}


def _get_container_state(state) -> str:
    if state.running:
        return "Running"
    elif state.waiting:
        return f"Waiting: {state.waiting.reason or 'unknown'}"
    elif state.terminated:
        return f"Terminated: {state.terminated.reason or 'unknown'} (exit: {state.terminated.exit_code})"
    return "Unknown"


async def _get_events(args: dict) -> dict:
    namespace = args.get("namespace", "all")
    event_type = args.get("event_type", "Warning")
    limit = args.get("limit", 20)

    if namespace == "all":
        events = v1.list_event_for_all_namespaces()
    else:
        events = v1.list_namespaced_event(namespace)

    result = []
    for event in events.items:
        if event_type and event.type != event_type:
            continue
        result.append({
            "type": event.type,
            "reason": event.reason,
            "message": event.message,
            "object": f"{event.involved_object.kind}/{event.involved_object.name}",
            "namespace": event.metadata.namespace,
            "count": event.count,
            "first_time": str(event.first_timestamp),
            "last_time": str(event.last_timestamp)
        })

    # 최신순
    result = result[-limit:]
    return {"events": result, "count": len(result)}


async def _get_pod_logs(args: dict) -> dict:
    pod_name = args["pod_name"]
    namespace = args["namespace"]
    lines = args.get("lines", 50)
    container = args.get("container") or None

    kwargs = {"tail_lines": lines}
    if container:
        kwargs["container"] = container

    logs = v1.read_namespaced_pod_log(pod_name, namespace, **kwargs)
    return {"pod": pod_name, "namespace": namespace, "logs": logs}


async def _get_nodes(args: dict) -> dict:
    nodes = []
    node_list = v1.list_node()

    for node in node_list.items:
        conditions = {}
        for cond in (node.status.conditions or []):
            conditions[cond.type] = cond.status

        # 리소스 정보
        capacity = {}
        if node.status.capacity:
            capacity = {
                "cpu": node.status.capacity.get("cpu"),
                "memory": node.status.capacity.get("memory")
            }

        nodes.append({
            "name": node.metadata.name,
            "ready": conditions.get("Ready", "Unknown"),
            "conditions": conditions,
            "capacity": capacity,
            "roles": [
                k.replace("node-role.kubernetes.io/", "")
                for k in (node.metadata.labels or {})
                if k.startswith("node-role.kubernetes.io/")
            ]
        })

    return {"nodes": nodes}


async def _get_deployments(args: dict) -> dict:
    namespace = args.get("namespace", "all")
    deploys = []

    if namespace == "all":
        deploy_list = apps_v1.list_deployment_for_all_namespaces()
    else:
        deploy_list = apps_v1.list_namespaced_deployment(namespace)

    for d in deploy_list.items:
        deploys.append({
            "name": d.metadata.name,
            "namespace": d.metadata.namespace,
            "desired": d.spec.replicas,
            "ready": d.status.ready_replicas or 0,
            "available": d.status.available_replicas or 0,
            "unavailable": d.status.unavailable_replicas or 0,
        })

    return {"deployments": deploys}


async def _restart_deployment(args: dict) -> dict:
    name = args["name"]
    namespace = args["namespace"]

    import datetime
    patch = {
        "spec": {
            "template": {
                "metadata": {
                    "annotations": {
                        "kubectl.kubernetes.io/restartedAt":
                            datetime.datetime.utcnow().isoformat() + "Z"
                    }
                }
            }
        }
    }
    apps_v1.patch_namespaced_deployment(name, namespace, patch)
    return {"success": True, "message": f"Deployment {name} 재시작 요청 완료"}


async def _scale_deployment(args: dict) -> dict:
    name = args["name"]
    namespace = args["namespace"]
    replicas = args["replicas"]

    patch = {"spec": {"replicas": replicas}}
    apps_v1.patch_namespaced_deployment(name, namespace, patch)
    return {"success": True, "message": f"Deployment {name} → {replicas} 레플리카로 스케일 완료"}


async def _delete_pod(args: dict) -> dict:
    pod_name = args["pod_name"]
    namespace = args["namespace"]
    v1.delete_namespaced_pod(pod_name, namespace)
    return {"success": True, "message": f"Pod {pod_name} 삭제 완료 (재생성 진행 중)"}


async def _describe_pod(args: dict) -> dict:
    pod_name = args["pod_name"]
    namespace = args["namespace"]

    pod = v1.read_namespaced_pod(pod_name, namespace)
    events = v1.list_namespaced_event(
        namespace,
        field_selector=f"involvedObject.name={pod_name}"
    )

    event_list = [{
        "type": e.type,
        "reason": e.reason,
        "message": e.message,
        "count": e.count
    } for e in events.items]

    return {
        "name": pod.metadata.name,
        "namespace": pod.metadata.namespace,
        "phase": pod.status.phase,
        "node": pod.spec.node_name,
        "events": event_list,
        "conditions": [
            {"type": c.type, "status": c.status, "reason": c.reason}
            for c in (pod.status.conditions or [])
        ]
    }


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="k8s-mcp-server",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
