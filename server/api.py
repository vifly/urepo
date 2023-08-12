import os
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from storage.onedrive import OneDrive


logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(funcName)s(): %(message)s",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.WARNING
)

app = FastAPI()
try:
    onedrive = OneDrive.init_from_env()
except KeyError:
    onedrive = OneDrive.init_from_json(
        os.path.normpath(
            os.path.join(os.path.dirname(__file__), "../auth.json")
        )
    )

templates = Jinja2Templates(directory="html_templates")


@app.get("/{file_path:path}")
async def list_or_get_file(request: Request, file_path: str):
    # encode illegal char
    if ":" in file_path:
        file_path = file_path.replace(":", "-colon-")

    try:
        is_folder = onedrive.is_folder(file_path)
    except Exception as exc:
        logging.error(exc)
        return HTTPException(500, "OneDrive API Error.")
    if is_folder is None:
        return HTTPException(404, f"{file_path} is not exist.")
    elif is_folder is True:
        file_info_list = onedrive.ls_folder(file_path)
        file_info_list = [i._asdict() for i in file_info_list]
        return templates.TemplateResponse(
            "index.html",
            context={"request": request, "file_info_list": file_info_list},
        )
    else:
        download_link = onedrive.get_download_link(file_path)
        if download_link:
            return RedirectResponse(download_link, status_code=307)
        else:
            return HTTPException(404, f"{file_path} is not exist.")
