import os
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("AZURE_AI_API_KEY")
ENDPOINT = os.getenv("AZURE_AI_ENDPOINT")
DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")

#Importar librerías necesarias
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, ToolMessage
from azure.core.credentials import AzureKeyCredential
import json
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

# Convertir funciones del servidor al formato LLM
def convert_to_llm_tool():
    return {
        "name": "add",
        "description": "Suma dos números",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer", "description": "Primer número"},
                "b": {"type": "integer", "description": "Segundo número"}
            },
            "required": ["a", "b"]
        }
    }

# Llamar al modelo de lenguaje con las funciones disponibles
def call_llm(prompt: str, functions: list):
    client = ChatCompletionsClient(ENDPOINT, AzureKeyCredential(API_KEY))
    messages = [{"role": "user", "content": prompt}]
    tools = [{"type": "function", "function": f} for f in functions]

    response = client.complete(
        model=DEPLOYMENT_NAME,  # Para Azure OpenAI usa deployment_name
        messages=messages,
        tools=tools
    )

    return response.choices[0].message.tool_calls

#Integrar todo
if __name__ == "__main__":
    prompt = "Agrega 2 a 20"
    tools = [convert_to_llm_tool()]

    print("Llamando al modelo de lenguaje...")
    tool_calls = call_llm(prompt, tools)

    if tool_calls:
        for call in tool_calls:
            print("Respuesta del modelo:")
            print(json.dumps(call, indent=2))
    else:
        print("No se obtuvo respuesta.")