import os
from dataclasses import dataclass

import requests
from fastapi import HTTPException

from src.keywords.interface import Keywords


@dataclass
class KeywordClient:
    keyword_api_url = os.environ.get("KEYWORD_API_URL", "").strip()

    def get_keywords(self, sentence: str):
        res = requests.get(f"{self.keyword_api_url}/keyword",
                           params={"sentence": sentence})
        if not res.ok:
            raise HTTPException(status_code=res.status_code, detail=res.json())

        return Keywords(**res.json())
