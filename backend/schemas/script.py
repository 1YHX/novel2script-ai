from pydantic import BaseModel


class ScriptGenerateRequest(BaseModel):
    style: str = "短剧风格"
    dialogue_density: str = "medium"
    include_camera_language: bool = True


class ScriptUpdateRequest(BaseModel):
    content: str


class ScriptResponse(BaseModel):
    script_id: int
    scene_id: int
    content: str
    version: int
