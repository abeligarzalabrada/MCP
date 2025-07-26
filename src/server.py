from fastmcp import FastMCP
import os
import time
import smtplib
from email.mime.text import MIMEText
from graphviz import Digraph
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure()

mcp = FastMCP("MCP Server")

@mcp.tool(
    title="Crea Archivo",
    description="Crea Archivos En El Sistema"
)
def create_archivo_tool(archivo: str):
    try:
        with open(archivo, 'x'):
            pass
        return {"resultado": f"Archivo {archivo} creado exitosamente."}
    except FileExistsError:
        return {"error": "El archivo ya existe."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Listar Archivos",
    description="Listar Archivos En El Sistema"
)
def search_archivo_tool(path: str):
    try:
        return {"archivos": os.listdir(path)}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Eliminar Archivo",
    description="Elimina Archivos En El Sistema"
)
def delete_archivo_tool(path: str):
    try:
        os.remove(path)
        return {"resultado": f"Archivo {path} eliminado exitosamente."}
    except FileNotFoundError:
        return {"error": "El archivo no existe."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Edita Archivo",
    description="Edita Archivos En El Sistema"
)
def editar_archivo_tool(path: str, text: str):
    try:
        with open(path, "w") as archivo:
            archivo.write(text)
        return {"resultado": f"Archivo {path} editado exitosamente."}
    except Exception as e:
        return {"error": str(e)}

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
    return detalles

@mcp.tool(
    title="Enviar correo electrónico",
    description="Envía correos desde la cuenta indicada. Se recomienda usar contraseñas de aplicación para Gmail u otros proveedores SMTP."
)
def enviar_correo_tool(remitente: str, contraseña: str, destinatario: str, asunto: str, mensaje: str):
    msg = MIMEText(mensaje)
    msg['Subject'] = asunto
    msg['From'] = remitente
    msg['To'] = destinatario

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as servidor:
            servidor.login(remitente, contraseña)
            servidor.send_message(msg)
        return {"resultado": f"Correo enviado exitosamente a {destinatario} desde {remitente}."}
    except smtplib.SMTPAuthenticationError:
        return {"error": "Error de autenticación. Verifica correo y contraseña."}
    except smtplib.SMTPRecipientsRefused:
        return {"error": "Destinatario inválido o rechazado."}
    except smtplib.SMTPException as e:
        return {"error": f"Error SMTP: {str(e)}"}
    except Exception as e:
        return {"error": f"Error inesperado: {str(e)}"}

@mcp.tool(
    title="Generar Workflow Avanzado",
    description="Genera diagramas de workflow complejos con sub-ramas y descripciones breves usando Graphviz y un modelo de IA."
)
def generar_workflow_avanzado_tool(solicitud: str):
    model = genai.GenerativeModel('gemini-1.0-pro')

    prompt = f"Genera un workflow detallado con subpasos y breves descripciones para: {solicitud}. Estructura claramente en ramas principales y subramas."

    response = model.generate_content(prompt)
    workflow_data = response.text

    dot = Digraph(comment="Workflow avanzado", format="png")

    lines = workflow_data.strip().split('\n')
    parent_stack = []

    for line in lines:
        if not line.strip():
            continue

        indent = len(line) - len(line.lstrip(' '))
        content = line.strip()

        node_id = f"{hash(content)}"
        dot.node(node_id, content, shape="box")

        if parent_stack:
            while parent_stack and parent_stack[-1][0] >= indent:
                parent_stack.pop()

            if parent_stack:
                dot.edge(parent_stack[-1][1], node_id)

        parent_stack.append((indent, node_id))

    output_path = "workflow_avanzado"
    dot.render(output_path, view=False, cleanup=True)

    return {"resultado": f"Workflow avanzado generado en {output_path}.png"}

if __name__ == "__main__":
    mcp.run()
