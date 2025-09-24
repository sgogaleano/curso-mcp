import os
from dotenv import load_dotenv
load_dotenv()


from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, ToolMessage
from azure.core.credentials import AzureKeyCredential
import json
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="/home/sgaleanoc/projects/curso-mcp/venv/bin/python",
    args=["server.py"],
    env=None,
)

def convert_to_llm_tool(tool):
    tool_schema = {
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "type": "function",
            "parameters": {
                "type": "object",
                "properties": tool.inputSchema["properties"],
                "required": tool.inputSchema.get("required", [])
            }
        }
    }
    return tool_schema

def call_llm(prompt, functions):
    token = os.getenv("AZURE_API_KEY")  # Get token from environment variable
    endpoint = os.getenv("AZURE_ENDPOINT", "https://models.inference.ai.azure.com")

    model_name = "gpt-4"

    client = ChatCompletionsClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(token)
    )

    print("Calling LLM")
    response = client.complete(
        messages=[
            {
            "role": "system",
            "content": "You are a helpful assistant that helps people find information. When asked about calculations, use the available tools."
            },
            {"role": "user",
             "content": prompt
            },
        ],
        model=model_name,
        tools=functions,
        temperature=0.7,
        max_tokens=1000,
        top_p=0.95,
        tool_choice="auto"  # Enable automatic tool selection
    )
    
    # Extract and return function calls from the response
    function_calls = []
    if response.choices and hasattr(response.choices[0], 'message'):
        message = response.choices[0].message
        if hasattr(message, 'function_call'):
            # Handle single function call
            function_calls.append({
                "name": message.function_call.name,
                "arguments": json.loads(message.function_call.arguments)
            })
        elif hasattr(message, 'tool_calls'):
            # Handle multiple tool calls
            for tool_call in message.tool_calls:
                if hasattr(tool_call, 'function'):
                    function_calls.append({
                        "name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    })
    return function_calls

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
                for tool in tools.tools:  # Access the tools list from the response
                    print("Tool:", tool)

                print("\nREADING RESOURCE")
                content, mime_type = await session.read_resource("greeting://hello")
                

                print("\nCALLING TOOL")
                result = await session.call_tool("add", arguments={"a": 1, "b": 7})
                print("Addition result:", result.content)

                functions = []
                
                for tool in tools.tools:  # Access the tools list from the response
                    print("Tool: ", tool.name)
                    print("Tool", tool.inputSchema["properties"])
                    functions.append(convert_to_llm_tool(tool))

                prompt = "What is the sum of 1 and 7?"

                function_call = call_llm(prompt, functions)

                for f in function_call:
                    result = await session.call_tool(f["name"], arguments=f["arguments"])
                    print("TOOLS result: ", result.content)

            except Exception as e:
                print(f"Error: {e}")


if __name__ == '__main__':    
    import asyncio
    asyncio.run(run())