# API Reference

Complete endpoint documentation for the Anime Voice Forge backend server.

Base URL: `http://localhost:5000`

---

## Health and Status

### GET /health

Server health check.

**Response:**
```json
{
  "status": "ok",
  "service": "voice-cloner"
}
```

---

### GET /model-status

Returns the current state of the TTS model loading process.

**Response:**
```json
{
  "status": "ready",
  "progress": 100,
  "message": "Model ready",
  "loaded": true,
  "started_at": 1716000000.0,
  "completed_at": 1716000075.0,
  "elapsed_seconds": 0,
  "error": ""
}
```

**Status values:** `idle`, `warming`, `ready`, `failed`

---

### POST /model/warmup

Trigger one-time model pre-loading. If the model is already loaded or warming, returns immediately.

**Response:**
```json
{
  "status": "warming",
  "message": "Model warmup started"
}
```

---

### GET /setup-status

Check if voice samples are properly configured for each character.

**Response:**
```json
{
  "madara": {
    "name": "Madara Uchiha",
    "ready": true,
    "voice_sample_path": "/path/to/voice_samples/madara_uchiha_sample.wav"
  }
}
```

---

## Character Management

### GET /characters

List all available characters with their voice sample status.

**Response:**
```json
{
  "madara": {
    "name": "Madara Uchiha",
    "language": "en",
    "voice_sample_exists": true
  }
}
```

---

### POST /characters

Upload a custom character voice sample.

**Content-Type:** `multipart/form-data`

**Form Fields:**
| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | Yes | Character display name |
| `language` | string | No | Language code (default: `en`) |
| `voice_sample` | file | Yes | Audio file (.wav, .mp3, .m4a, .flac, .ogg) |

**Response:**
```json
{
  "message": "Character added",
  "character_key": "custom-itachi-uchiha",
  "character": {
    "name": "Itachi Uchiha",
    "language": "en",
    "voice_sample_exists": true
  }
}
```

**Errors:**
| Code | Condition |
|---|---|
| 400 | Missing name or voice_sample file |
| 400 | Unsupported file type |

---

## Voice Generation

### POST /generate

Synchronous speech generation. Blocks until audio is ready, then returns the WAV file directly.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "text": "I will create a world without pain.",
  "character": "madara"
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `text` | string | Yes | 1-500 characters |
| `character` | string | No | Must match a registered character key (default: `madara`) |

**Response:** `audio/wav` binary stream

**Errors:**
| Code | Condition |
|---|---|
| 400 | Empty text |
| 400 | Text exceeds 500 characters |
| 400 | Unknown character |
| 500 | Voice sample file missing |
| 500 | Synthesis failure |

---

### POST /jobs

Create an asynchronous generation job. Returns immediately with a job ID for progress polling.

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "text": "Long script text here...",
  "character": "madara"
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| `text` | string | Yes | 1-2500 characters |
| `character` | string | No | Must match a registered character key (default: `madara`) |

**Response:**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "queued"
}
```

**Errors:**
| Code | Condition |
|---|---|
| 400 | Empty text |
| 400 | Text exceeds 2500 characters |
| 400 | Unknown character |
| 500 | Voice sample file missing |

---

### GET /jobs/:id

Poll the current status of a generation job.

**Response (in progress):**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "running",
  "progress": 67,
  "message": "Generating chunk 3/5",
  "character": "madara",
  "text_length": 450,
  "created_at": 1716000000.0,
  "started_at": 1716000001.0,
  "completed_at": null,
  "elapsed_seconds": 12.4,
  "eta_seconds": 6.1,
  "speed_chars_per_second": 18.5,
  "estimated_total_seconds": 18.5,
  "completed_chunks": 3,
  "total_chunks": 5,
  "audio_ready": false
}
```

**Response (completed):**
```json
{
  "job_id": "a1b2c3d4e5f6",
  "status": "completed",
  "progress": 100,
  "message": "Audio ready",
  "elapsed_seconds": 18.2,
  "speed_chars_per_second": 24.7,
  "completed_chunks": 5,
  "total_chunks": 5,
  "audio_ready": true,
  "eta_seconds": 0
}
```

**Status values:** `queued`, `running`, `completed`, `failed`

**Errors:**
| Code | Condition |
|---|---|
| 404 | Job ID not found |

---

### GET /jobs/:id/audio

Download or stream the generated audio for a completed job.

**Response:** `audio/wav` binary stream

**Errors:**
| Code | Condition |
|---|---|
| 404 | Job ID not found |
| 400 | Job not yet completed |
| 404 | Output file missing from disk |

---

## CORS

All responses include the following headers:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Headers: Content-Type
Access-Control-Allow-Methods: GET, POST, OPTIONS
```
