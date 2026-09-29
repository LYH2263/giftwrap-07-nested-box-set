from app.engines.wrap_math import paper_area

# seed 数据：1=书型盒(clean) 0.30×0.20×0.15，2=方形礼盒(clean) 0.25×0.25×0.10，3=脏数据-负高(dirty)
BOX1 = (0.30, 0.20, 0.15)
BOX2 = (0.25, 0.25, 0.10)


def _runs_count(client):
    return len(client.get("/api/runs").json()["items"])


def test_single_box_total_equals_individual(client):
    r = client.post("/api/estimate", json={"box_ids": [1], "save": True})
    assert r.status_code == 200
    data = r.json()
    expected = paper_area(*BOX1, 1.15)["paper_m2"]
    assert data["paper_m2"] == expected
    assert len(data["boxes"]) == 1
    assert data["boxes"][0]["box_id"] == 1
    assert data["run_id"] is not None


def test_merged_total_is_sum_of_boxes(client):
    r = client.post("/api/estimate", json={"box_ids": [1, 2], "save": True})
    assert r.status_code == 200
    data = r.json()
    assert len(data["boxes"]) == 2
    s = round(sum(b["paper_m2"] for b in data["boxes"]), 3)
    assert data["paper_m2"] == s
    assert data["paper_m2"] == round(paper_area(*BOX1, 1.15)["paper_m2"] + paper_area(*BOX2, 1.15)["paper_m2"], 3)


def test_empty_list_fails_no_row(client):
    before = _runs_count(client)
    r = client.post("/api/estimate", json={"box_ids": [], "save": True})
    assert r.status_code == 422
    assert _runs_count(client) == before


def test_dirty_box_fails_no_row(client):
    before = _runs_count(client)
    r = client.post("/api/estimate", json={"box_ids": [1, 3], "save": True})
    assert r.status_code == 422
    assert _runs_count(client) == before


def test_unknown_box_fails_no_row(client):
    before = _runs_count(client)
    r = client.post("/api/estimate", json={"box_ids": [999], "save": True})
    assert r.status_code == 404
    assert _runs_count(client) == before


def test_snapshot_stable_after_box_dim_change(client):
    r = client.post("/api/estimate", json={"box_ids": [1, 2], "save": True})
    assert r.status_code == 200
    run_id = r.json()["run_id"]
    snapshot = r.json()

    # 写入后改其中一盒长宽高
    from app.db import connect
    c = connect()
    c.execute("UPDATE boxes SET length=0.99 WHERE id=1")
    c.commit()
    c.close()

    run = client.get(f"/api/runs/{run_id}").json()
    # 合计仍等于写入快照，不按新尺寸重算
    assert run["result"]["paper_m2"] == snapshot["paper_m2"]
    # 分盒表尺寸仍是写入时快照
    box1_entry = next(b for b in run["result"]["boxes"] if b["box_id"] == 1)
    assert box1_entry["length"] == BOX1[0]
    # 合计与分盒彼此一致
    assert run["result"]["paper_m2"] == round(
        sum(b["paper_m2"] for b in run["result"]["boxes"]), 3
    )


def test_dry_run_matches_saved(client):
    dry = client.post("/api/estimate", json={"box_ids": [1, 2], "save": False})
    saved = client.post("/api/estimate", json={"box_ids": [1, 2], "save": True})
    assert dry.status_code == 200 and saved.status_code == 200
    d, s = dry.json(), saved.json()
    assert d["paper_m2"] == s["paper_m2"]
    assert [b["box_id"] for b in d["boxes"]] == [b["box_id"] for b in s["boxes"]]
    for db, sb in zip(d["boxes"], s["boxes"]):
        assert db["paper_m2"] == sb["paper_m2"]


def test_get_estimate_accepts_repeated_box_ids(client):
    r = client.get("/api/estimate", params=[("box_ids", 1), ("box_ids", 2)])
    assert r.status_code == 200
    data = r.json()
    assert len(data["boxes"]) == 2
    assert data["paper_m2"] == round(sum(b["paper_m2"] for b in data["boxes"]), 3)
