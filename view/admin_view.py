import discord
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

    @discord.ui.button(label="Update VIP", style=discord.ButtonStyle.blurple, custom_id="update_vip")
    async def update_vip(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)
        if not self.dbcon.is_admin(str(interaction.user.id)):
            await interaction.followup.send("This function only limit to Admin", ephemeral=True)
            return
        await interaction.followup.send("Fetching VIP Sheet... This may take sometime...", ephemeral=True)
        role = discord.utils.get(interaction.guild.roles, name="VIP")

        gsheet = GSheet(self.dbcon, self.config)
        json_data = gsheet.get_vip_data()
        if json_data != None and len(json_data) != 0:
            # Clearing roles
            await interaction.followup.send("Clearing Roles...", ephemeral=True)
            member_list = role.members
            for user in member_list:
                await user.remove_roles(role)
            # Adding Roles
            await interaction.followup.send("Assigning Roles...", ephemeral=True)
            success_number = 0
            failed_string = ""
            for j in json_data:
                if j.get('Discord Id') is None or j.get('Discord Id') == "" :
                    continue
                vip_id = int(j.get('Discord Id'))
                user = interaction.guild.get_member(vip_id)
                if user:
                    await user.add_roles(role)
                    success_number += 1
                else:
                    failed_string += f"{vip_id},\n"
            await interaction.followup.send(f"Successfully added {success_number} member(s) as VIP!", ephemeral=True)
        if failed_string != "":
            await interaction.followup.send(f"Following are member failed to assigned: \n {failed_string}", ephemeral=True)

        whitelist_success_number = 0
        whitelist_failed_string = ""
        white_list_json = gsheet.get_whitelist_data()
        await interaction.followup.send(f"Adding White Listed User...", ephemeral=True)
        if white_list_json != None and len(white_list_json) != 0:
            for j in white_list_json:
                if j.get('Discord Id') is None or j.get('Discord Id') == "" :
                    continue
                vip_id = int(j.get('Discord Id'))
                whitelist_user = interaction.guild.get_member(vip_id)
                if whitelist_user:
                    await whitelist_user.add_roles(role)
                    whitelist_success_number += 1
                else:
                    whitelist_failed_string += f"{vip_id},\n"
            await interaction.followup.send(f"(Whitelist) Successfully added {whitelist_success_number} member(s) as VIP!", ephemeral=True)
        if whitelist_failed_string != "":
            await interaction.followup.send(f"(Whitelist) Following are member failed to assigned: \n {whitelist_failed_string}", ephemeral=True)
        await interaction.followup.send("Done!", ephemeral=True)

    # @discord.ui.button(label="Update Bitget", style=discord.ButtonStyle.blurple, custom_id="update_bitget")
    # async def update_bitget(self, interaction: discord.Interaction, button: discord.ui.Button):
    #     await interaction.response.defer(ephemeral=True)
    #     if not self.dbcon.is_admin(str(interaction.user.id)):
    #         await interaction.followup.send("This function only limit to Admin", ephemeral=True)
    #         return
    #     await interaction.followup.send("Updating Bitget Table... This may take sometime...", ephemeral=True)
    #     gsheet = GSheet(self.dbcon, self.config)
    #     await gsheet.store_to_bitget_db()
    #     await interaction.followup.send("Updating User's Expiry", ephemeral=True)
    #     valid_vip_dict = self.dbcon.get_bitget_table_with_volume(300000)
    #     success_number = 0
    #     failed_string = ""
    #     if valid_vip_dict != None and len(valid_vip_dict) != 0:
    #         vip_list = [k.get("discord_id") for k in valid_vip_dict]
    #         self.dbcon.update_bitget_table_expired_date(",".join(vip_list), 30)
    #         await interaction.followup.send("Assigning Roles", ephemeral=True)
    #         role = discord.utils.get(interaction.guild.roles, name="VIPB")
    #         for vip in vip_list:
    #             user = interaction.guild.get_member(int(vip))
    #             if user:
    #                 await user.add_roles(role)
    #                 success_number += 1
    #             else:
    #                 failed_string += f"{vip},\n"
    #     await interaction.followup.send(f"Successfully added {success_number} member(s) as VIPB!", ephemeral=True)
    #     if failed_string != "":
    #         await interaction.followup.send(f"Following are member failed to assigned: \n {failed_string}", ephemeral=True)
    #     await interaction.followup.send("Done!", ephemeral=True)