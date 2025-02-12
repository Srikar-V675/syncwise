import base64

import requests

from syncwise.settings import (
    TRUE_CAPTCHA_API_KEY,
    TRUE_CAPTCHA_URL,
    TRUE_CAPTCHA_USER_ID,
)


class TrueCaptchaConfigError(Exception):
    """Raised when TrueCaptcha configuration is missing."""

    def __init__(
        self,
        message="TrueCaptcha API Key or User ID not found in environment variables",
    ):
        self.message = message
        super().__init__(self.message)


def solve_captcha(imagePath):
    if not TRUE_CAPTCHA_API_KEY or not TRUE_CAPTCHA_USER_ID:
        raise TrueCaptchaConfigError()

    try:
        with open(imagePath, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode("ascii")
            url = TRUE_CAPTCHA_URL

            data = {
                "userid": TRUE_CAPTCHA_USER_ID,
                "apikey": TRUE_CAPTCHA_API_KEY,
                "data": encoded_string,
                "mode": "auto",
                "len_str": "6",
            }
            response = requests.post(url=url, json=data, timeout=5)
            response.raise_for_status()
            return response.json()["result"]
    except Exception as e:
        raise Exception(f"Error in solving captcha: {str(e)}")


# print(solve_captcha("utils/captcha.png"))
