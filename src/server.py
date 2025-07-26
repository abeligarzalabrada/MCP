from fastmcp import FastMCP
import os 


mcp = FastMCP("MCP Server")

@mcp.tool(
    title= "Crea Archivo",
    description= "Crea Archivos En El Sistema"
)
def create_archivo_tool(archivo: str):
    open(archivo,'x')

@mcp.resource(
    title= "Listar Archivos",
    description= "Listar Archivos En El Sistema"
)
def search_archivo_tool(path:str):
    print(os.listdir(path))

@mcp.tool(
    title= "Eliminar Archivo",
    description= "Elimina Archivos En El Sistema"
)
def delete_archivo_tool(path:str):
    os.remove(path)

@mcp.tool(
    title= "Edita Archivo",
    description= "Edita Archivos En El Sistema"
)
def editar_archivo_tool(path:str, text:str):
    with open(path,"w") as archivo:
        archivo.write(text)

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
    mcp.run()
