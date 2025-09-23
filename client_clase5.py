from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="/home/sgaleanoc/projects/curso-mcp/venv/bin/python",
    args=["server.py"],
    env=None,
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Session initialized")

            try:
                resources = await session.list_resources()
                print("Available resources:", resources)

                tools = await session.list_tools()
                print("Available tools:", tools)
                for tool in tools:
                    print("Tool:", tool)

                print("\nREADING RESOURCE")
                content, mime_type = await session.read_resource("greeting://world")
                print("Resource content:", content)
                print("Resource mime type:", mime_type)

                print("\nCALLING TOOL")
                result = await session.call_tool("add", arguments={"a": 5, "b": 3})
                print("Addition result:", result.content)
            except Exception as e:
                print(f"Error: {e}")


if __name__ == '__main__':    
    import asyncio
    asyncio.run(run())