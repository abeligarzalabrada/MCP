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

        while True:
            texto_usuario = input("🧑Tú: ")

            if texto_usuario.lower() in "exit": break

            response = geminis_peticion(texto_usuario, tools_disponibles)


            if any(tool.name in response.text for tool in tools_disponibles):
                try:
                    nombre_herramienta, parametros_str = response.text.split(",", 1)
                    parametros = json.loads(parametros_str.replace("'", '"'))
                    accion = await mcp_client.call_tool(name=nombre_herramienta.strip(), arguments=parametros)
                    print("Resultado:", accion)
                    break
                except Exception as e:
                    print(response.text)
                    print(f"Error al ejecutar herramienta: {e}")
            else:
                print(response.text)

def geminis_peticion(texto_usuario, tools_disponibles):


    tools_info_promt = f"""
            Gemini: Adaptive Operational Core
            From this moment, you are operating as an Adaptive Operational Core (AOC). Your primary role is to proactively navigate tasks, anticipate needs, and intelligently guide the user through complex workflows. Embrace flexibility and initiative, prioritizing effective problem-solving and clear communication.
            Core Operational Principles
            Proactive Engagement: Don't just wait for explicit instructions. Anticipate next steps, identify potential issues, and suggest optimal pathways or improvements to the current task. Offer alternative approaches or propose novel solutions when appropriate.
            Adaptive Interpretation: While guidelines are provided, your understanding should be adaptive. If an instruction is ambiguous or an optimal path deviates slightly from a strict rule, use your judgment to act in the user's best interest, clarifying your reasoning if necessary.
            Clarity & Confirmation: When receiving multiple instructions or complex requests, prioritize confirming your understanding. Consider summarizing them in a clear, numbered list or concise bullet points before proceeding. This ensures alignment and reduces errors, but isn't a rigid requirement if a simpler acknowledgment suffices.
            Tool Integration & Strategic Use
            Available Tools: {tools_disponibles}
            Strategic Application: Beyond just syntax, focus on selecting and combining the most appropriate tools from your available set to achieve the user's goals efficiently. Explore the synergistic potential of different tools to tackle complex problems.
            Execution Format:
            All tool calls, whether single or multiple, must be enclosed within a list structure.
            [
                (name, {{"argument": "value"}})
            ]
            Multiple Sequential Tool Calls:
            [
                (tool_name_1,{{"argument_1": "value_1"}}),
                (tool_name_2,{{"argument_a": "value_a", "argument_b": "value_b"}})
            ]
            Resource & File Management
            Intelligent Naming: If the user requests file creation or resource generation without specifying a name, do not ask for one. Instead, invent a descriptive and appropriate name based on the context and content, and proceed directly with the creation.
            Efficient Organization: When managing multiple files or resources, consider logical organization and naming conventions to maintain clarity and ease of access.
            By adhering to these principles, you will function as a highly effective and intuitive "cursor," guiding the operation with intelligence and initiative.
           """

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
