import discord

from logger import Logger

logger_mod = Logger("Manual Assign Free VIP")
logger = logger_mod.get_logger()

free_vip_role = 'FREE_VIP'


class ManualAssignFreeVipModal(discord.ui.Modal, title="Manual assign Free VIP Role"):

    def __init__(self, dbcon, guild):
        super().__init__(timeout=None)
        self.dbcon = dbcon
        self.guild = guild

    uuid = discord.ui.TextInput(label="BingX Main Account UUID", placeholder="Enter user BingX Main Account UUID")

    async def on_submit(self, interaction: discord.Interaction):
        uuid = self.uuid.value
        vip_detail = self.dbcon.get_trade_volume_by_uuid(uuid)

        if not vip_detail:
            await interaction.followup.send(content="This User have not pair with a UUID yet", ephemeral=True)
            return

        discord_id = vip_detail['discord_id']
        member = self.guild.get_member(int(discord_id))
        if not member:
            await interaction.response.send_message("User not found in the server.", ephemeral=True)
            return

        role = discord.utils.get(self.guild.roles, name=free_vip_role)
        if not role:
            await interaction.response.send_message(f"Role {free_vip_role} not found in server.", ephemeral=True)
            return

        if role in member.roles:
            logger.info(f"Retained role {role} for {member.name}.")
        elif role not in member.roles:
            await member.add_roles(role)
            logger.info(f"Assigned role {role} to {member.name}.")

        await member.add_roles(role)
        await interaction.response.send_message(f"Assigned role {role} to {member.name}.", ephemeral=True)
