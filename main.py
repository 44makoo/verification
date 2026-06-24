import os
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from datetime import datetime

# ID di configurazione
ID_CANALE_VERIFICA = 1519312433586376714
ID_RUOLO_VERIFICATO = 1519307669364674662
ID_RUOLO_STAFF_SETUP = 1519316973614268566  # Ruolo abilitato a creare il widget

# URL del tuo Banner personalizzato
URL_BANNER = "https://cdn.discordapp.com/attachments/1516457598369533952/1518983715479490580/ce2828a1-7b03-46bb-b7d3-710697e0ae07.png?ex=6a3c9013&is=6a3b3e93&hm=e0d3d0c7f75e4cc65bab163778db658e5f8d6c72dbc2cdbec73f4dc4ab0cce40&"

class VistaConferma(View):
    """Vista secondaria che appare solo all'utente per confermare l'azione."""
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Conferma e Accetta", style=discord.ButtonStyle.green, emoji="✅", custom_id="conferma_finale_univoco")
    async def conferma_button(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        ruolo = guild.get_role(ID_RUOLO_VERIFICATO)

        if ruolo is None:
            await interaction.response.send_message("❌ Erreur: Ruolo di verifica non trovato. Contatta lo staff.", ephemeral=True)
            return

        if ruolo in interaction.user.roles:
            await interaction.response.send_message("ℹ️ Sei già verificato nel server!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(ruolo)
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(content="🎉 **Verifica completata con successo!** Ti è stato assegnato il ruolo. Benvenuto nella community!", view=self)
            except discord.Forbidden:
                await interaction.response.send_message("❌ Non ho i permessi necessari (Gerarchia Ruoli) per assegnarti questo ruolo.", ephemeral=True)

class VistaVerificaPrincipale(View):
    """Vista principale con il pulsante persistente nel canale."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Inizia Verifica", style=discord.ButtonStyle.primary, emoji="🛡️", custom_id="pulsante_verifica_principale")
    async def inizia_verifica(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        ruolo = guild.get_role(ID_RUOLO_VERIFICATO)
        
        if ruolo and ruolo in interaction.user.roles:
            await interaction.response.send_message("ℹ️ Hai già completato la verifica!", ephemeral=True)
            return

        # Design curato anche per il messaggio temporaneo di conferma delle regole
        embed_regole = discord.Embed(
            title="👋 Ci sei quasi!",
            description=(
                "Per accedere a tutte le sezioni del server, ti preghiamo di confermare che accetti i seguenti punti fondamentali:\n\n"
                "🔹 **Rispetto reciproco:** Rispetta tutti i membri della community.\n"
                "🔹 **Nessuno Spam:** Non inviare pubblicità o link non autorizzati.\n"
                "🔹 **Linee Guida:** Segui sempre i Termini di Servizio ufficiali di Discord.\n\n"
                "*Clicca sul pulsante verde qui sotto per completare definitivamente il processo e sbloccare le chat.*"
            ),
            color=discord.Color.green()
        )
        
        await interaction.response.send_message(embed=embed_regole, view=VistaConferma(), ephemeral=True)

class BotVerificaAvanzato(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Mantiene il pulsante attivo anche dopo il riavvio del bot
        self.add_view(VistaVerificaPrincipale())
        await self.tree.sync()

    async def on_ready(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Bot online come {self.user}")

bot = BotVerificaAvanzato()

# Comando Slash per creare il widget di verifica
@bot.tree.command(name="setup", description="Invia il widget di verifica con design avanzato.")
async def setup_verifica(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    # Controllo se l'utente ha il ruolo dello Staff abilitato
    ruolo_staff = interaction.guild.get_role(ID_RUOLO_STAFF_SETUP)
    
    if ruolo_staff not in interaction.user.roles:
        await interaction.followup.send("❌ Non hai i permessi necessari per usare questo comando.", ephemeral=True)
        return

    # Creazione dell'Embed principale (il Widget vero e proprio)
    embed_widget = discord.Embed(
        title="🔒 PORTALE DI VERIFICA",
        description=(
            "Benvenuto/a nel nostro server! Per garantire un ambiente sicuro ed evitare l'accesso a bot o malintenzionati, "
            "è richiesto un rapido passaggio di verifica prima di poter visualizzare i canali testuali e vocali.\n\n"
            "📌 **Come fare:**\n"
            "1️⃣ Clicca sul pulsante **Inizia Verifica** posizionato qui sotto.\n"
            "2️⃣ Leggi il breve regolamento nel messaggio temporaneo che ti apparirà.\n"
            "3️⃣ Clicca sul pulsante di conferma verde.\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        ),
        color=discord.Color.blurple()  # Colore elegante stile Discord
    )
    
    # Imposta il Banner personalizzato fornito
    embed_widget.set_image(url=URL_BANNER)
    
    # Aggiunge l'icona del server nel footer se disponibile
    icona_server = interaction.guild.icon.url if interaction.guild.icon else None
    embed_widget.set_footer(text=f"{interaction.guild.name} • Sistema di Protezione", icon_url=icona_server)
    
    # Inviamo il widget completo nel canale
    await interaction.channel.send(embed=embed_widget, view=VistaVerificaPrincipale())
    
    await interaction.followup.send("✅ Widget di verifica configurato e inviato con successo!", ephemeral=True)

# Recupera il token dalle variabili d'ambiente
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRORE: La variabile d'ambiente DISCORD_TOKEN non è configurata.")
