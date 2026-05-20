"""
Storage MCP Server - Snowflake Document Storage and Email Notifications
Handles storing PDFs in Snowflake stages and managing email notifications
"""

import os
import io
import uuid
import base64
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import snowflake.connector
from snowflake.connector import DictCursor


class StorageMCPServer:
    def __init__(self):
        self.conn = None
        self._connect()

    def _connect(self):
        import os
        try:
            self.conn = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
                database=os.getenv("SNOWFLAKE_DATABASE", "INSURANCE_DW"),
                schema=os.getenv("SNOWFLAKE_SCHEMA", "PRODUCTION"),
                role=os.getenv("SNOWFLAKE_ROLE")
            )
            print("  [STORAGE] Connected to Snowflake")
        except Exception as e:
            print(f"  [STORAGE] Connection failed: {e}")
            self.conn = None
            raise ConnectionError(f"Failed to connect to Snowflake: {e}")

    def execute(self, query, params=None):
        if not self.conn:
            return None
        try:
            cursor = self.conn.cursor(DictCursor)
            cursor.execute(query, params or ())
            self.conn.commit()
            return cursor.fetchall()
        except Exception as e:
            print(f"  [STORAGE] Query error: {e}")
            self.conn.rollback()
            return None

    def upload_pdf_to_stage(self, pdf_base64: str, policy_number: str, document_type: str = "renewal_quote") -> dict:
        """
        Upload PDF to Snowflake stage and record metadata
        Returns storage path and document ID
        """
        try:
            pdf_bytes = base64.b64decode(pdf_base64)
            file_size = len(pdf_bytes)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            document_id = f"DOC-{policy_number}-{timestamp[:8]}"
            file_name = f"Renewal_Quote_{policy_number}_{timestamp}.pdf"
            stage_path = f"@DOCUMENTS_STAGE/{policy_number}/{file_name}"

            output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output", "documents")
            os.makedirs(output_dir, exist_ok=True)
            local_file_path = os.path.join(output_dir, file_name)

            with open(local_file_path, "wb") as f:
                f.write(pdf_bytes)

            try:
                cursor = self.conn.cursor()
                put_query = f"PUT 'file://{local_file_path.replace(os.sep, '/')}' {stage_path}"
                cursor.execute(put_query)
                cursor.close()
                storage_location = "SNOWFLAKE_STAGE"
                actual_path = stage_path
            except Exception as e:
                print(f"  [STORAGE] Stage upload failed: {e}")
                storage_location = "LOCAL"
                actual_path = local_file_path

            insert_query = """
            INSERT INTO INSURANCE_DW.PRODUCTION.RENEWAL_DOCUMENTS
            (DOCUMENT_ID, POLICY_NUMBER, DOCUMENT_TYPE, FILE_NAME, STAGE_PATH, FILE_SIZE_BYTES, STORAGE_LOCATION)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            self.execute(insert_query, (document_id, policy_number, document_type, file_name, actual_path, file_size, storage_location))

            return {
                "status": "success",
                "data": {
                    "document_id": document_id,
                    "file_name": file_name,
                    "stage_path": actual_path,
                    "file_size_bytes": file_size,
                    "storage_location": storage_location
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_email(self, to_email: str, subject: str, body: str, pdf_base64: str = None, file_name: str = None) -> dict:
        """
        Send real email via SMTP with optional PDF attachment
        """
        smtp_host = os.getenv("SMTP_HOST", "")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER", "")
        smtp_password = os.getenv("SMTP_PASSWORD", "")
        smtp_from = os.getenv("SMTP_FROM", "")

        if not all([smtp_host, smtp_user, smtp_password, smtp_from]):
            return {"status": "error", "message": "SMTP not configured in .env"}

        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_from
            msg['To'] = to_email
            msg['Subject'] = subject
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
                server.sendmail(smtp_from, to_email, msg.as_string())

            return {
                "status": "success",
                "data": {
                    "recipient": to_email,
                    "subject": subject,
                    "status": "SENT"
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def create_email_notification(
        self,
        policy_number: str,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        body: str,
        attachment_path: str = None,
        attachment_filename: str = None,
        cc_emails: list = None
    ) -> dict:
        """
        Create email notification record in Snowflake
        """
        try:
            notification_id = f"NOTIF-{policy_number}-{datetime.now().strftime('%Y%m%d%H%M%S')}"

            cc_json = None
            if cc_emails:
                import json
                cc_json = json.dumps(cc_emails)

            insert_query = """
            INSERT INTO INSURANCE_DW.PRODUCTION.EMAIL_NOTIFICATIONS
            (NOTIFICATION_ID, POLICY_NUMBER, RECIPIENT_EMAIL, RECIPIENT_NAME, CC_EMAILS, SUBJECT, BODY, ATTACHMENT_PATH, ATTACHMENT_FILENAME, STATUS)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            self.execute(insert_query, (
                notification_id, policy_number, recipient_email, recipient_name,
                cc_json, subject, body, attachment_path, attachment_filename, "PENDING"
            ))

            return {
                "status": "success",
                "data": {
                    "notification_id": notification_id,
                    "recipient_email": recipient_email,
                    "subject": subject,
                    "attachment_path": attachment_path,
                    "status": "PENDING"
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def send_email_with_attachment(
        self,
        policy_number: str,
        recipient_email: str,
        recipient_name: str,
        subject: str,
        body: str,
        pdf_base64: str = None,
        cc_emails: list = None
    ) -> dict:
        """
        Complete workflow: Generate PDF, upload to Snowflake, create email notification
        """
        attachment_path = None
        attachment_filename = None

        if pdf_base64:
            upload_result = self.upload_pdf_to_stage(pdf_base64, policy_number)
            if upload_result.get("status") == "success":
                attachment_path = upload_result["data"]["stage_path"]
                attachment_filename = upload_result["data"]["file_name"]

        notification_result = self.create_email_notification(
            policy_number=policy_number,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            subject=subject,
            body=body,
            attachment_path=attachment_path,
            attachment_filename=attachment_filename,
            cc_emails=cc_emails
        )

        if notification_result.get("status") == "success":
            update_query = """
            UPDATE INSURANCE_DW.PRODUCTION.EMAIL_NOTIFICATIONS
            SET STATUS = 'SENT', SENT_AT = CURRENT_TIMESTAMP()
            WHERE NOTIFICATION_ID = %s
            """
            self.execute(update_query, (notification_result["data"]["notification_id"],))

        return notification_result

    def get_document_info(self, policy_number: str = None, document_id: str = None) -> dict:
        """
        Retrieve document metadata from Snowflake
        """
        if document_id:
            query = "SELECT * FROM INSURANCE_DW.PRODUCTION.RENEWAL_DOCUMENTS WHERE DOCUMENT_ID = %s"
            result = self.execute(query, (document_id,))
        elif policy_number:
            query = "SELECT * FROM INSURANCE_DW.PRODUCTION.RENEWAL_DOCUMENTS WHERE POLICY_NUMBER = %s ORDER BY GENERATED_AT DESC"
            result = self.execute(query, (policy_number,))
        else:
            return {"status": "error", "message": "Either document_id or policy_number required"}

        if result:
            return {"status": "success", "data": [dict(row) for row in result]}
        return {"status": "success", "data": []}

    def get_email_notifications(self, policy_number: str = None, status: str = None) -> dict:
        """
        Retrieve email notification records
        """
        query = "SELECT * FROM INSURANCE_DW.PRODUCTION.EMAIL_NOTIFICATIONS WHERE 1=1"
        params = []

        if policy_number:
            query += " AND POLICY_NUMBER = %s"
            params.append(policy_number)
        if status:
            query += " AND STATUS = %s"
            params.append(status)

        query += " ORDER BY CREATED_AT DESC"

        result = self.execute(query, tuple(params) if params else None)
        if result:
            return {"status": "success", "data": [dict(row) for row in result]}
        return {"status": "success", "data": []}

    def download_document_from_stage(self, document_id: str) -> dict:
        """
        Download PDF from Snowflake stage
        """
        query = "SELECT STAGE_PATH, FILE_NAME FROM INSURANCE_DW.PRODUCTION.RENEWAL_DOCUMENTS WHERE DOCUMENT_ID = %s"
        result = self.execute(query, (document_id,))

        if not result:
            return {"status": "error", "message": "Document not found"}

        stage_path = result[0]["STAGE_PATH"]
        file_name = result[0]["FILE_NAME"]

        cursor = self.conn.cursor()
        cursor.execute(f"GET {stage_path} file://{os.path.dirname(__file__)}/../temp_downloads/")
        cursor.close()

        return {
            "status": "success",
            "data": {
                "file_name": file_name,
                "download_path": f"temp_downloads/{file_name}"
            }
        }

    def close(self):
        if self.conn:
            self.conn.close()


TOOLS = [
    {
        "name": "upload_pdf_to_stage",
        "description": "Upload PDF document to Snowflake stage",
        "input_schema": {
            "type": "object",
            "properties": {
                "pdf_base64": {"type": "string"},
                "policy_number": {"type": "string"},
                "document_type": {"type": "string", "default": "renewal_quote"}
            },
            "required": ["pdf_base64", "policy_number"]
        }
    },
    {
        "name": "create_email_notification",
        "description": "Create email notification record in Snowflake",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "recipient_email": {"type": "string"},
                "recipient_name": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "attachment_path": {"type": "string"},
                "attachment_filename": {"type": "string"},
                "cc_emails": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["policy_number", "recipient_email", "recipient_name", "subject", "body"]
        }
    },
    {
        "name": "send_email_with_attachment",
        "description": "Complete workflow: upload PDF, create email notification with attachment",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "recipient_email": {"type": "string"},
                "recipient_name": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
                "pdf_base64": {"type": "string"},
                "cc_emails": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["policy_number", "recipient_email", "recipient_name", "subject", "body"]
        }
    },
    {
        "name": "get_document_info",
        "description": "Get document metadata from Snowflake",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "document_id": {"type": "string"}
            }
        }
    },
    {
        "name": "get_email_notifications",
        "description": "Get email notification records",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "status": {"type": "string"}
            }
        }
    }
]


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    server = StorageMCPServer()
    if hasattr(server, tool_name):
        return getattr(server, tool_name)(**arguments)
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}


if __name__ == "__main__":
    print("Storage MCP Server initialized")
    print(f"Available tools: {[t['name'] for t in TOOLS]}")