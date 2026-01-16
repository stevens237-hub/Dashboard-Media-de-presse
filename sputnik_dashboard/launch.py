#!/usr/bin/env python3
"""
Script de lancement du dashboard Sputnik News Africa
Vérifie la disponibilité des données avant de lancer l'application
"""

import os
import sys
import json

def check_data_files():
    """Vérifier la présence des fichiers de données"""
    files = [
        'fr.sputniknews.africa-2025/data/fr.sputniknews.africa-france-macron.json',
        'fr.sputniknews.africa-2025/data/fr.sputniknews.africa-russie-poutine.json'
    ]
    
    print("🔍 Vérification des fichiers de données...")
    all_ok = True
    
    for file_path in files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"✅ {os.path.basename(file_path)} - OK")
                    print(f"   └─ {len(data.get('metadata', {}).get('all', {}).get('kws', {}))} mots-clés")
            except Exception as e:
                print(f"❌ {os.path.basename(file_path)} - Erreur de lecture: {e}")
                all_ok = False
        else:
            print(f"❌ {os.path.basename(file_path)} - Fichier introuvable")
            all_ok = False
    
    return all_ok

def main():
    print("="*60)
    print("📊 SPUTNIK NEWS AFRICA - DASHBOARD ANALYTIQUE")
    print("="*60)
    print()
    
    # Vérifier les données
    if not check_data_files():
        print()
        print("⚠️  Erreur : Fichiers de données manquants ou incorrects")
        print("   Veuillez vérifier que les fichiers JSON sont disponibles")
        sys.exit(1)
    
    print()
    print("✨ Tous les fichiers sont OK!")
    print()
    print("🚀 Lancement du dashboard...")
    print("   └─ URL: http://localhost:8050")
    print("   └─ Appuyez sur Ctrl+C pour arrêter")
    print()
    print("-"*60)
    print()
    
    # Lancer l'application
    try:
        from dashboard_app import app
        app.run(debug=True, host='0.0.0.0', port=8050)
    except KeyboardInterrupt:
        print()
        print("👋 Dashboard arrêté par l'utilisateur")
    except Exception as e:
        print()
        print(f"❌ Erreur lors du lancement: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
