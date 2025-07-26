from google import genai
from google.genai import types
from dotenv import load_dotenv
from fastmcp import Client as MCPClient
import asyncio
import ast
import json

load_dotenv()

client_geminis = genai.Client()


async def client():
    async with MCPClient("./server.py") as mcp_client:

        tools_disponibles = await mcp_client.list_tools()

        tools_info_promt = f"""
        ## Gemini Instructions (MCP)
            
            From now on, when operating within the MCP environment, follow these strict guidelines for tool usage and file management:
            ---
            ### Tool Usage
            
            * **Available Tools:** {tools_disponibles}
            * **Single Tool Format:** When you want to use a tool, type its `name` **exactly** followed by its arguments in JSON format:
                ```
                name, {{"argument": "value"}}
                ```
            * **Multiple Tool Format:** If you need to use multiple tools in a single response, place each call on a separate line, following the same format. Each action will be executed in the order you provide them:
                ```
                [
                    tool_name_1,{{"argument_1": "value_1"}}
                    tool_name_2,{{"argument_a": "value_a", "argument_b": "value_b"}}
                ]
                ```
            ---
            ### File Creation
            * **Automatic Naming:** When the user asks you to create a file and **does not specify the name**, do not ask. Instead, **invent an appropriate name** and proceed to create it directly.
        """

        while True:
            texto_usuario = input("🧑Tú: ")

            if texto_usuario.lower() in "exit": break

            response = geminis_peticion(texto_usuario, tools_info_promt)

            with open("test.txt", "w") as f:
                print(response.text)

            if isinstance(response.text, list):
                print(type(response.text))

            elif any(tool.name in response.text for tool in tools_disponibles):
                try:
                    nombre_herramienta, parametros_str = response.text.split(",", 1)
                    parametros = json.loads(parametros_str.replace("'", '"'))
                    resultado = await mcp_client.call_tool(name=nombre_herramienta.strip(), arguments=parametros)
                    print("Resultado:", resultado)
                except Exception as e:
                    print(f"Error al ejecutar herramienta: {e}")
                else:
                    print(response.text)

def geminis_peticion(texto_usuario, tools_info_promt):

    response = client_geminis.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Estas son tus instrucciones {tools_info_promt} y el susuario dijo {texto_usuario} ",
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),

    )
    return response

if __name__ == "__main__":
    asyncio.run(client())
