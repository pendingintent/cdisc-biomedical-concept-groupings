KNOWN_BC_ID = "C127127"  # has 5 existing classification assignments


def test_list_biomedical_concepts(client):
    resp = client.get("/biomedical-concepts", params={"limit": 5})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 304
    assert len(body["items"]) == 5


def test_list_filter_by_short_name(client):
    resp = client.get("/biomedical-concepts", params={"short_name_contains": "6mwt"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] >= 1
    assert all("6mwt" in item["short_name"].lower() for item in body["items"])


def test_get_biomedical_concept(client):
    resp = client.get(f"/biomedical-concepts/{KNOWN_BC_ID}")
    assert resp.status_code == 200
    assert resp.json()["bc_id"] == KNOWN_BC_ID


def test_get_biomedical_concept_not_found(client):
    resp = client.get("/biomedical-concepts/DOES_NOT_EXIST")
    assert resp.status_code == 404


def test_biomedical_concept_classifications(client):
    resp = client.get(f"/biomedical-concepts/{KNOWN_BC_ID}/classifications")
    assert resp.status_code == 200
    body = resp.json()
    assert body["biomedical_concept"]["bc_id"] == KNOWN_BC_ID
    scheme_ids = {group["scheme"]["scheme_id"] for group in body["classifications"]}
    assert "collection_method" in scheme_ids
    collection_method_group = next(g for g in body["classifications"] if g["scheme"]["scheme_id"] == "collection_method")
    value_ids = {v["value_id"] for v in collection_method_group["values"]}
    assert {"cm_crf_local_lab", "cm_dta_central_lab"} <= value_ids


def test_create_update_delete_biomedical_concept_round_trip(client):
    create_resp = client.post(
        "/biomedical-concepts", json={"bc_id": "TEST_BC_001", "short_name": "Test Concept", "ncit_code": None}
    )
    assert create_resp.status_code == 201
    assert create_resp.json() == {"bc_id": "TEST_BC_001", "short_name": "Test Concept", "ncit_code": None}

    dup_resp = client.post(
        "/biomedical-concepts", json={"bc_id": "TEST_BC_001", "short_name": "Duplicate", "ncit_code": None}
    )
    assert dup_resp.status_code == 409

    update_resp = client.put(
        "/biomedical-concepts/TEST_BC_001", json={"short_name": "Updated Concept", "ncit_code": "C999999"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["short_name"] == "Updated Concept"

    delete_resp = client.delete("/biomedical-concepts/TEST_BC_001")
    assert delete_resp.status_code == 204

    get_resp = client.get("/biomedical-concepts/TEST_BC_001")
    assert get_resp.status_code == 404


def test_delete_biomedical_concept_with_assignments_conflicts(client):
    resp = client.delete(f"/biomedical-concepts/{KNOWN_BC_ID}")
    assert resp.status_code == 409
