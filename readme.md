🤖 Twitch AI Chatbot via Channel Points A Python bot that connects to
your Twitch chat, listens for a specific channel point reward, and uses
the OpenAI API (e.g., GPT-4o) to answer user prompts directly in chat.

(Tipp: Erstelle ein kurzes GIF, das den Bot in Aktion zeigt, und ersetze
den Link oben, um dein Projekt zu präsentieren.)

✨ Features - Channel Point Integration: Löst nur bei einer
benutzerdefinierten Kanalpunkte-Belohnung aus, die du festlegst. -
OpenAI API Integration: Nutzt moderne Sprachmodelle wie gpt-4o oder
gpt-3.5-turbo, um intelligente Antworten zu generieren. - Automatic
Token Refresh: Verwendet einen sicheren Refresh-Token-Mechanismus, um
sich bei jedem Start automatisch und sicher bei Twitch zu
authentifizieren. Keine manuellen Passwort-Updates mehr. - Customizable
Personality: Der System-Prompt kann einfach geändert werden, um dem Bot
eine einzigartige Persönlichkeit zu verleihen. - Simple Configuration:
Alle wichtigen Einstellungen sind am Anfang des Skripts für einen
einfachen Zugriff gesammelt.

🛠️ Setup & Installation Befolge diese Schritte, um den Bot für deinen
Kanal zum Laufen zu bringen.

1. Repository klonen

Klone dieses Repository auf deinen lokalen Rechner:

    git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
    cd YOUR_REPO_NAME

2. Virtuelle Umgebung erstellen

Es wird dringend empfohlen, eine virtuelle Umgebung zu verwenden, um die
Abhängigkeiten sauber zu halten.

    # Umgebung erstellen
    python3 -m venv venv

    # Umgebung aktivieren
    # Windows:
    venv\Scripts ctivate
    # macOS / Linux:
    source venv/bin/activate

3. Abhängigkeiten installieren

Installiere die erforderlichen Python-Bibliotheken:

    pip install twitchio openai requests

⚙️ Configuration Öffne die Datei main.py und fülle die folgenden
Konfigurationsvariablen mit deinen eigenen Daten aus.

Twitch-Konfiguration

-   TWITCH_CLIENT_ID & TWITCH_CLIENT_SECRET:
    Gehe zur Twitch Developer Console.
    Registriere eine neue Anwendung (Kategorie: “Chat Bot”).
    Setze die “OAuth Redirect URL” auf http://localhost:3000.
    Kopiere die Client ID und erstelle/kopiere das Client Secret.

-   TWITCH_REFRESH_TOKEN:
    Du musst diesen Token einmalig generieren. Folge den Anweisungen im
    offiziellen Twitch Guide, insbesondere dem “Authorization Code Grant
    Flow”. Dieser Prozess gibt dir den langlebigen Refresh-Token, der
    für das Skript erforderlich ist.
    Wichtig: Generiere diesen Token für den Bot-Account.

-   TWITCH_BOT_NICK: Der Benutzername deines Bot-Accounts (alles in
    Kleinbuchstaben). Es wird dringend empfohlen, einen separaten
    Twitch-Account für deinen Bot zu erstellen.

-   TWITCH_CHANNEL: Der Name deines Haupt-Streaming-Kanals, auf dem der
    Bot arbeiten wird (alles in Kleinbuchstaben).

OpenAI-Konfiguration

-   OPENAI_API_KEY: Deinen API-Schlüssel findest du in deinem OpenAI
    Dashboard.

Kanalbelohnungs-Konfiguration

-   CUSTOM_REWARD_ID:
    Erstelle in deinem Twitch Creator Dashboard eine neue
    Kanalpunkte-Belohnung. Wichtig: Aktiviere die Option “Requires
    Viewer to Enter Text”.
    Führe das beiliegende Skript get_rewards.py aus, um die IDs all
    deiner Belohnungen aufzulisten.
    Kopiere die richtige ID und füge sie hier ein.

▶️ Bot starten Stelle sicher, dass deine virtuelle Umgebung (venv)
aktiviert ist und alle Konfigurationsvariablen gesetzt sind. Starte dann
das Skript:

    python main.py

Wenn alles korrekt ist, siehst du eine Erfolgsmeldung in deinem Terminal
und der Bot postet eine “online”-Nachricht in deinem Twitch-Chat.

🎨 Anpassung Du kannst das Verhalten des Bots leicht anpassen.

Persönlichkeit der KI ändern

Ändere den System-Prompt in der event_message-Funktion, um die
Persönlichkeit und das Verhalten der KI zu steuern.

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # ÄNDERE DIESE ZEILE:
            {"role": "system", "content": "You are a grumpy robot who answers questions reluctantly."},
            {"role": "user", "content": prompt}
        ],
        # ...
    )

KI-Modell ändern

Ändere das model-Argument, um ein anderes OpenAI-Modell zu verwenden (z.
B. für bessere Leistung oder niedrigere Kosten).
gpt-4o ist eine ausgezeichnete moderne Wahl.

    response = client.chat.completions.create(
        model="gpt-4o",  # <-- HIER ÄNDERN
        # ...
    )

📄 Lizenz Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe die
LICENSE-Datei für Details.
