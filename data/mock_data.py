"""
Mock Data Layer for Insurance Renewal Agent Demo
Provides realistic sample data for testing without Snowflake connection
"""

MOCK_POLICIES = {
    "HW-88712": {
        "POLICY_NUMBER": "HW-88712",
        "POLICY_HOLDER_ID": "PH001",
        "POLICY_TYPE": "HOMEOWNERS",
        "COVERAGE_EFFECTIVE_DATE": "2025-06-01",
        "COVERAGE_EXPIRATION_DATE": "2026-06-01",
        "ANNUAL_PREMIUM": 1850.00,
        "POLICY_STATUS": "ACTIVE",
        "PAYMENT_STATUS": "CURRENT",
        "DEDUCTIBLE_AMOUNT": 1000.00,
        "LAST_PAYMENT_DATE": "2025-05-15",
        "RENEWAL_ELIGIBILITY_FLAG": "Y",
        "AGENT_ID": "AGT001",
        "POLICY_HOLDER_NAME": "John Anderson",
        "POLICY_HOLDER_EMAIL": "john.anderson@email.com",
        "POLICY_HOLDER_PHONE": "555-0101",
        "ADDRESS_LINE_1": "123 Oak Street",
        "CITY": "Dallas",
        "STATE": "TX",
        "ZIP_CODE": "75201"
    },
    "HW-44521": {
        "POLICY_NUMBER": "HW-44521",
        "POLICY_HOLDER_ID": "PH002",
        "POLICY_TYPE": "HOMEOWNERS",
        "COVERAGE_EFFECTIVE_DATE": "2025-05-15",
        "COVERAGE_EXPIRATION_DATE": "2026-05-15",
        "ANNUAL_PREMIUM": 2100.00,
        "POLICY_STATUS": "ACTIVE",
        "PAYMENT_STATUS": "CURRENT",
        "DEDUCTIBLE_AMOUNT": 1500.00,
        "LAST_PAYMENT_DATE": "2025-05-01",
        "RENEWAL_ELIGIBILITY_FLAG": "Y",
        "AGENT_ID": "AGT002",
        "POLICY_HOLDER_NAME": "Sarah Mitchell",
        "POLICY_HOLDER_EMAIL": "sarah.m@email.com",
        "POLICY_HOLDER_PHONE": "555-0102",
        "ADDRESS_LINE_1": "456 Maple Ave",
        "CITY": "Houston",
        "STATE": "TX",
        "ZIP_CODE": "77001"
    },
    "AU-99234": {
        "POLICY_NUMBER": "AU-99234",
        "POLICY_HOLDER_ID": "PH003",
        "POLICY_TYPE": "AUTO",
        "COVERAGE_EFFECTIVE_DATE": "2025-07-01",
        "COVERAGE_EXPIRATION_DATE": "2026-07-01",
        "ANNUAL_PREMIUM": 1200.00,
        "POLICY_STATUS": "ACTIVE",
        "PAYMENT_STATUS": "CURRENT",
        "DEDUCTIBLE_AMOUNT": 500.00,
        "LAST_PAYMENT_DATE": "2025-06-20",
        "RENEWAL_ELIGIBILITY_FLAG": "Y",
        "AGENT_ID": "AGT003",
        "POLICY_HOLDER_NAME": "Michael Chen",
        "POLICY_HOLDER_EMAIL": "m.chen@email.com",
        "POLICY_HOLDER_PHONE": "555-0103",
        "ADDRESS_LINE_1": "789 Pine Road",
        "CITY": "Austin",
        "STATE": "TX",
        "ZIP_CODE": "78701"
    },
    "HW-55678": {
        "POLICY_NUMBER": "HW-55678",
        "POLICY_HOLDER_ID": "PH004",
        "POLICY_TYPE": "HOMEOWNERS",
        "COVERAGE_EFFECTIVE_DATE": "2025-04-01",
        "COVERAGE_EXPIRATION_DATE": "2026-04-01",
        "ANNUAL_PREMIUM": 1650.00,
        "POLICY_STATUS": "ACTIVE",
        "PAYMENT_STATUS": "CURRENT",
        "DEDUCTIBLE_AMOUNT": 1000.00,
        "LAST_PAYMENT_DATE": "2025-03-15",
        "RENEWAL_ELIGIBILITY_FLAG": "Y",
        "AGENT_ID": "AGT001",
        "POLICY_HOLDER_NAME": "Emily Rodriguez",
        "POLICY_HOLDER_EMAIL": "emily.r@email.com",
        "POLICY_HOLDER_PHONE": "555-0104",
        "ADDRESS_LINE_1": "321 Cedar Lane",
        "CITY": "San Antonio",
        "STATE": "TX",
        "ZIP_CODE": "78201"
    },
    "AU-77889": {
        "POLICY_NUMBER": "AU-77889",
        "POLICY_HOLDER_ID": "PH005",
        "POLICY_TYPE": "AUTO",
        "COVERAGE_EFFECTIVE_DATE": "2025-08-01",
        "COVERAGE_EXPIRATION_DATE": "2026-08-01",
        "ANNUAL_PREMIUM": 980.00,
        "POLICY_STATUS": "ACTIVE",
        "PAYMENT_STATUS": "CURRENT",
        "DEDUCTIBLE_AMOUNT": 500.00,
        "LAST_PAYMENT_DATE": "2025-07-25",
        "RENEWAL_ELIGIBILITY_FLAG": "Y",
        "AGENT_ID": "AGT002",
        "POLICY_HOLDER_NAME": "David Thompson",
        "POLICY_HOLDER_EMAIL": "d.thompson@email.com",
        "POLICY_HOLDER_PHONE": "555-0105",
        "ADDRESS_LINE_1": "654 Birch Blvd",
        "CITY": "Fort Worth",
        "STATE": "TX",
        "ZIP_CODE": "76101"
    }
}

