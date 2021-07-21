import requests
import json
from os.path import join as pathjoin
from typing import Optional, NamedTuple, Callable


class FileInfo(NamedTuple):
    name: str
    size: int
    last_update_date: str


class OneDrive:
    def __init__(
        self,
        cliend_id: str,
        client_secret: str,
        code: str,
        refresh_token: str,
        path: str,
    ):
        self.client_id = cliend_id
        self.client_secret = client_secret
        self.code = code
        self.refresh_token = refresh_token
        self.path = path
        if self.path.startswith("/"):
            self.path = self.path[1:]
        self.access_token = ""

        self.refresh()

    @staticmethod
    def init_from_dict(key_val: dict) -> "OneDrive":
        client_id = key_val["client_id"]
        client_secret = key_val["client_secret"]
        code = key_val["code"]
        refresh_token = key_val["refresh_token"]
        path = key_val["path"]

        return OneDrive(client_id, client_secret, code, refresh_token, path)

    @staticmethod
    def init_from_json(config_path: str) -> "OneDrive":
        with open(config_path, "r") as f:
            config = json.load(f)

        return OneDrive.init_from_dict(config)

    @staticmethod
    def init_from_env() -> "OneDrive":
        from os import environ

        return OneDrive.init_from_dict(environ)

    def _http_get(self, url: str) -> requests.Response:
        header = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        resp = requests.get(url, headers=header, timeout=3)

        return resp

    def refresh(self):
        header = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        r = requests.post(
            "https://login.microsoftonline.com/common/oauth2/v2.0/token",
            data={
                "client_id": self.client_id,
                "redirect_uri": "http://localhost",
                "client_secret": self.client_secret,
                "code": self.code,
                "grant_type": "refresh_token",
                "scope": "offline_access Files.Read.All profile openid",
                "refresh_token": self.refresh_token,
            },
            headers=header,
            timeout=3,
        )
        response_json = r.json()
        if "access_token" not in response_json:
            raise RuntimeError(r.text)

        self.access_token = response_json["access_token"]

    def _try_refresh(func: Callable) -> Callable:
        """If func raise exception, this decorator will try to refresh token.
           It can only solve the problem of access token expiration.

        Args:
            func (Callable): Any method in class.

        Returns:
            Callable: Wrapper.
        """

        def wrapper(self, *args, **kwargs):
            try:
                return func(self, *args, **kwargs)
            except:
                self.refresh()
                return func(self, *args, **kwargs)

        return wrapper

    @_try_refresh
    def is_folder(self, path: str) -> Optional[bool]:
        onedrive_path = pathjoin(self.path, path)

        if not onedrive_path:
            url = "https://graph.microsoft.com/v1.0/me/drive/root"
        else:
            url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_path}"

        r = self._http_get(url)

        if r.status_code == 404:
            return None
        elif "error" in r.json():
            raise RuntimeError(r.text)

        if "folder" in r.json():
            return True
        else:
            return False

    @_try_refresh
    def ls_folder(self, path: str) -> Optional[list]:
        onedrive_path = pathjoin(self.path, path)
        if not onedrive_path:
            url = "https://graph.microsoft.com/v1.0/me/drive/root/children"
        else:
            url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_path}:/children"

        r = self._http_get(url)

        if r.status_code == 404:
            return None
        elif "error" in r.json():
            raise RuntimeError(r.text)

        file_info_list = [
            FileInfo(
                i["name"],
                int(float(i["size"]) / 1024),
                i["lastModifiedDateTime"][0:10],
            )
            for i in r.json()["value"]
        ]

        return file_info_list

    @_try_refresh
    def get_download_link(self, file_name: str) -> Optional[str]:
        onedrive_path = pathjoin(self.path, file_name)
        url = f"https://graph.microsoft.com/v1.0/me/drive/root:/{onedrive_path}"

        r = self._http_get(url)

        if r.status_code == 404:
            return None
        elif "error" in r.json():
            raise RuntimeError(r.text)

        return r.json()["@microsoft.graph.downloadUrl"]
