import discord
from discord.interactions import Interaction
from logger import Logger

# Logger setup
logger_mod = Logger("Role Manager")
logger = logger_mod.get_logger()
MIN_VOLUME = 100000

class RoleManager():
    def __init__(self, dbcon, guild, interaction:Interaction):
        self.dbcon = dbcon
        self.user_list = None
        self.guild = guild
        self.interaction = interaction
        pass

    def get_bingx_user(self):
        self.user_list = self.dbcon.get_bingx_table_with_uid(100000)
        logger.info(f"{len(self.user_list)} user to be update")
    
    def get_propW_user(self):
        self.user_list = self.dbcon.get_propw_table_with_uid()

    async def give_role(self, role_name):
        update_user_list = []
        role = discord.utils.get(self.interaction.guild.roles, name=role_name)
        for user in self.user_list:
            user_id = user.get("discord_id")
            user = self.guild.get_member(int(user_id))
            if user:
                await user.add_roles(role)
                update_user_list.append(user_id)
                logger.info(f"""{user_id} gained/pro-long role {role_name}""")
        if len(update_user_list) > 0:
            self.dbcon.update_bingx_table_expired_date(",".join(update_user_list))
        logger.info(f"""{len(update_user_list)} user have gain {role_name}/pro-long their expiry""")
        
    
    async def remove_role(self, role_name):
        role = discord.utils.get(self.interaction.guild.roles, name=role_name)
        free_vip_role = discord.utils.get(self.interaction.guild.roles, name="FREE_VIP")
        user_amount = len(self.user_list)
        for user in self.user_list:
            user_id = user.get("discord_id")
            user = self.guild.get_member(int(user_id))
            if user:
                await user.remove_roles(role)
                await user.remove_roles(free_vip_role)
        logger.info(f"{user_amount} user have been removed from {role_name}")
