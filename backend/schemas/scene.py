from pydantic import BaseModel


class SceneResponse(BaseModel):
    scene_id: int
    title: str
    time: str
    location: str
    characters: list[str]
    plot_goal: str
    conflict: str
    source_paragraphs: list[int]


class SceneListResponse(BaseModel):
    scenes: list[SceneResponse]
