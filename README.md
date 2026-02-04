# TikTok AI Ad Creation Agent

An AI-powered conversational agent that guides users through creating TikTok ad campaigns.  
The agent handles OAuth authentication, business rule validation, API error interpretation, and graceful failure handling.

---

## 🚀 Features

1. **OAuth2 Authentication**
   - Full TikTok Ads OAuth Authorization Code flow
   - Automatic token refresh
   - Clear error explanations

2. **Conversational Interface**
   - Step-by-step guided ad creation
   - Progress tracking
   - User-friendly prompts

3. **Business Rule Enforcement**
   - Enforces TikTok Ads requirements
   - Prevents invalid campaign submissions

4. **Music Logic Handling**
   - Supports three music scenarios with validation
   - Blocks unsupported combinations

5. **API Error Interpretation**
   - Converts API errors into actionable user guidance

6. **Graceful Failure Handling**
   - Retry logic
   - Recovery suggestions

---

## 🏗 Architecture

```
User
 ↓
Conversational AI Agent
 ↓
Validation Layer (Business Rules)
 ↓
OAuth Manager
 ↓
Mocked TikTok Ads API
```

---

## 🔐 OAuth Implementation

The agent implements the **TikTok OAuth Authorization Code flow**:

1. Generates authorization URL with required scope (`ads.manage`)
2. Redirects user to TikTok authentication
3. Receives authorization code from callback
4. Exchanges code for an access token
5. Stores token for API usage
6. Automatically refreshes token when expired

### Error Handling

| Error Type | Behavior |
|----------|----------|
| Invalid client credentials | Suggest checking TikTok App settings |
| Missing permission scope | Guide user to enable `ads.manage` |
| Token expired | Attempt automatic refresh |
| Geo-restriction | Explain regional limitations |

---

## 🧠 Prompt Design

### System Prompt Structure

The LLM system prompt:

- Defines the assistant role and responsibilities
- Enforces conversation flow
- Applies business logic rules (music rules, character limits)
- Requires structured JSON output

---

## 📦 Structured Output Format

```json
{
  "user_message": "Response to show user",
  "internal_reasoning": "Agent's decision-making process",
  "collected_data": {
    "campaign_name": "",
    "objective": "",
    "ad_text": "",
    "cta": "",
    "music_option": "",
    "music_id": ""
  },
  "next_step": "Field to collect next or 'validation'"
}
```

---

## ✅ Business Rule Enforcement

### Campaign Rules

- **Campaign Name**: Minimum 3 characters
- **Objective**: Only `TRAFFIC` or `CONVERSIONS`
- **Ad Text**: Required, maximum 100 characters
- **CTA**: Required

---

## 🎵 Music Logic

Three supported music scenarios:

1. **Existing Music ID**
   - Validated via TikTok API
   - Submission blocked if invalid

2. **Custom Music**
   - Simulated upload process
   - Randomized failure handling

3. **No Music**
   - Allowed only for `TRAFFIC`
   - Blocked for `CONVERSIONS`

---

## 🧪 API Assumptions & Mocks

All TikTok API calls are mocked for this assignment.

### Mocked Endpoints

- Music ID validation
- Custom music upload
- Campaign submission

### Error Simulation Rates

| Scenario | Probability |
|--------|------------|
| Invalid OAuth token | 15% |
| Missing permissions | 10% |
| Geo-restriction | 5% |
| Invalid music ID | 10% |
| Success | 60% |

---

## 🛠 Installation & Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation Steps

```bash
git clone https://github.com/yourusername/tiktok-ad-agent.git
cd tiktok-ad-agent
```

```bash
pip install -r requirements.txt
```

```bash
cp .env.example .env
# Add your OpenAI API key to .env
```


```bash
# NVIDIA NIM Configuration
# Your API key (the one you provided or get new from https://build.nvidia.com/)
NVIDIA_API_KEY=enter_your_api_key

# NVIDIA NIM Endpoint
NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1

# Choose a model (using your example model)
NVIDIA_MODEL=nvidia/nemotron-3-nano-30b-a3b

# TikTok Configuration (Mocked)
TIKTOK_CLIENT_ID=mock_client_id
TIKTOK_CLIENT_SECRET=mock_client_secret
```


```bash
python app.py
```

---

## ▶️ Usage Example

```
TikTok AI Ad Creation Agent
============================================================

TikTok Ads Authentication
============================================================

1. Redirecting to TikTok for authentication...
   Auth URL: https://ads.tiktok.com/marketing_api/auth/authorize?...

2. Please enter the authorization code from the callback URL:
   (Use 'valid_code' for success, 'invalid_client' for error)

   Authorization code: valid_code

✓ Authentication successful

TikTok Ad Creation
============================================================

Hello! I'll help you create a TikTok ad campaign...

[Progress: 1/6 fields collected]
```

---

## 📌 Notes

- This project uses **mocked TikTok APIs**
- Designed for **demonstration and evaluation purposes**
- Easily extendable to real TikTok Ads API integration

---


