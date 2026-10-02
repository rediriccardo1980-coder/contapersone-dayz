"""
Contapersone DayZ per GitHub Actions: una sola esecuzione.
Legge i giocatori online da Nitrado e rinomina il canale vocale Discord
solo se il nome e' cambiato.

I dati arrivano dai "Secrets" di GitHub come variabili d'ambiente:
  NITRADO_TOKEN, NITRADO_SERVICE_ID, DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID
"""
import os

import requests

NITRADO_TOKEN = os.environ["NITRADO_TOKEN"]
SERVICE_ID = os.environ["NITRADO_SERVICE_ID"]
DISCORD_TOKEN = os.environ["DISCORD_BOT_TOKEN"]
CHANNEL_ID = os.environ["DISCORD_CHANNEL_ID"]

DISCORD_URL = f"https://discord.com/api/v10/channels/{CHANNEL_ID}"
DISCORD_HEADERS = {"Authorization": f"Bot {DISCORD_TOKEN}"}


def giocatori_online():
    r = requests.get(
        f"https://api.nitrado.net/services/{SERVICE_ID}/gameservers",
        headers={"Authorization": f"Bearer {NITRADO_TOKEN}"},
        timeout=15,
    )
    r.raise_for_status()
    gs = r.json()["data"]["gameserver"]
    if gs.get("status") != "started":
        return None, None  # server spento o in riavvio
    q = gs.get("query", {})
    return q.get("player_current", 0), q.get("player_max", gs.get("slots", 0))


def main():
    attuali, massimi = giocatori_online()
    if attuali is None:
        nome = "🔴｜Server offline"
    else:
        nome = f"🟢｜Online: {attuali}/{massimi}"

    # Evita rinomine inutili (Discord limita le rinomine dei canali)
    r = requests.get(DISCORD_URL, headers=DISCORD_HEADERS, timeout=15)
    r.raise_for_status()
    if r.json().get("name") == nome:
        print("Nessun cambiamento:", nome)
        return

    r = requests.patch(
        DISCORD_URL, headers=DISCORD_HEADERS, json={"name": nome}, timeout=15
    )
    r.raise_for_status()
    print("Aggiornato:", nome)


if __name__ == "__main__":
    main()
