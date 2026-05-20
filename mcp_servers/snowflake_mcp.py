"""
Snowflake MCP Server for Insurance Renewal Agent
Provides tools to query policy data, claims history, and risk scoring from Snowflake
"""

import json
import os
from typing import Any, Optional
from datetime import datetime, timedelta
import snowflake.connector
from snowflake.connector import DictCursor

class SnowflakeMCPServer:
    def __init__(self):
        self.connection = None
        self._connect()

    def _connect(self):
        try:
            self.connection = snowflake.connector.connect(
                account=os.getenv("SNOWFLAKE_ACCOUNT"),
                user=os.getenv("SNOWFLAKE_USER"),
                password=os.getenv("SNOWFLAKE_PASSWORD"),
                warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "COMPUTE_WH"),
                database=os.getenv("SNOWFLAKE_DATABASE", "INSURANCE_DW"),
                schema=os.getenv("SNOWFLAKE_SCHEMA", "PRODUCTION"),
                role=os.getenv("SNOWFLAKE_ROLE")
            )
            print("Connected to Snowflake")
        except Exception as e:
            print(f"Snowflake connection failed: {e}")
            self.connection = None

    def execute_query(self, query: str, params: Optional[tuple] = None) -> list[dict]:
        if not self.connection:
            return [{"error": "Not connected to Snowflake"}]
        try:
            cursor = self.connection.cursor(DictCursor)
            cursor.execute(query, params or ())
            columns = [d[0] for d in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            return [{"error": str(e)}]

    # === POLICY MANAGEMENT TOOLS ===

    def get_policy(self, policy_number: str = None, claim_id: str = None) -> dict:
        """
        Fetch policy details by policy number or claim ID
        """
        if policy_number:
            query = """
            SELECT
                p.POLICY_NUMBER,
                p.POLICY_HOLDER_ID,
                p.POLICY_TYPE,
                p.COVERAGE_EFFECTIVE_DATE,
                p.COVERAGE_EXPIRATION_DATE,
                p.ANNUAL_PREMIUM,
                p.POLICY_STATUS,
                p.PAYMENT_STATUS,
                p.DEDUCTIBLE_AMOUNT,
                p.LAST_PAYMENT_DATE,
                p.RENEWAL_ELIGIBILITY_FLAG,
                p.AGENT_ID,
                ph.FIRST_NAME || ' ' || ph.LAST_NAME as POLICY_HOLDER_NAME,
                ph.EMAIL as POLICY_HOLDER_EMAIL,
                ph.PHONE as POLICY_HOLDER_PHONE,
                ph.ADDRESS_LINE_1,
                ph.CITY,
                ph.STATE,
                ph.ZIP_CODE
            FROM INSURANCE_DW.PRODUCTION.POLICIES p
            JOIN INSURANCE_DW.PRODUCTION.POLICY_HOLDERS ph ON p.POLICY_HOLDER_ID = ph.POLICY_HOLDER_ID
            WHERE p.POLICY_NUMBER = %s
            """
            result = self.execute_query(query, (policy_number,))
        elif claim_id:
            query = """
            SELECT
                p.POLICY_NUMBER,
                p.POLICY_HOLDER_ID,
                p.POLICY_TYPE,
                p.COVERAGE_EFFECTIVE_DATE,
                p.COVERAGE_EXPIRATION_DATE,
                p.ANNUAL_PREMIUM,
                p.POLICY_STATUS,
                p.PAYMENT_STATUS,
                p.DEDUCTIBLE_AMOUNT,
                p.RENEWAL_ELIGIBILITY_FLAG,
                ph.FIRST_NAME || ' ' || ph.LAST_NAME as POLICY_HOLDER_NAME,
                ph.EMAIL as POLICY_HOLDER_EMAIL,
                ph.PHONE as POLICY_HOLDER_PHONE
            FROM INSURANCE_DW.PRODUCTION.POLICIES p
            JOIN INSURANCE_DW.PRODUCTION.POLICY_HOLDERS ph ON p.POLICY_HOLDER_ID = ph.POLICY_HOLDER_ID
            JOIN INSURANCE_DW.PRODUCTION.CLAIMS c ON c.POLICY_NUMBER = p.POLICY_NUMBER
            WHERE c.CLAIM_ID = %s
            """
            result = self.execute_query(query, (claim_id,))
        else:
            return {"error": "Either policy_number or claim_id must be provided"}

        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0] if result else None}
        return {"status": "error", "message": "Policy not found", "data": None}

    def get_coverage_details(self, policy_number: str) -> dict:
        """
        Fetch detailed coverage information for a policy
        """
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
        result = self.execute_query(query, (policy_number,))
        return {"status": "success", "data": result}

    def get_policyholder(self, policy_holder_id: str) -> dict:
        """
        Fetch policyholder contact information
        """
        query = """
        SELECT
            POLICY_HOLDER_ID,
            FIRST_NAME,
            LAST_NAME,
            EMAIL,
            PHONE,
            ADDRESS_LINE_1,
            ADDRESS_LINE_2,
            CITY,
            STATE,
            ZIP_CODE,
            DATE_OF_BIRTH,
            PREFERRED_CONTACT_METHOD
        FROM INSURANCE_DW.PRODUCTION.POLICY_HOLDERS
        WHERE POLICY_HOLDER_ID = %s
        """
        result = self.execute_query(query, (policy_holder_id,))
        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0]}
        return {"status": "error", "message": "Policyholder not found"}

    # === CLAIMS & EXPERIENCE RATING TOOLS ===

    def get_claims_history(self, policy_number: str = None, contact_id: str = None) -> dict:
        """
        Fetch claims history for experience rating
        """
        if policy_number:
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
            result = self.execute_query(query, (policy_number,))
        elif contact_id:
            query = """
            SELECT
                c.CLAIM_ID,
                c.CLAIM_DATE,
                c.CLAIM_TYPE,
                c.CLAIM_STATUS,
                c.LOSS_DESCRIPTION,
                c.TOTAL_INCURRED_AMOUNT,
                p.POLICY_NUMBER
            FROM INSURANCE_DW.PRODUCTION.CLAIMS c
            JOIN INSURANCE_DW.PRODUCTION.POLICIES p ON c.POLICY_NUMBER = p.POLICY_NUMBER
            WHERE p.POLICY_HOLDER_ID = %s
            ORDER BY c.CLAIM_DATE DESC
            """
            result = self.execute_query(query, (contact_id,))
        else:
            return {"error": "Either policy_number or contact_id must be provided"}

        return {"status": "success", "data": result}

    def calculate_experience_rating(self, policy_number: str) -> dict:
        """
        Calculate experience rating based on claims history
        """
        query = """
        SELECT
            POLICY_NUMBER,
            POLICY_TYPE,
            EFFECTIVE_YEARS,
            TOTAL_CLAIMS,
            TOTAL_INCURRED,
            CLAIMS_LAST_3_YEARS,
            LOSS_RATIO,
            EXPERIENCE_MODIFIER,
            RISK_TIER,
            RECOMMENDED_PREMIUM_ADJUSTMENT
        FROM INSURANCE_DW.PRODUCTION.EXPERIENCE_RATING
        WHERE POLICY_NUMBER = %s
        """
        result = self.execute_query(query, (policy_number,))
        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0]}
        return {"status": "error", "message": "Experience rating not found"}

    def get_risk_tier(self, policy_number: str) -> dict:
        """
        Get current risk tier for a policy
        """
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
        result = self.execute_query(query, (policy_number,))
        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0]}
        return {"status": "error", "message": "Risk tier not found"}

    # === PRICING & RENEWAL TOOLS ===

    def get_market_rates(self, policy_type: str, state: str) -> dict:
        """
        Get current market rates for comparison
        """
        query = """
        SELECT
            POLICY_TYPE,
            STATE,
            BASE_RATE_PER_1000,
            AVERAGE_PREMIUM,
            MARKET_TREND_PCT,
            RATE_CHANGE_YTD,
            COMPETITIVE_QUOTE_LOW,
            COMPETITIVE_QUOTE_HIGH
        FROM INSURANCE_DW.PRODUCTION.MARKET_RATES
        WHERE POLICY_TYPE = %s AND STATE = %s
        """
        result = self.execute_query(query, (policy_type, state))
        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0]}
        return {"status": "success", "data": {"policy_type": policy_type, "state": state, "market_trend_pct": 8.0, "note": "Using default market data"}}

    def calculate_renewal_premium(
        self,
        policy_number: str,
        apply_loyalty_discount: bool = True
    ) -> dict:
        """
        Calculate renewal premium with all adjustments
        """
        policy_data = self.get_policy(policy_number)
        if policy_data.get("status") != "success":
            return policy_data

        policy = policy_data["data"]
        current_premium = float(policy.get("ANNUAL_PREMIUM", 0))

        market_query = """
        SELECT MARKET_TREND_PCT FROM INSURANCE_DW.PRODUCTION.MARKET_RATES
        WHERE POLICY_TYPE = %s AND STATE = %s
        """
        market_result = self.execute_query(market_query, (policy.get("POLICY_TYPE"), policy.get("STATE")))
        market_trend = float(market_result[0].get("MARKET_TREND_PCT", 8.0)) if market_result else 8.0

        exp_rating_query = """
        SELECT EXPERIENCE_MODIFIER FROM INSURANCE_DW.PRODUCTION.EXPERIENCE_RATING
        WHERE POLICY_NUMBER = %s
        """
        exp_result = self.execute_query(exp_rating_query, (policy_number,))
        exp_modifier = float(exp_result[0].get("EXPERIENCE_MODIFIER", 1.0)) if exp_result else 1.0

        loyalty_discount = 0.05 if apply_loyalty_discount else 0.0

        base_premium = current_premium * (1 + market_trend / 100)
        adjusted_premium = base_premium * exp_modifier
        final_premium = adjusted_premium * (1 - loyalty_discount)

        return {
            "status": "success",
            "data": {
                "policy_number": policy_number,
                "current_premium": current_premium,
                "market_trend_adjustment_pct": market_trend,
                "experience_modifier": exp_modifier,
                "loyalty_discount_pct": loyalty_discount * 100,
                "base_premium_after_market": base_premium,
                "adjusted_premium": adjusted_premium,
                "final_renewal_premium": round(final_premium, 2),
                "premium_change_amount": round(final_premium - current_premium, 2),
                "premium_change_pct": round(((final_premium - current_premium) / current_premium) * 100, 2) if current_premium > 0 else 0
            }
        }

    def get_renewal_eligibility(self, policy_number: str) -> dict:
        """
        Check if policy is eligible for renewal
        """
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
        result = self.execute_query(query, (policy_number,))
        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0]}
        return {"status": "error", "message": "Policy not found"}

    # === AGENT & DISPATCH TOOLS ===

    def get_agent_info(self, agent_id: str) -> dict:
        """
        Fetch agent details for communication routing
        """
        query = """
        SELECT
            AGENT_ID,
            AGENT_NAME,
            AGENT_EMAIL,
            AGENT_PHONE,
            AGENT_TERRITORY,
            PRODUCER_CODE,
            APPOINTMENT_STATUS
        FROM INSURANCE_DW.PRODUCTION.AGENTS
        WHERE AGENT_ID = %s
        """
        result = self.execute_query(query, (agent_id,))
        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0]}
        return {"status": "error", "message": "Agent not found"}

    def list_pending_renewals(self, days_window: int = 30) -> dict:
        """
        List all policies up for renewal within the given window
        """
        query = """
        SELECT
            p.POLICY_NUMBER,
            p.POLICY_TYPE,
            p.ANNUAL_PREMIUM,
            p.COVERAGE_EXPIRATION_DATE,
            ph.FIRST_NAME || ' ' || ph.LAST_NAME as POLICY_HOLDER_NAME,
            ph.EMAIL as POLICY_HOLDER_EMAIL,
            ph.PREFERRED_CONTACT_METHOD,
            a.AGENT_NAME,
            a.AGENT_EMAIL,
            er.EXPERIENCE_MODIFIER,
            er.RISK_TIER
        FROM INSURANCE_DW.PRODUCTION.POLICIES p
        JOIN INSURANCE_DW.PRODUCTION.POLICY_HOLDERS ph ON p.POLICY_HOLDER_ID = ph.POLICY_HOLDER_ID
        LEFT JOIN INSURANCE_DW.PRODUCTION.AGENTS a ON p.AGENT_ID = a.AGENT_ID
        LEFT JOIN INSURANCE_DW.PRODUCTION.EXPERIENCE_RATING er ON p.POLICY_NUMBER = er.POLICY_NUMBER
        WHERE p.RENEWAL_ELIGIBILITY_FLAG = 'Y'
            AND p.COVERAGE_EXPIRATION_DATE BETWEEN CURRENT_DATE()
                AND DATEADD('day', %s, CURRENT_DATE())
        ORDER BY p.COVERAGE_EXPIRATION_DATE ASC
        """
        result = self.execute_query(query, (days_window,))
        return {"status": "success", "data": result}

    # === H3 RISK DATA (reusing your existing data) ===

    def get_h3_risk_scores(self, h3_index: str) -> dict:
        """
        Get H3 risk scores for property location
        """
        query = """
        SELECT
            H3_INDEX,
            H3_RESOLUTION,
            H3_US_WILDFIRE_SCORE,
            H3_US_PROPERTY_CRIME_SCORE,
            H3_US_VIOLENT_CRIME_SCORE,
            H3_US_FLOOD_SCORE,
            H3_US_HAIL_SCORE,
            H3_US_HURRICANE_SCORE
        FROM INSURANCE_DW.PRODUCTION.H3_RISK_SCORES
        WHERE H3_INDEX = %s
        """
        result = self.execute_query(query, (h3_index,))
        if result and "error" not in result[0]:
            return {"status": "success", "data": result[0]}
        return {"status": "success", "data": None}


