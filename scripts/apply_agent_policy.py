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
        "GET /v1/billing/balance (previous policy)",
        "Phone numbers are 2.00 USD one-time.",
        "Phone numbers are 2.00 USD per month.",
    ),
    (
        "GET /v1/billing/balance (billed per second)",
        "Calls are 0.10 USD per minute, billed per second.",
        "Calls are 0.10 USD per minute in both directions. A 0-second call is free. A connected call has a one-minute minimum, then the actual duration rounded up to the cent.",
    ),
    (
        "POST /v1/numbers cost (previous policy)",
        "Costs `$2.00` one-time per number.",
        "Costs $2.00/month per number.",
    ),
    (
        "POST /v1/numbers cost",
        "Costs $2.00 per number.",
        "Costs $2.00/month per number.",
    ),
    (
        "POST /v1/numbers capability",
        "the agent can make outbound calls and receive inbound calls on this number.",
        "the agent can make outbound calls, receive inbound calls, and receive inbound SMS on this number. Outbound SMS is not enabled.",
    ),
    (
        "GET /v1/billing/balance",
        "Get your AI telephony account balance and rate card.\\n\\nReturns the current balance, currency, billing rates for calls,\\nphone numbers, and inbound SMS, plus what the balance can cover.\\nUse this to check affordability before paid telephony operations.",
        "Get your AI telephony account balance and rate card.\\n\\nReturns the current balance and currency. Calls are 0.10 USD per minute in both directions. A 0-second call is free. A connected call has a one-minute minimum, then the actual duration rounded up to the cent. Phone numbers are 2.00 USD per month. The rate card also includes inbound SMS.\\nUse this to check affordability before paid telephony operations.",
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
    (
        "GET /v1/calls/{id}/transcript roles",
        'with each turn labeled by role (\\"human\\" for the caller, \\"assistant\\"\\nfor the AI agent).',
        'with each turn labeled by role (\\"human\\" for the caller, \\"agent\\"\\nfor the AI agent). The call.utterance conversation field uses user and assistant instead.',
    ),
    (
        "POST /v1/calls/{id}/context disposition",
        "Do your work, then\\nPOST facts for the hosted voice to phrase in its own words. Send ``disposition: progress``\\nas the work advances; the turn stays open. ``done``, ``failed``, or\\n``facts`` settles it. The hosted voice keeps the facts for the rest of the call.\\nIt does not read your text aloud. You receive this request only for something\\nthe hosted voice does not know. Poll ``GET /v1/calls/{call_id}`` for updates.",
        "Do your work, then\\nPOST short facts, not a script. Include ``disposition``.\\n``progress`` adds a note and keeps the caller on hold with canned lines; the text is not spoken, and the turn stays open.\\n``done`` (the default), ``facts``, and ``failed`` close the turn. The hosted voice rephrases the facts in one or two sentences. It does not read your text aloud.\\n``noop`` closes the turn with no facts.\\nYou receive this request only for something\\nthe hosted voice does not know. Poll ``GET /v1/calls/{call_id}`` for updates.",
    ),
    (
        "POST /v1/calls/{id}/context returns",
        'delivered=true, status=\\"live\\"      — voice agent will speak it now\\n    delivered=true, status=\\"duplicate\\" — identical retry already accepted\\n    HTTP 409                            — turn is stale/cancelled\\n    HTTP 410                            — **call has ended.** STOP working\\n      on this request and abandon any in-flight lookup. No further context\\n      will be spoken.',
        'delivered=true, status=\\"live\\"      — accepted for this turn\\n    delivered=true, status=\\"duplicate\\" — identical retry already accepted\\n    HTTP 409                            — turn is stale/cancelled\\n    HTTP 410                            — **call has ended.** STOP working\\n      on this request and abandon any in-flight lookup.',
    ),
    (
        "POST /v1/webhooks event types",
        "The configured URL receives ALL of that agent's event types — call lifecycle\\n(`call.received`, `call.completed`, `call.failed`), SMS (`sms.received`),\\nand future events — as signed JSON POSTs.",
        "The configured URL receives ALL of that agent's event types — `call.received` (inbound answer), `call.utterance`, `call.completed`, `call.owner_task`, `call.failed`, `call.busy`, `call.no-answer`, `call.canceled`, `sms.received`, and `webhook.test` — as signed JSON POSTs.",
    ),
]


def drop_openapi_path(text: str, path: str) -> str:
    """Remove one path object. No-op when the path is absent."""
    needle = f'"{path}":'
    start = 0
    idx = -1
    line_start = 0
    while True:
        found = text.find(needle, start)
        if found < 0:
            return text
        line_start = text.rfind("\n", 0, found) + 1
        prefix = text[line_start:found]
        if prefix.strip() == "" and prefix == "    ":
            idx = found
            break
        start = found + len(needle)
    if idx < 0:
        return text
    brace = text.find("{", idx)
    if brace < 0:
        raise SystemExit(f"{path}: missing object")
    depth = 0
    in_str = False
    esc = False
    end = None
    for i in range(brace, len(text)):
        ch = text[i]
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    if end is None:
        raise SystemExit(f"{path}: unterminated object")
    j = end
    while j < len(text) and text[j] in " \t":
        j += 1
    if j < len(text) and text[j] == ",":
        j += 1
        if j < len(text) and text[j] == "\n":
            j += 1
        return text[:line_start] + text[j:]
    comma = text.rfind(",", 0, line_start)
    if comma < 0:
        raise SystemExit(f"{path}: could not find a comma around the path")
    return text[:comma] + text[end:]


def replace_once(text: str, old: str, new: str, label: str, *, required: bool) -> str:
    if old in text:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{label}: expected 1 occurrence, found {count}")
        return text.replace(old, new, 1)
    if new in text or not required:
        return text
    raise SystemExit(f"{label}: neither the upstream wording nor the policy text was found")


def main() -> None:
    text = drop_openapi_path(SPEC.read_text(), "/v1/numbers/attach")
    optional = {
        "GET /v1/billing/balance (previous policy)",
        "GET /v1/billing/balance (billed per second)",
        "POST /v1/numbers cost (previous policy)",
    }
    for label, old, new in REPLACEMENTS:
        text = replace_once(text, old, new, label, required=label not in optional)

    forbidden = [
        "Send an outbound SMS",
        "calls and SMS autonomously",
        "Bearer sk_live_",
        "API key (sk_live_",
        "USD one-time",
        "one-time per number",
        "billed per second",
        '"/v1/numbers/attach"',
        "voice agent will speak it now",
        '"assistant"\\nfor the AI agent',
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
