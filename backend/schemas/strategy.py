from pydantic import BaseModel


class StrategyResponse(BaseModel):
    strategy_id: int
    novel_id: int
    content: str
