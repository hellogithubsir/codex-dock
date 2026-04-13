from __future__ import annotations

import json
import subprocess
import sys
import threading
from dataclasses import dataclass, field
from typing import BinaryIO, Iterable, Mapping


INTERCEPT_METHODS = frozenset({"resources/list", "resources/templates"})


@dataclass(frozen=True)
class MCPMessage:
    body: bytes

    @classmethod
    def from_json(cls, payload: Mapping[str, object]) -> "MCPMessage":
        return cls(json.dumps(payload).encode("utf-8"))

    def decode_json(self) -> dict[str, object] | None:
        try:
            value = json.loads(self.body.decode("utf-8"))
        except Exception:
            return None
        return value if isinstance(value, dict) else None


@dataclass
class MCPWireCodec:
    stream: BinaryIO

    def read_message(self) -> MCPMessage | None:
        headers = self._read_headers()
        if headers is None:
            return None
        length = self._content_length(headers)
        if length is None:
            return None
        body = self.stream.read(length)
        if not body:
            return None
        return MCPMessage(body)

    def write_message(self, message: MCPMessage) -> None:
        self.stream.write(f"Content-Length: {len(message.body)}\r\n\r\n".encode("utf-8"))
        self.stream.write(message.body)
        self.stream.flush()

    def _read_headers(self) -> dict[bytes, bytes] | None:
        headers: dict[bytes, bytes] = {}
        while True:
            line = self.stream.readline()
            if not line:
                return None
            if line in (b"\r\n", b"\n"):
                return headers
            if b":" not in line:
                continue
            key, value = line.split(b":", 1)
            headers[key.strip().lower()] = value.strip()

    @staticmethod
    def _content_length(headers: Mapping[bytes, bytes]) -> int | None:
        value = headers.get(b"content-length")
        if not value:
            return None
        try:
            return int(value)
        except Exception:
            return None


@dataclass(frozen=True)
class InterceptPolicy:
    methods: frozenset[str] = field(default_factory=lambda: INTERCEPT_METHODS)

    def build_reply(self, payload: Mapping[str, object]) -> MCPMessage | None:
        method = payload.get("method")
        message_id = payload.get("id")
        if method not in self.methods or message_id is None:
            return None
        if method == "resources/templates":
            result: dict[str, object] = {"resourceTemplates": []}
        else:
            result = {"resources": []}
        return MCPMessage.from_json({"jsonrpc": "2.0", "id": message_id, "result": result})


@dataclass
class ServerProcess:
    command: list[str]
    process: subprocess.Popen[bytes] | None = None
    stdin_codec: MCPWireCodec | None = None
    stdout_codec: MCPWireCodec | None = None

    def start(self) -> None:
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,
        )
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        self.stdin_codec = MCPWireCodec(self.process.stdin)
        self.stdout_codec = MCPWireCodec(self.process.stdout)

    def stop(self) -> None:
        if self.process is None:
            return
        try:
            self.process.terminate()
        except Exception:
            pass


@dataclass
class MCPProxyBridge:
    client_input: MCPWireCodec
    client_output: MCPWireCodec
    server: ServerProcess
    intercept_policy: InterceptPolicy = field(default_factory=InterceptPolicy)

    def serve(self) -> None:
        self.server.start()
        relay_thread = threading.Thread(target=self._relay_server_output, daemon=True)
        relay_thread.start()

        try:
            while True:
                incoming = self.client_input.read_message()
                if incoming is None:
                    return
                payload = incoming.decode_json()
                if payload is None:
                    self._write_to_server(incoming)
                    continue
                intercepted = self.intercept_policy.build_reply(payload)
                if intercepted is not None:
                    self.client_output.write_message(intercepted)
                    continue
                self._write_to_server(incoming)
        finally:
            self.server.stop()

    def _relay_server_output(self) -> None:
        assert self.server.stdout_codec is not None
        while True:
            outgoing = self.server.stdout_codec.read_message()
            if outgoing is None:
                return
            self.client_output.write_message(outgoing)

    def _write_to_server(self, message: MCPMessage) -> None:
        assert self.server.stdin_codec is not None
        self.server.stdin_codec.write_message(message)


def normalize_command(args: Iterable[str]) -> list[str]:
    items = list(args)
    if items[:1] == ["--"]:
        items = items[1:]
    return items


def run_proxy(command: list[str]) -> None:
    bridge = MCPProxyBridge(
        client_input=MCPWireCodec(sys.stdin.buffer),
        client_output=MCPWireCodec(sys.stdout.buffer),
        server=ServerProcess(command=command),
    )
    bridge.serve()


def main() -> None:
    command = normalize_command(sys.argv[1:])
    if not command:
        sys.stderr.write("Usage: mcp_stdio_proxy.py -- <server> [args...]\n")
        sys.exit(2)
    run_proxy(command)


if __name__ == "__main__":
    main()
