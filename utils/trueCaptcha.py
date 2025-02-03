import base64
import os

import requests
from dotenv import load_dotenv

# Get the absolute path to the directory containing this Python script (alembic folder)
current_dir = os.path.dirname(os.path.abspath(__file__))
print(f"Current directory: {current_dir}", flush=True)

# Get the absolute path to the project root directory (one levels up from the current directory)
project_root = os.path.abspath(os.path.join(current_dir, ".."))
print(f"Project root directory: {project_root}", flush=True)

# Load environment variables from the .env file located in the project root directory
dotenv_path = os.path.join(project_root, ".env")
print(f"Loading environment variables from: {dotenv_path}", flush=True)
load_dotenv(dotenv_path)

# defining credentials file path from environment variable
apikey = os.getenv("TRUE_CAPTCHA_API_KEY")


def solve_captcha(imagePath):
    # logger.info("Solving captcha using TrueCaptcha API.")
    with open(imagePath, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("ascii")
        url = "https://api.apitruecaptcha.org/one/gettext"

        data = {
            "userid": "srikarvuchiha@gmail.com",
            "apikey": apikey,
            "data": encoded_string,
            "mode": "auto",
            "len_str": "6",
        }
        response = requests.post(url=url, json=data, timeout=5)
        data = response.json()
        return data["result"]


print(solve_captcha("utils/captcha.png"))
