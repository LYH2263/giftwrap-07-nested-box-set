import json
from datetime import datetime, timezone
from app.db import connect


def _derive(result):
    """从分盒数组派生合计，保证合计与分盒口径自洽、两路读数不打架。

    分盒数组是写入时落地的快照（含尺寸），为唯一真值；合计一律由它派生，
    不按 boxes 表新尺寸重算。
    """
    boxes = result.get("boxes")
    if not isinstance(boxes, list):
        return result  # 兼容旧形状
    result["paper_m2"] = round(sum(b.get("paper_m2", 0) for b in boxes), 3)
    result["box_surface"] = round(sum(b.get("box_surface", 0) for b in boxes), 3)
    result["ribbon"] = {
        "wrap_style": result.get("wrap_style", "cross"),
        "ribbon_m": round(sum(b.get("ribbon", {}).get("ribbon_m", 0) for b in boxes), 2),
    }
    return result


def insert_run(box_id, overlap, result, note=""):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (box_id, overlap, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()


def _row_to_run(row):
    d = dict(row)
    d["result"] = _derive(json.loads(d.pop("result_json")))
    return d


def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, b.name box_name FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id ORDER BY r.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [_row_to_run(row) for row in rows]
    finally:
        c.close()


def get_run(run_id):
    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, b.name box_name FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id WHERE r.id=?""",
            (run_id,),
        ).fetchone()
        return _row_to_run(row) if row else None
    finally:
        c.close()
