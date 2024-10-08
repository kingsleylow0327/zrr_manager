import discord
import message as ms
from discord.interactions import Interaction

TITLE = "Submit Your API Credential"
class APIModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon, selected_account):
        self.dbcon = dbcon
        self.user_account_name = selected_account
        super().__init__(title=TITLE, timeout=120)

    api = discord.ui.TextInput(label="API Key",placeholder="api key",style=discord.TextStyle.short)
    secret = discord.ui.TextInput(label="API Secret",placeholder="api secret",style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        api = interaction.data.get("components")[0].get("components")[0].get("value")
        key = interaction.data.get("components")[1].get("components")[0].get("value")
        player_id = interaction.user.id
        if not self.dbcon.check_user_exist_with_ref(player_id, self.user_account_name):
            await interaction.response.send_message(ms.NON_REGISTERED, ephemeral=True)
            return
        self.dbcon.set_player_api(player_id, api, key, self.user_account_name)
        await interaction.response.send_message("API Set", ephemeral=True)