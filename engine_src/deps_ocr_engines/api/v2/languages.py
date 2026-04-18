from typing import Dict, List

from fastapi import APIRouter

language_router = APIRouter(prefix="/languages")

languages = {
    "eng": "English",
    "rus": "Russian",
    "chi_sim": "Simplified Chinese",
    "deu": "German",
    "spa": "Spanish",
    "ukr": "Ukrainian",
}


@language_router.get("", response_model=List[Dict[str, str]])
def get_languages():
    return [{"code": code, "name": name} for code, name in languages.items()]
