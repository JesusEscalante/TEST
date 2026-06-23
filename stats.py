import os
import json
from stats import obtener_estadisticas_detalladas, guardar_en_readme

def main():
    # Obtener información del repositorio desde el entorno de GitHub
    github_repository = os.environ.get('GITHUB_REPOSITORY', '')
    token = os.environ.get('GITHUB_TOKEN', '')
    
    if not github_repository:
        print("❌ No se encontró GITHUB_REPOSITORY")
        return
    
    # Parsear owner/repo
    owner, repo = github_repository.split('/')
    
    print(f"🔄 Obteniendo estadísticas para {owner}/{repo}")
    
    # Obtener estadísticas
    estadisticas = obtener_estadisticas_detalladas(owner, repo, token)
    
    if not estadisticas:
        print("❌ Error al obtener estadísticas")
        return
    
    # Guardar JSON
    with open("estadisticas_lenguajes.json", "w", encoding="utf-8") as f:
        json.dump(estadisticas, f, indent=2, ensure_ascii=False)
    print("✅ Estadísticas guardadas en JSON")
    
    # Actualizar README si existe
    try:
        guardar_en_readme(estadisticas)
    except Exception as e:
        print(f"⚠️ No se pudo actualizar README: {e}")

if __name__ == "__main__":
    main()