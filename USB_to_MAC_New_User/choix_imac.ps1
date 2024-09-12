# Liste des interfaces réseau actives
$adapters = Get-NetAdapter | Where-Object {$_.Status -eq 'Up'}
$index = 0

# Affichage des interfaces réseau avec un index (sans adresses MAC)
Write-Host "Veuillez choisir pour quel matériel vous souhaitez voir l'adresse MAC :"
foreach ($adapter in $adapters) {
    $index++
    Write-Host "$index. $($adapter.Name)"
}

# Demande à l'utilisateur de choisir une interface réseau
$selection = Read-Host "Entrez le numéro correspondant au matériel que vous souhaitez choisir"
$chosenAdapter = $adapters[$selection - 1]

# Afficher le message en gros et en rouge avec l'adresse MAC choisie
Write-Host ""
Write-Host "**************************************************************************" -ForegroundColor Red
Write-Host "* Voici votre adresse MAC. Notez-la avant de vous rendre sur le serveur. *" -ForegroundColor Red
Write-Host "**************************************************************************" -ForegroundColor Red
Write-Host ""
Write-Host "Adresse MAC du matériel sélectionné ($($chosenAdapter.Name)) : $($chosenAdapter.MacAddress)" -ForegroundColor Red
Write-Host ""

# Extraire l'adresse MAC et remplacer les tirets par des deux-points
$macAddress = $chosenAdapter.MacAddress -replace "-", ":"

# Demande du nom d'utilisateur
$username = Read-Host "Choisissez un nom d'utilisateur"

# Demande du mot de passe et vérification
$password = Read-Host "Choisissez un mot de passe" -AsSecureString
$confirmPassword = Read-Host "Confirmez votre mot de passe" -AsSecureString

# Convertir les mots de passe en texte brut pour la comparaison
$plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))
$plainConfirmPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto([System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($confirmPassword))

# Vérification que les deux mots de passe correspondent
if ($plainPassword -ne $plainConfirmPassword) {
    Write-Host "Les mots de passe ne correspondent pas. Veuillez réessayer." -ForegroundColor Red
    exit
}

# Détection automatique de la clé USB (lecteurs amovibles)
$usbDrive = Get-WmiObject Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 } | Select-Object -ExpandProperty DeviceID

if (-not $usbDrive) {
    Write-Host "Aucune clé USB détectée. Veuillez insérer une clé USB." -ForegroundColor Red
    exit
}

# Chemin du fichier texte sur la clé USB
$outputFile = Join-Path -Path $usbDrive -ChildPath "credentials.txt"

# Enregistrement de toutes les informations dans un fichier texte
@"
Adresse MAC : $macAddress
Nom d'utilisateur : $username
Mot de passe : $plainPassword
"@ | Out-File -FilePath $outputFile -Encoding utf8

Write-Host "Les informations de l'utilisateur ont été enregistrées sur la clé USB ($outputFile)" -ForegroundColor Green

# Demande à l'utilisateur d'appuyer sur une touche pour quitter
Write-Host "Appuyez sur une touche pour quitter..." -ForegroundColor Green
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')
