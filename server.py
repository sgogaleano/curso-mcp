from starlette.applications import Starlette
from starlette.routing import Mount, Host
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("SEE Platzi")

app = Starlette(
        routes=[
            Mount('/', app=mcp.sse_app()),
        ]
    )


@mcp.tool()
def add(a: float, b: float) -> float:
    """Suma dos números y devuelve el resultado."""
    return a + b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Resta dos números y devuelve el resultado."""
    return a - b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplica dos números y devuelve el resultado."""
    return a * b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divide dos números y devuelve el resultado.
    
    Error:
        ValueError: Si b es cero, se lanza un error de división por cero.
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b