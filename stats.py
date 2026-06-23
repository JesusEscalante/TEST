import os
import json
import requests
from collections import defaultdict
from typing import Dict, List, Tuple

def obtener_lenguajes_repositorio(owner: str, repo: str, token: str = None) -> Dict[str, int]:
    """
    Obtiene las estadísticas de lenguajes de un repositorio de GitHub
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los lenguajes: {e}")
        return {}

def calcular_porcentajes(lenguajes: Dict[str, int]) -> Dict[str, float]:
    """Calcula el porcentaje de cada lenguaje"""
    total_bytes = sum(lenguajes.values())
    
    if total_bytes == 0:
        return {}
    
    porcentajes = {}
    for lenguaje, bytes_ in lenguajes.items():
        porcentaje = (bytes_ / total_bytes) * 100
        porcentajes[lenguaje] = round(porcentaje, 2)
    
    return porcentajes

def obtener_estadisticas_detalladas(owner: str, repo: str, token: str = None) -> Dict:
    """Obtiene estadísticas detalladas del repositorio"""
    # Obtener lenguajes
    lenguajes = obtener_lenguajes_repositorio(owner, repo, token)
    
    if not lenguajes:
        return {}
    
    # Obtener información del repositorio
    url_repo = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url_repo, headers=headers)
        response.raise_for_status()
        repo_info = response.json()
        
        # Calcular porcentajes
        porcentajes = calcular_porcentajes(lenguajes)
        
        # Crear estadísticas completas
        estadisticas = {
            "nombre": repo,
            "dueño": owner,
            "lenguajes": lenguajes,
            "porcentajes": porcentajes,
            "total_bytes": sum(lenguajes.values()),
            "total_kb": round(sum(lenguajes.values()) / 1024, 2),
            "total_mb": round(sum(lenguajes.values()) / (1024 * 1024), 2),
            "numero_lenguajes": len(lenguajes),
            "lenguaje_principal": max(lenguajes, key=lenguajes.get) if lenguajes else None,
            "repo_publico": repo_info.get("private", False) == False,
            "estrellas": repo_info.get("stargazers_count", 0),
            "forks": repo_info.get("forks_count", 0),
            "ultima_actualizacion": repo_info.get("updated_at", "")
        }
        
        return estadisticas
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener información del repositorio: {e}")
        return {"lenguajes": lenguajes, "porcentajes": calcular_porcentajes(lenguajes)}

def generar_markdown_estadisticas(estadisticas: Dict) -> str:
    """Genera un markdown con las estadísticas"""
    if not estadisticas:
        return "## 📊 Estadísticas de lenguajes\n\nNo se pudieron obtener las estadísticas."
    
    markdown = []
    markdown.append("## 📊 Estadísticas de lenguajes")
    markdown.append("")
    markdown.append(f"**Repositorio:** {estadisticas.get('dueño')}/{estadisticas.get('nombre')}")
    markdown.append(f"**⭐ Estrellas:** {estadisticas.get('estrellas', 0)}")
    markdown.append(f"**🔀 Forks:** {estadisticas.get('forks', 0)}")
    markdown.append(f"**📦 Total código:** {estadisticas.get('total_mb', 0)} MB")
    markdown.append("")
    markdown.append("### Lenguajes utilizados")
    markdown.append("")
    
    # Crear tabla de lenguajes
    markdown.append("| Lenguaje | Porcentaje | Tamaño |")
    markdown.append("|----------|------------|--------|")
    
    porcentajes = estadisticas.get('porcentajes', {})
    lenguajes_ordenados = sorted(porcentajes.items(), key=lambda x: x[1], reverse=True)
    
    for lenguaje, porcentaje in lenguajes_ordenados:
        bytes_ = estadisticas.get('lenguajes', {}).get(lenguaje, 0)
        mb = round(bytes_ / (1024 * 1024), 2)
        markdown.append(f"| {lenguaje} | {porcentaje}% | {mb} MB |")
    
    markdown.append("")
    
    # Crear gráfico de barras de texto
    markdown.append("### Distribución visual")
    markdown.append("```")
    for lenguaje, porcentaje in lenguajes_ordenados[:10]:  # Top 10 lenguajes
        barra = "█" * int(porcentaje / 2)
        markdown.append(f"{lenguaje:12} {barra} {porcentaje}%")
    markdown.append("```")
    
    return "\n".join(markdown)

def guardar_en_readme(estadisticas: Dict, archivo_readme: str = "README.md"):
    """Actualiza el README con las estadísticas de lenguajes"""
    markdown = generar_markdown_estadisticas(estadisticas)
    
    # Leer README actual
    try:
        with open(archivo_readme, "r", encoding="utf-8") as f:
            contenido = f.read()
    except FileNotFoundError:
        contenido = f"# {estadisticas.get('nombre', 'Mi Repositorio')}\n\n"
    
    # Buscar y reemplazar sección de estadísticas
    inicio = contenido.find("<!-- ESTADISTICAS_START -->")
    fin = contenido.find("<!-- ESTADISTICAS_END -->")
    
    if inicio != -1 and fin != -1:
        # Reemplazar sección existente
        nuevo_contenido = (
            contenido[:inicio] +
            "<!-- ESTADISTICAS_START -->\n" +
            markdown +
            "\n<!-- ESTADISTICAS_END -->" +
            contenido[fin + len("<!-- ESTADISTICAS_END -->"):]
        )
    else:
        # Añadir nueva sección al final
        nuevo_contenido = contenido + "\n\n<!-- ESTADISTICAS_START -->\n" + markdown + "\n<!-- ESTADISTICAS_END -->\n"
    
    # Guardar README actualizado
    with open(archivo_readme, "w", encoding="utf-8") as f:
        f.write(nuevo_contenido)
    
    print(f"✅ README actualizado con las estadísticas en '{archivo_readme}'")

def formatear_estadisticas(estadisticas: Dict) -> str:
    """Formatea las estadísticas para mostrarlas en consola"""
    if not estadisticas:
        return "No se pudieron obtener las estadísticas"
    
    output = []
    output.append("=" * 50)
    output.append(f"📊 ESTADÍSTICAS DE LENGUAJES")
    output.append("=" * 50)
    output.append(f"📁 Repositorio: {estadisticas.get('dueño')}/{estadisticas.get('nombre')}")
    output.append(f"⭐ Estrellas: {estadisticas.get('estrellas', 0)}")
    output.append(f"🔀 Forks: {estadisticas.get('forks', 0)}")
    output.append(f"📅 Última actualización: {estadisticas.get('ultima_actualizacion', 'N/A')}")
    output.append("")
    output.append("📝 LENGUAJES UTILIZADOS:")
    output.append("-" * 50)
    
    porcentajes = estadisticas.get('porcentajes', {})
    lenguajes_ordenados = sorted(porcentajes.items(), key=lambda x: x[1], reverse=True)
    
    for lenguaje, porcentaje in lenguajes_ordenados[:15]:  # Top 15 lenguajes
        bytes_ = estadisticas.get('lenguajes', {}).get(lenguaje, 0)
        kb = round(bytes_ / 1024, 2)
        mb = round(bytes_ / (1024 * 1024), 2)
        
        barra = "█" * int(porcentaje / 2)
        
        output.append(f"  {lenguaje}:")
        output.append(f"    {barra} {porcentaje}%")
        output.append(f"    {kb} KB ({mb} MB)")
    
    output.append("")
    output.append(f"📈 Total lenguajes: {estadisticas.get('numero_lenguajes', 0)}")
    output.append(f"📦 Total código: {estadisticas.get('total_mb', 0)} MB")
    
    if estadisticas.get('lenguaje_principal'):
        output.append(f"🏆 Lenguaje principal: {estadisticas.get('lenguaje_principal')}")
    
    output.append("=" * 50)
    
    return "\n".join(output)

def main():
    """Función principal"""
    # Para ejecución local
    owner = "tu-usuario"  # Cambia esto
    repo = "tu-repositorio"  # Cambia esto
    token = None  # o usa tu token
    
    # Para GitHub Actions (usa variables de entorno)
    github_repository = os.environ.get('GITHUB_REPOSITORY', '')
    token = os.environ.get('GITHUB_TOKEN', '')
    
    if github_repository:
        owner, repo = github_repository.split('/')
        print(f"🔄 Ejecutando en GitHub Actions para {owner}/{repo}")
    
    print("🔄 Obteniendo estadísticas...")
    
    estadisticas = obtener_estadisticas_detalladas(owner, repo, token)
    
    if not estadisticas:
        print("❌ Error al obtener estadísticas")
        return
    
    # Mostrar en consola
    print(formatear_estadisticas(estadisticas))
    
    # Guardar en JSON
    with open("estadisticas_lenguajes.json", "w", encoding="utf-8") as f:
        json.dump(estadisticas, f, indent=2, ensure_ascii=False)
    print("\n✅ Estadísticas guardadas en 'estadisticas_lenguajes.json'")
    
    # Actualizar README
    try:
        guardar_en_readme(estadisticas)
    except Exception as e:
        print(f"⚠️ No se pudo actualizar README: {e}")

if __name__ == "__main__":
    main()