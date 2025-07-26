import os
import time
import shutil
import zipfile
import smtplib
import json
from email.mime.text import MIMEText
from graphviz import Digraph
from dotenv import load_dotenv
from fastmcp import FastMCP
from google import genai
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

# === Cargar variables de entorno ===
load_dotenv()

# === Inicialización ===
mcp = FastMCP("MCP Server")

# === API Key y variables seguras ===
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyDufiJBwy7DMq6vVxn67LhbKSawlnjX51Q")
EMAIL_DEFAULT_PASSWORD = os.getenv("EMAIL_DEFAULT_PASSWORD", "nsur vtbj wyfj nmzb")

genai.configure(api_key=GOOGLE_API_KEY)
client_gemini = genai

# === Rutas internas ===
USERDATA_DIR = "userdata"
os.makedirs(USERDATA_DIR, exist_ok=True)
DRIVE_TOKEN_FILE = os.path.join(USERDATA_DIR, "mycreds.txt")
drive_instancia = None

# === Herramientas de archivos ===

@mcp.tool(title="Crea Archivo", description="Crea Archivos En El Sistema")
def create_archivo_tool(archivo: str):
    try:
        with open(archivo, 'x'):
            pass
        return {"resultado": f"Archivo {archivo} creado exitosamente."}
    except FileExistsError:
        return {"error": "El archivo ya existe."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Crear Directorio", description="Crea un nuevo directorio en la ubicación especificada.")
def crear_directorio_tool(ruta: str):
    try:
        os.makedirs(ruta, exist_ok=True)
        return {"resultado": f"Directorio '{ruta}' creado exitosamente."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Renombrar Archivo", description="Renombra un archivo o carpeta especificado.")
def renombrar_archivo_tool(ruta_original: str, nueva_ruta: str):
    try:
        os.rename(ruta_original, nueva_ruta)
        return {"resultado": f"Renombrado exitosamente de '{ruta_original}' a '{nueva_ruta}'."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Mover Archivo", description="Mueve un archivo desde una ubicación hacia otra especificada.")
def mover_archivo_tool(origen: str, destino: str):
    try:
        shutil.move(origen, destino)
        return {"resultado": f"Archivo movido exitosamente desde {origen} a {destino}."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Copiar Archivo", description="Copia un archivo desde una ubicación hacia otra especificada.")
def copiar_archivo_tool(origen: str, destino: str):
    try:
        shutil.copy2(origen, destino)
        return {"resultado": f"Archivo copiado exitosamente desde {origen} a {destino}."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Listar Archivos", description="Listar Archivos En El Sistema")
def search_archivo_tool(path: str):
    try:
        return {"archivos": os.listdir(path)}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Eliminar Archivo", description="Elimina Archivos En El Sistema")
def delete_archivo_tool(path: str):
    try:
        os.remove(path)
        return {"resultado": f"Archivo {path} eliminado exitosamente."}
    except FileNotFoundError:
        return {"error": "El archivo no existe."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Edita Archivo", description="Edita Archivos En El Sistema")
def editar_archivo_tool(path: str, text: str):
    try:
        with open(path, "w") as archivo:
            archivo.write(text)
        return {"resultado": f"Archivo {path} editado exitosamente."}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Obtener detalles de archivo", description="Retorna metadatos de un archivo específico.")
def obtener_detalles_archivo_tool(path: str):
    if not os.path.exists(path):
        return {"error": "El archivo no existe."}
    try:
        return {
            "ruta_absoluta": os.path.abspath(path),
            "tamaño_bytes": os.path.getsize(path),
            "fecha_creacion": time.ctime(os.path.getctime(path)),
            "fecha_modificacion": time.ctime(os.path.getmtime(path)),
            "es_directorio": os.path.isdir(path),
            "es_archivo": os.path.isfile(path)
        }
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Estructura de carpetas", description="Devuelve una estructura jerárquica desde la ruta dada.")
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

@mcp.tool(title="Comprimir Archivos", description="Crea un archivo .zip con archivos separados por coma.")
def comprimir_tool(archivos: str, salida_zip: str):
    try:
        with zipfile.ZipFile(salida_zip, 'w') as zipf:
            for archivo in archivos.split(','):
                zipf.write(archivo.strip())
        return {"resultado": f"Archivos comprimidos en {salida_zip}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Descomprimir ZIP", description="Descomprime un archivo ZIP en la carpeta destino.")
def descomprimir_zip_tool(archivo_zip: str, carpeta_destino: str):
    try:
        with zipfile.ZipFile(archivo_zip, 'r') as zip_ref:
            zip_ref.extractall(carpeta_destino)
        return {"resultado": f"Archivo {archivo_zip} descomprimido en {carpeta_destino}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Organizar archivos por tipo", description="Agrupa archivos en carpetas por su extensión.")
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

# === Herramientas adicionales ===

@mcp.tool(title="Enviar correo electrónico", description="Envía correos con configuración opcional.")
def enviar_correo_tool(destinatario: str, asunto: str, mensaje: str, remitente: str = None, contrasena: str = None):
    try:
        if not remitente or not contrasena:
            contrasena = contrasena or EMAIL_DEFAULT_PASSWORD
        if not remitente or not contrasena:
            return {"error": "Faltan datos para autenticación."}

        msg = MIMEText(mensaje)
        msg["Subject"] = asunto
        msg["From"] = remitente
        msg["To"] = destinatario

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
            servidor.login(remitente, contrasena)
            servidor.send_message(msg)

        return {"resultado": f"Correo enviado exitosamente a {destinatario} desde {remitente}."}
    except smtplib.SMTPAuthenticationError as e:
        return {"error": f"Autenticación fallida: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

@mcp.tool(title="Conectar cuenta de Google Drive", description="Conecta a Google Drive y reutiliza token.")
def configurar_drive_tool(token_path: str = DRIVE_TOKEN_FILE):
    global drive_instancia
    try:
        gauth = GoogleAuth()
        if os.path.exists(token_path):
            gauth.LoadCredentialsFile(token_path)
        if gauth.credentials is None:
            gauth.LocalWebserverAuth()
        elif gauth.access_token_expired:
            gauth.Refresh()
        else:
            gauth.Authorize()
        gauth.SaveCredentialsFile(token_path)
        drive_instancia = GoogleDrive(gauth)
        archivos = drive_instancia.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
        return {"resultado": f"Conectado a Google Drive. {len(archivos)} archivos listados."}
    except Exception as e:
        return {"error": str(e)}

#workflow visual para facil entendimiento del ususrio

@mcp.tool(title="Generar Workflow Avanzado", description="Genera diagramas de workflows usando Gemini y Graphviz.")
def generar_workflow_avanzado_tool(solicitud: str):
    prompt = f"Genera un workflow detallado con subpasos y descripciones para: {solicitud}."
    response = client_gemini.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
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
        while parent_stack and parent_stack[-1][0] >= indent:
            parent_stack.pop()
        if parent_stack:
            dot.edge(parent_stack[-1][1], node_id)
        parent_stack.append((indent, node_id))

    output_path = "workflow_avanzado"
    dot.render(output_path, view=False, cleanup=True)
    return {"resultado": f"Workflow generado en {output_path}.png"}

# === Lanzador principal ===
if __name__ == "__main__":
    mcp.run()
