#!/usr/bin/env python3
"""
Litera Model Context Protocol (MCP) Server
Entry point and JSON-RPC 2.0 stdio transport implementation.
Course: Human-Computer Interaction Design (HCI) / BSU FAMCS 2026
Authors: Kirill Zaidal, Anna-Maria Savitskaya (Group 12)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from typing import Any, Dict, Optional

from prompts import get_prompt_definitions, render_prompt
from resources import get_resource_definitions, read_resource
from storage import LiteraStorage, StorageError
from tools import get_tool_definitions, handle_tool_call

# All server diagnostic logs go to stderr to prevent corrupting stdio JSON-RPC transport!
logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [Litera-MCP] %(message)s",
)
logger = logging.getLogger("litera_mcp")

SERVER_NAME = "litera-bookstore-mcp-server"
SERVER_VERSION = "1.0.0"
PROTOCOL_VERSION = "2024-11-05"


class McpServer:
    def __init__(self, db_path: str = ":memory:"):
        self.storage = LiteraStorage(db_path=db_path)
        self.initialized = False

    def handle_request(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        msg_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {}) or {}

        # Handle notifications (requests without id)
        if msg_id is None:
            if method == "notifications/initialized":
                logger.info("Client completed initialization handshake.")
                self.initialized = True
            elif method == "notifications/cancelled":
                logger.info("Received request cancellation notification.")
            else:
                logger.debug(f"Ignored unhandled notification: {method}")
            return None

        # Standard JSON-RPC responses
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {
                        "tools": {"listChanged": False},
                        "resources": {"subscribe": False, "listChanged": False},
                        "prompts": {"listChanged": False},
                    },
                    "serverInfo": {
                        "name": SERVER_NAME,
                        "version": SERVER_VERSION,
                    },
                }
                return self._jsonrpc_success(msg_id, result)

            elif method == "ping":
                return self._jsonrpc_success(msg_id, {})

            # ---------------- TOOLS ----------------
            elif method == "tools/list":
                tools = get_tool_definitions()
                return self._jsonrpc_success(msg_id, {"tools": tools})

            elif method == "tools/call":
                tool_name = params.get("name", "")
                args = params.get("arguments", {}) or {}
                result = handle_tool_call(self.storage, tool_name, args)
                return self._jsonrpc_success(msg_id, result)

            # ---------------- RESOURCES ----------------
            elif method == "resources/list":
                defs = get_resource_definitions()
                return self._jsonrpc_success(
                    msg_id,
                    {
                        "resources": defs["resources"],
                        "resourceTemplates": defs.get("resourceTemplates", []),
                    },
                )

            elif method == "resources/read":
                uri = params.get("uri", "")
                result = read_resource(self.storage, uri)
                return self._jsonrpc_success(msg_id, result)

            elif method == "resources/templates/list":
                defs = get_resource_definitions()
                return self._jsonrpc_success(msg_id, {"resourceTemplates": defs.get("resourceTemplates", [])})

            # ---------------- PROMPTS ----------------
            elif method == "prompts/list":
                prompts = get_prompt_definitions()
                return self._jsonrpc_success(msg_id, {"prompts": prompts})

            elif method == "prompts/get":
                prompt_name = params.get("name", "")
                args = params.get("arguments", {}) or {}
                result = render_prompt(self.storage, prompt_name, args)
                return self._jsonrpc_success(msg_id, result)

            else:
                return self._jsonrpc_error(msg_id, -32601, f"Метод '{method}' не найден на сервере Litera MCP")

        except StorageError as se:
            return self._jsonrpc_error(msg_id, -32602, str(se))
        except Exception as e:
            logger.exception(f"Unhandled exception while processing method {method}")
            return self._jsonrpc_error(msg_id, -32603, f"Внутренняя ошибка сервера: {str(e)}")

    def _jsonrpc_success(self, msg_id: Any, result: Any) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    def _jsonrpc_error(self, msg_id: Any, code: int, message: str) -> Dict[str, Any]:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}

    def run_stdio(self) -> None:
        logger.info(f"Starting Litera MCP Server v{SERVER_VERSION} on stdio...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
            except json.JSONDecodeError as err:
                err_resp = self._jsonrpc_error(None, -32700, f"Parse error: {str(err)}")
                sys.stdout.write(json.dumps(err_resp, ensure_ascii=False) + "\n")
                sys.stdout.flush()
                continue

            response = self.handle_request(msg)
            if response is not None:
                sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
                sys.stdout.flush()


def main() -> None:
    parser = argparse.ArgumentParser(description="Litera Model Context Protocol (MCP) Server")
    parser.add_argument("--db-path", default=":memory:", help="SQLite database path (default: in-memory)")
    args = parser.parse_args()

    server = McpServer(db_path=args.db_path)
    server.run_stdio()


if __name__ == "__main__":
    main()
