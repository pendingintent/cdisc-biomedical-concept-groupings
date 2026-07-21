KNOWN_VALUE_ID = "cm_crf_local_lab"
KNOWN_SCHEME_ID = "collection_method"


def test_list_values_filter_by_scheme(client):
    resp = client.get("/classification-values", params={"scheme_id": "qrs_age_category"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3


def test_get_value(client):
    resp = client.get(f"/classification-values/{KNOWN_VALUE_ID}")
    assert resp.status_code == 200
    assert resp.json()["scheme_id"] == KNOWN_SCHEME_ID


def test_get_value_not_found(client):
    resp = client.get("/classification-values/does_not_exist")
    assert resp.status_code == 404


def test_value_biomedical_concepts(client):
    resp = client.get(f"/classification-values/{KNOWN_VALUE_ID}/biomedical-concepts")
    assert resp.status_code == 200
    body = resp.json()
    assert body["value"]["value_id"] == KNOWN_VALUE_ID
    bc_ids = {bc["bc_id"] for bc in body["biomedical_concepts"]}
    assert "C105585" in bc_ids


def test_create_value_with_bad_scheme_conflicts(client):
    resp = client.post(
        "/classification-values",
        json={"value_id": "test_value", "scheme_id": "does_not_exist", "label": "Test", "description": "Test"},
    )
    assert resp.status_code == 409


def test_create_update_delete_value_round_trip(client):
    create_resp = client.post(
        "/classification-values",
        json={
            "value_id": "test_value",
            "scheme_id": KNOWN_SCHEME_ID,
            "label": "Test Value",
            "description": "A value for testing",
        },
    )
    assert create_resp.status_code == 201

    update_resp = client.put(
        f"/classification-values/test_value",
        json={"scheme_id": KNOWN_SCHEME_ID, "label": "Test Value Updated", "description": "Updated"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["label"] == "Test Value Updated"

    delete_resp = client.delete("/classification-values/test_value")
    assert delete_resp.status_code == 204

    get_resp = client.get("/classification-values/test_value")
    assert get_resp.status_code == 404


def test_delete_value_with_assignments_conflicts(client):
    resp = client.delete(f"/classification-values/{KNOWN_VALUE_ID}")
    assert resp.status_code == 409
