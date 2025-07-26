from fastmcp import FastMCP
import os
import time
import smtplib
from email.mime.text import MIMEText
from graphviz import Digraph
from google import genai
from dotenv import load_dotenv
import shutil
import zipfile
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive


load_dotenv()

client_gemini = genai.Client()
mcp = FastMCP("MCP Server")

#Control de archivos, carpetas y rutas

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
    title="Crear Directorio",
    description="Crea un nuevo directorio en la ubicación especificada."
)
def crear_directorio_tool(ruta: str):
    try:
        os.makedirs(ruta, exist_ok=True)
        return {"resultado": f"Directorio '{ruta}' creado exitosamente."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Renombrar Archivo",
    description="Renombra un archivo o carpeta especificado."
)
def renombrar_archivo_tool(ruta_original: str, nueva_ruta: str):
    try:
        os.rename(ruta_original, nueva_ruta)
        return {"resultado": f"Renombrado exitosamente de '{ruta_original}' a '{nueva_ruta}'."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Mover Archivo",
    description="Mueve un archivo desde una ubicación hacia otra especificada."
)
def mover_archivo_tool(origen: str, destino: str):
    try:
        shutil.move(origen, destino)
        return {"resultado": f"Archivo movido exitosamente desde {origen} a {destino}."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Copiar Archivo",
    description="Copia un archivo desde una ubicación hacia otra especificada."
)
def copiar_archivo_tool(origen: str, destino: str):
    try:
        shutil.copy2(origen, destino)
        return {"resultado": f"Archivo copiado exitosamente desde {origen} a {destino}."}
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
    title="Estructura de carpetas",
    description="Devuelve una estructura jerárquica de archivos desde la ruta dada."
)
def estructura_directorio_tool(path: str):
    try:
        estructura = []
        for root, dirs, files in os.walk(path):
            nivel = root.replace(path, "").count(os.sep)
            indent = " " * 2 * nivel
            estructura.append(f"{indent}{os.path.basename(root)}/")
            for f in files:
                estructura.append(f"{indent}  {f}")
        return {"estructura": "\n".join(estructura)}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Comprimir Archivos",
    description="Crea un archivo .zip con archivos especificados separados por coma."
)
def comprimir_tool(archivos: str, salida_zip: str):
    try:
        with zipfile.ZipFile(salida_zip, 'w') as zipf:
            for archivo in archivos.split(','):
                zipf.write(archivo.strip())
        return {"resultado": f"Archivos comprimidos en {salida_zip}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(
    title="Descomprimir ZIP",
    description="Descomprime un archivo ZIP en la carpeta destino especificada."
)
def descomprimir_zip_tool(archivo_zip: str, carpeta_destino: str):
    try:
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)
        return {"resultado": f"Archivo {archivo_zip} descomprimido en {carpeta_destino}"}
    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    title="Organizar archivos por tipo",
    description="Agrupa archivos en carpetas según su extensión."
)
def organizar_por_tipo_tool(path: str):
    try:
        for archivo in os.listdir(path):
            archivo_path = os.path.join(path, archivo)
            if os.path.isfile(archivo_path):
                ext = os.path.splitext(archivo)[1][1:] or "sin_extension"
                destino = os.path.join(path, ext)
                os.makedirs(destino, exist_ok=True)
                shutil.move(archivo_path, os.path.join(destino, archivo))
        return {"resultado": "Archivos organizados por tipo exitosamente."}
    except Exception as e:
        return {"error": str(e)}


#Tools oficina, enviar correos y workflows

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

#conectar drive

@mcp.tool(
    title="Conectar a Google Drive",
    description="Autentica al usuario en Google Drive usando un token personalizado (clave de acceso)."
)
def conectar_drive_tool(token_path: str):
    try:
        gauth = GoogleAuth()
        gauth.LoadCredentialsFile(token_path)

        if gauth.credentials is None:
            return {"error": "Token no válido o vencido. Se requiere autorización inicial."}
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()

        drive = GoogleDrive(gauth)
        # Verificamos que funcione intentando obtener los archivos raíz
        archivos = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        return {"resultado": f"Conexión exitosa. {len(archivos)} archivos disponibles en tu Drive."}

    except Exception as e:
        return {"error": str(e)}


@mcp.tool(
    title="Generar Workflow Avanzado",
    description="Genera diagramas de workflow complejos con sub-ramas y descripciones breves usando Graphviz y un modelo de IA."
)
def generar_workflow_avanzado_tool(solicitud: str):

    prompt = f"Genera un workflow detallado con subpasos y breves descripciones para: {solicitud}. Estructura claramente en ramas principales y subramas."

    response = client_gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"{prompt}",
    )

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
