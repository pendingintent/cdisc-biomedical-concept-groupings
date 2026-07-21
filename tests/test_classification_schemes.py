KNOWN_SCHEME_ID = "qrs_age_category"


def test_list_schemes(client):
    resp = client.get("/classification-schemes")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 6


def test_get_scheme(client):
    resp = client.get(f"/classification-schemes/{KNOWN_SCHEME_ID}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Age Category"


def test_get_scheme_not_found(client):
    resp = client.get("/classification-schemes/does_not_exist")
    assert resp.status_code == 404


def test_list_scheme_values(client):
    resp = client.get(f"/classification-schemes/{KNOWN_SCHEME_ID}/values")
    assert resp.status_code == 200
    body = resp.json()
    labels = {v["label"] for v in body["items"]}
    assert {"Adolescent", "Adult", "Child"} <= labels


def test_list_values_for_unknown_scheme_404s(client):
    resp = client.get("/classification-schemes/does_not_exist/values")
    assert resp.status_code == 404


def test_create_update_delete_scheme_round_trip(client):
    create_resp = client.post(
        "/classification-schemes",
        json={
            "scheme_id": "test_scheme",
            "scheme_prefix": "tst",
            "name": "Test Scheme",
            "description": "A scheme for testing",
            "purpose": "Testing",
            "intended_use": "Testing",
        },
    )
    assert create_resp.status_code == 201

    update_resp = client.put(
        "/classification-schemes/test_scheme",
        json={
            "scheme_prefix": "tst",
            "name": "Test Scheme Updated",
            "description": "Updated",
            "purpose": "Testing",
            "intended_use": "Testing",
        },
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "Test Scheme Updated"

    delete_resp = client.delete("/classification-schemes/test_scheme")
    assert delete_resp.status_code == 204

    get_resp = client.get("/classification-schemes/test_scheme")
    assert get_resp.status_code == 404


def test_delete_scheme_with_values_conflicts(client):
    resp = client.delete(f"/classification-schemes/{KNOWN_SCHEME_ID}")
    assert resp.status_code == 409
