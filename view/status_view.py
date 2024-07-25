import discord
from bingx import BINGX

MIN_WALLET = 300
MAX_WALLET = 3000


def add_embed_fields(embed, trader_api, msg_api, msg_wallet_min, msg_wallet_max, balance, msg_trader, expiry):
    embed.add_field(name=f"Account Name: {trader_api.get('player_id')}", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name=f"API Setup: {msg_api}", value="", inline=False)
    embed.add_field(name=f"Future Wallet > {MIN_WALLET}: {msg_wallet_min}", value="", inline=False)
    embed.add_field(name=f"Future Wallet < {MAX_WALLET}: {msg_wallet_max}", value="", inline=False)
    embed.add_field(name=f"Wallet Amount: `{balance}`", value="", inline=False)
    embed.add_field(name="", value="", inline=False)
    embed.add_field(name=f"Following Traders: {msg_trader}", value="", inline=False)
    embed.add_field(name=f"Damage Cost: `{trader_api.get('damage_cost')}%`", value="", inline=False)
    embed.add_field(name=f"Expiry Date: `{expiry}`", value="", inline=False)


def create_account_embed(trader_api, count):
    embed = discord.Embed(title=f"# Your AutoTrade Account {count} Status", description="")
    bingx = BINGX(trader_api.get("api_key"), trader_api.get("api_secret"))
    response = bingx.get_wallet()

    msg_api = "❌"
    msg_wallet_min = "❌"
    msg_wallet_max = "❌"
    msg_trader = "❌"
    balance = "❌"
    expiry = "None"
    if trader_api.get('expiry_date'):
        expiry = trader_api.get('expiry_date')

    if trader_api.get("trader_name"):
        msg_trader = f" `{trader_api.get('trader_name')}`"

    if response.get("code") == 0 or response.get("code") == 200:
        msg_api = "✅"
        balance = float(response.get("data").get("balance").get("availableMargin"))
        if balance > float(MIN_WALLET):
            msg_wallet_min = "✅"
        if balance < float(MAX_WALLET):
            msg_wallet_max = "✅"

    add_embed_fields(embed, trader_api, msg_api, msg_wallet_min, msg_wallet_max, balance, msg_trader, expiry)
    return embed


class StatusView:

    def __init__(self, dbcon, interaction, trader_api_list, discord_id):
        self.dbcon = dbcon
        self.interaction = interaction
        self.trader_api_list = trader_api_list
        self.discord_id = discord_id

    def compute(self):
        if not self.trader_api_list:
            return []

        embed_list = []

        for count, trader_api in enumerate(self.trader_api_list, start=1):
            embed = create_account_embed(trader_api, count)
            embed_list.append(embed)

        return embed_list