MOCK_EXPERIENCE_RATING = {
    "HW-88712": {
        "POLICY_NUMBER": "HW-88712",
        "POLICY_TYPE": "HOMEOWNERS",
        "EFFECTIVE_YEARS": 5,
        "TOTAL_CLAIMS": 1,
        "TOTAL_INCURRED": 8500.00,
        "CLAIMS_LAST_3_YEARS": 1,
        "LOSS_RATIO": 0.092,
        "EXPERIENCE_MODIFIER": 0.95,
        "RISK_TIER": "PREFERRED",
        "RECOMMENDED_PREMIUM_ADJUSTMENT": -5.00
    },
    "HW-44521": {
        "POLICY_NUMBER": "HW-44521",
        "POLICY_TYPE": "HOMEOWNERS",
        "EFFECTIVE_YEARS": 3,
        "TOTAL_CLAIMS": 1,
        "TOTAL_INCURRED": 12000.00,
        "CLAIMS_LAST_3_YEARS": 1,
        "LOSS_RATIO": 0.190,
        "EXPERIENCE_MODIFIER": 1.05,
        "RISK_TIER": "STANDARD",
        "RECOMMENDED_PREMIUM_ADJUSTMENT": 5.00
    },
    "AU-99234": {
        "POLICY_NUMBER": "AU-99234",
        "POLICY_TYPE": "AUTO",
        "EFFECTIVE_YEARS": 1,
        "TOTAL_CLAIMS": 1,
        "TOTAL_INCURRED": 4200.00,
        "CLAIMS_LAST_3_YEARS": 1,
        "LOSS_RATIO": 0.350,
        "EXPERIENCE_MODIFIER": 1.15,
        "RISK_TIER": "STANDARD",
        "RECOMMENDED_PREMIUM_ADJUSTMENT": 15.00
    },
    "HW-55678": {
        "POLICY_NUMBER": "HW-55678",
        "POLICY_TYPE": "HOMEOWNERS",
        "EFFECTIVE_YEARS": 2,
        "TOTAL_CLAIMS": 0,
        "TOTAL_INCURRED": 0,
        "CLAIMS_LAST_3_YEARS": 0,
        "LOSS_RATIO": 0.000,
        "EXPERIENCE_MODIFIER": 0.85,
        "RISK_TIER": "PREFERRED",
        "RECOMMENDED_PREMIUM_ADJUSTMENT": -15.00
    },
    "AU-77889": {
        "POLICY_NUMBER": "AU-77889",
        "POLICY_TYPE": "AUTO",
        "EFFECTIVE_YEARS": 4,
        "TOTAL_CLAIMS": 0,
        "TOTAL_INCURRED": 0,
        "CLAIMS_LAST_3_YEARS": 0,
        "LOSS_RATIO": 0.000,
        "EXPERIENCE_MODIFIER": 0.80,
        "RISK_TIER": "PREFERRED",
        "RECOMMENDED_PREMIUM_ADJUSTMENT": -20.00
    }
}

