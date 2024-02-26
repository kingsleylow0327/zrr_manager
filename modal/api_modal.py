import discord
import message as ms
from discord.interactions import Interaction

TITLE = "Submit Your API Credential"
class APIModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    api = discord.ui.TextInput(label="API Key",placeholder="api key",style=discord.TextStyle.short)
    secret = discord.ui.TextInput(label="API Secret",placeholder="api secret",style=discord.TextStyle.short)
    player_ref_id = discord.ui.TextInput(label="Player Ref ID",placeholder="player ref id",style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        api = interaction.data.get("components")[0].get("components")[0].get("value")
        key = interaction.data.get("components")[1].get("components")[0].get("value")
        player_ref_id = interaction.data.get("components")[2].get("components")[0].get("value")
        player_id = interaction.user.id
        if not self.dbcon.check_user_exist_with_ref(player_id, player_ref_id):
            await interaction.response.send_message(ms.NON_REGISTERED, ephemeral=True)
            return
        self.dbcon.set_player_api(player_id, api, key, player_ref_id)
        await interaction.response.send_message("API Set", ephemeral=True)
