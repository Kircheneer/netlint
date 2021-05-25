"""Webserver component for netlint."""
import random
import typing
from pathlib import Path

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from netlint.checks.checker import Checker
from netlint.checks.utils import NOS

app = FastAPI()

this_dir = Path(__file__).parent

templates = Jinja2Templates(directory=str(this_dir / "templates"))


class Configuration(BaseModel):
    """The model with which the frontend posts the configuration."""

    configuration: str
    nos: str


@app.get("/", response_class=HTMLResponse)
async def root(request: Request) -> Response:
    """Return the web site."""
    # Pick a random faulty config from the tests folder
    config_folder = Path(__file__).parents[2] / "tests" / "configurations" / "cisco_ios"
    faulty_configs = list(config_folder.glob("*_faulty-*.conf"))
    with open(random.choice(faulty_configs)) as f:
        configuration = f.read()
    return templates.TemplateResponse(
        "base.j2", context={"request": request, "initial": configuration}
    )


@app.post("/check")
async def check(configuration: Configuration) -> typing.Dict:
    """Run checks on POSTed configurations."""
    checker = Checker()
    nos = NOS.from_napalm(configuration.nos)
    results = checker.run_checks(configuration.configuration.splitlines(), nos)
    return {key: value._asdict() for key, value in results.items() if value is not None}
