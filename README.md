# README — Alerte perturbations SNCF pour certains trajets, jours et horaires précis

Ce script envoie une notification si le train prévu est perturbé (retard, suppression…).

## Pourquoi ce script ?

L’app SNCF ne permet pas de :
- recevoir des notifications **seulement certains jours** (ex : jours de travail),
- cibler **un trajet précis** à **une heure précise**.

Ce script contourne cette limite :
- il ne s’exécute **que les jours choisis**,
- il interroge **un seul trajet** (départ → arrivée) à **l’heure cible**,
- il envoie une notif via **notify.run**.

---

## Ce que fait le script

1. Vérifie si on est un jour autorisé.
2. Calcule l’horodatage à surveiller (aujourd’hui à `CHECK_HOUR:CHECK_MINUTE`, sinon demain).
3. Appelle l’API SNCF en **temps réel** pour ce trajet.
4. Envoie une notification s’il y a une perturbation

---

## Prérequis

- Python 3.1
- Un compte et **clé API** SNCF https://numerique.sncf.com/startup/api/token-developpeur/
- Un **topic** notify.run (pour recevoir les notifications). https://notify.run/  Scanner le QR code avec votre téléphone et copiez l’URL dans la variable `NOTIFICATION_TOPIC_URL`.

- Les identifiants d’arrêt SNCF 

Les identifiants sont au format suivant `stop_area:SNCF:*******` pour **DEPARTURE** et **ARRIVAL**. 
L’API “places” de SNCF permet de chercher les gares.
Exemple :
`curl -u "VOTRE_TOKEN_SNCF:" "https://api.sncf.com/v1/coverage/sncf/places?q=paris"`
Le résultat contient des objets avec des champs comme :
```{
  "id": "stop_area:SNCF:87686006",
  "name": "Paris Gare de Lyon"
}
```

L’ID est celui qu’il faut utiliser.

---

## Installation

```bash
# 1) Cloner le dépôt
git clone <votre-repo>
cd <votre-repo>

# 2) Créer un venv (optionnel mais conseillé)
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3) Installer les dépendances
pip install -r requirements.txt
# Si pas de requirements.txt :
pip install requests notify-run python-dotenv
```

---

## Configuration (.env)

Créez un fichier `.env` à la racine :

```ini
# Identifiants d'arrêts SNCF (stop_area)

DEPARTURE=stop_area:SNCF:87686006      # exemple
ARRIVAL=stop_area:SNCF:87686045        # exemple

# Heure cible (24h)
CHECK_HOUR=8
CHECK_MINUTE=0

# Jours autorisés (0=lundi ... 6=dimanche). Ex: lundi uniquement
RUN_ONLY_ON_DAYS=0
# Exemple "lundi, mardi, mercredi, jeudi, vendredi"
# RUN_ONLY_ON_DAYS=0,1,2,3,4

# Clé API SNCF (token)
API_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# URL du topic notify.run (issue de 'notify-run register')
NOTIFICATION_TOPIC_URL=https://notify.run/abcd1234
```

---

## Lancer un test

```bash
python main.py   # ou le nom du fichier contenant le script
```

- Si **aujourd’hui n’est pas** dans `RUN_ONLY_ON_DAYS` → “Not running today.”
- Sinon, vous verrez le statut API et recevrez une notification si retard. 

---

## Exécution automatique (cron)

Exécutez le script à intervalles réguliers (ex : toutes les 15 min).  
Le script lui-même décidera **de ne rien faire** si ce n’est pas un jour autorisé.

```bash
crontab -e
```

Ajoutez par exemple :

```
# Toutes les 15 min, 6h–9h en semaine
*/15 6-9 * * 1-5 /usr/bin/env bash -lc 'cd /chemin/vers/le/projet && source .venv/bin/activate && python main.py >> cron.log 2>&1'
```

> Ajustez les heures selon votre besoin.  
> `CHECK_HOUR`/`CHECK_MINUTE` définissent **le train visé** (ex. 08:00).  
> Le cron n’a qu’à “réveiller” le script ; la requête vise l’horaire cible.

---

## Détails des variables

- `DEPARTURE`, `ARRIVAL`  
  Identifiants `stop_area` SNCF. Cherchez l’ID de votre gare.  
  Format attendu : `stop_area:SNCF:NNNNNNN`.

- `CHECK_HOUR`, `CHECK_MINUTE`  
  Heure du **départ visé**. Si l’heure du jour est déjà passée, on regarde **demain** à la même heure.

- `RUN_ONLY_ON_DAYS`  
  Liste CSV de jours (0=lundi à 6=dimanche).  
  Exemple : `0,1,2,3,4` pour les jours ouvrés.

- `API_TOKEN`  
  Votre token API SNCF.

- `NOTIFICATION_TOPIC_URL`  
  L’URL du topic notify.run