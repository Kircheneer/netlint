import typing
from pathlib import Path

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from netlint.checks.checker import Checker
from netlint.checks.utils import NOS

app = FastAPI()

this_dir = Path(__file__).parent

templates = Jinja2Templates(directory=this_dir / "templates")


class Configuration(BaseModel):
    configuration: str
    nos: str


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("base.j2", context={"request": request})


@app.post("/check")
async def check(configuration: Configuration) -> typing.Dict:
    checker = Checker()
    nos = NOS.from_napalm(configuration.nos)
    results = checker.run_checks(configuration.configuration.splitlines(), nos)
    return {key: value._asdict() for key, value in results.items() if value is not None}
