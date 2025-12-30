# Azure Container Apps MCP Server - Troubleshooting Guide

## Current Issue: 504 Timeout on /sse endpoint

### Root Causes Identified:

1. **Missing Environment Variable**: The `API_KEYS` environment variable is not set in Azure Container Apps
2. **Code Issue Fixed**: Indentation error in `main.py` (already fixed)

### Solution Steps:

#### 1. Set the API_KEYS Environment Variable in Azure

Run this command to update your Azure Container App with the required environment variable:

```bash
az containerapp update \
  --name testmcpgaleano \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --set-env-vars API_KEYS=t3stCl1m4MCP001
```

Or use the Azure Portal:
1. Go to Azure Portal → Container Apps
2. Select your app: `testmcpgaleano`
3. Go to "Containers" → "Environment variables"
4. Add: `API_KEYS` = `t3stCl1m4MCP001`
5. Save and restart

#### 2. Verify the Deployment

Check if the container is running:
```bash
az containerapp show \
  --name testmcpgaleano \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --query "properties.runningStatus"
```

Check container logs:
```bash
az containerapp logs show \
  --name testmcpgaleano \
  --resource-group <YOUR_RESOURCE_GROUP> \
  --follow
```

#### 3. Test the Endpoint

After setting the environment variable, test:
```bash
curl -v -H "x-api-key: t3stCl1m4MCP001" \
  https://testmcpgaleano.wittyhill-1fbd292d.eastus2.azurecontainerapps.io/sse
```

#### 4. Redeploy (if needed)

If the above doesn't work, redeploy with the fixed code:

```bash
cd clase10/azure-container-apps-mcp-sample
az containerapp up \
  -g <YOUR_RESOURCE_GROUP> \
  -n testmcpgaleano \
  --environment mcp \
  -l eastus2 \
  --env-vars API_KEYS=t3stCl1m4MCP001 \
  --source .
```

### Additional Checks:

1. **Container Health**: Ensure the container is not crashing
   ```bash
   az containerapp revision list \
     --name testmcpgaleano \
     --resource-group <YOUR_RESOURCE_GROUP> \
     --query "[].{Name:name, Active:properties.active, Health:properties.healthState}"
   ```

2. **Increase Timeout** (if still timing out): Add to `.vscode/mcp.json`:
   ```json
   {
       "servers": {
           "testmcpgaleano": {
               "type": "sse",
               "url": "https://testmcpgaleano.wittyhill-1fbd292d.eastus2.azurecontainerapps.io/sse",
               "headers": {
                   "x-api-key": "t3stCl1m4MCP001"
               },
               "timeout": 30000
           }
       }
   }
   ```

3. **Check Container Startup**: The container might be taking too long to start. Consider:
   - Using a smaller base image
   - Pre-building dependencies
   - Enabling "Always On" in Azure Container Apps

### Expected Behavior:

Once fixed, you should see in the logs:
```
App starting up...
/sse endpoint called
SSE connection established
Initialization options created
```

And VS Code should successfully connect to the MCP server.
