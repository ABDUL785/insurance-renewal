"""
Communication MCP Server for Insurance Renewal Agent
Handles email, SMS, and portal notifications
"""

from datetime import datetime
from typing import Optional


class CommunicationMCPServer:
    def __init__(self):
        self.sent_messages = []

    def send_email(
        self,
        recipient: str,
        subject: str,
        body: str,
        template_id: str = None,
        policy_number: str = None,
        cc: list = None
    ) -> dict:
        """
        Send email notification to policyholder or agent
        """
        message_id = f"EML-{len(self.sent_messages) + 1:06d}"

        email_record = {
            "message_id": message_id,
            "channel": "EMAIL",
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "template_id": template_id,
            "policy_number": policy_number,
            "cc": cc or [],
            "status": "SENT",
            "sent_at": datetime.now().isoformat()
        }

        self.sent_messages.append(email_record)

        return {
            "status": "success",
            "data": {
                "message_id": message_id,
                "channel": "EMAIL",
                "recipient": recipient,
                "subject": subject,
                "status": "DELIVERED",
                "sent_at": email_record["sent_at"]
            }
        }

    def send_sms(
        self,
        phone_number: str,
        message: str,
        policy_number: str = None
    ) -> dict:
        """
        Send SMS notification
        """
        message_id = f"SMS-{len(self.sent_messages) + 1:06d}"

        sms_record = {
            "message_id": message_id,
            "channel": "SMS",
            "recipient": phone_number,
            "message": message,
            "policy_number": policy_number,
            "status": "SENT",
            "sent_at": datetime.now().isoformat()
        }

        self.sent_messages.append(sms_record)

        return {
            "status": "success",
            "data": {
                "message_id": message_id,
                "channel": "SMS",
                "recipient": phone_number,
                "message_length": len(message),
                "status": "DELIVERED",
                "sent_at": sms_record["sent_at"]
            }
        }

    def update_portal(
        self,
        contact_id: str,
        message_type: str,
        content: str,
        policy_number: str = None
    ) -> dict:
        """
        Update customer portal with notification
        """
        notification_id = f"PRT-{len(self.sent_messages) + 1:06d}"

        portal_record = {
            "notification_id": notification_id,
            "channel": "PORTAL",
            "contact_id": contact_id,
            "message_type": message_type,
            "content": content,
            "policy_number": policy_number,
            "status": "POSTED",
            "posted_at": datetime.now().isoformat()
        }

        self.sent_messages.append(portal_record)

        return {
            "status": "success",
            "data": {
                "notification_id": notification_id,
                "contact_id": contact_id,
                "message_type": message_type,
                "status": "POSTED",
                "posted_at": portal_record["posted_at"]
            }
        }

    def send_renewal_notification(
        self,
        policy_holder_name: str,
        email: str,
        phone: str,
        preferred_contact: str,
        policy_number: str,
        renewal_premium: float,
        expiration_date: str,
        agent_name: str = None
    ) -> dict:
        """
        Send comprehensive renewal notification via preferred channel
        """
        results = {
            "policy_number": policy_number,
            "notifications_sent": []
        }

        email_subject = f"Your Policy {policy_number} Renewal Quote is Ready"
        email_body = f"""
Dear {policy_holder_name},

Your policy {policy_number} is up for renewal on {expiration_date}.

Renewal Premium: ${renewal_premium:,.2f}

Please review your renewal quote and contact us if you have any questions.

Thank you for your continued business.

Best regards,
{agent_name or 'Your Insurance Team'}
"""
        email_result = self.send_email(
            recipient=email,
            subject=email_subject,
            body=email_body,
            template_id="RENEWAL_NOTIFICATION",
            policy_number=policy_number
        )
        results["notifications_sent"].append(email_result["data"])

        if preferred_contact == "SMS" and phone:
            sms_message = f"Insurance: Your policy {policy_number} renewal quote of ${renewal_premium:,.2f} is ready. Check your email or portal for details."
            sms_result = self.send_sms(
                phone_number=phone,
                message=sms_message,
                policy_number=policy_number
            )
            results["notifications_sent"].append(sms_result["data"])

        portal_result = self.update_portal(
            contact_id=email,
            message_type="RENEWAL_QUOTE_READY",
            content=f"Renewal quote for policy {policy_number} is available. Premium: ${renewal_premium:,.2f}",
            policy_number=policy_number
        )
        results["notifications_sent"].append(portal_result["data"])

        return {"status": "success", "data": results}

    def get_message_history(
        self,
        policy_number: str = None,
        contact_id: str = None,
        limit: int = 50
    ) -> dict:
        """
        Retrieve message history for audit trail
        """
        filtered = self.sent_messages
        if policy_number:
            filtered = [m for m in filtered if m.get("policy_number") == policy_number]
        if contact_id:
            filtered = [m for m in filtered if m.get("recipient") == contact_id or m.get("contact_id") == contact_id]

        return {
            "status": "success",
            "data": {
                "total_messages": len(filtered),
                "messages": filtered[:limit]
            }
        }


TOOLS = [
    {
        "name": "send_email",
        "description": "Send email notification",
        "input_schema": {
            "type": "object",
            "properties": {
                "recipient": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "template_id": {"type": "string"},
                "policy_number": {"type": "string"},
                "cc": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["recipient", "subject", "body"]
        }
    },
    {
        "name": "send_sms",
        "description": "Send SMS notification",
        "input_schema": {
            "type": "object",
            "properties": {
                "phone_number": {"type": "string"},
                "message": {"type": "string"},
                "policy_number": {"type": "string"}
            },
            "required": ["phone_number", "message"]
        }
    },
    {
        "name": "update_portal",
        "description": "Post notification to customer portal",
        "input_schema": {
            "type": "object",
            "properties": {
                "contact_id": {"type": "string"},
                "message_type": {"type": "string"},
                "content": {"type": "string"},
                "policy_number": {"type": "string"}
            },
            "required": ["contact_id", "message_type", "content"]
        }
    },
    {
        "name": "send_renewal_notification",
        "description": "Send comprehensive renewal notification via all preferred channels",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_holder_name": {"type": "string"},
                "email": {"type": "string"},
                "phone": {"type": "string"},
                "preferred_contact": {"type": "string", "enum": ["EMAIL", "SMS", "PORTAL"]},
                "policy_number": {"type": "string"},
                "renewal_premium": {"type": "number"},
                "expiration_date": {"type": "string"},
                "agent_name": {"type": "string"}
            },
            "required": ["policy_holder_name", "email", "preferred_contact", "policy_number", "renewal_premium", "expiration_date"]
        }
    },
    {
        "name": "get_message_history",
        "description": "Retrieve message history for audit trail",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "contact_id": {"type": "string"},
                "limit": {"type": "integer", "default": 50}
            }
        }
    }
]


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    server = CommunicationMCPServer()
    if hasattr(server, tool_name):
        return getattr(server, tool_name)(**arguments)
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}