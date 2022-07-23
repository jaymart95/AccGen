from lib.bot import bot
import logging


VERSION = '1.0'

formatter = logging.Formatter(
    fmt="[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
)
logger = logging.getLogger()
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("bot.log")
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)


bot.run(VERSION)
