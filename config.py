from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
FACEBOOK_CLIENT_ID = os.getenv("FACEBOOK_CLIENT_ID")
FACEBOOK_CLIENT_SECRET = os.getenv("FACEBOOK_CLIENT_SECRET")

BASE_URL = "https://graph.facebook.com/v16.0/"
FACEBOOK_LOGIN_URL = f"https://www.facebook.com/v16.0/dialog/oauth"
ACCESS_TOKEN_ENDPOINT = f"{BASE_URL}oauth/access_token"
USER_INFO_ENDPOINT = f"{BASE_URL}me"
REDIRECT_URI = "http://localhost:3000"

CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")
FACEBOOK_APP_ACCESS_TOKEN = f"{FACEBOOK_CLIENT_ID}|{CLIENT_TOKEN}"

DEVICE_ACCESS_TOKEN_URL = f"{BASE_URL}device/login_status"
DEVICE_LOGIN_CODE_URL = f"{BASE_URL}device/login"
POLLING_INTERVAL_FOR_ACCESS_TOKEN = 5