# Tool registry for MCP protocol
TOOLS = [
    {
        "name": "get_policy",
        "description": "Fetch policy details by policy number or claim ID",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string", "description": "Policy number (e.g., HW-88712)"},
                "claim_id": {"type": "string", "description": "Claim ID if policy lookup is not available"}
            }
        }
    },
    {
        "name": "get_coverage_details",
        "description": "Fetch detailed coverage information for a policy",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string", "description": "Policy number"}
            },
            "required": ["policy_number"]
        }
    },
    {
        "name": "get_claims_history",
        "description": "Fetch claims history for experience rating",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "contact_id": {"type": "string"}
            }
        }
    },
    {
        "name": "calculate_experience_rating",
        "description": "Calculate experience rating based on claims history",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"}
            },
            "required": ["policy_number"]
        }
    },
    {
        "name": "get_market_rates",
        "description": "Get current market rates for comparison",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_type": {"type": "string"},
                "state": {"type": "string"}
            },
            "required": ["policy_type", "state"]
        }
    },
    {
        "name": "calculate_renewal_premium",
        "description": "Calculate renewal premium with all adjustments",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"},
                "apply_loyalty_discount": {"type": "boolean", "default": True}
            },
            "required": ["policy_number"]
        }
    },
    {
        "name": "get_renewal_eligibility",
        "description": "Check if policy is eligible for renewal",
        "input_schema": {
            "type": "object",
            "properties": {
                "policy_number": {"type": "string"}
            },
            "required": ["policy_number"]
        }
    },
    {
        "name": "get_agent_info",
        "description": "Fetch agent details for communication routing",
        "input_schema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string"}
            },
            "required": ["agent_id"]
        }
    },
    {
        "name": "list_pending_renewals",
        "description": "List all policies up for renewal within the given window",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_window": {"type": "integer", "default": 30}
            }
        }
    },
    {
        "name": "get_h3_risk_scores",
        "description": "Get H3 risk scores for property location",
        "input_schema": {
            "type": "object",
            "properties": {
                "h3_index": {"type": "string"}
            },
            "required": ["h3_index"]
        }
    }
]


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Route tool calls to appropriate methods"""
    server = SnowflakeMCPServer()

    if hasattr(server, tool_name):
        method = getattr(server, tool_name)
        return method(**arguments)
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}


if __name__ == "__main__":
    print("Snowflake MCP Server initialized")
    print(f"Available tools: {[t['name'] for t in TOOLS]}")