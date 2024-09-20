import os
import requests
import re
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Récupération des informations depuis le fichier .env
api_key = os.getenv('TRELLO_API_KEY')
api_token = os.getenv('TRELLO_API_TOKEN')
board_id = os.getenv('BOARD_ID')
google_credentials_path = os.getenv('GOOGLE_CREDENTIALS_PATH')

# Connexion à Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = Credentials.from_service_account_file(google_credentials_path, scopes=scope)
client = gspread.authorize(creds)

# URL du Google Sheet
google_sheet_url = "https://docs.google.com/spreadsheets/d/1F63z65yysET2hRKyJ0FDzvVqxXjbP6G5M_QcVYDCFx8/edit?usp=sharing"
spreadsheet = client.open_by_url(google_sheet_url)
spreadsheet_id = google_sheet_url.split('/')[5]  # Extraire l'ID du Google Sheets depuis l'URL

# Connexion à l'API Google Sheets v4
service = build('sheets', 'v4', credentials=creds)

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

# Fonction pour obtenir les cartes d'une colonne spécifique
def get_cards_in_list(list_id):
    url = f"https://api.trello.com/1/lists/{list_id}/cards"
    query = {
        'key': api_key,
        'token': api_token
    }
    response = requests.get(url, params=query)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erreur lors de la récupération des cartes: {response.text}")
        return []

# Fonction pour extraire un prix d'une description de carte
def extract_price(card_desc):
    # Rechercher un prix (ex : "prix : 233 euro" ou "prix : 233€")
    match_single = re.search(r"prix\s*:\s*(\d+)\s*[€euro]*", card_desc, re.IGNORECASE)
    if match_single:
        return int(match_single.group(1))

    return 0

# Fonction pour dupliquer ou réinitialiser la feuille modèle
def setup_sheet(column_name):
    try:
        try:
            # Essayer de récupérer la feuille existante
            sheet = spreadsheet.worksheet(column_name)
            sheet.clear()  # Si elle existe, la vider
        except gspread.exceptions.WorksheetNotFound:
            # Si la feuille n'existe pas, la dupliquer depuis le modèle
            model_sheet = spreadsheet.worksheet('modele')
            sheet = spreadsheet.duplicate_sheet(model_sheet.id, new_sheet_name=column_name)
            sheet = client.open_by_url(google_sheet_url).worksheet(column_name)
        return sheet
    except Exception as e:
        print(f"Erreur lors de la configuration de la feuille : {str(e)}")
        return None

# Fonction pour étendre les bordures avec l'API Google Sheets
def extend_borders(sheet_id, start_row, end_row):
    requests = []
    for row in range(start_row, end_row + 1):
        requests.append({
            "updateBorders": {
                "range": {
                    "sheetId": sheet_id,
                    "startRowIndex": row - 1,  # Les index de Google Sheets commencent à 0
                    "endRowIndex": row,
                    "startColumnIndex": 1,  # Colonne B
                    "endColumnIndex": 4  # Colonne E (inclus)
                },
                "bottom": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "top": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "left": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                },
                "right": {
                    "style": "SOLID",
                    "width": 1,
                    "color": {
                        "red": 0,
                        "green": 0,
                        "blue": 0
                    }
                }
            }
        })
    
    body = {
        'requests': requests
    }
    
    service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body).execute()

# Fonction principale pour traiter les cartes et les mettre à jour dans Google Sheets
def process_and_update_sheet():
    existing_lists = get_existing_lists(board_id)
    print("Colonnes disponibles :")
    for idx, name in enumerate(existing_lists.keys()):
        print(f"{idx}: {name}")

    column_index = input("Dans quelle colonne voulez-vous calculer les prix (entrez l'index)? ").strip()
    try:
        column_index = int(column_index)
        column_name = list(existing_lists.keys())[column_index]
        list_id = existing_lists[column_name]

        # Récupérer les cartes de la colonne Trello
        cards = get_cards_in_list(list_id)
        total_price = 0
        card_data = []

        for card in cards:
            price = extract_price(card['desc'])
            total_price += price
            card_data.append([card['name'], card['desc'], price, card['url']])  # Ajout de l'URL de la carte

        # Configurer la feuille (la réinitialiser si elle existe déjà ou la dupliquer depuis le modèle)
        sheet = setup_sheet(column_name)

        if sheet:
            start_row = 5  # Début des données à la ligne 5 (B5, C5, D5, E5)
            data_row = start_row + 1  # Première ligne où les données seront insérées

            # Insérer les en-têtes à la ligne 5
            sheet.update_cell(5, 2, "Nom du composant")  # B5
            sheet.update_cell(5, 3, "Description")  # C5
            sheet.update_cell(5, 4, "Prix")  # D5
            sheet.update_cell(5, 5, "Lien")  # E5 (pour les hyperliens)

            # Insérer les données des composants à partir de la ligne 6
            for idx, data in enumerate(card_data):
                sheet.update_cell(data_row + idx, 2, data[0])  # Nom du composant en B
                sheet.update_cell(data_row + idx, 3, data[1])  # Description en C
                sheet.update_cell(data_row + idx, 4, data[2])  # Prix en D
                # Ajout du lien hypertexte avec la fonction HYPERLINK
                sheet.update_cell(data_row + idx, 5, f'=HYPERLINK("{data[3]}", "Voir")')  # Lien en E

            # Calculer la nouvelle ligne pour le total
            sum_row = data_row + len(card_data)

            # Déplacer et mettre à jour les cellules "Total" et la somme des prix
            sheet.update_cell(sum_row, 2, "Total")  # B<sum_row>
            sheet.update_cell(sum_row, 3, "")  # C<sum_row> (vide)
            sheet.update_cell(sum_row, 4, total_price)  # D<sum_row> - Total Prix

            # Appliquer les bordures aux nouvelles lignes ajoutées
            sheet_id = sheet.id
            extend_borders(sheet_id, data_row, sum_row)

            print(f"Feuille '{column_name}' mise à jour avec succès.")
            print(f"Somme totale des prix : {total_price}€")

    except (ValueError, IndexError):
        print("Index invalide. Veuillez entrer un nombre correspondant à une colonne existante.")

# Appel de la fonction principale
process_and_update_sheet()
