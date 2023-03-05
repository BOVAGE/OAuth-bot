import discord
import logging
from discord.ext import commands
from config import (
    BOT_TOKEN,
    FACEBOOK_CLIENT_ID,
    FACEBOOK_LOGIN_URL,
    FACEBOOK_CLIENT_SECRET,
    REDIRECT_URI,
    ACCESS_TOKEN_ENDPOINT,
    USER_INFO_ENDPOINT,
)

from authlib.integrations.httpx_client import AsyncOAuth2Client
import server
import utils

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s, %(levelname)s: %(name)s:%(lineno)d - %(message)s",
)
logger = logging.getLogger(__name__)

client_intents = discord.Intents.default()
client_intents.message_content = True
client = commands.Bot(command_prefix=".", intents=client_intents)


@client.event
async def on_ready() -> None:
    logger.info(f"Logged in as a bot {client.user.name}")


@client.command()
async def ping(ctx) -> None:
    """check whether bot is active or not
    ping ->  pong!!!"""
    await ctx.send("Pong!")


class FacebookLogin(discord.ui.View):
    @discord.ui.button(label="Login with Facebook", style=discord.ButtonStyle.primary)
    async def device_code_login(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        code, user_code = await utils.get_device_login_codes()
        login_code_embed = discord.Embed(
            title="Login with Facebook",
            description="Connecting to Facebook",
            color=discord.Colour.blue(),
        )
        login_code_embed.add_field(
            name="Instruction",
            value="Next, visit facebook.com/device (http://facebook.com/device) on your desktop or smartphone and enter this code. "
            "You could click the link below to avoid typing.",
        )
        code_link = f"http://facebook.com/device?user_code={user_code}"
        login_code_embed.add_field(name="Code Link", value=code_link)
        login_code_embed.add_field(name="Code", value=user_code)
        login_code_embed.set_footer(text="Awesome!")
        await interaction.response.send_message(embed=login_code_embed)

        access_token_details = await utils.get_access_token_from_login_code(
            code=code, should_poll=True, poll_interval=5
        )
        fb_client = AsyncOAuth2Client(token=access_token_details)
        user_info = await fb_client.get(f"{USER_INFO_ENDPOINT}")
        await interaction.channel.send(user_info.json())


@client.command(name="dlogin")
async def device_login(ctx) -> None:
    """Login using Device Authorization Grant Flow"""
    await ctx.send("Welcome to the Facebook Device Login!")
    fb_login_button = FacebookLogin()
    await ctx.reply(view=fb_login_button)


@client.command(name="login")
async def login_with_fb(ctx) -> None:
    """starts login with facebook process"""
    await ctx.send("Login with Facebook")
    fb_client = AsyncOAuth2Client(
        client_id=FACEBOOK_CLIENT_ID,
        client_secret=FACEBOOK_CLIENT_SECRET,
        redirect_uri=REDIRECT_URI + "/",
    )
    uri, state = fb_client.create_authorization_url(FACEBOOK_LOGIN_URL, state="test#")
    await ctx.send(f"Click this link to login with facebook {uri}")
    # define callback function to handle code parameter
    async def handle_authorization_response(authorization_response):
        # update state of the fb_client so it can match the one sent in the authorization url
        fb_client.state = state
        token = await fb_client.fetch_token(
            ACCESS_TOKEN_ENDPOINT,
            authorization_response=f"{REDIRECT_URI}{authorization_response}",
        )
        fb_client.token = token
        user_info = await fb_client.get(f"{USER_INFO_ENDPOINT}")
        await ctx.send(user_info.json())

    # start http server
    server.start(handle_authorization_response)


client.run(BOT_TOKEN)
