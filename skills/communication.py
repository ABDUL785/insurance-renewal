"""
Communication Skill
Sends email, SMS, and portal notifications to insured and agents
"""

import os
import io
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from typing import Optional, List


class CommunicationSkill:
    def __init__(self, snowflake_conn=None):
        self.conn = snowflake_conn
        self.sent_messages = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        pdf_base64: str = None,
        file_name: str = None,
        cc: List[str] = None
    ) -> dict:
        """
        Send email notification with optional PDF attachment
        """
        smtp_host = os.getenv("SMTP_HOST", "")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        smtp_from = os.getenv("SMTP_FROM", "")

        if not all([smtp_host, smtp_user, smtp_password, smtp_from]):
            message_id = f"EML-{len(self.sent_messages) + 1:06d}"
            self.sent_messages.append({
                "message_id": message_id,
                "channel": "EMAIL",
                "recipient": to_email,
                "subject": subject,
                "status": "SIMULATED"
            })
            return {
                "status": "success",
                "data": {
                    "message_id": message_id,
                    "channel": "EMAIL",
                    "recipient": to_email,
                    "status": "SIMULATED",
                    "note": "SMTP not configured - simulated send"
                }
            }

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject

            if cc:
                msg['Cc'] = ', '.join(cc)

            msg.attach(MIMEText(body, 'plain'))

            if pdf_base64 and file_name:
                pdf_bytes = base64.b64decode(pdf_base64)
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(pdf_bytes)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename={file_name}')
                msg.attach(part)

            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                recipients = [to_email] + (cc or [])
                server.sendmail(smtp_from, recipients, msg.as_string())

            message_id = f"EML-{len(self.sent_messages) + 1:06d}"
            self.sent_messages.append({
                "message_id": message_id,
                "channel": "EMAIL",
                "recipient": to_email,
                "subject": subject,
                "status": "SENT"
            })

            return {
                "status": "success",
                "data": {
                    "message_id": message_id,
                    "channel": "EMAIL",
                    "recipient": to_email,
                    "status": "DELIVERED"
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

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
                "status": "SIMULATED"
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
                "status": "POSTED"
            }
        }

    def create_email_notification_record(
        self,
        policy_number: str,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        body: str,
        attachment_path: str = None,
        attachment_filename: str = None
    ) -> dict:
        """
        Create email notification record in Snowflake for failed sends
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        try:
            notification_id = f"NOTIF-{policy_number}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            insert_query = """
            INSERT INTO INSURANCE_DW.PRODUCTION.EMAIL_NOTIFICATIONS
            (NOTIFICATION_ID, POLICY_NUMBER, RECIPIENT_EMAIL, RECIPIENT_NAME, SUBJECT, BODY, ATTACHMENT_PATH, ATTACHMENT_FILENAME, STATUS)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor = self.conn.cursor()
            cursor.execute(insert_query, (
                notification_id, policy_number, recipient_email, recipient_name,
                subject, body, attachment_path, attachment_filename, "PENDING"
            ))
            self.conn.commit()
            cursor.close()

            return {
                "status": "success",
                "data": {
                    "notification_id": notification_id,
                    "recipient_email": recipient_email,
                    "status": "PENDING"
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_renewal_notification(
        self,
        policy_holder_name: str,
        email: str,
        phone: str,
        preferred_contact: str,
        policy_number: str,
        renewal_premium: float,
        expiration_date: str,
        agent_name: str = None,
        pdf_base64: str = None,
        file_name: str = None
    ) -> dict:
        """
        Send comprehensive renewal notification via preferred channel
        """
        results = {
            "policy_number": policy_number,
            "notifications_sent": []
        }

        email_subject = f"Your Policy {policy_number} Renewal Quote is Ready"
        email_body = f"""Dear {policy_holder_name},

Your policy {policy_number} is up for renewal on {expiration_date}.

Renewal Premium: ${renewal_premium:,.2f}

Please review your renewal quote and contact us if you have any questions.

Thank you for your continued business.

Best regards,
{agent_name or 'Your Insurance Team'}
"""
        email_result = self.send_email(
            to_email=email,
            subject=email_subject,
            body=email_body,
            pdf_base64=pdf_base64,
            file_name=file_name
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

        if preferred_contact == "PORTAL":
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