import requests
import json
from collections import defaultdict
from typing import Dict, List, Tuple

def obtener_lenguajes_repositorio(owner: str, repo: str, token: str = None) -> Dict[str, int]:
    """
    Obtiene las estadísticas de lenguajes de un repositorio de GitHub
    
    Args:
        owner: Nombre del dueño del repositorio
        repo: Nombre del repositorio
        token: Token de acceso personal (opcional pero recomendado)
    
    Returns:
        Diccionario con lenguajes y sus bytes de código
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/languages"
    
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    
    if token:
        headers["Authorization"] = f"token {token}"
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Lanza excepción si hay error
        
        lenguajes = response.json()
        return lenguajes
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener los lenguajes: {e}")
        return {}

def calcular_porcentajes(lenguajes: Dict[str, int]) -> Dict[str, float]:
    """
    Calcula el porcentaje de cada lenguaje
    
    Args:
        lenguajes: Diccionario con lenguajes y bytes
    
    Returns:
        Diccionario con lenguajes y porcentajes
    """
    total_bytes = sum(lenguajes.values())
    
    if total_bytes == 0:
        return {}
    
    porcentajes = {}
    for lenguaje, bytes_ in lenguajes.items():
        porcentaje = (bytes_ / total_bytes) * 100
        porcentajes[lenguaje] = round(porcentaje, 2)
    
    return porcentajes

def obtener_estadisticas_detalladas(owner: str, repo: str, token: str = None) -> Dict:
    """
    Obtiene estadísticas detalladas del repositorio
    
    Args:
        owner: Dueño del repositorio
        repo: Nombre del repositorio
        token: Token de acceso personal
    
    Returns:
        Diccionario con estadísticas detalladas
    """
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

def formatear_estadisticas(estadisticas: Dict) -> str:
    """
    Formatea las estadísticas para mostrarlas en consola
    
    Args:
        estadisticas: Diccionario con estadísticas
    
    Returns:
        String formateado
    """
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
    
    # Mostrar lenguajes ordenados por porcentaje
    porcentajes = estadisticas.get('porcentajes', {})
    lenguajes_ordenados = sorted(porcentajes.items(), key=lambda x: x[1], reverse=True)
    
    for lenguaje, porcentaje in lenguajes_ordenados:
        bytes_ = estadisticas.get('lenguajes', {}).get(lenguaje, 0)
        kb = round(bytes_ / 1024, 2)
        mb = round(bytes_ / (1024 * 1024), 2)
        
        # Crear barra visual
        barra = "█" * int(porcentaje / 2)  # Escalar para que no sea demasiado larga
        
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

# ============================================
# EJEMPLOS DE USO
# ============================================

def main():
    """Función principal con ejemplos de uso"""
    
    # Configuración
    owner = "tu-usuario"  # Cambia esto por tu usuario
    repo = "tu-repositorio"  # Cambia esto por tu repositorio
    
    # Opcional: Usa un token para evitar límites de API
    # Obtén tu token en: Settings > Developer settings > Personal access tokens
    token = None  # o "tu-token-personal"
    
    print("🔄 Obteniendo estadísticas...")
    
    # Obtener estadísticas detalladas
    estadisticas = obtener_estadisticas_detalladas(owner, repo, token)
    
    # Mostrar estadísticas formateadas
    print(formatear_estadisticas(estadisticas))
    
    # Guardar en archivo JSON
    with open("estadisticas_lenguajes.json", "w", encoding="utf-8") as f:
        json.dump(estadisticas, f, indent=2, ensure_ascii=False)
    print("\n✅ Estadísticas guardadas en 'estadisticas_lenguajes.json'")

# ============================================
# FUNCIONES ADICIONALES PARA EL ACTION
# ============================================

def generar_markdown_estadisticas(estadisticas: Dict) -> str:
    """
    Genera un markdown con las estadísticas para usar en README
    """
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
    for lenguaje, porcentaje in lenguajes_ordenados:
        barra = "█" * int(porcentaje / 2)
        markdown.append(f"{lenguaje:12} {barra} {porcentaje}%")
    markdown.append("```")
    
    return "\n".join(markdown)

def guardar_en_readme(estadisticas: Dict, archivo_readme: str = "README.md"):
    """
    Actualiza el README con las estadísticas de lenguajes
    """
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

if __name__ == "__main__":
    main()