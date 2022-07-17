import os
from disnake.colour import Color
from disnake.embeds import Embed
from dotenv.main import load_dotenv

load_dotenv()

BOT_NAME = "ShockMart"

TOKEN = os.getenv("TOKEN")