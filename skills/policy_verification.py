"""
Policy Verification Skill
Fetches policy details, checks for cancellations, and verifies payment status
"""

from datetime import datetime
from typing import Optional


class PolicyVerificationSkill:
    def __init__(self, snowflake_conn=None):
        self.conn = snowflake_conn

    def verify_policy(self, policy_number: str) -> dict:
        """
        Verify policy exists, get basic details and status
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            p.POLICY_NUMBER,
            p.POLICY_TYPE,
            p.POLICY_STATUS,
            p.PAYMENT_STATUS,
            p.COVERAGE_EXPIRATION_DATE,
            p.ANNUAL_PREMIUM,
            p.RENEWAL_ELIGIBILITY_FLAG,
            p.LAST_PAYMENT_DATE,
            ph.FIRST_NAME || ' ' || ph.LAST_NAME as POLICY_HOLDER_NAME,
            ph.EMAIL as POLICY_HOLDER_EMAIL,
            ph.PHONE as POLICY_HOLDER_PHONE,
            ph.STATE
        FROM INSURANCE_DW.PRODUCTION.POLICIES p
        JOIN INSURANCE_DW.PRODUCTION.POLICY_HOLDERS ph ON p.POLICY_HOLDER_ID = ph.POLICY_HOLDER_ID
        WHERE p.POLICY_NUMBER = %s
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_number,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"status": "error", "message": f"Policy {policy_number} not found"}

            columns = [d[0] for d in cursor.description]
            return {"status": "success", "data": dict(zip(columns, result))}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def check_eligibility(self, policy_number: str) -> dict:
        """
        Check if policy is eligible for renewal
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            p.POLICY_NUMBER,
            p.POLICY_STATUS,
            p.PAYMENT_STATUS,
            p.RENEWAL_ELIGIBILITY_FLAG,
            p.COVERAGE_EXPIRATION_DATE,
            CASE
                WHEN p.POLICY_STATUS = 'ACTIVE' AND p.PAYMENT_STATUS = 'CURRENT'
                    AND p.RENEWAL_ELIGIBILITY_FLAG = 'Y' THEN 'ELIGIBLE'
                WHEN p.POLICY_STATUS != 'ACTIVE' THEN 'NOT_ELIGIBLE_STATUS'
                WHEN p.PAYMENT_STATUS != 'CURRENT' THEN 'NOT_ELIGIBLE_PAYMENT'
                ELSE 'NOT_ELIGIBLE_OTHER'
            END as ELIGIBILITY_STATUS,
            DATEDIFF('day', CURRENT_DATE(), p.COVERAGE_EXPIRATION_DATE) as DAYS_TO_EXPIRATION
        FROM INSURANCE_DW.PRODUCTION.POLICIES p
        WHERE p.POLICY_NUMBER = %s
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_number,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"status": "error", "message": f"Policy {policy_number} not found"}

            columns = [d[0] for d in cursor.description]
            return {"status": "success", "data": dict(zip(columns, result))}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_policyholder_info(self, policy_number: str) -> dict:
        """
        Get policyholder contact information
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            ph.POLICY_HOLDER_ID,
            ph.FIRST_NAME,
            ph.LAST_NAME,
            ph.EMAIL,
            ph.PHONE,
            ph.ADDRESS_LINE_1,
            ph.CITY,
            ph.STATE,
            ph.ZIP_CODE,
            ph.PREFERRED_CONTACT_METHOD
        FROM INSURANCE_DW.PRODUCTION.POLICIES p
        JOIN INSURANCE_DW.PRODUCTION.POLICY_HOLDERS ph ON p.POLICY_HOLDER_ID = ph.POLICY_HOLDER_ID
        WHERE p.POLICY_NUMBER = %s
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_number,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"status": "error", "message": "Policyholder not found"}

            columns = [d[0] for d in cursor.description]
            return {"status": "success", "data": dict(zip(columns, result))}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def list_eligible_policies(self, days_ahead: int = 60) -> dict:
        """
        List all policies eligible for renewal within window
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            p.POLICY_NUMBER,
            p.POLICY_TYPE,
            p.ANNUAL_PREMIUM,
            p.COVERAGE_EXPIRATION_DATE,
            ph.FIRST_NAME || ' ' || ph.LAST_NAME as POLICY_HOLDER_NAME,
            ph.EMAIL as POLICY_HOLDER_EMAIL
        FROM INSURANCE_DW.PRODUCTION.POLICIES p
        JOIN INSURANCE_DW.PRODUCTION.POLICY_HOLDERS ph ON p.POLICY_HOLDER_ID = ph.POLICY_HOLDER_ID
        WHERE p.RENEWAL_ELIGIBILITY_FLAG = 'Y'
        AND p.COVERAGE_EXPIRATION_DATE BETWEEN CURRENT_DATE()
            AND DATEADD('day', %s, CURRENT_DATE())
        ORDER BY p.COVERAGE_EXPIRATION_DATE ASC
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (days_ahead,))
            results = cursor.fetchall()
            cursor.close()

            columns = [d[0] for d in cursor.description] if cursor.description else []
            return {"status": "success", "data": [dict(zip(columns, row)) for row in results]}
        except Exception as e:
            return {"status": "error", "message": str(e)}