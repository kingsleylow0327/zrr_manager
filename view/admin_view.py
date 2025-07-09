import discord
from modal.add_vip_role_modal import AddVipRoleModal
from service.gsheet import GSheet


ROLE_TABLE = {
    "VIP": "trade_volume_table",
    "VIP30": "pionex_table",
    "VIPB": "bitget_table"
}
class AdminView(discord.ui.View):

    def __init__(self, dbcon, config):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.config = config

    @discord.ui.button(label="Update BingX", style=discord.ButtonStyle.blurple, custom_id="update_bingx")
    async def update_bingx(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not self.dbcon.is_admin(str(interaction.user.id)):
            await interaction.response.send_message("This function only limit to Admin", ephemeral=True)
            return
        await interaction.followup.send("Updating BingX Table... This may take sometime...", ephemeral=True)
        gsheet = GSheet(self.dbcon, self.config)
        await gsheet.store_to_bingx_db()
        await interaction.followup.send("Updating User's Expiry", ephemeral=True)
        valid_vip_dict = self.dbcon.get_bingx_table_with_volume(300000)
        vip_list = [k.get("discord_id") for k in valid_vip_dict]
        self.dbcon.update_bingx_table_expired_date(",".join(vip_list))
        await interaction.followup.send("Assigning Roles", ephemeral=True)
        role = discord.utils.get(interaction.guild.roles, name="VIP")
        success_number = 0
        failed_string = ""
        for vip in vip_list:
            user = interaction.guild.get_member(int(vip))
            if user:
                await user.add_roles(role)
                success_number += 1
            else:
                failed_string += f"{vip},\n"
        await interaction.followup.send(f"Successfully added {success_number} member(s) as VIP!", ephemeral=True)
        if failed_string != "":
            await interaction.followup.send(f"Following are member failed to assigned: \n {failed_string}", ephemeral=True)
        await interaction.followup.send("Done!", ephemeral=True)

    @discord.ui.button(label="Update Bitget", style=discord.ButtonStyle.blurple, custom_id="update_bitget")
    async def update_bitget(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not self.dbcon.is_admin(str(interaction.user.id)):
            await interaction.response.send_message("This function only limit to Admin", ephemeral=True)
            return
        await interaction.followup.send("Updating Bitget Table... This may take sometime...", ephemeral=True)
        gsheet = GSheet(self.dbcon, self.config)
        await gsheet.store_to_bitget_db()
        await interaction.followup.send("Updating User's Expiry", ephemeral=True)
        valid_vip_dict = self.dbcon.get_bitget_table_with_volume(300000)
        vip_list = [k.get("discord_id") for k in valid_vip_dict]
        self.dbcon.update_bitget_table_expired_date(",".join(vip_list))
        await interaction.followup.send("Assigning Roles", ephemeral=True)
        role = discord.utils.get(interaction.guild.roles, name="VIPB")
        success_number = 0
        failed_string = ""
        for vip in vip_list:
            user = interaction.guild.get_member(int(vip))
            if user:
                await user.add_roles(role)
                success_number += 1
            else:
                failed_string += f"{vip},\n"
        await interaction.followup.send(f"Successfully added {success_number} member(s) as VIPB!", ephemeral=True)
        if failed_string != "":
            await interaction.followup.send(f"Following are member failed to assigned: \n {failed_string}", ephemeral=True)
        await interaction.followup.send("Done!", ephemeral=True)