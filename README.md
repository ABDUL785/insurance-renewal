# Insurance Renewal Intelligence Agent - Demo

A demonstration of an AI Agent with MCP (Model Context Protocol) servers for insurance policy renewal processing, built on Snowflake data warehouse.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    INSURANCE RENEWAL AGENT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Policy   │    │Experience│    │ Pricing  │    │Document  │  │
│  │ Verify   │───▶│ Rating   │───▶│ Engine   │───▶│Generate  │  │
│  │ Skill    │    │ Skill    │    │ Skill    │    │ Skill    │  │
│  └────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘  │
│       │               │               │               │         │
│       ▼               ▼               ▼               ▼         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │Snowflake │    │Snowflake │    │Snowflake │    │ Document │  │
│  │   MCP    │    │   MCP    │    │   MCP    │    │   MCP    │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                                                              │  │
│                                 ┌──────────┐                 │  │
│                                 │Communicat│◀────────────────┘  │
│                                 │   MCP    │                   │
│                                 └──────────┘                   │
│                                                              │
└─────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
demo_insurance_agent/
├── agent/
│   └── renewal_agent.py           # Main agent orchestration
├── mcp_servers/
│   ├── snowflake_mcp.py           # Snowflake MCP server (tools)
│   ├── document_mcp.py            # Document generation MCP server
│   └── communication_mcp.py       # Communication MCP server
├── skills/                        # Skill definitions (YAML)
├── ui/
│   └── app.py                     # Streamlit demo UI
├── sql/
│   └── setup_snowflake.sql        # Snowflake schema setup
├── data/
│   └── mock_data.py               # Mock data for demo without Snowflake
├── agent_config.yaml              # Agent configuration
└── requirements.txt               # Python dependencies
```

## Features

- **5-Step Renewal Pipeline**: Verifies policy → Analyzes experience → Calculates premium → Generates documents → Sends notifications
- **3 MCP Servers**: Snowflake (data), Document (PDF generation), Communication (email/SMS/portal)
- **Real-time Processing Log**: See each step as it executes
- **Batch Processing**: Process multiple renewals at once
- **Demo Mode**: Works without Snowflake connection using mock data

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Setup Snowflake

Run the SQL script in `sql/setup_snowflake.sql` to create the schema and sample data:

```sql
-- In Snowflake worksheet
@setup_snowflake.sql
```

Set environment variables:
```bash
export SNOWFLAKE_ACCOUNT=your_account
export SNOWFLAKE_USER=your_user
export SNOWFLAKE_PASSWORD=your_password
export SNOWFLAKE_WAREHOUSE=COMPUTE_WH
export SNOWFLAKE_DATABASE=INSURANCE_DW
```

### 3. Run the Demo UI

```bash
cd ui
streamlit run app.py
```

### 4. Or Run the Agent Directly (No UI)

```bash
python agent/renewal_agent.py
```

## Demo Scenarios

### Scenario 1: Single Policy Renewal
```
User: "Process renewal for HW-88712"
Agent:
  Step 1: Policy Verification → Active, Current payment
  Step 2: Experience Rating → Preferred tier, 0.95 modifier
  Step 3: Pricing Engine → Market +8.5%, Final $1,957
  Step 4: Document Generation → Quote PDF generated
  Step 5: Communication → Email + SMS sent to John Anderson
```

### Scenario 2: Batch Processing
```
User: "Process renewals for HW-88712, HW-44521, AU-99234"
Agent processes all three in sequence, returns summary
```

### Scenario 3: View Processing Logs
```
User: "Show me the processing steps"
Agent displays full audit trail of all MCP calls
```

## Available MCP Tools

### Snowflake MCP Server
| Tool | Description |
|------|-------------|
| `get_policy` | Fetch policy details by policy number |
| `get_renewal_eligibility` | Check if policy is eligible for renewal |
| `get_claims_history` | Fetch claims history for experience rating |
| `calculate_experience_rating` | Get experience modifier and risk tier |
| `get_market_rates` | Get current market rates by policy type/state |
| `calculate_renewal_premium` | Calculate final renewal premium with all adjustments |
| `get_agent_info` | Fetch agent details for communication |
| `list_pending_renewals` | List all policies up for renewal in window |

### Document MCP Server
| Tool | Description |
|------|-------------|
| `generate_renewal_quote` | Create renewal quote PDF |
| `generate_coverage_comparison` | Create coverage comparison document |

### Communication MCP Server
| Tool | Description |
|------|-------------|
| `send_email` | Send email notification |
| `send_sms` | Send SMS notification |
| `update_portal` | Post notification to customer portal |
| `send_renewal_notification` | Send comprehensive notification via all channels |

## Example Output

```
======================================================================
INSURANCE RENEWAL AGENT - Processing HW-88712
======================================================================

[Step 1] Verifying Policy Eligibility...
----------------------------------------
Status: SUCCESS - Fields: POLICY_NUMBER, ELIGIBILITY_STATUS

[Step 2] Fetching Policy Details...
----------------------------------------
Status: SUCCESS - Fields: POLICY_NUMBER, POLICY_HOLDER_NAME

[Step 3] Analyzing Experience Rating & Claims History...
----------------------------------------
Status: SUCCESS - Fields: RISK_TIER, EXPERIENCE_MODIFIER

[Step 4] Calculating Market Rates & Premium...
----------------------------------------
Status: SUCCESS - Fields: final_renewal_premium, premium_change_pct

[Step 5] Generating Renewal Quote Document...
----------------------------------------
Status: SUCCESS - Fields: document_type, pdf_base64

[Step 6] Sending Notifications...
----------------------------------------
Status: SUCCESS - Fields: total_messages

======================================================================
FINAL RESPONSE:
======================================================================
{
  "summary": "Policy HW-88712 renewal processed successfully.",
  "policy_holder": "John Anderson",
  "current_premium": "$1,850.00",
  "renewal_premium": "$1,957.25",
  "premium_change": "+5.8%",
  "loyalty_discount": "5% applied",
  "risk_tier": "PREFERRED",
  "claims_history": "1 claims in last 3 years",
  "expiration_date": "2026-06-01",
  "notifications_sent": true,
  "quote_document": "Generated",
  "status": "SUCCESS"
}
```

## Extending the Agent

Add new skills by:
1. Creating a new MCP server in `mcp_servers/`
2. Adding skill configuration to `agent_config.yaml`
3. Implementing the skill logic in `renewal_agent.py`

## Tech Stack

- **Agent Framework**: Custom Python orchestration
- **MCP Protocol**: Model Context Protocol for tool discovery
- **Data Warehouse**: Snowflake
- **UI**: Streamlit
- **Document Generation**: ReportLab
- **Mock Data**: JSON fixtures for demo mode