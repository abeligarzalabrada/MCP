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



if __name__ == "__main__":
    mcp.run()