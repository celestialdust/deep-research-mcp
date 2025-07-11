# 🚀 Deploy Deep Research MCP Server on Render

This guide provides step-by-step instructions for deploying your Deep Research MCP Server on Render.

## 🌟 Why Render?

- **Free Tier**: 750 hours/month free hosting
- **Zero Config**: Minimal setup required
- **Auto-Deploy**: Automatic deployments from GitHub
- **HTTPS**: Free SSL certificates
- **Scaling**: Automatic scaling based on traffic
- **Global CDN**: Fast performance worldwide

## 📋 Prerequisites

Before you begin, ensure you have:

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Render Account**: Create a free account at [render.com](https://render.com)
3. **Gemini API Key**: Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

## 🔧 Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Verify required files exist**:
   - ✅ `requirements.txt` (dependencies)
   - ✅ `render.yaml` (deployment config)
   - ✅ `src/mcp_server/server.py` (main server file)

## 🌐 Step 2: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **"Get Started"**
3. Sign up using your GitHub account
4. Authorize Render to access your repositories

## 🚀 Step 3: Deploy Your Service

### Option A: Using Render Dashboard (Recommended)

1. **Create New Web Service**:
   - Click **"New +"** → **"Web Service"**
   - Connect your GitHub repository
   - Select your `deep-research-mcp` repository

2. **Configure Service Settings**:
   ```
   Name: deep-research-mcp-server
   Region: Oregon (US-West) or nearest to you
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python -m src.mcp_server.server
   ```

3. **Set Environment Variables**:
   Click **"Advanced"** → **"Environment Variables"**:
   ```
   GEMINI_API_KEY = your_gemini_api_key_here
   HOST = 0.0.0.0
   LOG_LEVEL = INFO
   MAX_CONCURRENT_REQUESTS = 10
   DEFAULT_MAX_RESEARCH_LOOPS = 2
   DEFAULT_INITIAL_SEARCH_QUERY_COUNT = 3
   DEFAULT_REASONING_MODEL = gemini-2.5-pro
   REQUEST_TIMEOUT = 300
   ```

4. **Deploy**:
   - Click **"Create Web Service"**
   - Wait for deployment to complete (5-10 minutes)

### Option B: Using Blueprint (render.yaml)

1. **Deploy from Blueprint**:
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click **"New +"** → **"Blueprint"**
   - Connect your repository
   - Render will automatically detect `render.yaml`

2. **Set Secret Environment Variables**:
   - After deployment, go to your service settings
   - Add `GEMINI_API_KEY` in Environment Variables

## 🔑 Step 4: Configure API Keys

1. **Get Your Gemini API Key**:
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Create a new API key
   - Copy the key

2. **Add to Render**:
   - Go to your service dashboard
   - Click **"Environment"** tab
   - Add environment variable:
     ```
     Key: GEMINI_API_KEY
     Value: your_api_key_here
     ```
   - Click **"Save Changes"**

## ✅ Step 5: Test Your Deployment

1. **Check Service Health**:
   - Your service URL: `https://your-service-name.onrender.com`
   - Health check: `https://your-service-name.onrender.com/health`

2. **Test MCP Connection**:
   ```bash
   curl -X GET "https://your-service-name.onrender.com/health"
   ```

3. **Expected Response**:
   ```json
   {
     "status": "healthy",
     "service": "Deep Research MCP Server",
     "version": "1.0.0",
     "agent_status": "ready"
   }
   ```

## 🔧 Step 6: Connect to Your MCP Server

### For Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "deep-research": {
      "url": "https://your-service-name.onrender.com/mcp/"
    }
  }
}
```

### For FastMCP Client

```python
import asyncio
from fastmcp import Client

async def test_server():
    client = Client("https://your-service-name.onrender.com/mcp/")
    async with client:
        result = await client.call_tool("research", {
            "topic": "What are the latest developments in AI?"
        })
        print(result)

