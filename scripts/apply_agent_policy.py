#!/usr/bin/env python3
"""Reapply production agent-skill policy to the vendored OpenAPI spec.

``openapi.json`` is refreshed from agentline-sdks. That spec still documents
``POST /v1/messages`` as a send operation and shows ``sk_live_...`` keys.
The generated API reference is agent-facing, so this script stamps the
production skill facts onto those fields after each sync.

The replacements are textual and idempotent: if the upstream wording is
already the policy text, the file is left unchanged. A missing target fails
the sync instead of publishing the old send-SMS copy.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "openapi.json"

# (label, old, new). ``old`` is the upstream wording. ``new`` is the skill policy.
REPLACEMENTS: list[tuple[str, str, str]] = [
    (
        "info.description",
        "AgentLine gives every AI agent a real phone number, a human-like voice, and the ability to make and receive calls and SMS autonomously. This SDK covers the core developer surface: agents, numbers, calls, messages, events, webhooks, billing, and voice.",
        "AgentLine gives every AI agent a real US phone number and a human-like voice. Agents can make and receive calls. Inbound SMS can be read. Outbound SMS is not enabled for agents and is not exposed on MCP. This spec covers the core developer surface: agents, numbers, calls, messages, events, webhooks, billing, and voice.",
    ),
    (
        "info.summary",
        "Phone numbers, voice, and SMS for AI agents.",
        "US phone numbers and voice for AI agents. Inbound SMS can be read.",
    ),
    (
        "POST /v1/messages",
        '"summary": "Send Message",\n        "description": "Send an outbound SMS message from an AI agent\'s phone number."',
        '"summary": "Outbound SMS is not enabled",\n        "description": "Outbound SMS is not enabled for agents.\\n\\nThis operation is not exposed on the MCP server. `send_sms` and `send_message` are not MCP tools. Do not send SMS or MMS.\\n\\nInbound SMS is listed with GET /v1/messages (`list_messages`) and delivered as `sms.received` events."',
    ),
    (
        "GET /v1/messages",
        "List SMS messages sent and received by your AI agents.\\n\\nReturns message history with optional filters by AI agent or\\nconversation. Each entry includes direction (inbound/outbound),\\nphone numbers, message body, and delivery status.",
        "List SMS messages for your AI agents.\\n\\nReturns inbound texts and stored message history. Outbound SMS is not enabled for agents. Optional filters: AI agent or conversation. Each entry includes direction (inbound/outbound), phone numbers, message body, and delivery status.",
    ),
    (
        "GET /v1/messages/conversations",
        "List all SMS conversations for your AI agents.\\n\\nReturns conversation threads, optionally filtered by AI agent.\\nEach conversation represents an ongoing SMS exchange between\\nan AI agent's phone number and an external contact.",
        "List stored SMS conversation threads for your AI agents.\\n\\nOutbound SMS is not enabled for agents. Threads can be filtered by AI agent and include inbound messages on the agent's phone number.",
    ),
    (
        "MessageSend",
        '''      "MessageSend": {
        "properties": {
          "agent_id": {
            "type": "string",
            "title": "Agent Id",
            "description": "ID of the AI agent sending the SMS (e.g. 'agt_abc123')"
          },
          "to_number": {
            "type": "string",
            "title": "To Number",
            "description": "Destination phone number in E.164 format (e.g. '+12125551234')"
          },
          "body": {
            "type": "string",
            "title": "Body",
            "description": "SMS message text content"
          },
          "media_url": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Media Url",
            "description": "URL of media to attach (MMS)"
          },
          "from_number_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "From Number Id",
            "description": "Specific phone number ID to send from; defaults to the agent's assigned number"
          }
        },''',
        '''      "MessageSend": {
        "description": "Request body for POST /v1/messages. Outbound SMS is not enabled for agents and is not exposed on MCP.",
        "properties": {
          "agent_id": {
            "type": "string",
            "title": "Agent Id",
            "description": "Agent id. Outbound SMS is not enabled for agents."
          },
          "to_number": {
            "type": "string",
            "title": "To Number",
            "description": "E.164 destination. Outbound SMS is not enabled for agents."
          },
          "body": {
            "type": "string",
            "title": "Body",
            "description": "Message text. Outbound SMS is not enabled for agents."
          },
          "media_url": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "Media Url",
            "description": "Media URL. Outbound MMS is not enabled for agents."
          },
          "from_number_id": {
            "anyOf": [
              {
                "type": "string"
              },
              {
                "type": "null"
              }
            ],
            "title": "From Number Id",
            "description": "Phone number id. Outbound SMS is not enabled for agents."
          }
        },''',
    ),
    (
        "POST /v1/numbers cost",
        "Costs $2.00 per number.",
        "Costs $2.00 one-time per number.",
    ),
    (
        "POST /v1/numbers capability",
        "the agent can make outbound calls and receive inbound calls on this number.",
        "the agent can make outbound calls, receive inbound calls, and receive inbound SMS on this number. Outbound SMS is not enabled.",
    ),
    (
        "GET /v1/billing/balance",
        "billing rates for calls,\\nphone numbers, and inbound SMS",
        "billing rates for calls ($0.10/min, billed per second),\\nphone numbers ($2.00 one-time), and inbound SMS",
    ),
    (
        "security.description",
        "AgentLine API key. Get one via the email OTP flow (POST /v1/auth/otp then POST /v1/auth/verify). Pass as: Authorization: Bearer sk_live_...",
        "AgentLine API key. Get one via the email OTP flow (POST /v1/auth/otp then POST /v1/auth/verify). Pass as: Authorization: Bearer al_live_... (legacy sk_live_... still works).",
    ),
    (
        "security.bearerFormat",
        '"bearerFormat": "API key (sk_live_...)"',
        '"bearerFormat": "API key (al_live_...)"',
    ),
]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if old in text:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
        return text.replace(old, new, 1)
    if new in text:
        return text
    raise SystemExit(f"{label}: neither the upstream wording nor the policy text was found")


def main() -> None:
    text = SPEC.read_text()
    for label, old, new in REPLACEMENTS:
        text = replace_once(text, old, new, label)

    forbidden = [
        "Send an outbound SMS",
        "calls and SMS autonomously",
        "Bearer sk_live_",
        "API key (sk_live_",
        "$2/month",
        "$2.00/month",
        "$0.08",
        "$0.02",
        "Canada",
        "Canadian",
    ]
    for phrase in forbidden:
        if phrase in text:
            raise SystemExit(f"openapi.json still contains {phrase!r}")

    if text != SPEC.read_text():
        SPEC.write_text(text)
        print("Applied agent skill policy to openapi.json")
    else:
        print("openapi.json already matches the agent skill policy")


if __name__ == "__main__":
    sys.exit(main())
