import os
from twitchio.ext import commands
from openai import OpenAI

# --- Konfiguration ---
# Setze hier deine Zugangsdaten ein.
# Es wird dringend empfohlen, diese als Umgebungsvariablen zu setzen,
# anstatt sie direkt in den Code zu schreiben.

# Twitch-Konfiguration
TWITCH_TOKEN = os.environ.get("TWITCH_TOKEN", "oauth:dein_twitch_oauth_token")
TWITCH_NICK = os.environ.get("TWITCH_NICK", "dein_bot_benutzername")
TWITCH_CHANNEL = os.environ.get("TWITCH_CHANNEL", "dein_twitch_kanalname")

# OpenAI-Konfiguration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "dein_openai_api_schlüssel")

# Initialisiere den OpenAI-Client
# Stelle sicher, dass der API-Schlüssel gesetzt ist.
if not OPENAI_API_KEY or OPENAI_API_KEY == "dein_openai_api_schlüssel":
    print("Fehler: Der OpenAI API-Schlüssel wurde nicht gefunden. Bitte setze die Umgebungsvariable OPENAI_API_KEY.")
    exit()

client = OpenAI(api_key=OPENAI_API_KEY)


class Bot(commands.Bot):

    def __init__(self):
        # Initialisiere den Bot mit den Twitch-Zugangsdaten
        super().__init__(token=TWITCH_TOKEN, prefix='!', initial_channels=[TWITCH_CHANNEL])

    async def event_ready(self):
        # Diese Funktion wird aufgerufen, sobald der Bot erfolgreich verbunden ist.
        print(f'Bot ist als {self.nick} eingeloggt.')
        print(f'Beobachtet Kanal: {TWITCH_CHANNEL}')
        print('-----------------------------------------')
        print('Der Bot ist jetzt einsatzbereit!')
        print('Benutzer können den Befehl "!AIbot <Ihre Frage>" verwenden.')

    async def event_message(self, message):
        # Verhindert, dass der Bot auf seine eigenen Nachrichten reagiert.
        if message.echo:
            return

        # Verarbeitet Befehle, die mit dem Prefix '!' beginnen.
        await self.handle_commands(message)

    @commands.command(name='AIbot')
    async def ai_bot_command(self, ctx: commands.Context, *, prompt: str):
        """
        Dieser Befehl wird ausgelöst, wenn ein Benutzer "!AIbot <prompt>" eingibt.
        Der Text nach dem Befehl wird als 'prompt' an diese Funktion übergeben.
        """
        if not prompt:
            await ctx.send(f"@{ctx.author.name}, du musst eine Frage nach dem !AIbot-Befehl stellen.")
            return

        print(f'Anfrage von {ctx.author.name}: {prompt}')
        
        # Sende eine kurze "Denke nach..." Nachricht, um zu zeigen, dass die Anfrage bearbeitet wird.
        await ctx.send(f"🤖 @{ctx.author.name}, ich denke über deine Frage nach...")

        try:
            # Sende den Prompt an die OpenAI API
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Du kannst hier auch andere Modelle wie "gpt-4" verwenden
                messages=[
                    {"role": "system", "content": "Du bist ein hilfreicher AI-Assistent in einem Twitch-Chat. Antworte kurz und prägnant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=80,  # Begrenzt die Länge der Antwort, um den Chat nicht zu fluten.
                temperature=0.7, # Steuert die "Kreativität" der Antwort.
            )
            
            # Extrahiere die Textantwort aus dem API-Ergebnis.
            ai_response = response.choices[0].message.content.strip()

            # Sende die Antwort in den Twitch-Chat.
            # Formatiere die Antwort, um klarzustellen, wer gefragt hat.
            await ctx.send(f"@{ctx.author.name}: {ai_response}")
            print(f'Antwort an {ctx.author.name}: {ai_response}')

        except Exception as e:
            # Fehlerbehandlung, falls die API-Anfrage fehlschlägt.
            print(f"Fehler bei der OpenAI-API-Anfrage: {e}")
            await ctx.send(f"@{ctx.author.name}, es gab einen Fehler bei der Bearbeitung deiner Anfrage. Bitte versuche es später erneut.")


# Erstellt und startet den Bot
if __name__ == "__main__":
    # Überprüfen der Twitch-Konfiguration vor dem Start
    if (not TWITCH_TOKEN or TWITCH_TOKEN == "oauth:dein_twitch_oauth_token" or
        not TWITCH_NICK or TWITCH_NICK == "dein_bot_benutzername" or
        not TWITCH_CHANNEL or TWITCH_CHANNEL == "dein_twitch_kanalname"):
        print("Fehler: Bitte fülle die Twitch-Konfigurationsdaten (Token, Nick, Channel) aus.")
    else:
        bot = Bot()
        bot.run()
