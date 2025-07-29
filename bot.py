import discord
from discord import app_commands
import requests
import json
import os
from dotenv import load_dotenv
import keyring
import jwt
import datetime
import cryptography
from convex import ConvexClient
import random

convex_client = ConvexClient("https://sensible-hawk-744.convex.cloud")

load_dotenv()

keyring.set_keyring
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client=client)
list_group = app_commands.Group(name="list", description="List related commands")

userCount = json.loads(requests.get('https://sensible-hawk-744.convex.site/users', headers={"X-API-KEY": os.getenv("DOTLIST_DEV_KEY")}).text).get("totalUsers")

def authenticate(discordUsername: str, login: bool = False) -> str | None:
    userId = keyring.get_password("dotbot_uid", discordUsername)
    currentToken = keyring.get_password("dotlist_jwt", userId)
    try:
        decoded = jwt.decode(currentToken, algorithms="RS256", key=os.getenv("DOTLIST_PUBLIC_KEY"), audience="convex").get("exp")
    except Exception as e:
        decoded = 0
        #raise e
    if currentToken == None and login == False:
        print("Not logged in")
    elif currentToken == None or decoded <= int(datetime.datetime.now().timestamp()):
        print("Generating new token")
        payload = {
            "sub": userId,
            "iss": "https://sensible-hawk-744.convex.site",
            "aud": "convex",
            "iat": int(datetime.datetime.now().timestamp()),
            "exp": int((datetime.datetime.now() + datetime.timedelta(hours=1)).timestamp())
        }
        print(f'iat: {payload.get("iat")}')
        print(f'exp: {payload.get("exp")}')
        header = {
            "alg": "RS256"
        }
        newToken = jwt.encode(payload=payload, key=os.getenv("DOTLIST_PRIVATE_KEY"), headers=header)
        keyring.set_password("dotlist_jwt", userId, newToken)
        return newToken
    else:
        print("Using old token")
        return currentToken
    return None

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Activity(name=f"custom", type=discord.ActivityType.custom, state=f"dotlisting with {userCount} users"))
    tree.add_command(list_group)
    await tree.sync()
    print(f'Logged in as {client.user}')

@tree.command(name="aadish", description="Aadish message")
async def aadish_cmd(interaction: discord.Interaction):
    random.seed(int(datetime.datetime.now().timestamp()))
    sel1 = random.random()
    if (sel1 < 0.5): await interaction.response.send_message("...")
    else:
        await interaction.response.send_message("use dotlist lite")

@tree.command(name="login", description="Log in to Dotbot. Requires a key generated in Dotlist.")
@app_commands.describe(username="Your Dotlist username")
@app_commands.describe(key="Dotlist authentication key, generated in Dotlist settings")
async def login_cmd(interaction: discord.Interaction, username: str, key: int):
    user = convex_client.query("main:findUserByUsername", {"username": username})

    try:
        userId = user.get("userId")
    except Exception as e:
        await interaction.response.send_message("Could not login. No user exists with that username.")
        #raise e
    else:
        try:
            keyring.set_password("dotbot_uid", interaction.user.name, userId)
            convex_client.set_auth(authenticate(interaction.user.name, True))
            verifiedKey = convex_client.query("auth:getAuthKey")
            if (verifiedKey != key) :
                convex_client.set_auth(None)
                await interaction.response.send_message("Invalid key passed.")
                return
                #raise KeyError
        except Exception as e:
            await interaction.response.send_message("Error authenticating. Please try again.")
            #raise e
        else:
            await interaction.response.send_message(f"Logged in as {user.get('username')}")

    print(f'Command `login` run by {interaction.user.name} returned {user}')

@tree.command(name="ping", description="Ping the server's health")
async def ping_cmd(interaction: discord.Interaction):
    params = {

    }
    response = requests.get(
        'https://sensible-hawk-744.convex.site/health',
        params=params
    )
    try:
        await interaction.response.send_message(json.dumps(json.loads(response.text), indent=4))
    except Exception as e:
        await interaction.response.send_message(response.text)

    print(f'Command `ping` run by {interaction.user.name} returned {response.text}')

@list_group.command(name="all", description="Returns all user lists")
async def list_all_cmd(interaction: discord.Interaction):
    convex_client.set_auth(authenticate(interaction.user.name))
    lists = convex_client.query("lists:getLists")
    excluded_keys = {"nodes", "userId", "order", "_creationTime", "teamId", "updatedAt"}
    just_lists = [
        {k: v for k, v in list_entry.items() if k not in excluded_keys}
        for list_entry in lists
    ]
    print(json.dumps(just_lists, indent=4))
    await interaction.response.send_message(json.dumps(just_lists, indent=4))
    convex_client.set_auth(None)


@tree.command(name="user", description="Get info about your user profile")
async def user_cmd(interaction: discord.Interaction):
    params = {

    }
    response = requests.get(
        'https://polished-beagle-841.convex.site/api/user',
        params=params
    )
    user = convex_client.query("main:findUserByUsername", {"username": "danivation"})
    print(f'Convex: {user}')
    try:
        await interaction.response.send_message(json.dumps(json.loads(response.text), indent=4))
    except Exception as e:
        await interaction.response.send_message(response.text)

    print(f'Command `user` run by {interaction.user.name} returned {response.text}')


client.run(os.getenv("BOT_TOKEN"))
