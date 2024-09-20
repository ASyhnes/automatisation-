import os
import requests
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération des informations depuis le fichier .env
api_key = os.getenv('TRELLO_API_KEY')
api_token = os.getenv('TRELLO_API_TOKEN')
board_id = os.getenv('BOARD_ID')

# Liste des composants matériels pour un ordinateur de développement IA
hardware_components = {
    "Processeur (CPU)": "Objectif : Le CPU doit être performant pour gérer les tâches de calcul général, les charges de travail de machine learning et le multitâche.\n"
                        "Spécifications : Processeur avec au moins 8 cœurs, Fréquence : 3.0 GHz ou plus, Support AVX pour les instructions de calcul intensif.\n"
                        "Prix moyen : 300€ - 600€.",

    "Carte graphique (GPU)": "Objectif : Le GPU est essentiel pour les tâches de deep learning, offrant une accélération massive pour l'entraînement des modèles.\n"
                             "Spécifications : GPU avec au moins 10 Go de VRAM (ex. NVIDIA RTX 3060 ou supérieur), support CUDA pour les bibliothèques de deep learning.\n"
                             "Prix moyen : 600€ - 1500€.",

    "Mémoire vive (RAM)": "Objectif : La RAM doit être suffisante pour gérer de grandes charges de données lors de l'entraînement des modèles et pour le multitâche.\n"
                          "Spécifications : 32 Go de RAM DDR4 ou DDR5, Fréquence : 3200 MHz ou plus.\n"
                          "Prix moyen : 150€ - 300€.",

    "Stockage principal (SSD)": "Objectif : Le stockage rapide est crucial pour charger les datasets, les modèles, et pour un accès rapide aux fichiers.\n"
                                "Spécifications : SSD NVMe d'au moins 1 To pour la rapidité, optionnellement un second SSD de 2 To pour les données.\n"
                                "Prix moyen : 100€ - 300€.",

    "Alimentation (PSU)": "Objectif : Fournir une puissance stable pour tous les composants, surtout pour le GPU qui consomme beaucoup d'énergie.\n"
                          "Spécifications : Alimentation de 750W, certification 80+ Gold ou mieux.\n"
                          "Prix moyen : 100€ - 200€.",

    "Boîtier (Carlingue)": "Objectif : Offrir une bonne circulation d'air pour refroidir tous les composants, avec un espace suffisant pour les futures mises à niveau.\n"
                           "Spécifications : Boîtier moyen tour avec gestion des câbles et support pour plusieurs ventilateurs ou un radiateur de refroidissement liquide.\n"
                           "Prix moyen : 70€ - 150€.",

    "Système de refroidissement": "Objectif : Garder les températures du CPU et du GPU à un niveau optimal pendant les longues sessions d'entraînement.\n"
                                  "Spécifications : Ventirad ou système de refroidissement liquide AIO pour le CPU, ventilateurs supplémentaires pour le boîtier.\n"
                                  "Prix moyen : 70€ - 150€.",

    "Carte mère": "Objectif : Connecter et prendre en charge tous les composants de manière efficace, avec des options de mise à niveau.\n"
                  "Spécifications : Compatible avec le CPU et la RAM choisis, supporte PCIe 4.0 pour le GPU, plusieurs emplacements M.2 pour SSD.\n"
                  "Prix moyen : 150€ - 300€."
}

# Fonction pour obtenir les colonnes existantes sur le tableau Trello
def get_existing_lists(board_id):
    url = f"https://api.trello.com/1/boards/{board_id}/lists"
    query = {
        'key': api_key,
        'token': api_token
    }
    response = requests.get(url, params=query)
    if response.status_code == 200:
        return {lst['name']: lst['id'] for lst in response.json()}
    else:
        print(f"Erreur lors de la récupération des listes: {response.text}")
        return {}

# Fonction pour créer une carte dans une colonne (liste)
def create_card(list_id, card_name, card_desc):
    url = "https://api.trello.com/1/cards"
    query = {
        'key': api_key,
        'token': api_token,
        'idList': list_id,
        'name': card_name,
        'desc': card_desc,
        'pos': 'bottom'
    }
    response = requests.post(url, params=query)
    if response.status_code == 200:
        print(f"Carte '{card_name}' créée avec succès dans la liste ID {list_id}.")
    else:
        print(f"Erreur lors de la création de la carte '{card_name}': {response.text}")

# Fonction principale pour créer les cartes à partir de la liste de composants
def create_cards_from_hardware_list():
    existing_lists = get_existing_lists(board_id)
    print("Colonnes disponibles :")
    for idx, name in enumerate(existing_lists.keys()):
        print(f"{idx}: {name}")

    column_index = input("Dans quelle colonne voulez-vous ajouter les cartes (entrez l'index)? ").strip()
    try:
        column_index = int(column_index)
        column_name = list(existing_lists.keys())[column_index]
        list_id = existing_lists[column_name]

        # Créer une carte pour chaque composant matériel
        for component_name, component_desc in hardware_components.items():
            create_card(list_id, component_name, component_desc)
    except (ValueError, IndexError):
        print("Index invalide. Veuillez entrer un nombre correspondant à une colonne existante.")

# Appel de la fonction pour créer les cartes
create_cards_from_hardware_list()
