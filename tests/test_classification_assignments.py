KNOWN_ASSIGNMENT_ID = "tag_0000001"
KNOWN_BC_ID = "C105585"
KNOWN_SCHEME_ID = "collection_method"
KNOWN_VALUE_ID = "cm_crf_local_lab"


def test_list_assignments_filter_by_bc(client):
    resp = client.get("/classification-assignments", params={"bc_id": "C127127"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 5


def test_get_assignment(client):
    resp = client.get(f"/classification-assignments/{KNOWN_ASSIGNMENT_ID}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["bc_id"] == KNOWN_BC_ID
    assert body["value_id"] == KNOWN_VALUE_ID


def test_get_assignment_not_found(client):
    resp = client.get("/classification-assignments/does_not_exist")
    assert resp.status_code == 404


def test_create_assignment_bad_bc_conflicts(client):
    resp = client.post(
        "/classification-assignments",
        json={"bc_id": "does_not_exist", "scheme_id": KNOWN_SCHEME_ID, "value_id": KNOWN_VALUE_ID},
    )
    assert resp.status_code == 409


def test_create_assignment_bad_value_scheme_pair_conflicts(client):
    resp = client.post(
        "/classification-assignments",
        json={"bc_id": KNOWN_BC_ID, "scheme_id": "qrs_age_category", "value_id": KNOWN_VALUE_ID},
    )
    assert resp.status_code == 409


def test_create_duplicate_assignment_conflicts(client):
    resp = client.post(
        "/classification-assignments",
        json={"bc_id": KNOWN_BC_ID, "scheme_id": KNOWN_SCHEME_ID, "value_id": KNOWN_VALUE_ID},
    )
    assert resp.status_code == 409


def test_create_update_delete_assignment_round_trip(client):
    create_resp = client.post(
        "/classification-assignments",
        json={"bc_id": "C127127", "scheme_id": "qrs_age_category", "value_id": "ac_adult"},
    )
    assert create_resp.status_code == 201
    assignment_id = create_resp.json()["assignment_id"]

    update_resp = client.put(
        f"/classification-assignments/{assignment_id}",
        json={"bc_id": "C127127", "scheme_id": "qrs_age_category", "value_id": "ac_child"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["value_id"] == "ac_child"

    delete_resp = client.delete(f"/classification-assignments/{assignment_id}")
    assert delete_resp.status_code == 204

    get_resp = client.get(f"/classification-assignments/{assignment_id}")
    assert get_resp.status_code == 404


def test_delete_assignment_not_found(client):
    resp = client.delete("/classification-assignments/does_not_exist")
    assert resp.status_code == 404