MOCK_MARKET_RATES = {
    ("HOMEOWNERS", "TX"): {
        "POLICY_TYPE": "HOMEOWNERS",
        "STATE": "TX",
        "BASE_RATE_PER_1000": 3.50,
        "AVERAGE_PREMIUM": 1800.00,
        "MARKET_TREND_PCT": 8.5,
        "RATE_CHANGE_YTD": 3.2,
        "COMPETITIVE_QUOTE_LOW": 1500.00,
        "COMPETITIVE_QUOTE_HIGH": 2200.00
    },
    ("AUTO", "TX"): {
        "POLICY_TYPE": "AUTO",
        "STATE": "TX",
        "BASE_RATE_PER_1000": 2.80,
        "AVERAGE_PREMIUM": 1100.00,
        "MARKET_TREND_PCT": 6.5,
        "RATE_CHANGE_YTD": 2.1,
        "COMPETITIVE_QUOTE_LOW": 900.00,
        "COMPETITIVE_QUOTE_HIGH": 1400.00
    }
}

MOCK_AGENTS = {
    "AGT001": {
        "AGENT_ID": "AGT001",
        "AGENT_NAME": "Jennifer Wilson",
        "AGENT_EMAIL": "jennifer.wilson@insurance.com",
        "AGENT_PHONE": "555-1001",
        "AGENT_TERRITORY": "Dallas",
        "PRODUCER_CODE": "PROD-001"
    },
    "AGT002": {
        "AGENT_ID": "AGT002",
        "AGENT_NAME": "Robert Martinez",
        "AGENT_EMAIL": "robert.m@insurance.com",
        "AGENT_PHONE": "555-1002",
        "AGENT_TERRITORY": "Houston",
        "PRODUCER_CODE": "PROD-002"
    },
    "AGT003": {
        "AGENT_ID": "AGT003",
        "AGENT_NAME": "Lisa Brown",
        "AGENT_EMAIL": "lisa.brown@insurance.com",
        "AGENT_PHONE": "555-1003",
        "AGENT_TERRITORY": "Austin",
        "PRODUCER_CODE": "PROD-003"
    }
}

MOCK_CLAIMS = {
    "HW-88712": [
        {
            "CLAIM_ID": "CLM-001",
            "CLAIM_DATE": "2024-03-15",
            "CLAIM_TYPE": "WATER",
            "CLAIM_STATUS": "CLOSED",
            "LOSS_DESCRIPTION": "Pipe burst causing water damage",
            "TOTAL_INCURRED_AMOUNT": 8500.00,
            "PAID_AMOUNT": 8500.00,
            "RESERVES_AMOUNT": 0
        }
    ],
    "HW-44521": [
        {
            "CLAIM_ID": "CLM-002",
            "CLAIM_DATE": "2023-08-20",
            "CLAIM_TYPE": "WIND",
            "CLAIM_STATUS": "CLOSED",
            "LOSS_DESCRIPTION": "Roof damage from storm",
            "TOTAL_INCURRED_AMOUNT": 12000.00,
            "PAID_AMOUNT": 12000.00,
            "RESERVES_AMOUNT": 0
        }
    ],
    "AU-99234": [
        {
            "CLAIM_ID": "CLM-003",
            "CLAIM_DATE": "2025-01-10",
            "CLAIM_TYPE": "COLLISION",
            "CLAIM_STATUS": "CLOSED",
            "LOSS_DESCRIPTION": "Rear-end collision at intersection",
            "TOTAL_INCURRED_AMOUNT": 4200.00,
            "PAID_AMOUNT": 4200.00,
            "RESERVES_AMOUNT": 0
        }
    ]
}


