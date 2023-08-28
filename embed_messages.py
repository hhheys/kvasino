import disnake

import json_manager
from json_manager import get_free_croupiers,get_tables
import config


def call_message(bot):
    embed = disnake.Embed(
        title="Вызов персонала",
        description="Перед вызовом, ознакомьтесь со свободными на данный момент крупье.",
        color=disnake.Colour.yellow()
    )
    embed.set_thumbnail('https://cdn-icons-png.flaticon.com/512/5585/5585856.png')
    embed.add_field(name="ㅤ", value="", inline=False)
    embed.add_field(name="Свободные крупье:", value="", inline=False)
    if len(get_free_croupiers()) == 0:
        embed.add_field(name='', value='Сейчас нет свободных крупье, для вызова нажмите на необходимую Вам игру.',
                        inline=False)
    else:
        for user_id in get_free_croupiers():
            string = f'<@{user_id}> - '
            if disnake.utils.get(bot.get_guild(config.GUILD_ID).members, id=user_id).get_role(
                    config.CROUPIER_POKER_ROLE_ID) is not None:
                string += f'<@&{config.CROUPIER_POKER_ROLE_ID}>'
            if disnake.utils.get(bot.get_guild(config.GUILD_ID).members, id=user_id).get_role(
                    config.CROUPIER_BLACKJACK_ROLE_ID) is not None:
                string += f'<@&{config.CROUPIER_BLACKJACK_ROLE_ID}>'
            embed.add_field(name='', value=string, inline=False)

    tables = get_tables()
    if tables['poker'][0]["croupier"] is not None or tables['poker'][1]["croupier"] is not None:
        embed.add_field(name="Покер", value="", inline=False)
    for table in tables['poker']:
        if table["croupier"] is not None:
            embed.add_field(name="",
                            value=f'<@{table["croupier"]}> {table["current_players"]}/{table["max_players"]} игроков, блайнды - {table["blinds"]}',
                            inline=False)

    if tables['blackjack'][0]["croupier"] is not None or tables['blackjack'][1]["croupier"] is not None:
        embed.add_field(name="Блекджек", value="", inline=False)
    for table in tables['blackjack']:
        if table["croupier"] is not None:
            embed.add_field(name="ㅤ",
                            value=f'<@{table["croupier"]}> {table["current_players"]}/{table["max_players"]} игроков',
                            inline=False)
    return embed


async def roulette_table_message(number):
    embed = disnake.Embed(
        title=f"Рулетка №{number+1}",
        description="",
        color=disnake.Colour.yellow()
    )
    embed.add_field(name=" ", value=" ", inline=False)
    table_info = json_manager.get_tables()[0][number]
    if table_info['croupier'] is None:
        embed.add_field(name="", value="Этот стол сейчас свободен. Нажмите на кнопку ниже чтобы занять стол.", inline=False)
    else:
        embed.add_field(name="Крупье", value=f"<@{table_info['croupier']}>", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Количество игроков",
                        value=f"{table_info['current_players']}/{table_info['max_players']}", inline=False)
    return embed


async def poker_table_message(number):
    embed = disnake.Embed(
        title=f"Стол для покера №{number+1}",
        description="",
        color=disnake.Colour.yellow()
    )
    embed.add_field(name=" ", value=" ", inline=False)
    table_info = json_manager.get_tables()[1][number]
    if table_info['croupier'] is None:
        embed.add_field(name="", value="Этот стол сейчас свободен. Нажмите на кнопку ниже чтобы занять стол.", inline=False)
    else:
        embed.add_field(name="Крупье", value=f"<@{table_info['croupier']}>", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Количество игроков",
                        value=f"{table_info['current_players']}/{table_info['max_players']}", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Блайнды", value=f"{table_info['blinds']}", inline=False)
    return embed


async def blackjack_table_message(number):
    embed = disnake.Embed(
        title=f"Стол для блекджека №{number+1}",
        description="",
        color=disnake.Colour.yellow()
    )
    embed.add_field(name=" ", value=" ", inline=False)
    table_info = json_manager.get_tables()[2][number]
    if table_info['croupier'] is None:
        embed.add_field(name="", value="Этот стол сейчас свободен. Нажмите на кнопку ниже чтобы занять стол.", inline=False)
    else:
        embed.add_field(name="Крупье", value=f"<@{table_info['croupier']}>", inline=False)
        embed.add_field(name="", value="", inline=False)
        embed.add_field(name="Количество игроков",
                        value=f"{table_info['current_players']}/{table_info['max_players']}", inline=False)
    return embed
