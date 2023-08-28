import config
from disnake.ext import commands
from json_manager import add_report


class Reports(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, inter) -> None:
        if inter.channel.id == config.REPORTING_CHANNEL_ID:
            if (inter.content[0] == '+' or inter.content[0] == '-') and (inter.content[1] != ' '):
                try:
                    if len(inter.content[1::].split('ст ')) > 1:
                        res = inter.content[0] + str((int(inter.content[1::].split('ст ')[0])*64) + int(inter.content[1::].split('ст ')[1]))
                        add_report(inter.author.name, res)
                        await inter.add_reaction(emoji='✅')
                    elif len(inter.content[1::].split(' ')) == 1:
                        res = inter.content
                        add_report(inter.author.name, res)
                        await inter.add_reaction(emoji='✅')
                    else:
                        await inter.add_reaction(emoji='❌')
                except:
                    await inter.add_reaction(emoji='❌')
            else:
                await inter.add_reaction(emoji='❌')


def setup(bot):
    bot.add_cog(Reports(bot))
