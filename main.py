
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

class VistaConferma(View):
    """Vista secondaria che appare solo all'utente per confermare l'azione."""
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="Conferma Lettura e Accetta", style=discord.ButtonStyle.green, emoji="✅", custom_id="conferma_finale_univoco")
    async def conferma_button(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        ruolo = guild.get_role(ID_RUOLO_VERIFICATO)

        if ruolo is None:
            await interaction.response.send_message("Errore: Ruolo di verifica non trovato. Contatta lo staff.", ephemeral=True)
            return

        if ruolo in interaction.user.roles:
            await interaction.response.send_message("Sei già verificato nel server!", ephemeral=True)
        else:
            try:
                await interaction.user.add_roles(ruolo)
                for child in self.children:
                    child.disabled = True
                await interaction.response.edit_message(content="🎉 **Verifica completata!** Ti è stato assegnato il ruolo. Benvenuto a bordo!", view=self)
            except discord.Forbidden:
                await interaction.response.send_message("Non ho i permessi necessari (Gerarchia Ruoli) per assegnarti questo ruolo.", ephemeral=True)

class VistaVerificaPrincipale(View):
    """Vista principale con il pulsante persistente nel canale."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Inizia Verifica", style=discord.ButtonStyle.secondary, emoji="🛡️", custom_id="pulsante_verifica_principale")
    async def inizia_verifica(self, interaction: discord.Interaction, button: Button):
        guild = interaction.guild
        ruolo = guild.get_role(ID_RUOLO_VERIFICATO)
        
        if ruolo and ruolo in interaction.user.roles:
            await interaction.response.send_message("Hai già completato la verifica!", ephemeral=True)
            return

        testo_conferma = (
            "👋 **Ci sei quasi!**\n\n"
            "Per accedere alle stanze del server, ti preghiamo di confermare che accetti i seguenti punti:\n"
            "• Rispetta tutti i membri della community.\n"
            "• Non inviare spam o link non autorizzati nei canali.\n"
            "• Segui i Termini di Servizio di Discord.\n\n"
            "Clicca sul pulsante verde qui sotto per completare definitivamente il processo."
        )
        
        await interaction.response.send_message(content=testo_conferma, view=VistaConferma(), ephemeral=True)

class BotVerificaAvanzato(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Mantiene il pulsante attivo anche dopo il riavvio del bot
        self.add_view(VistaVerificaPrincipale())
        # Sincronizza i comandi slash (/) con Discord
        await self.tree.sync()

    async def on_ready(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Bot online come {self.user}")


bot = BotVerificaAvanzato()

# Comando Slash per creare il widget di verifica
@bot.tree.command(name="setup_verifica", description="Invia il widget con il pulsante di verifica nel canale corrente.")
async def setup_verifica(interaction: discord.Interaction):
    # Controllo se l'utente ha il ruolo dello Staff abilitato (ID_RUOLO_STAFF_SETUP)
    ruolo_staff = interaction.guild.get_role(ID_RUOLO_STAFF_SETUP)
    
    if ruolo_staff not in interaction.user.roles:
        await interaction.response.send_message("❌ Non hai i permessi necessari (ruolo richiesto) per usare questo comando.", ephemeral=True)
        return

    # Invia il messaggio con la vista persistente
    testo_widget = "🛡️ **Sistema di Verifica del Server**\n\nClicca sul pulsante qui sotto per avviare il processo di verifica e sbloccare tutti i canali."
    
    # Inviamo il messaggio nel canale in cui è stato digitato il comando
    await interaction.channel.send(content=testo_widget, view=VistaVerificaPrincipale())
    
    # Risposta effimera di conferma visibile solo a chi ha eseguito il comando
    await interaction.response.send_message("✅ Widget di verifica inviato con successo!", ephemeral=True)


# Recupera il token in modo sicuro dalle variabili d'ambiente di Railway
TOKEN = os.getenv("DISCORD_TOKEN")

if TOKEN:
    bot.run(TOKEN)
else:
    print("ERRORE: La variabile d'ambiente DISCORD_TOKEN non è configurata.")