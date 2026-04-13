from __future__ import annotations

import io
import json
import unittest

from scripts.mcp_stdio_proxy import InterceptPolicy, MCPMessage, MCPWireCodec, normalize_command


def frame(payload: bytes) -> bytes:
    return f"Content-Length: {len(payload)}\r\n\r\n".encode("utf-8") + payload


class FlushBytesIO(io.BytesIO):
    def flush(self) -> None:
        return None


class ProxyTests(unittest.TestCase):
    def test_wire_codec_reads_message(self) -> None:
        body = b'{"jsonrpc":"2.0","id":1,"method":"ping"}'
        codec = MCPWireCodec(io.BytesIO(frame(body)))

        message = codec.read_message()

        self.assertIsNotNone(message)
        assert message is not None
        self.assertEqual(message.body, body)

    def test_wire_codec_writes_message(self) -> None:
        output = FlushBytesIO()
        codec = MCPWireCodec(output)

        codec.write_message(MCPMessage(b'{"ok":true}'))

        self.assertEqual(output.getvalue(), frame(b'{"ok":true}'))

    def test_intercept_policy_handles_resources_list(self) -> None:
        policy = InterceptPolicy()

        reply = policy.build_reply({"jsonrpc": "2.0", "id": 9, "method": "resources/list"})

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertEqual(json.loads(reply.body.decode("utf-8")), {"jsonrpc": "2.0", "id": 9, "result": {"resources": []}})

    def test_intercept_policy_handles_templates_list(self) -> None:
        policy = InterceptPolicy()

        reply = policy.build_reply({"jsonrpc": "2.0", "id": "abc", "method": "resources/templates"})

        self.assertIsNotNone(reply)
        assert reply is not None
        self.assertEqual(
            json.loads(reply.body.decode("utf-8")),
            {"jsonrpc": "2.0", "id": "abc", "result": {"resourceTemplates": []}},
        )

    def test_intercept_policy_leaves_other_messages_alone(self) -> None:
        policy = InterceptPolicy()

        reply = policy.build_reply({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})

        self.assertIsNone(reply)

    def test_normalize_command_strips_optional_separator(self) -> None:
        self.assertEqual(normalize_command(["--", "python", "server.py"]), ["python", "server.py"])
        self.assertEqual(normalize_command(["python", "server.py"]), ["python", "server.py"])


if __name__ == "__main__":
    unittest.main()
