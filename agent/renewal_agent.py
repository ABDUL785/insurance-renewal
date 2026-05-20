"""
Insurance Renewal Agent - Snowflake Integrated with Skills Architecture
Usage:
  python renewal_agent.py              # Live Snowflake mode
  python renewal_agent.py --batch     # Batch processing for all eligible policies
  python renewal_agent.py --policy <number>  # Process specific policy
"""

import sys
import os
import argparse
from datetime import datetime
import snowflake.connector
from snowflake.connector import DictCursor

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "mcp_servers"))

from policy_verification import PolicyVerificationSkill
from experience_rating import ExperienceRatingSkill
from pricing_engine import PricingEngineSkill
from document_generation import DocumentGenerationSkill
from communication import CommunicationSkill
from storage_mcp import StorageMCPServer


ENV_FILE = os.path.join(os.path.dirname(__file__), "..", ".env")


def load_env():
    """Load .env file if it exists"""
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())
        print(f"  [CONFIG] Loaded from .env file")

    snowflake_account = os.getenv("SNOWFLAKE_ACCOUNT", "")
    snowflake_user = os.getenv("SNOWFLAKE_USER", "")
    print(f"  [CONFIG] Snowflake Account: {snowflake_account or 'NOT SET'}")
    print(f"  [CONFIG] Snowflake User:    {snowflake_user or 'NOT SET'}")


def get_snowflake_connection():
    """Create and return a Snowflake connection"""
    account = os.getenv("SNOWFLAKE_ACCOUNT")
    user = os.getenv("SNOWFLAKE_USER")
    password = os.getenv("SNOWFLAKE_PASSWORD")

    if not all([account, user, password]):
        return None

    try:
        conn = snowflake.connector.connect(
            account=account,
            user=user,
            password=password,
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
            database=os.getenv("SNOWFLAKE_DATABASE", "INSURANCE_DW"),
            schema=os.getenv("SNOWFLAKE_SCHEMA", "PRODUCTION"),
            role=os.getenv("SNOWFLAKE_ROLE")
        )
        print("  [SNOWFLAKE] Connected successfully")
        return conn
    except Exception as e:
        print(f"  [SNOWFLAKE] Connection failed: {e}")
        return None


