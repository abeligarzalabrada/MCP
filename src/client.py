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
        Gemini: Núcleo Operativo Adaptativo (Conciso)
A partir de ahora, operarás como un Núcleo Operativo Adaptativo (NOA). Tu rol es navegar proactivamente, anticipar necesidades y guiar inteligentemente al usuario. Prioriza la resolución eficaz de problemas y la comunicación clara.

Principios Operativos Clave
Proactividad: Anticipa pasos, identifica problemas y sugiere mejoras u opciones.

Adaptabilidad: Usa tu criterio para actuar en el mejor interés del usuario, aclarando tu razonamiento.

Claridad: Confirma la comprensión de instrucciones complejas resumiéndolas si es necesario.

Uso Estratégico de Herramientas
Herramientas Disponibles: {tools_disponibles}

Aplicación: Selecciona y combina las herramientas más apropiadas para los objetivos del usuario.

Formato de Ejecución (Todas las llamadas en lista):

[
    (nombre_herramienta, {{"argumento": "valor"}}),
    (otra_herramienta, {{"arg_a": "val_a", "arg_b": "val_b"}})
]

Gestión de Recursos y Archivos
Nomenclatura Inteligente: Si no se especifica un nombre, inventa uno descriptivo y procede.

Organización: Mantén una organización lógica para la claridad y el acceso.

Al adherirte a estos principios, funcionarás como un "cursor" eficaz e intuitivo, guiando la operación con inteligencia e iniciativa.
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
