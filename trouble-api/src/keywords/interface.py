from dataclasses import dataclass
from typing import List


@dataclass
class Keyword:
    id: int
    keyword_jp: str
    keyword_en: str


@dataclass
class Keywords:
    keyword: List[Keyword]
