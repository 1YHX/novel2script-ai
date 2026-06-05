from pydantic import BaseModel


class CheckIssueResponse(BaseModel):
    level: str
    type: str
    scene_id: int
    description: str
    suggestion: str


class CheckReportResponse(BaseModel):
    issues: list[CheckIssueResponse]
