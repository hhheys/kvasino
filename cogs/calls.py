import asyncio
import time

import disnake
from disnake.ext import commands

import json_manager
from json_manager import get_tables, take_table, update_statement, vacate_table, save_session
import config

import embed_messages

import datetime as dt


class Calls(commands.Cog):
    calls_info_message = None
    free_croupiers = []
    table_messages_id = []
    cooldown_users = {}
    confirm_tables = {}
    current_sessions = {}

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        await self.update_call_message_embed()
        await self.update_table_messages()

    async def update_call_message_embed(self):
        embed = disnake.Embed(
            title="Вызов персонала",
            description="Перед вызовом, ознакомьтесь со свободными на данный момент крупье.",
            color=disnake.Colour.yellow()
        )
        embed.set_thumbnail('https://cdn-icons-png.flaticon.com/512/5585/5585856.png')
        embed.add_field(name="ㅤ", value="", inline=False)
        embed.add_field(name="Свободные крупье:", value="", inline=False)
        if len(self.free_croupiers) == 0:
            embed.add_field(name='', value='Сейчас нет свободных крупье, для вызова нажмите на необходимую Вам игру.',
                            inline=False)
        else:
            for user_id in self.free_croupiers:
                string = f'<@{user_id}> - '
                if disnake.utils.get(self.bot.get_guild(config.GUILD_ID).members, id=user_id).get_role(
                        config.CROUPIER_POKER_ROLE_ID) is not None:
                    string += f'<@&{config.CROUPIER_POKER_ROLE_ID}>'
                if disnake.utils.get(self.bot.get_guild(config.GUILD_ID).members, id=user_id).get_role(
                        config.CROUPIER_BLACKJACK_ROLE_ID) is not None:
                    string += f'<@&{config.CROUPIER_BLACKJACK_ROLE_ID}>'
                embed.add_field(name='', value=string, inline=False)

        tables = get_tables()
        embed.add_field(name="Идущие игры", value=" ", inline=False)
        if tables[0][0]["croupier"] is not None or tables[0][1]["croupier"] is not None:
            embed.add_field(name="Рулетка", value="", inline=False)
        for table in tables[0]:
            if table["croupier"] is not None:
                embed.add_field(name="",
                                value=f'<@{table["croupier"]}> {table["current_players"]}/{table["max_players"]} игроков',
                                inline=False)

        if tables[1][0]["croupier"] is not None or tables[1][1]["croupier"] is not None:
            embed.add_field(name="Покер", value="", inline=False)
        for table in tables[1]:
            if table["croupier"] is not None:
                embed.add_field(name="",
                                value=f'<@{table["croupier"]}> {table["current_players"]}/{table["max_players"]} игроков, блайнды - {table["blinds"]}',
                                inline=False)

        if tables[2][0]["croupier"] is not None:
            embed.add_field(name="Блекджек", value="", inline=False)
        for table in tables[2]:
            if table["croupier"] is not None:
                embed.add_field(name="",
                                value=f'<@{table["croupier"]}> {table["current_players"]}/{table["max_players"]} игроков',
                                inline=False)
        if self.calls_info_message is None:
            channel = self.bot.get_channel(config.CALLS_CHANNEL_ID)
            await channel.purge(limit=10)
            await channel.send(embed=embed, components=[
                disnake.ui.Button(label="Покер", style=disnake.ButtonStyle.secondary, custom_id="call_poker"),
                disnake.ui.Button(label="Блэкджек", style=disnake.ButtonStyle.secondary, custom_id="call_blackjack"),
                disnake.ui.Button(label="Рулетка", style=disnake.ButtonStyle.secondary, custom_id="call_roulette"),
                disnake.ui.Button(label="Скачки", style=disnake.ButtonStyle.secondary,
                                  custom_id="call_races"),
                disnake.ui.Button(label="Другое", style=disnake.ButtonStyle.secondary, custom_id="call_other"),
                disnake.ui.Button(label="Тех.Персонал", style=disnake.ButtonStyle.secondary,
                                  custom_id="call_technical"),
            ],)
            self.calls_info_message = await channel.fetch_message(channel.last_message_id)
        else:
            await self.calls_info_message.edit(embed=embed)

    async def update_table_messages(self):
        tables = json_manager.get_tables()
        table_messages = []
        for i in range(0, len(tables[0])):
            channel = self.bot.get_channel(config.TABLES_CHANNEL_ID[0][i])
            await channel.purge(limit=10)
            if tables[0][i]['croupier'] is None:
                msg = await channel.send(embed=await embed_messages.roulette_table_message(i), components=[
                    disnake.ui.Button(label="Занять стол",
                                      style=disnake.ButtonStyle.secondary, custom_id="take_table")])
                table_messages.append(msg)
            else:
                msg = await channel.send(embed=await embed_messages.roulette_table_message(i), components=[
                    disnake.ui.Button(label="+ 1 игрок", style=disnake.ButtonStyle.success, custom_id="plus_1"),
                    disnake.ui.Button(label="- 1 игрок", style=disnake.ButtonStyle.danger, custom_id="minus_1"),
                    disnake.ui.Button(label="Освободить стол",
                                      style=disnake.ButtonStyle.danger, custom_id="vacate_table", row=3),
                ], )
                table_messages.append(msg)
        self.table_messages_id.append(table_messages)
        table_messages = []
        for i in range(0, len(tables[1])):
            channel = self.bot.get_channel(config.TABLES_CHANNEL_ID[1][i])
            await channel.purge(limit=10)
            if tables[1][i]['croupier'] is None:
                msg = await channel.send(embed=await embed_messages.poker_table_message(i), components=[
                    disnake.ui.Button(label="Занять стол",
                                      style=disnake.ButtonStyle.secondary, custom_id="take_table")])
                table_messages.append(msg)
            else:
                options = [disnake.SelectOption(label='2/4', value='blind_2/4'),
                           disnake.SelectOption(label='3/6', value='blind_3/6'),
                           disnake.SelectOption(label='4/8', value='blind_4/8'),
                           disnake.SelectOption(label='5/10', value='blind_5/10'),
                           disnake.SelectOption(label='8/16', value='blind_8/16'),
                           disnake.SelectOption(label='10/20', value='blind_10/20'),
                           disnake.SelectOption(label='20/40', value='blind_20/40'),
                           disnake.SelectOption(label='32/64', value='blind_32/64')]
                msg = await channel.send(embed=await embed_messages.poker_table_message(i), components=[
                    disnake.ui.Button(label="+ 1 игрок", style=disnake.ButtonStyle.success, custom_id="plus_1"),
                    disnake.ui.Button(label="- 1 игрок", style=disnake.ButtonStyle.danger, custom_id="minus_1"),
                    disnake.ui.StringSelect(placeholder="Блайнды", options=options, custom_id="change_blind", min_values=1, max_values=1),
                    disnake.ui.Button(label="Освободить стол", style=disnake.ButtonStyle.danger, custom_id="vacate_table"),
                ], )
                table_messages.append(msg)
        self.table_messages_id.append(table_messages)
        table_messages = []
        channel = self.bot.get_channel(config.TABLES_CHANNEL_ID[2][0])
        await channel.purge(limit=10)
        if tables[2][0]['croupier'] is None:
            msg = await channel.send(embed=await embed_messages.blackjack_table_message(0), components=[
                disnake.ui.Button(label="Занять стол",
                                  style=disnake.ButtonStyle.secondary, custom_id="take_table")])
            table_messages.append(msg)
        else:
            msg = await channel.send(embed=await embed_messages.blackjack_table_message(0), components=[
                disnake.ui.Button(label="+ 1 игрок", style=disnake.ButtonStyle.success, custom_id="plus_1"),
                disnake.ui.Button(label="- 1 игрок", style=disnake.ButtonStyle.danger, custom_id="minus_1"),
                disnake.ui.Button(label="Освободить стол",
                                  style=disnake.ButtonStyle.danger, custom_id="vacate_table", row=3),
            ], )
            table_messages.append(msg)
        self.table_messages_id.append(table_messages)

    async def update_table_message(self, table_type, table_id):
        table_info = json_manager.get_tables()[table_type][table_id]
        if table_info['croupier'] is not None:
            if table_type == 0:
                await self.table_messages_id[0][table_id].edit(embed=await embed_messages.roulette_table_message(table_id), components=[
                    disnake.ui.Button(label="+ 1 игрок", style=disnake.ButtonStyle.success, custom_id="plus_1"),
                    disnake.ui.Button(label="- 1 игрок", style=disnake.ButtonStyle.danger, custom_id="minus_1"),
                    disnake.ui.Button(label="Освободить стол",
                                      style=disnake.ButtonStyle.danger, custom_id="vacate_table", row=3),
                ],)
            elif table_type == 1:

                options = [disnake.SelectOption(label='2/4', value='blind_2/4'),
                           disnake.SelectOption(label='3/6', value='blind_3/6'),
                           disnake.SelectOption(label='4/8', value='blind_4/8'),
                           disnake.SelectOption(label='5/10', value='blind_5/10'),
                           disnake.SelectOption(label='8/16', value='blind_8/16'),
                           disnake.SelectOption(label='10/20', value='blind_10/20'),
                           disnake.SelectOption(label='20/40', value='blind_20/40'),
                           disnake.SelectOption(label='32/64', value='blind_32/64')]
                await self.table_messages_id[1][table_id].edit(embed=await embed_messages.poker_table_message(table_id), components=[
                    disnake.ui.Button(label="+ 1 игрок", style=disnake.ButtonStyle.success, custom_id="plus_1"),
                    disnake.ui.Button(label="- 1 игрок", style=disnake.ButtonStyle.danger, custom_id="minus_1"),
                    disnake.ui.StringSelect(placeholder="Блайнды", options=options, custom_id="change_blind", min_values=1,
                                            max_values=1),
                    disnake.ui.Button(label="Освободить стол", style=disnake.ButtonStyle.danger, custom_id="vacate_table"),
                ],)
            elif table_type == 2:
                await self.table_messages_id[table_type][0].edit(embed=await embed_messages.blackjack_table_message(table_id), components=[
                    disnake.ui.Button(label="+ 1 игрок", style=disnake.ButtonStyle.success, custom_id="plus_1"),
                    disnake.ui.Button(label="- 1 игрок", style=disnake.ButtonStyle.danger, custom_id="minus_1"),
                    disnake.ui.Button(label="Освободить стол",
                                      style=disnake.ButtonStyle.danger, custom_id="vacate_table", row=3),
                ],)
        else:
            table_name = ""
            if table_type == 0:
                table_name = "Рулетка"
            elif table_type == 1:
                table_name = "Стол для покера"
            elif table_type == 2:
                table_name = "Стол для блекджека"
            embed = disnake.Embed(
                title=f"{table_name} №{table_id + 1}",
                description="",
                color=disnake.Colour.yellow()
            )
            embed.add_field(name=" ", value=" ", inline=False)
            embed.add_field(name="", value="Этот стол сейчас свободен. Нажмите на кнопку ниже чтобы занять стол.",
                            inline=False)
            await self.table_messages_id[table_type][table_id].edit(embed=embed, components=[
                disnake.ui.Button(label="Занять стол",
                                  style=disnake.ButtonStyle.secondary, custom_id="take_table")])

    @commands.slash_command()
    async def online(self, inter):
        if inter.user.id not in self.free_croupiers:
            self.free_croupiers.append(inter.user.id)
            await self.update_call_message_embed()
            await inter.response.send_message('Вы успешно отметились как ОНЛАЙН', ephemeral=True)
        else:
            await inter.response.send_message('Вы уже онлайн', ephemeral=True)

    @commands.slash_command()
    async def offline(self, inter):
        if inter.user.id in self.free_croupiers:
            self.free_croupiers.remove(inter.user.id)
            await self.update_call_message_embed()
            await inter.response.send_message('Вы успешно отметились как ОФФЛАЙН', ephemeral=True)
        else:
            await inter.response.send_message('Вы не были онлайн!', ephemeral=True)

    @commands.slash_command()
    async def calls_update(self, inter):
        await self.update_call_message_embed()

    @commands.slash_command()
    async def tables_update(self, inter):
        await self.update_table_messages()

    def get_table_type(self, channel_id):
        tables = config.TABLES_CHANNEL_ID
        for i in range(0, len(tables)):
            if channel_id in tables[i]:
                return i

    @commands.Cog.listener(name="on_button_click")
    async def help_listener(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id not in ["call_poker", "call_blackjack", "call_roulette", "call_races",
                                             "call_other", "call_technical", "confirm_call", "take_table", "plus_1",
                                             "minus_1", "vacate_table", "change_blind", "confirm", "confirm_table"]:
            return

        if inter.component.custom_id[:4:] == "call":
            perm = True
            if inter.author.id in self.cooldown_users:
                time5 = dt.timedelta(minutes=5)
                if dt.datetime.now() - self.cooldown_users[inter.author.id] < time5:
                    perm = False
                    await inter.response.send_message('Подождите немного перед следующим вызовом крупье.', ephemeral=True)
                else:
                    perm = True
                    self.cooldown_users[inter.author.id] = dt.datetime.now()
            else:
                self.cooldown_users[inter.author.id] = dt.datetime.now()
            if perm:
                await inter.response.send_message('Вы успешно вызвали крупье!', ephemeral=True)
                if inter.component.custom_id[5::] == 'poker':
                    await self.bot.get_channel(config.NOTIFICATION_CROUPIER_CHANNEL_ID).send(
                        f'<@&{config.CROUPIER_POKER_ROLE_ID}> игрок <@{inter.author.id}> вызвал крупье для Покера!',
                        components=[disnake.ui.Button(label="Принять вызов", style=disnake.ButtonStyle.secondary,
                                                      custom_id="confirm")])

                elif inter.component.custom_id[5::] == 'blackjack':
                    await self.bot.get_channel(config.NOTIFICATION_CROUPIER_CHANNEL_ID).send(
                        f'<@&{config.CROUPIER_BLACKJACK_ROLE_ID}> игрок <@{inter.author.id}> вызвал крупье для Блекджека!',
                        components=[disnake.ui.Button(label="Принять вызов", style=disnake.ButtonStyle.secondary,
                                                      custom_id="confirm")])

                elif inter.component.custom_id[5::] == 'races':
                    await self.bot.get_channel(config.NOTIFICATION_CROUPIER_CHANNEL_ID).send(
                        f'<@&{config.CROUPIER_RACES_ROLE_ID}> игрок <@{inter.author.id}> вызвал крупье для Скачек!',
                        components=[disnake.ui.Button(label="Принять вызов", style=disnake.ButtonStyle.secondary,
                                                      custom_id="confirm")])

                elif inter.component.custom_id[5::] == 'roulette':
                    await self.bot.get_channel(config.NOTIFICATION_CROUPIER_CHANNEL_ID).send(
                        f'<@&{config.CROUPIER_ROULETTE_ROLE_ID}> игрок <@{inter.author.id}> вызвал крупье для Рулетки!',
                        components=[disnake.ui.Button(label="Принять вызов", style=disnake.ButtonStyle.secondary,
                                                      custom_id="confirm")])

                elif inter.component.custom_id[5::] == 'other':
                    await self.bot.get_channel(config.NOTIFICATION_CROUPIER_CHANNEL_ID).send(
                        f'<@&{config.CROUPIER_ROLE_ID}> игрок <@{inter.author.id}> вызвал крупье!',
                        components=[disnake.ui.Button(label="Принять вызов", style=disnake.ButtonStyle.secondary,
                                                      custom_id="confirm")])

                elif inter.component.custom_id[5::] == 'technical':
                    await inter.response.send_message('Вы успешно вызвали тех.персонал!', ephemeral=True)
                    await self.bot.get_channel(config.NOTIFICATION_CROUPIER_CHANNEL_ID).send(
                        f'<@&{config.TECHNICAL_ROLE_ID}> игрок <@{inter.author.id}> вызвал Тех.Персонал!')

        elif inter.component.custom_id == "confirm":
            await inter.response.defer()
            await inter.message.edit(f"ПРИНЯТО <@{inter.author.id}> || {inter.message.content}", components=[])
            user = await self.bot.fetch_user(inter.author.id)
            await user.send(f'Крупье {inter.author.name} принял вызов! В скором времени он с вами свяжется.')

        elif inter.component.custom_id == "take_table":
            tables = json_manager.get_tables()
            table_type = self.get_table_type(inter.channel_id)
            permission = True
            for i in tables:
                for table in i:
                    if table["croupier"] == inter.author.id:
                        permission = False
                        await inter.response.send_message('Вы уже заняли стол. Нельзя занимать несколько столов одновременно', ephemeral=True)
            if permission:
                if tables[table_type][config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id)]["croupier"] is None:
                    take_table(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id), inter.author.id)
                    await self.update_table_message(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id))
                    await self.update_call_message_embed()
                    await inter.response.send_message('Вы заняли стол', ephemeral=True)
                    await self.open_session(inter.author.id)
                    self.current_sessions[inter.author.id]["table_type"] = self.get_table_type(inter.channel_id)
                    await self.table_check(inter.channel_id)

        elif inter.component.custom_id in ["plus_1", "minus_1", "vacate_table", "change_blind", "confirm_table"] and json_manager.get_tables()[self.get_table_type(inter.channel_id)][config.TABLES_CHANNEL_ID[self.get_table_type(inter.channel_id)].index(inter.channel_id)]["croupier"] != inter.author.id:
            await inter.response.send_message('Это не ваш стол.', ephemeral=True)

        elif inter.component.custom_id == "plus_1":
            tables = json_manager.get_tables()
            table_type = self.get_table_type(inter.channel_id)
            current_players = tables[table_type][config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id)]["current_players"]
            max_players = tables[table_type][config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id)]["max_players"]
            if current_players < max_players:
                if self.current_sessions[inter.author.id]['max_players'] < current_players:
                    self.current_sessions[inter.author.id]['max_players'] = current_players + 1
                update_statement(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id),
                                     'current_players', current_players + 1)
                await self.update_table_message(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id))
                await self.update_call_message_embed()
                await inter.response.defer()

            else:
                await inter.response.send_message('Стол переполнен, невозможно добавить игрока.', ephemeral=True)

        elif inter.component.custom_id == "minus_1":
            tables = json_manager.get_tables()
            table_type = self.get_table_type(inter.channel_id)
            current_players = tables[table_type][config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id)]["current_players"]
            if current_players > 0:
                update_statement(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id),
                                 'current_players', current_players - 1)
                await self.update_table_message(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id))
                await self.update_call_message_embed()
                await inter.response.defer()
            else:
                await inter.response.send_message('Стол пуст, невозможно убавить игрока.', ephemeral=True)

        elif inter.component.custom_id == "change_blind":
            table_type = self.get_table_type(inter.channel_id)
            update_statement(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id),
                             'blinds', inter.values)
            await self.update_table_message(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id))
            await self.update_call_message_embed()
            await inter.response.defer()

        elif inter.component.custom_id == "vacate_table":
            if inter.author.id in self.confirm_tables:
                self.confirm_tables.pop(inter.author.id)
            tables = json_manager.get_tables()
            table_type = self.get_table_type(inter.channel_id)
            vacate_table(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id))
            update_statement(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id),
                             'current_players', 0)
            await self.update_table_message(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id))
            await self.update_call_message_embed()
            await self.close_session(inter.author.id, False)
            await inter.response.send_message('Вы освободили стол', ephemeral=True)

        elif inter.component.custom_id == "confirm_table":
            if inter.author.id in self.confirm_tables:
                self.confirm_tables.pop(inter.author.id)
                await inter.message.delete()
                await inter.response.defer()

    @commands.Cog.listener()
    async def on_dropdown(self, inter):
        if inter.component.custom_id == "change_blind":
            table_type = self.get_table_type(inter.channel_id)
            update_statement(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id),
                             'blinds', inter.values[0][6::])
            await self.update_table_message(table_type, config.TABLES_CHANNEL_ID[table_type].index(inter.channel_id))
            await self.update_call_message_embed()
            await inter.response.defer()

    async def table_check(self, channel_id):
        while get_tables()[self.get_table_type(channel_id)][config.TABLES_CHANNEL_ID[self.get_table_type(channel_id)].index(channel_id)]["croupier"] is not None:
            await asyncio.sleep(30)
            croupier_id = get_tables()[self.get_table_type(channel_id)][config.TABLES_CHANNEL_ID[self.get_table_type(channel_id)].index(channel_id)]["croupier"]
            if croupier_id in self.confirm_tables:
                channel = self.bot.get_channel(channel_id)
                await channel.purge(limit=1)
                user = await self.bot.fetch_user(croupier_id)
                await user.send(f'Стол был закрыт из-за неактивности с вашей стороны.')
                await self.close_session(croupier_id, True)
                vacate_table(self.get_table_type(channel_id), config.TABLES_CHANNEL_ID[self.get_table_type(channel_id)].index(channel_id))
                self.confirm_tables.pop(croupier_id)
                await self.update_call_message_embed()
                await self.update_table_message(self.get_table_type(channel_id), config.TABLES_CHANNEL_ID[self.get_table_type(channel_id)].index(channel_id))
            else:
                await self.send_confirm_message(channel_id, croupier_id)
                self.confirm_tables[croupier_id] = dt.datetime.now()

    async def send_confirm_message(self, channel_id, croupier_id):
        channel = self.bot.get_channel(channel_id)
        for i in range(0, 3):
            msg = await channel.send(f"<@{croupier_id}>")
            await msg.delete()
        await channel.send("Вы еще тут? Нажмите на кнопку внизу в течение 5-ти минут иначе стол автоматически закроется.", components=[
                    disnake.ui.Button(label="Я тут!", style=disnake.ButtonStyle.success, custom_id="confirm_table")])

    async def open_session(self, croupier_id):
        session = {
            "open_date": str(dt.datetime.now()),
            "close_date": None,
            "max_players": 0,
            "table_type": None,
            "is_close_inactive": False
        }
        self.current_sessions[croupier_id] = session

    async def close_session(self, croupier_id, is_inactive):
        if croupier_id in self.current_sessions:
            self.current_sessions[croupier_id]["close_date"] = str(dt.datetime.now())
            if is_inactive:
                self.current_sessions[croupier_id]["is_close_inactive"] = True
            save_session(croupier_id, self.current_sessions[croupier_id])
            self.current_sessions.pop(croupier_id)



def setup(bot):
    bot.add_cog(Calls(bot))

