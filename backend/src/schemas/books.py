from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated

from datetime import datetime

class BookSchema(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str = Field(min_length=1, max_length=30)
    year: int = Field(ge=500, le=datetime.now().year)

    model_config = ConfigDict(extra='forbid')

class PaginationParams(BaseModel):
    limit: int = Field(5, ge=0, le=100, description="Количество элементов на странице")
    offset: int = Field(0, ge=0, description="Смещение для пагинации")
