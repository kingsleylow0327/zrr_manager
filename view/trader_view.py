import discord
import message as ms
from discord.interactions import Interaction

class TraderSelectView(discord.ui.View):
    def __init__(self, dbcon, account_name, player, following_trader_id):
        super().__init__()
        trader_list = dbcon.get_trader_list(following_trader_id)
        self.add_item(PlayerDropDown(dbcon, trader_list, player, account_name))

class PlayerDropDown(discord.ui.Select):
    def __init__(self, dbcon, trader_list, player, account_name):
        self.dbcon = dbcon
        self.account_name = account_name
        self.player = player
        trader_options = []
        for trader in trader_list:
            count = int(trader.get('count'))
            if count >= 20:
                continue
            if count < 2:
                count = '🟢' + str(count)
            elif count < 5:
                count = '🤯' + str(count)
            else:
                count = '🔥' + str(count)
            
            trader_options.append(discord.SelectOption(label=f"{trader.get('trader_name')} ({count})",
                                                       value=f"{trader.get('trader_name')},{trader.get('trader_id')}"))
        
        super().__init__(placeholder="Trader Name", options=trader_options, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        trader_info = self.values[0].split(",")
        trader_dict = {"name": trader_info[0],
                       "id": trader_info[1]}
        await interaction.response.edit_message(content=ms.SELECT_TRADER_MESSAGE.format(trader_dict.get("name")),
                                                view=ConfimationView(self.dbcon, trader_dict, self.account_name, self.player))

class ConfimationView(discord.ui.View):
    def __init__(self, dbcon, trader_info, account_name, player):
        super().__init__()
        self.add_item(ConfirmationDropDown(dbcon, trader_info, account_name, player))

class ConfirmationDropDown(discord.ui.Select):
    def __init__(self, dbcon, trader_info, account_name, player):
        self.dbcon = dbcon
        self.trader_info = trader_info
        self.account_name = account_name
        self.player = player
        traders = [discord.SelectOption(label="Yes, please proceed!", value="yes"),
                   discord.SelectOption(label="Nope!", value="no")]
        super().__init__(placeholder="Are you Sure?", options=traders, min_values=1, max_values=1)

    async def callback(self, interaction: Interaction):
        message = ms.REMAIN_TRADER
        is_changed_trader = False
        prev_trader_name = None
        if self.values[0] == "yes":
            pos_ret = self.player.close_all_pos()
            order_ret = self.player.close_all_order()
            if pos_ret.get("code") == 0:
                message = ms.CLOSED_POS
            else:
                message = ms.ERROR_CLOSED_POS
            if order_ret.get("code") == 0:
                message += ms.CLOSED_ORDER
            else:
                message += ms.ERROR_CLOSED_ORDER
            prev_trader_name = self.dbcon.get_trader_by_id(self.account_name).get("trader_name")
            self.dbcon.update_trader_list(self.trader_info.get("id"), self.account_name)
            message += ms.SELECTED_NEW_TRADER.format(self.trader_info.get("name"))
            is_changed_trader = True
        await interaction.response.edit_message(content=message, view=MessageBlockView())
        # Set role
        if is_changed_trader:
            user = interaction.user
            role = discord.utils.get(interaction.guild.roles, name=self.trader_info.get("name"))
            if prev_trader_name:
                original_role = discord.utils.get(interaction.guild.roles, name=prev_trader_name)
                await user.remove_roles(original_role)
            if role:
                await user.add_roles(role)

class MessageBlockView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label="DONE!", disabled=True))