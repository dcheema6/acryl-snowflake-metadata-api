from typing import Dict, Optional, Union
from pydantic import BaseModel


class Database(BaseModel):
    name: str


class Schema(BaseModel):
    name: str


class Table(BaseModel):
    name: str


class Column(BaseModel):
    name: str
    type: str
    description: Optional[str] = None


class NumericSummary(BaseModel):
    non_null_count: int
    mean: float
    min: float
    max: float
    unique_count: Optional[int] = None


class NonNumericSummary(BaseModel):
    non_null_count: int
    unique_count: int


class TableSummary(BaseModel):
    table_name: str
    row_count: int
    column_summaries: Dict[str, Union[NumericSummary, NonNumericSummary]]
