import logging
import sys
from fastapi import FastAPI, Request, Depends
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount
from weather import mcp
from api_key_auth import ensure_valid_api_key
import uvicorn


# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)
logger.info("App starting up...")

app = FastAPI(docs_url=None, redoc_url=None, dependencies=[Depends(ensure_valid_api_key)])

sse = SseServerTransport("/messages/")
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))


@app.get("/sse", tags=["MCP"])
async def handle_sse(request: Request):
    logger.info("/sse endpoint called")
    try:
        async with sse.connect_sse(request.scope, request.receive, request._send) as (
            read_stream,
            write_stream,
        ):
            logger.info("SSE connection established")
            init_options = mcp._mcp_server.create_initialization_options()
            logger.info("Initialization options created")
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                init_options,
            )
            logger.info("mcp._mcp_server.run completed")
    except Exception as e:
        logger.error(f"Error in /sse handler: {e}")
        raise


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)