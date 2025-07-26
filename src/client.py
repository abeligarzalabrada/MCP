from google import genai
from google.genai import types
from dotenv import load_dotenv
from fastmcp import Client as MCPClient
import asyncio
import ast

load_dotenv()

async def client():

    async with MCPClient("./server.py") as mcp_client:

        tools_disponibles = await mcp_client.list_tools()


        tools_info_promt = f"""
        Herramientas disponibles: : {tools_disponibles}

        Cuando quieras usar una herramienta, escribe exactamente:
            nombre,{{"argumento": "valor"}}
        
        Genera una lista de herramientas en formato Python. Cada herramienta debe ser una tupla que contenga el nombre de la herramienta (como una cadena) y un diccionario de sus argumentos. Si hay más de una herramienta, sepáralas con comas dentro de la lista principal. La salida completa debe ser una lista de Python, debe estar entre [] siempre, escribelo exactamente asi: [(nombre, {{"argumento": "valor"}}), (nombre, {{"argumento": "valor"}})]
        Ejemplo de lo que espero para dos herramientas:
        [(herramienta_uno, {{"parametro1": "valor1"}}), (herramienta_dos, {{"parametroA": "valorA"}})]
        Cuando el usuario te pida crear un archivo y no te especifica el nombre no le preguntes el nombre, solo crealo iventatelo
        """

        client = genai.Client()

        while True:
            texto_usuario = input("🧑 Tú: ")

            if texto_usuario.lower() in "salir": break

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=f" estas sos tus instrucciones {tools_info_promt} y el susuario dijo {texto_usuario} ",
                config=types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0)  # Disables thinking
                ),
            )
            with open("ahora.txt", "w") as f:
                j = response.text
                print(j)



            if isinstance(response.text, list):
                print(type(response.text))

            elif any(tool.name in response.text for tool in tools_disponibles):
                partes = response.text.split(",", )
                nombre_herramienta = partes[0]
                parametros = eval(partes[1])

                await mcp_client.call_tool(name=nombre_herramienta, arguments=parametros)

                print("Ya lo hice")
            else:
                print(response.text)

@mcp.tool(
    title="Obtener detalles de archivo",
    description="Retorna metadatos como tamaño, fecha creación y fecha modificación de un archivo específico."
)
def obtener_detalles_archivo_tool(path: str):
    if not os.path.exists(path):
        return {"error": "El archivo no existe."}

    detalles = {
        "ruta_absoluta": os.path.abspath(path),
        "tamaño_bytes": os.path.getsize(path),
        "fecha_creacion": time.ctime(os.path.getctime(path)),
        "fecha_modificacion": time.ctime(os.path.getmtime(path)),
        "es_directorio": os.path.isdir(path),
        "es_archivo": os.path.isfile(path)
    }


if __name__ == "__main__":
    asyncio.run(client())