class RenewalAgent:
    def __init__(self):
        load_env()
        try:
            self.conn = get_snowflake_connection()
            if not self.conn:
                raise ConnectionError("Could not connect to Snowflake")

            self.policy_verification = PolicyVerificationSkill(self.conn)
            self.experience_rating = ExperienceRatingSkill(self.conn)
            self.pricing_engine = PricingEngineSkill(self.conn)
            self.document_generation = DocumentGenerationSkill()
            self.communication = CommunicationSkill(self.conn)
            self.storage = StorageMCPServer()

            print(f"\n  Mode: LIVE (Snowflake)")
        except Exception as e:
            print(f"\n  ERROR: {e}")
            print("  Cannot proceed without Snowflake connection.")
            sys.exit(1)

    def get_agent_info(self, agent_id):
        """Fetch agent details from Snowflake"""
        query = """
        SELECT AGENT_NAME, AGENT_PHONE FROM INSURANCE_DW.PRODUCTION.AGENTS
        WHERE AGENT_ID = %s
        """
        try:
            cursor = self.conn.cursor(DictCursor)
            cursor.execute(query, (agent_id,))
            result = cursor.fetchone()
            cursor.close()
            return dict(result) if result else None
        except:
            return None

    def process_renewal(self, policy_number):
        print(f"\n{'='*55}\n  PROCESSING: {policy_number}\n{'='*55}\n")

        eligibility = self.policy_verification.check_eligibility(policy_number)
        if eligibility.get("status") != "success":
            return {"error": f"Policy {policy_number} not found", "policy_number": policy_number}

        elig_data = eligibility.get("data", {})
        if elig_data.get("ELIGIBILITY_STATUS") != "ELIGIBLE":
            print(f"  [1] Policy Eligibility     -> NOT ELIGIBLE ({elig_data.get('ELIGIBILITY_STATUS', 'UNKNOWN')})")
            return {"error": "Policy not eligible for renewal", "policy_number": policy_number}

        policy_result = self.policy_verification.verify_policy(policy_number)
        if policy_result.get("status") != "success":
            return {"error": f"Policy {policy_number} not found", "final_response": None}

        policy = policy_result.get("data", {})
        exp_rating = self.experience_rating.get_experience_rating(policy_number)
        exp_data = exp_rating.get("data", {}) if exp_rating.get("status") == "success" else {}

        agent_id = policy.get("AGENT_ID")
        agent = self.get_agent_info(agent_id) or {}

        current_premium = float(policy.get("ANNUAL_PREMIUM", 0))
        premium_calc = self.pricing_engine.calculate_renewal_premium(
            policy_number=policy_number,
            current_premium=current_premium,
            policy_type=policy.get("POLICY_TYPE"),
            state=policy.get("STATE", "TX"),
            experience_modifier=float(exp_data.get("EXPERIENCE_MODIFIER", 1.0)),
            loyalty_discount_pct=5.0
        )

        calc_data = premium_calc.get("data", {})
        final = calc_data.get("final_renewal_premium", current_premium)
        change_pct = calc_data.get("premium_change_pct", 0)

        effective_date = datetime.now().strftime("%Y-%m-%d")
        expiration_date = policy.get("COVERAGE_EXPIRATION_DATE")

        print(f"  [1] Policy Eligibility      -> ELIGIBLE")
        print(f"  [2] Policy Holder            -> {policy.get('POLICY_HOLDER_NAME')}")
        print(f"  [3] Experience Rating        -> {exp_data.get('RISK_TIER', 'N/A')} (modifier: {exp_data.get('EXPERIENCE_MODIFIER', 'N/A')})")
        print(f"  [4] Market Adjustment        -> +{calc_data.get('market_trend_adjustment_pct', 0)}%")
        print(f"  [5] Loyalty Discount         -> -5%")

        doc_result = self.document_generation.generate_renewal_quote(
            policy_number=policy_number,
            policy_holder_name=policy.get("POLICY_HOLDER_NAME"),
            policy_type=policy.get("POLICY_TYPE"),
            current_premium=current_premium,
            renewal_premium=final,
            premium_change_pct=change_pct,
            effective_date=effective_date,
            expiration_date=expiration_date,
            loyalty_discount_pct=5.0,
            agent_name=agent.get("AGENT_NAME"),
            agent_phone=agent.get("AGENT_PHONE"),
            risk_tier=exp_data.get("RISK_TIER"),
            claims_history=f"{exp_data.get('CLAIMS_LAST_3_YEARS', 0)} in last 3 years"
        )

        pdf_base64 = None
        file_name = None
        stage_path = None
        document_id = None

        if doc_result.get("status") == "success":
            pdf_base64 = doc_result["data"]["pdf_base64"]
            file_name = doc_result["data"]["file_name"]

            storage_result = self.storage.upload_pdf_to_stage(pdf_base64, policy_number)
            if storage_result.get("status") == "success":
                stage_path = storage_result["data"]["stage_path"]
                document_id = storage_result["data"]["document_id"]
                print(f"  [6] Document Generated      -> {file_name}")
                print(f"      Storage Path:           {stage_path}")
            else:
                print(f"  [6] Document Generated      -> {file_name} (local only)")
        else:
            print(f"  [6] Document Generation     -> FAILED")

        email_subject = f"Your Policy {policy_number} Renewal Quote"

        doc_info = f"\n\nDOCUMENT:\n- Stored in Snowflake Stage: {stage_path}\n- Document ID: {document_id}" if stage_path else ""
        email_body = f"""Dear {policy.get('POLICY_HOLDER_NAME')},

Your policy {policy_number} is up for renewal.

POLICY DETAILS:
- Policy Type: {policy.get('POLICY_TYPE')}
- Current Premium: ${current_premium:,.2f}
- Renewal Premium: ${final:,.2f}
- Premium Change: {change_pct:+.1f}%
- Expiration Date: {expiration_date}
- Risk Tier: {exp_data.get('RISK_TIER', 'N/A')}{doc_info}

Your renewal quote PDF has been generated and stored in our system.

Please review and contact us if you have any questions.

Best regards,
{agent.get('AGENT_NAME', 'Your Insurance Team')}
"""

        email_result = self.communication.send_email(
            to_email=policy.get("POLICY_HOLDER_EMAIL"),
            subject=email_subject,
            body=email_body,
            pdf_base64=pdf_base64,
            file_name=file_name
        )

        if email_result.get("status") == "success":
            print(f"  [7] Email Sent              -> {policy.get('POLICY_HOLDER_EMAIL')} (with PDF)")
        else:
            print(f"  [7] Email Failed            -> {email_result.get('message', 'Unknown error')}")
            print(f"      Recording notification in Snowflake...")
            self.communication.create_email_notification_record(
                policy_number=policy_number,
                recipient_email=policy.get("POLICY_HOLDER_EMAIL"),
                recipient_name=policy.get("POLICY_HOLDER_NAME"),
                subject=email_subject,
                body=email_body,
                attachment_path=stage_path,
                attachment_filename=file_name if stage_path else None
            )

        return {
            "policy_number": policy_number,
            "source": "Snowflake",
            "eligibility": elig_data.get("RENEWAL_ELIGIBILITY_FLAG"),
            "document_id": document_id,
            "email_status": email_result.get("status"),
            "final_response": {
                "policy_holder": policy.get("POLICY_HOLDER_NAME"),
                "current_premium": f"${current_premium:,.2f}",
                "renewal_premium": f"${final:,.2f}",
                "premium_change": f"{change_pct:+.1f}%",
                "risk_tier": exp_data.get("RISK_TIER"),
                "claims_history": f"{exp_data.get('CLAIMS_LAST_3_YEARS', 0)} in last 3 years",
                "expiration_date": expiration_date,
                "agent": agent.get("AGENT_NAME"),
                "status": "SUCCESS"
            }
        }

    def list_eligible_policies(self, days_ahead=60):
        """List policies eligible for renewal"""
        result = self.policy_verification.list_eligible_policies(days_ahead)
        if result.get("status") == "success":
            return [p["POLICY_NUMBER"] for p in result.get("data", [])]
        return []

    def list_all_policies(self):
        """List all active policies"""
        query = """
        SELECT POLICY_NUMBER FROM INSURANCE_DW.PRODUCTION.POLICIES
        WHERE POLICY_STATUS = 'ACTIVE'
        ORDER BY COVERAGE_EXPIRATION_DATE ASC
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            return [row[0] for row in results] if results else []
        except:
            return []

    def batch_process(self):
        policies = self.list_eligible_policies(days_ahead=60)
        print(f"  [BATCH] Found {len(policies)} eligible policies from Snowflake")

        if not policies:
            print("  No eligible policies found for renewal.")
            return []

        results = []
        for p in policies:
            result = self.process_renewal(p)
            fr = result.get("final_response")
            if fr:
                print(f"\n  >> {fr['policy_holder']}: {fr['current_premium']} -> {fr['renewal_premium']} ({fr['premium_change']})")
            results.append(result)
        return results

    def close(self):
        if self.conn:
            self.conn.close()
        if self.storage:
            self.storage.close()


def main():
    parser = argparse.ArgumentParser(description="Insurance Renewal Agent")
    parser.add_argument("--batch", action="store_true", help="Run batch processing for all eligible policies")
    parser.add_argument("--policy", type=str, help="Specific policy number")
    parser.add_argument("--all", action="store_true", help="Process all active policies (not just eligible)")
    args = parser.parse_args()

    print("\n" + "="*55)
    print("  INSURANCE RENEWAL INTELLIGENCE AGENT")
    print("="*55)

    agent = RenewalAgent()

    if args.batch:
        print("\n  Running batch processing...")
        results = agent.batch_process()
        print(f"\n  Batch complete: {len(results)} policies processed")
    elif args.all:
        print("\n  Processing all active policies...")
        policies = agent.list_all_policies()
        print(f"  Found {len(policies)} active policies")
        results = []
        for p in policies:
            result = agent.process_renewal(p)
            fr = result.get("final_response")
            if fr:
                print(f"\n  >> {fr['policy_holder']}: {fr['current_premium']} -> {fr['renewal_premium']} ({fr['premium_change']})")
            results.append(result)
        print(f"\n  Complete: {len(results)} policies processed")
    elif args.policy:
        result = agent.process_renewal(args.policy)
        if result.get("error"):
            print(f"\n  ERROR: {result['error']}")
    else:
        eligible = agent.list_eligible_policies(days_ahead=90)
        print(f"\n  Eligible Policies for Renewal: {', '.join(eligible) if eligible else 'None found'}")

        all_policies = agent.list_all_policies()
        print(f"  All Active Policies: {', '.join(all_policies) if all_policies else 'None found'}")

        default_policy = eligible[0] if eligible else (all_policies[0] if all_policies else "")
        if not default_policy:
            print("  No policies found in database.")
            agent.close()
            return

        policy = input(f"\n  Enter policy number [{default_policy}]: ").strip() or default_policy
        result = agent.process_renewal(policy)

        if result.get("final_response"):
            fr = result["final_response"]
            print("\n" + "-"*55)
            print("  RESULT:")
            print("-"*55)
            print(f"  Policy Holder:     {fr['policy_holder']}")
            print(f"  Current Premium:   {fr['current_premium']}")
            print(f"  Renewal Premium:   {fr['renewal_premium']} ({fr['premium_change']})")
            print(f"  Risk Tier:         {fr['risk_tier']}")
            print(f"  Claims History:    {fr['claims_history']}")
            print(f"  Expiration:        {fr['expiration_date']}")
            print(f"  Agent:             {fr['agent']}")
            print(f"  Status:            {fr['status']}")
            print(f"  Data Source:       {result.get('source', 'Snowflake')}")
            print("-"*55)

    agent.close()


if __name__ == "__main__":
    main()