import discord
from discord.interactions import Interaction

TITLE = "Activate User"
class ActivateModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    player_id = discord.ui.TextInput(label="User Id",placeholder="user id",style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        player_id = str(interaction.data.get("components")[0].get("components")[0].get("value"))
        if not self.dbcon.check_user_exist(player_id):
            self.dbcon.activate_user(player_id)
            await interaction.response.send_message("User Activated", ephemeral=True)
            return
        await interaction.response.send_message("User already Activated", ephemeral=True)
