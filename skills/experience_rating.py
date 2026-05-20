"""
Experience Rating Skill
Analyzes claims history, loss ratio, and assigns industry risk tier
"""

from datetime import datetime
from typing import Optional


class ExperienceRatingSkill:
    def __init__(self, snowflake_conn=None):
        self.conn = snowflake_conn

    def get_experience_rating(self, policy_number: str) -> dict:
        """
        Get experience rating for a policy
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            RISK_TIER,
            EXPERIENCE_MODIFIER,
            CLAIMS_LAST_3_YEARS,
            LOSS_RATIO,
            TOTAL_CLAIMS,
            TOTAL_INCURRED,
            EFFECTIVE_YEARS
        FROM INSURANCE_DW.PRODUCTION.EXPERIENCE_RATING
        WHERE POLICY_NUMBER = %s
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_number,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"status": "error", "message": f"Experience rating not found for {policy_number}"}

            columns = [d[0] for d in cursor.description]
            return {"status": "success", "data": dict(zip(columns, result))}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_claims_history(self, policy_number: str) -> dict:
        """
        Fetch claims history for a policy
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            CLAIM_ID,
            CLAIM_DATE,
            CLAIM_TYPE,
            CLAIM_STATUS,
            LOSS_DESCRIPTION,
            TOTAL_INCURRED_AMOUNT,
            PAID_AMOUNT,
            RESERVES_AMOUNT,
            CLAIM_YEAR
        FROM INSURANCE_DW.PRODUCTION.CLAIMS
        WHERE POLICY_NUMBER = %s
        ORDER BY CLAIM_DATE DESC
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_number,))
            results = cursor.fetchall()
            cursor.close()

            columns = [d[0] for d in cursor.description] if cursor.description else []
            return {"status": "success", "data": [dict(zip(columns, row)) for row in results]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def get_risk_tier_info(self, policy_number: str) -> dict:
        """
        Get risk tier details for a policy
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            RISK_TIER,
            RISK_SCORE,
            UNDERWRITING_CLASS,
            TERRITORY_CODE,
            PREMIUM_BAND,
            ELIGIBLE_FOR_DISCOUNT,
            DISCOUNT_REASON
        FROM INSURANCE_DW.PRODUCTION.RISK_TIER_LOOKUP
        WHERE POLICY_NUMBER = %s
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_number,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"status": "error", "message": f"Risk tier not found for {policy_number}"}

            columns = [d[0] for d in cursor.description]
            return {"status": "success", "data": dict(zip(columns, result))}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def calculate_loss_ratio(self, policy_number: str) -> dict:
        """
        Calculate loss ratio based on claims history
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            p.ANNUAL_PREMIUM,
            COALESCE(SUM(c.TOTAL_INCURRED_AMOUNT), 0) as TOTAL_INCURRED,
            COALESCE(SUM(c.PAID_AMOUNT), 0) as TOTAL_PAID,
            COUNT(c.CLAIM_ID) as TOTAL_CLAIMS
        FROM INSURANCE_DW.PRODUCTION.POLICIES p
        LEFT JOIN INSURANCE_DW.PRODUCTION.CLAIMS c ON p.POLICY_NUMBER = c.POLICY_NUMBER
            AND c.CLAIM_DATE >= DATEADD('year', -3, CURRENT_DATE())
        WHERE p.POLICY_NUMBER = %s
        GROUP BY p.ANNUAL_PREMIUM
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_number,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"status": "error", "message": f"Policy {policy_number} not found"}

            annual_premium = result[0]
            total_incurred = float(result[1])
            loss_ratio = (total_incurred / annual_premium * 100) if annual_premium > 0 else 0

            columns = [d[0] for d in cursor.description]
            data = dict(zip(columns, result))
            data["LOSS_RATIO_PCT"] = round(loss_ratio, 2)

            return {"status": "success", "data": data}
        except Exception as e:
            return {"status": "error", "message": str(e)}