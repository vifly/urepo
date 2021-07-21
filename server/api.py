from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from storage.onedrive import OneDrive


app = FastAPI()
try:
    onedrive = OneDrive.init_from_env()
except KeyError:
    onedrive = OneDrive.init_from_json("./auth.json")

templates = Jinja2Templates(directory="html_templates")


@app.get("/{file_path:path}")
async def list_or_get_file(request: Request, file_path: str):
    is_folder = onedrive.is_folder(file_path)
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
        return RedirectResponse(download_link, status_code=307)