def get_mock_policy(policy_number: str) -> dict:
    """Return mock policy data"""
    if policy_number in MOCK_POLICIES:
        return {"status": "success", "data": MOCK_POLICIES[policy_number]}
    return {"status": "error", "message": "Policy not found"}


def get_mock_experience_rating(policy_number: str) -> dict:
    """Return mock experience rating data"""
    if policy_number in MOCK_EXPERIENCE_RATING:
        return {"status": "success", "data": MOCK_EXPERIENCE_RATING[policy_number]}
    return {"status": "error", "message": "Experience rating not found"}


def get_mock_market_rates(policy_type: str, state: str) -> dict:
    """Return mock market rates"""
    key = (policy_type, state)
    if key in MOCK_MARKET_RATES:
        return {"status": "success", "data": MOCK_MARKET_RATES[key]}
    return {"status": "success", "data": {"policy_type": policy_type, "state": state, "market_trend_pct": 8.0}}


def get_mock_agent(agent_id: str) -> dict:
    """Return mock agent data"""
    if agent_id in MOCK_AGENTS:
        return {"status": "success", "data": MOCK_AGENTS[agent_id]}
    return {"status": "error", "message": "Agent not found"}


def get_mock_claims_history(policy_number: str) -> dict:
    """Return mock claims history"""
    claims = MOCK_CLAIMS.get(policy_number, [])
    return {"status": "success", "data": claims}


def get_mock_renewal_eligibility(policy_number: str) -> dict:
    """Return mock renewal eligibility"""
    if policy_number in MOCK_POLICIES:
        policy = MOCK_POLICIES[policy_number]
        return {
            "status": "success",
            "data": {
                "POLICY_NUMBER": policy_number,
                "POLICY_STATUS": policy["POLICY_STATUS"],
                "PAYMENT_STATUS": policy["PAYMENT_STATUS"],
                "RENEWAL_ELIGIBILITY_FLAG": policy["RENEWAL_ELIGIBILITY_FLAG"],
                "COVERAGE_EXPIRATION_DATE": policy["COVERAGE_EXPIRATION_DATE"],
                "ELIGIBILITY_STATUS": "ELIGIBLE",
                "DAYS_TO_EXPIRATION": 30
            }
        }
    return {"status": "error", "message": "Policy not found"}


def calculate_mock_renewal_premium(policy_number: str, apply_loyalty_discount: bool = True) -> dict:
    """Calculate mock renewal premium"""
    policy = MOCK_POLICIES.get(policy_number)
    if not policy:
        return {"status": "error", "message": "Policy not found"}

    current_premium = float(policy["ANNUAL_PREMIUM"])
    exp_rating = MOCK_EXPERIENCE_RATING.get(policy_number, {})
    market_trend = 8.5 if policy["POLICY_TYPE"] == "HOMEOWNERS" else 6.5
    exp_modifier = float(exp_rating.get("EXPERIENCE_MODIFIER", 1.0))
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
            "base_premium_after_market": round(base_premium, 2),
            "adjusted_premium": round(adjusted_premium, 2),
            "final_renewal_premium": round(final_premium, 2),
            "premium_change_amount": round(final_premium - current_premium, 2),
            "premium_change_pct": round(((final_premium - current_premium) / current_premium) * 100, 2)
        }
    }