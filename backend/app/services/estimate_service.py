from fastapi import HTTPException
from app.engines.wrap_math import paper_area, ribbon_estimate
from app.repositories import boxes, history, settings_repo


def _normalize_ids(box_ids, box_id):
    ids = list(box_ids or [])
    if not ids and box_id is not None:
        ids = [box_id]
    return ids


def run_estimate(box_ids, overlap, wrap_style, save, note, box_id=None):
    ids = _normalize_ids(box_ids, box_id)
    if not ids:
        raise HTTPException(422, "box_ids must not be empty")

    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()

    box_entries = []
    for bid in ids:
        box = boxes.get_box(bid)
        if not box:
            raise HTTPException(404, f"box {bid} not found")
        if box.get("data_quality") == "dirty":
            raise HTTPException(422, f"box {bid} is dirty")
        calc = paper_area(box["length"], box["width"], box["height"], ov)
        rb = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
        # 分盒快照：写入时尺寸一并落地，后续改尺寸不得重算
        box_entries.append({
            "box_id": box["id"],
            "name": box["name"],
            "length": box["length"],
            "width": box["width"],
            "height": box["height"],
            "box_surface": calc["box_surface"],
            "paper_m2": calc["paper_m2"],
            "ribbon": rb,
        })

    # 先写分盒再派生合计：合计由分盒数组派生，口径自洽
    payload = {
        "overlap": ov,
        "wrap_style": wrap_style,
        "boxes": box_entries,
        "paper_m2": round(sum(b["paper_m2"] for b in box_entries), 3),
        "box_surface": round(sum(b["box_surface"] for b in box_entries), 3),
        "ribbon": {
            "wrap_style": wrap_style,
            "ribbon_m": round(sum(b["ribbon"]["ribbon_m"] for b in box_entries), 2),
        },
    }

    run_id = history.insert_run(ids[0], ov, payload, note) if save else None
    return {"run_id": run_id, **payload}
