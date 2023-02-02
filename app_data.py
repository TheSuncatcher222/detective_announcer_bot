from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN: str = os.getenv('TELEGRAM_BOT_TOKEN')
VK_TOKEN: str = os.getenv('VK_TOKEN')
VK_USER_ME: str = os.getenv('VK_USER_ME')
VK_CHAT_TARGET: int = os.getenv('VK_CHAT_TARGET')
VK_GROUP_TARGET: int = os.getenv('VK_GROUP_TARGET')
