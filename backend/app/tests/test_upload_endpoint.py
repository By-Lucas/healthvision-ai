from app.tests.conftest import make_png_bytes


def test_upload_valid_image_creates_pending_analysis(client):
    resp = client.post(
        "/api/v1/analysis/upload",
        files={"file": ("scan.png", make_png_bytes(), "image/png")},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "PENDING"
    assert body["original_filename"] == "scan.png"
    assert "educational" in body["warning"].lower()


def test_upload_rejects_unsupported_extension(client):
    resp = client.post(
        "/api/v1/analysis/upload",
        files={"file": ("notes.txt", b"hello world", "text/plain")},
    )
    assert resp.status_code == 415


def test_upload_rejects_non_image_bytes(client):
    # .png extension but the bytes are not a real image.
    resp = client.post(
        "/api/v1/analysis/upload",
        files={"file": ("fake.png", b"not-an-image", "image/png")},
    )
    assert resp.status_code == 422


def test_list_then_detail_roundtrip(client):
    upload = client.post(
        "/api/v1/analysis/upload",
        files={"file": ("scan.png", make_png_bytes(), "image/png")},
    )
    analysis_id = upload.json()["id"]

    listing = client.get("/api/v1/analysis")
    assert listing.status_code == 200
    assert listing.json()["count"] == 1

    detail = client.get(f"/api/v1/analysis/{analysis_id}")
    assert detail.status_code == 200
    assert detail.json()["id"] == analysis_id


def test_detail_not_found_returns_404(client):
    resp = client.get("/api/v1/analysis/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_delete_analysis_removes_it(client):
    upload = client.post(
        "/api/v1/analysis/upload",
        files={"file": ("scan.png", make_png_bytes(), "image/png")},
    )
    analysis_id = upload.json()["id"]

    deleted = client.delete(f"/api/v1/analysis/{analysis_id}")
    assert deleted.status_code == 204

    assert client.get(f"/api/v1/analysis/{analysis_id}").status_code == 404
    assert client.get("/api/v1/analysis").json()["count"] == 0


def test_delete_missing_analysis_returns_404(client):
    resp = client.delete("/api/v1/analysis/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_dashboard_summary_shape(client):
    resp = client.get("/api/v1/dashboard/summary")
    assert resp.status_code == 200
    body = resp.json()
    assert {"total_analyses", "average_confidence", "by_class", "by_status",
            "recent_analyses"} <= body.keys()
