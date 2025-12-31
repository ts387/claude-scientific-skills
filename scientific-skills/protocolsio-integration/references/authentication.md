# Protocols.io Authentication

## Overview

The protocols.io API supports two types of access tokens for authentication, enabling access to both public and private content.

## Quick Start: One-Time Setup

For the easiest experience, use the setup script to configure your token once, then it will be automatically loaded for all future uses:

### Step 1: Get Your Access Token

1. Log into protocols.io at https://www.protocols.io/
2. Go to your **Profile Settings** (click your profile picture → Settings)
3. Look for the **API** or **Developer** section
4. Copy your **CLIENT_ACCESS_TOKEN**

### Step 2: Run the Setup Script

```bash
cd scientific-skills/protocolsio-integration/scripts
python setup_config.py --token YOUR_TOKEN_HERE
```

This will:
- Save your token securely (file permissions set to 600)
- Test that the token works
- Configure automatic loading for future uses

### Step 3: Use the Client

Now you can use the `protocols_client.py` module without entering your token each time:

```python
from protocols_client import ProtocolsClient

# Token is loaded automatically!
client = ProtocolsClient()

# Search for protocols
results = client.search_protocols(key="CRISPR")

# Get a protocol
protocol = client.get_protocol(protocol_id=12345)
```

**That's it!** Your token is now configured and will be automatically loaded.

## Access Token Types

### 1. CLIENT_ACCESS_TOKEN

- **Purpose**: Enables access to public content and the private content of the client user
- **Use case**: When accessing your own protocols and public protocols
- **Scope**: Limited to the token owner's private content plus all public content

### 2. OAUTH_ACCESS_TOKEN

- **Purpose**: Grants access to specific users' private content plus all public content
- **Use case**: When building applications that need to access other users' content with their permission
- **Scope**: Full access to authorized user's private content plus all public content

## Authentication Header

All API requests must include an Authorization header:

```
Authorization: Bearer [ACCESS_TOKEN]
```

## OAuth Flow

### Step 1: Generate Authorization Link

Direct users to the authorization URL to grant access:

```
GET https://protocols.io/api/v3/oauth/authorize
```

**Parameters:**
- `client_id` (required): Your application's client ID
- `redirect_uri` (required): URL to redirect users after authorization
- `response_type` (required): Set to "code"
- `state` (optional but recommended): Random string to prevent CSRF attacks

**Example:**
```
https://protocols.io/api/v3/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&response_type=code&state=RANDOM_STRING
```

### Step 2: Exchange Authorization Code for Token

After user authorization, protocols.io redirects to your `redirect_uri` with an authorization code. Exchange this code for an access token:

```
POST https://protocols.io/api/v3/oauth/token
```

**Parameters:**
- `grant_type`: Set to "authorization_code"
- `code`: The authorization code received
- `client_id`: Your application's client ID
- `client_secret`: Your application's client secret
- `redirect_uri`: Must match the redirect_uri used in Step 1

**Response includes:**
- `access_token`: The OAuth access token to use for API requests
- `token_type`: "Bearer"
- `expires_in`: Token lifetime in seconds (typically 1 year)
- `refresh_token`: Token for refreshing the access token

### Step 3: Refresh Access Token

Before the access token expires (typically 1 year), use the refresh token to obtain a new access token:

```
POST https://protocols.io/api/v3/oauth/token
```

**Parameters:**
- `grant_type`: Set to "refresh_token"
- `refresh_token`: The refresh token received in Step 2
- `client_id`: Your application's client ID
- `client_secret`: Your application's client secret

## Rate Limits

Be aware of rate limiting when making API requests:

- **Standard endpoints**: 100 requests per minute per user
- **PDF endpoint** (`/view/[protocol-uri].pdf`):
  - Signed-in users: 5 requests per minute
  - Unsigned users: 3 requests per minute

## Best Practices

1. **Store tokens securely**: Never expose access tokens in client-side code or version control
2. **Handle token expiration**: Implement automatic token refresh before expiration
3. **Respect rate limits**: Implement exponential backoff for rate limit errors
4. **Use state parameter**: Always include a state parameter in OAuth flow for security
5. **Validate redirect_uri**: Ensure redirect URIs match exactly between authorization and token requests
