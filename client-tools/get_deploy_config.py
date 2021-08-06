from urllib.parse import parse_qsl, quote, urlsplit
from config import CLITENT_ID, CLITENT_SECRET
import requests


def get_code() -> str:
    scope = "offline_access Files.Read.All profile openid"
    url = (
        "https://login.microsoftonline.com/common/oauth2/v2.0/authorize?client_id="
        + CLITENT_ID
        + "&response_type=code&redirect_uri=http://localhost&response_mode=query&scope="
        + quote(scope)
        + "&state=200"
    )

    print("请在浏览器打开下面的链接进行授权，完成后把跳转到的以 localhost 为开头的地址粘贴下来并按回车")
    print(
        "Please open the link below in your browser to authorize, after completion, paste redirect address starting with localhost and press Enter"
    )
    print(url)

    redirect_url = input("Please paste redirect URL: ")

    querys = dict(parse_qsl(urlsplit(redirect_url).query))
    if "code" in querys:
        return querys["code"]
    else:
        print("跳转 URL 有误，没有包含 code 参数")
        print("The redirect URL is incorrect, because it does not contain the code")
        exit(-1)


def get_refresh_token(code: str) -> str:
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "client_id": CLITENT_ID,
        "scope": "offline_access Files.Read.All profile openid",
        "code": code,
        "redirect_uri": "http://localhost",
        "grant_type": "authorization_code",
        "client_secret": CLITENT_SECRET,
    }
    resp_json = requests.post(url, data=data, headers=headers).json()
    if "refresh_token" not in resp_json:
        print("Can't get refresh token.")
        print(resp_json)
        exit(-1)
    refresh_token = resp_json["refresh_token"]
    return refresh_token


if __name__ == "__main__":
    code = get_code()
    refresh_token = get_refresh_token(code)
    print(f"code: {code}")
    print(f"refresh token: {refresh_token}")
