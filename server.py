from aiohttp import web
from discord.ext import commands, tasks
import discord
import os
import aiohttp

app = web.Application()
routes = web.RouteTableDef()


async def setup(bot: commands.Bot):
    await bot.add_cog(Webserver(bot))

class Webserver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.web_server.start()

        @routes.get('/')
        async def welcome(request):
            return web.Response(text="Hello, world")

        @routes.post('/github')
        async def github(request):
            data = await request.json()

            print(data)

            actor = data.get("actor")
            payload = data.get("payload")
            commits = payload.get("commits")
            last_commit = commits[-1]

            embed = discord.Embed(title="New push", color=0xff00, url=last_commit.get("url"))
            embed.add_field(name="Message", value=last_commit.get("message"), inline=False)
            embed.add_field(name="Author", value=last_commit.get("author").get("name"), inline=False)
            embed.set_author(name=last_commit.get("author").get("name"), icon_url=actor["avatar_url"])


            channel = await self.bot.fetch_channel(1137701853853929592)
            await channel.send(embed=embed)

            return web.Response(text="Received GitHub Webhook")

        self.webserver_port = os.environ.get('PORT', 10000)
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()