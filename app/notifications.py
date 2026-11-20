import json
import re
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import (
    WHATSAPP_ACCESS_TOKEN,
    WHATSAPP_API_VERSION,
    WHATSAPP_PHONE_NUMBER_ID,
    WHATSAPP_TEMPLATE_LANGUAGE,
    WHATSAPP_TEMPLATE_NAME,
)


def send_job_completed_whatsapp(
    phone: str,
    customer_name: str,
    job_label: str,
    job_id: int,
) -> tuple[str, str | None]:
    if not all((WHATSAPP_ACCESS_TOKEN, WHATSAPP_PHONE_NUMBER_ID, WHATSAPP_API_VERSION)):
        return "not_configured", "WhatsApp Cloud API credentials are not configured."

    recipient = re.sub(r"\D", "", phone)
    if not phone.strip().startswith("+") or len(recipient) < 8:
        return "failed", "Customer phone must include an international country code."

    payload = {
        "messaging_product": "whatsapp",
        "to": recipient,
        "type": "template",
        "template": {
            "name": WHATSAPP_TEMPLATE_NAME,
            "language": {"code": WHATSAPP_TEMPLATE_LANGUAGE},
            "components": [{
                "type": "body",
                "parameters": [
                    {"type": "text", "text": customer_name[:100]},
                    {"type": "text", "text": job_label[:100]},
                    {"type": "text", "text": str(job_id)},
                ],
            }],
        },
    }
    request = Request(
        f"https://graph.facebook.com/{WHATSAPP_API_VERSION}/"
        f"{WHATSAPP_PHONE_NUMBER_ID}/messages",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=10) as response:
            if 200 <= response.status < 300:
                return "sent", None
            return "failed", f"WhatsApp API returned HTTP {response.status}."
    except HTTPError as error:
        response_body = error.read(2048).decode("utf-8", errors="replace")
        return "failed", f"WhatsApp API returned HTTP {error.code}: {response_body}"
    except (TimeoutError, URLError, OSError) as error:
        return "failed", f"WhatsApp delivery failed: {error}"
