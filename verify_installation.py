#!/usr/bin/env python3
"""
Script de vérification de l'installation
=========================================

Ce script vérifie que toutes les dépendances sont correctement installées
et que la structure du projet est en place.

Usage:
    python verify_installation.py
"""

import sys
import os
from pathlib import Path


def print_header(text):
    """Affiche un en-tête formaté"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def print_success(text):
    """Affiche un message de succès"""
    print(f"✅ {text}")


def print_error(text):
    """Affiche un message d'erreur"""
    print(f"❌ {text}")


def print_warning(text):
    """Affiche un avertissement"""
    print(f"⚠️  {text}")


def check_python_version():
    """Vérifie la version de Python"""
    print_header("Vérification de Python")
    
    version = sys.version_info
    print(f"Version Python: {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 10:
        print_success("Version Python compatible (3.10+)")
        return True
    else:
        print_error("Python 3.10+ requis. Version actuelle: {}.{}.{}".format(
            version.major, version.minor, version.micro))
        return False


def check_directory_structure():
    """Vérifie la structure des dossiers"""
    print_header("Vérification de la structure des dossiers")
    
    required_dirs = [
        "config",
        "src",
        "src/connectors",
        "src/collectors",
        "src/analyzers",
        "src/validators",
        "src/risk",
        "src/execution",
        "src/monitoring",
        "src/notifications",
        "src/reporting",
        "src/utils",
        "logs",
        "tests",
        "data"
    ]
    
    all_good = True
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print_success(f"Dossier '{dir_path}' présent")
        else:
            print_error(f"Dossier '{dir_path}' manquant")
            all_good = False
    
    return all_good


def check_required_files():
    """Vérifie les fichiers requis"""
    print_header("Vérification des fichiers de configuration")
    
    required_files = [
        "requirements.txt",
        ".env.template",
        ".gitignore",
        "README.md",
        "src/__init__.py"
    ]
    
    all_good = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print_success(f"Fichier '{file_path}' présent")
        else:
            print_error(f"Fichier '{file_path}' manquant")
            all_good = False
    
    # Vérifier si .env existe
    env_path = Path(".env")
    if env_path.exists():
        print_success("Fichier .env configuré")
    else:
        print_warning("Fichier .env non trouvé. Copier .env.template vers .env")
    
    return all_good


def check_dependencies():
    """Vérifie les dépendances Python"""
    print_header("Vérification des dépendances Python")
    
    dependencies = [
        "ccxt",
        "pandas",
        "sqlalchemy",
        "psycopg2",
        "aiohttp",
        "dotenv",
        "redis"
    ]
    
    all_good = True
    for dep in dependencies:
        try:
            if dep == "dotenv":
                __import__("dotenv")
            else:
                __import__(dep)
            print_success(f"Module '{dep}' installé")
        except ImportError:
            print_error(f"Module '{dep}' manquant")
            all_good = False
    
    return all_good


def check_git():
    """Vérifie que Git est initialisé"""
    print_header("Vérification de Git")
    
    git_path = Path(".git")
    if git_path.exists():
        print_success("Dépôt Git initialisé")
        return True
    else:
        print_error("Git non initialisé. Exécuter: git init")
        return False


def print_summary(checks):
    """Affiche le résumé des vérifications"""
    print_header("RÉSUMÉ")
    
    total = len(checks)
    passed = sum(checks.values())
    
    print(f"\nTests passés: {passed}/{total}")
    
    if passed == total:
        print_success("✨ Installation complète et fonctionnelle!")
        print("\n📋 Prochaines étapes:")
        print("  1. Copier .env.template vers .env")
        print("  2. Configurer vos clés API dans .env")
        print("  3. Installer les dépendances: pip install -r requirements.txt")
        print("  4. Passer à l'Étape 1.2 du plan d'action")
        return True
    else:
        print_error("❌ Certaines vérifications ont échoué")
        print("\n🔧 Actions requises:")
        
        for check_name, result in checks.items():
            if not result:
                print(f"  - Corriger: {check_name}")
        
        return False


def main():
    """Fonction principale"""
    print("\n" + "🤖 BOT D'ARBITRAGE CRYPTO - VÉRIFICATION D'INSTALLATION".center(60))
    
    checks = {
        "Version Python": check_python_version(),
        "Structure des dossiers": check_directory_structure(),
        "Fichiers requis": check_required_files(),
        "Dépendances Python": check_dependencies(),
        "Git": check_git()
    }
    
    success = print_summary(checks)
    
    # Code de sortie
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
