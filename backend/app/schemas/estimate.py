from pydantic import BaseModel

class EstimateRequest(BaseModel):
    # 套盒合并用纸：一次可提交多个 clean 礼盒 id
    box_ids: list[int] = []
    # 兼容单盒旧调用
    box_id: int | None = None
    overlap: float | None = None
    wrap_style: str = "cross"
    save: bool = False
    note: str = ""
