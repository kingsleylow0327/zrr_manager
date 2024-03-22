import discord
from discord.interactions import Interaction

TITLE = "Activate User"
class ActivateModal(discord.ui.Modal, title=TITLE):

    def __init__(self, dbcon):
        self.dbcon = dbcon
        super().__init__(title=TITLE, timeout=30)

    package = [discord.SelectOption(label="2 Weeks", value="2 week"),
              discord.SelectOption(label="3 Months", value="3 month"),
              discord.SelectOption(label="6 Months", value="6 month"),
              discord.SelectOption(label="1 Year", value="1 year")]
    
    player_id = discord.ui.TextInput(label="User Id",placeholder="user id",style=discord.TextStyle.short)
    player_account_name = discord.ui.TextInput(label="Account Name",placeholder="user account name",style=discord.TextStyle.short)
    expiry_date = discord.ui.Select(placeholder="Package Detail", options=package, min_values=1, max_values=1)

    async def on_submit(self, interaction: Interaction):
        player_id = str(interaction.data.get("components")[0].get("components")[0].get("value"))
        user_account_name = str(interaction.data.get("components")[1].get("components")[0].get("value"))
        user_account_name = user_account_name.lower()
        expiry_date = str(interaction.data.get("components")[2].get("components")[0].get("value"))

        if not self.dbcon.check_user_exist_with_ref(player_id, user_account_name):
            self.dbcon.activate_user(player_id, user_account_name, expiry_date)
            await interaction.response.send_message("User Activated", ephemeral=True)
            return
        await interaction.response.send_message(f"User Id {player_id} has been activated before", ephemeral=True)