asyncio.run(test_server())
```

## 🛠️ Configuration Options

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | **Required** | Your Google Gemini API key |
| `HOST` | `0.0.0.0` | Server host address |
| `PORT` | `10000` | Server port (auto-assigned by Render) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MAX_CONCURRENT_REQUESTS` | `10` | Max concurrent research requests |
| `DEFAULT_MAX_RESEARCH_LOOPS` | `2` | Default research iterations |
| `DEFAULT_INITIAL_SEARCH_QUERY_COUNT` | `3` | Default initial search queries |
| `DEFAULT_REASONING_MODEL` | `gemini-2.5-pro` | Default AI model |
| `REQUEST_TIMEOUT` | `300` | Request timeout in seconds |

### Render Service Settings

- **Plan**: Free (750 hours/month)
- **Region**: Choose closest to your users
- **Auto-Deploy**: Enabled for main branch
- **Health Check**: `/health` endpoint
- **Build Time**: ~5-10 minutes
- **Cold Start**: ~10-30 seconds

## 📊 Monitoring and Logs

1. **View Logs**:
   - Go to your service dashboard
   - Click **"Logs"** tab
   - Monitor real-time logs

2. **Monitor Performance**:
   - Check **"Metrics"** tab
   - Monitor CPU and memory usage
   - Track request rates

3. **Set Up Alerts**:
   - Configure notifications for downtime
   - Set up email/Slack alerts

## 🐛 Troubleshooting

### Common Issues

1. **Build Failures**:
   ```bash
   # Check requirements.txt for typos
   # Verify Python version compatibility
   # Check build logs for specific errors
   ```

2. **API Key Issues**:
   ```bash
   # Verify GEMINI_API_KEY is set correctly
   # Check API key permissions
   # Test key locally first
   ```

3. **Port Issues**:
   ```bash
   # Ensure your server uses PORT environment variable
   # Don't hardcode port numbers
   ```

4. **Memory Issues**:
   ```bash
   # Monitor memory usage in Render dashboard
   # Consider upgrading to paid plan for more resources
   ```

### Debug Commands

```bash
# Check environment variables
curl "https://your-service-name.onrender.com/health"

# Test research functionality
curl -X POST "https://your-service-name.onrender.com/mcp/" \
  -H "Content-Type: application/json" \
  -d '{"topic": "test research"}'
```

## 🔄 Updates and Maintenance

1. **Auto-Deploy**:
   - Push to main branch triggers automatic deployment
   - Monitor deployment status in Render dashboard

2. **Manual Deploy**:
   - Click **"Manual Deploy"** → **"Deploy latest commit"**

3. **Rollback**:
   - Use **"Rollback"** button in dashboard
   - Select previous successful deployment

## 💰 Cost Considerations

### Free Tier Limits:
- **750 hours/month** (about 31 days)
- **0.5 CPU / 512MB RAM**
- **Sleeps after 15 minutes** of inactivity
- **Cold start delay** (~10-30 seconds)

### Paid Plans:
- **$7/month**: Always-on, faster performance
- **$25/month**: 1 CPU, 2GB RAM
- **$85/month**: 2 CPU, 4GB RAM

## 🎯 Optimization Tips

1. **Performance**:
   - Use caching for repeated requests
   - Optimize Docker image size
   - Monitor resource usage

2. **Cost**:
   - Use free tier for development
   - Upgrade to paid for production
   - Monitor usage patterns

3. **Reliability**:
   - Implement proper error handling
   - Use health checks
   - Set up monitoring alerts

## 🔗 Useful Links

- [Render Documentation](https://render.com/docs)
- [FastMCP Documentation](https://gofastmcp.com)
- [Google AI Studio](https://aistudio.google.com)
- [Python on Render](https://render.com/docs/python)

## 🆘 Support

If you encounter issues:

1. Check the [Render Community Forum](https://community.render.com)
2. Review [Render Documentation](https://render.com/docs)
3. Submit issues to the project GitHub repository

---

**🎉 Congratulations! Your Deep Research MCP Server is now deployed on Render!**

You can now access your server at: `https://your-service-name.onrender.com/mcp/` 