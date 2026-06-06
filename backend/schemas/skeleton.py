from pydantic import BaseModel


class SkeletonResponse(BaseModel):
    skeleton_id: int
    novel_id: int
    content: str
