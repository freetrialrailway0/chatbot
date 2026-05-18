"""
greenapi_client.py — Thin wrapper around the Green API HTTP REST API.

Green API docs: https://green-api.com/en/docs/
"""
import os
import requests
from tracer import trace

GREENAPI_ID_INSTANCE   = os.environ["GREENAPI_ID_INSTANCE"]
GREENAPI_API_TOKEN     = os.environ["GREENAPI_API_TOKEN"]
_BASE = f"https://api.green-api.com/waInstance{GREENAPI_ID_INSTANCE}"


@trace
def send_message(to: str, body: str) -> dict:
    """
    Send a WhatsApp text message via Green API.

    :param to:   Phone number in international format, e.g. '628572251xxxx'
                 (no '+', no 'whatsapp:' prefix).
    :param body: Message text.
    :returns:    JSON response dict from Green API.
    """
    url  = f"{_BASE}/sendMessage/{GREENAPI_API_TOKEN}"
    payload = {
        "chatId": f"{to}@c.us",
        "message": body,
    }
    resp = requests.post(url, json=payload, timeout=15)
    resp.raise_for_status()
    return resp.json()


def parse_incoming(data: dict) -> tuple[str, str]:
    """
    Extract (sender_phone, text) from a Green API webhook notification.

    Green API sends a JSON body with a 'body' key containing the notification.
    Supports:
      - textMessage
      - extendedTextMessage (links / quoted messages)

    Returns (sender, text). sender is a bare phone number like '6285722516521'.
    """
    sender = ""
    text   = ""

    try:
        # Green API sends senderData and messageData at the TOP LEVEL of the JSON body
        sender_data  = data.get("senderData", {})
        sender       = sender_data.get("sender", "").replace("@c.us", "")
        msg_data     = data.get("messageData", {})
        type_message = msg_data.get("typeMessage", "")

        if type_message == "textMessage":
            text = msg_data.get("textMessageData", {}).get("textMessage", "")
        elif type_message == "extendedTextMessage":
            text = msg_data.get("extendedTextMessageData", {}).get("text", "")
    except Exception:
        pass

    return sender, text
