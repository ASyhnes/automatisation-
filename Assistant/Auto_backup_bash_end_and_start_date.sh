#!/bin/bash

# Définir le fichier de log principal
LOG_FILE="/var/log/backup.log"
RSYNC_LOG_FILE="/var/log/backup_rsync.log"

# Fonction de journalisation
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') : $1" | tee -a "$LOG_FILE"
}

# Définir les chemins source et destination
SOURCE="/srv/ServeurDocument/"
DESTINATION="/mnt/backup/"

# Démarrage du script de backup
log_message "Démarrage du script de backup..."

# Étape 1 : Synchroniser les fichiers avec rsync
log_message "Synchronisation des fichiers de $SOURCE vers $DESTINATION..."
sudo rsync -avh --delete "$SOURCE" "$DESTINATION" >> "$RSYNC_LOG_FILE" 2>&1

# Vérifier si rsync s'est exécuté correctement
if [ $? -eq 0 ]; then
    log_message "Synchronisation terminée avec succès."
else
    log_message "Erreur lors de la synchronisation des fichiers. Voir le log $RSYNC_LOG_FILE pour plus de détails."
    exit 1
fi

# Étape 2 : Fin de la synchronisation
log_message "Backup terminé avec succès."

# Étape 3 : Programmer le réveil du serveur pour 8h du matin le jour même
WAKE_TIME="08:00"
log_message "Programmation du réveil du serveur à $WAKE_TIME..."

# Si l'heure actuelle est après 08:00, programmer pour le lendemain à 08:00
if [ $(date +%s) -ge $(date +%s -d "$WAKE_TIME") ]; then
    WAKE_TIMESTAMP=$(date +%s -d "tomorrow $WAKE_TIME")
else
    WAKE_TIMESTAMP=$(date +%s -d "$WAKE_TIME")
fi

sudo rtcwake -m off -t $WAKE_TIMESTAMP

if [ $? -eq 0 ]; then
    log_message "Réveil programmé avec succès pour le $(date -d "@$WAKE_TIMESTAMP" '+%Y-%m-%d %H:%M:%S')."
else
    log_message "Erreur lors de la programmation du réveil. Vérifiez la commande rtcwake."
    exit 1
fi

# Étape 4 : Arrêter le serveur après le backup
log_message "Arrêt du serveur en cours..."
sudo shutdown -h now

# Fin du script (cette ligne ne sera pas atteinte si le serveur s'éteint correctement)
log_message "Le script de backup s'est terminé avec succès."
