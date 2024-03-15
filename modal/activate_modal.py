import discord
from discord.interactions import Interaction

TITLE = "Activate User"
class ActivateModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    player_id = discord.ui.TextInput(label="User Id",placeholder="user id",style=discord.TextStyle.short)
    player_account_name = discord.ui.TextInput(label="Account Name",placeholder="user account name",style=discord.TextStyle.short)

    async def on_submit(self, interaction: Interaction):
        player_id = str(interaction.data.get("components")[0].get("components")[0].get("value"))
        user_account_name = str(interaction.data.get("components")[1].get("components")[0].get("value"))
        user_account_name = user_account_name.lower()
        if not self.dbcon.check_user_exist_with_ref(player_id, user_account_name):
            self.dbcon.activate_user(player_id, user_account_name)
            await interaction.response.send_message("User Activated", ephemeral=True)
            return
        await interaction.response.send_message(f"User Id {player_id} has been activated before", ephemeral=True)
