# 🚀 Quick Start: Deploy MCP Server on Render

Deploy your Deep Research MCP Server on Render in just a few minutes!

## ⚡ 5-Minute Setup

### Step 1: Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Render Account
- Go to [render.com](https://render.com)
- Sign up with your GitHub account
- Authorize Render to access your repositories

### Step 3: Deploy Your Service
1. Click **"New +"** → **"Web Service"**
2. Select your repository
3. Configure settings:
   ```
   Name: deep-research-mcp-server
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python -m src.mcp_server.server
   ```

### Step 4: Add Environment Variables
Click **"Advanced"** → **"Environment Variables"**:
```
GEMINI_API_KEY = your_gemini_api_key_here
```

### Step 5: Deploy
Click **"Create Web Service"** and wait 5-10 minutes for deployment.

## 🧪 Test Your Deployment

```bash
# Install test dependencies
pip install httpx fastmcp

# Test your server
python test_render_deployment.py https://your-service-name.onrender.com
```

## 🔗 Connect to Claude Desktop

Add to your Claude Desktop config:
```json
{
  "mcpServers": {
    "deep-research": {
      "url": "https://your-service-name.onrender.com/mcp/"
    }
  }
}
```

## 📋 Required Files

✅ **requirements.txt** - Python dependencies
✅ **render.yaml** - Render configuration
✅ **src/mcp_server/server.py** - Main server file
✅ **test_render_deployment.py** - Test script

## 🎉 That's It!

Your MCP server is now live at:
`https://your-service-name.onrender.com/mcp/`

---

🔧 **Need help?** See the full [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md) for detailed instructions. 