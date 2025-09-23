from mcp.server.fastmcp import FastMCP

# Create an MCP server instance
server = FastMCP("Demo")

# Add on addition tool
@server.tool()
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b 

# Add a dynamic greeting resource
@server.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"

if __name__ == '__main__':    
    server.run()