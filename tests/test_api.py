"""Integration tests for the Flask API server."""

import json
import sys
from pathlib import Path

import pytest

# Add backend to import path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from tts_server import app


@pytest.fixture
def client():
    """Create a Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for GET /health."""

    def test_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_ok_status(self, client):
        data = json.loads(response := client.get("/health").data)
        assert data["status"] == "ok"

    def test_returns_service_name(self, client):
        data = json.loads(client.get("/health").data)
        assert data["service"] == "voice-cloner"


class TestCharactersEndpoint:
    """Tests for GET /characters."""

    def test_returns_200(self, client):
        response = client.get("/characters")
        assert response.status_code == 200

    def test_contains_madara(self, client):
        data = json.loads(client.get("/characters").data)
        assert "madara" in data
        assert data["madara"]["name"] == "Madara Uchiha"

    def test_character_has_required_fields(self, client):
        data = json.loads(client.get("/characters").data)
        for key, char in data.items():
            assert "name" in char
            assert "language" in char
            assert "voice_sample_exists" in char


class TestGenerateEndpoint:
    """Tests for POST /generate — input validation only (no model loaded)."""

    def test_empty_text_returns_400(self, client):
        response = client.post(
            "/generate",
            data=json.dumps({"text": "", "character": "madara"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_missing_text_returns_400(self, client):
        response = client.post(
            "/generate",
            data=json.dumps({"character": "madara"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_unknown_character_returns_400(self, client):
        response = client.post(
            "/generate",
            data=json.dumps({"text": "Hello", "character": "nonexistent"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "not found" in data["error"].lower() or "Available" in data["error"]

    def test_text_too_long_returns_400(self, client):
        response = client.post(
            "/generate",
            data=json.dumps({"text": "x" * 501, "character": "madara"}),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "too long" in data["error"].lower()


class TestJobsEndpoint:
    """Tests for POST /jobs — input validation only."""

    def test_empty_text_returns_400(self, client):
        response = client.post(
            "/jobs",
            data=json.dumps({"text": "", "character": "madara"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_unknown_character_returns_400(self, client):
        response = client.post(
            "/jobs",
            data=json.dumps({"text": "Hello", "character": "nonexistent"}),
            content_type="application/json",
        )
        assert response.status_code == 400

    def test_text_over_2500_returns_400(self, client):
        response = client.post(
            "/jobs",
            data=json.dumps({"text": "x" * 2501, "character": "madara"}),
            content_type="application/json",
        )
        assert response.status_code == 400


class TestJobStatusEndpoint:
    """Tests for GET /jobs/<id>."""

    def test_nonexistent_job_returns_404(self, client):
        response = client.get("/jobs/nonexistent-id")
        assert response.status_code == 404


class TestSetupStatusEndpoint:
    """Tests for GET /setup-status."""

    def test_returns_200(self, client):
        response = client.get("/setup-status")
        assert response.status_code == 200

    def test_contains_character_entries(self, client):
        data = json.loads(client.get("/setup-status").data)
        assert "madara" in data
        assert "name" in data["madara"]
        assert "ready" in data["madara"]


class TestModelStatusEndpoint:
    """Tests for GET /model-status."""

    def test_returns_200(self, client):
        response = client.get("/model-status")
        assert response.status_code == 200

    def test_contains_status_fields(self, client):
        data = json.loads(client.get("/model-status").data)
        assert "status" in data
        assert "progress" in data
        assert "message" in data
        assert "loaded" in data


class TestCorsHeaders:
    """Verify CORS headers are present."""

    def test_cors_allow_origin(self, client):
        response = client.get("/health")
        assert response.headers.get("Access-Control-Allow-Origin") == "*"

    def test_cors_allow_methods(self, client):
        response = client.get("/health")
        assert "GET" in response.headers.get("Access-Control-Allow-Methods", "")
        assert "POST" in response.headers.get("Access-Control-Allow-Methods", "")
