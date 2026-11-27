from datetime import date
from pydantic import BaseModel, Field, ConfigDict

class WorkflowInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=3, max_length=100)

class TaskInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    workflow_id: int = Field(gt=0)
    owner: str = Field(min_length=1, max_length=120)
    title: str = Field(min_length=3, max_length=160)
    due: date
