"""
Pricing Engine Skill
Calculates current market rates and generates renewal premium quotes
"""

from datetime import datetime
from typing import Optional


class PricingEngineSkill:
    def __init__(self, snowflake_conn=None):
        self.conn = snowflake_conn

    def get_market_rates(self, policy_type: str, state: str) -> dict:
        """
        Get current market rates for comparison
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            BASE_RATE_PER_1000,
            AVERAGE_PREMIUM,
            MARKET_TREND_PCT,
            RATE_CHANGE_YTD,
            COMPETITIVE_QUOTE_LOW,
            COMPETITIVE_QUOTE_HIGH
        FROM INSURANCE_DW.PRODUCTION.MARKET_RATES
        WHERE POLICY_TYPE = %s AND STATE = %s
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(query, (policy_type, state))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {
                    "status": "success",
                    "data": {
                        "policy_type": policy_type,
                        "state": state,
                        "market_trend_pct": 8.0,
                        "note": "Using default market data"
                    }
                }

            columns = [d[0] for d in cursor.description]
            return {"status": "success", "data": dict(zip(columns, result))}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def calculate_renewal_premium(
        self,
        policy_number: str,
        current_premium: float,
        policy_type: str,
        state: str,
        experience_modifier: float = 1.0,
        loyalty_discount_pct: float = 5.0
    ) -> dict:
        """
        Calculate renewal premium with all adjustments
        """
        market_data = self.get_market_rates(policy_type, state)
        market_trend = 8.0
        if market_data.get("status") == "success":
            market_trend = float(market_data["data"].get("MARKET_TREND_PCT", 8.0))

        base_premium = current_premium * (1 + market_trend / 100)
        adjusted_premium = base_premium * experience_modifier
        loyalty_discount = loyalty_discount_pct / 100
        final_premium = adjusted_premium * (1 - loyalty_discount)

        return {
            "status": "success",
            "data": {
                "policy_number": policy_number,
                "current_premium": current_premium,
                "market_trend_adjustment_pct": market_trend,
                "experience_modifier": experience_modifier,
                "loyalty_discount_pct": loyalty_discount_pct,
                "base_premium_after_market": round(base_premium, 2),
                "adjusted_premium": round(adjusted_premium, 2),
                "final_renewal_premium": round(final_premium, 2),
                "premium_change_amount": round(final_premium - current_premium, 2),
                "premium_change_pct": round(((final_premium - current_premium) / current_premium) * 100, 2) if current_premium > 0 else 0
            }
        }

    def get_coverage_details(self, policy_number: str) -> dict:
        """
        Get coverage details for a policy
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        query = """
        SELECT
            COVERAGE_TYPE,
            COVERAGE_LIMIT,
            COVERAGE_PREMIUM,
            DEDUCTIBLE,
            CO_PAYMENT_PCT,
            IS_SUB_LIMIT,
            SUB_LIMIT_AMOUNT
        FROM INSURANCE_DW.PRODUCTION.POLICY_COVERAGES
        WHERE POLICY_NUMBER = %s
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

    def generate_premium_breakdown(self, policy_number: str) -> dict:
        """
        Generate detailed premium breakdown for a policy
        """
        if not self.conn:
            return {"status": "error", "message": "No database connection"}

        policy_query = """
        SELECT
            p.ANNUAL_PREMIUM,
            p.POLICY_TYPE,
            ph.STATE,
            er.EXPERIENCE_MODIFIER,
            er.RISK_TIER
        FROM INSURANCE_DW.PRODUCTION.POLICIES p
        JOIN INSURANCE_DW.PRODUCTION.POLICY_HOLDERS ph ON p.POLICY_HOLDER_ID = ph.POLICY_HOLDER_ID
        LEFT JOIN INSURANCE_DW.PRODUCTION.EXPERIENCE_RATING er ON p.POLICY_NUMBER = er.POLICY_NUMBER
        WHERE p.POLICY_NUMBER = %s
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute(policy_query, (policy_number,))
            result = cursor.fetchone()
            cursor.close()

            if not result:
                return {"status": "error", "message": f"Policy {policy_number} not found"}

            current_premium = float(result[0])
            policy_type = result[1]
            state = result[2]
            exp_modifier = float(result[3]) if result[3] else 1.0
            risk_tier = result[4]

            premium_calc = self.calculate_renewal_premium(
                policy_number=policy_number,
                current_premium=current_premium,
                policy_type=policy_type,
                state=state,
                experience_modifier=exp_modifier,
                loyalty_discount_pct=5.0
            )

            return {
                "status": "success",
                "data": {
                    "policy_number": policy_number,
                    "risk_tier": risk_tier,
                    **premium_calc["data"]
                }
            }
        except Exception as e:
            return {"status": "error", "message": str(e)}