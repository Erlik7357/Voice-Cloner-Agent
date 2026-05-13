"""Flask API server for voice cloning with job progress tracking."""

from pathlib import Path
import os
import re
import threading
import time
import uuid
from typing import Any

from flask import Flask, jsonify, request, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024  # 50MB max
app.config["UPLOAD_EXTENSIONS"] = {".wav", ".mp3", ".m4a", ".flac", ".ogg"}


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

# Initialize voice cloner (lazy loading)
voice_cloner = None
PROJECT_ROOT = Path(__file__).parent.parent
VOICE_SAMPLES_DIR = PROJECT_ROOT / "voice_samples"
OUTPUT_DIR = PROJECT_ROOT / "output"
CACHE_DIR = OUTPUT_DIR / "cache"
CUSTOM_VOICE_DIR = VOICE_SAMPLES_DIR / "custom"

# Create directories
for directory in [VOICE_SAMPLES_DIR, OUTPUT_DIR, CACHE_DIR, CUSTOM_VOICE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Character configurations
CHARACTERS = {
    "madara": {
        "name": "Madara Uchiha",
        "voice_sample": VOICE_SAMPLES_DIR / "madara_uchiha_sample.wav",
        "language": "en",
    }
}

jobs_lock = threading.Lock()
jobs: dict[str, dict[str, Any]] = {}
cloner_lock = threading.Lock()
model_state_lock = threading.Lock()

model_state: dict[str, Any] = {
    "status": "idle",
    "progress": 0,
    "message": "Model not loaded",
    "loaded": False,
    "started_at": None,
    "completed_at": None,
    "error": "",
}

PROGRESS_TICK_SECONDS = 0.5
COLD_START_MODEL_SECONDS = 75.0
WARM_START_MODEL_SECONDS = 4.0
VOICE_PROFILE_SECONDS = 3.0
SYNTHESIS_BASE_SECONDS = 10.0
SYNTHESIS_SECONDS_PER_CHAR = 0.18
MODEL_PREP_MESSAGE = "Loading model weights"
VOICE_PROFILE_MESSAGE = "Preparing speaker embedding"
SYNTHESIS_MESSAGE = "Generating audio chunks"
FINALIZING_MESSAGE = "Finalizing audio file"
COMPLETED_MESSAGE = "Audio ready"


def _progress_from_chunks(completed_chunks: int, total_chunks: int) -> int:
    """Map completed chunk count to generation progress."""
    if total_chunks <= 0:
        return 45
    ratio = min(1.0, completed_chunks / total_chunks)
    return 45 + int(ratio * 50)


def _update_job(job_id: str, **changes: Any) -> None:
    """Update a job record safely."""
    with jobs_lock:
        job = jobs.get(job_id)
        if job:
            job.update(changes)


def _estimate_synthesis_seconds(text_length: int) -> float:
    """Estimate synthesis time for smoother progress updates."""
    return max(12.0, SYNTHESIS_BASE_SECONDS + (text_length * SYNTHESIS_SECONDS_PER_CHAR))


def _update_model_state(**changes: Any) -> None:
    """Update the model warmup state safely."""
    with model_state_lock:
        model_state.update(changes)


def _track_model_warmup_progress(stop_event: threading.Event, estimated_seconds: float) -> None:
    """Advance model warmup progress while initialization is blocking."""
    started_at = time.time()
    while not stop_event.wait(PROGRESS_TICK_SECONDS):
        elapsed = time.time() - started_at
        ratio = min(0.97, elapsed / max(1.0, estimated_seconds))
        progress = 10 + int(80 * ratio)
        message = "Loading model weights" if progress < 45 else "Preparing inference engine"
        _update_model_state(status="warming", progress=progress, message=message)


def _track_stage_progress(
    job_id: str,
    *,
    start_progress: int,
    end_progress: int,
    message: str,
    estimated_seconds: float,
    stop_event: threading.Event,
) -> None:
    """Advance progress gradually while a blocking stage is running."""
    stage_started_at = time.time()
    progress_span = max(1, end_progress - start_progress)

    while not stop_event.wait(PROGRESS_TICK_SECONDS):
        elapsed = time.time() - stage_started_at
        stage_ratio = min(0.985, elapsed / max(1.0, estimated_seconds))
        next_progress = start_progress + int(progress_span * stage_ratio)
        _update_job(job_id, progress=max(start_progress, next_progress), message=message)


def get_cloner():
    """Lazy load voice cloner."""
    global voice_cloner
    if voice_cloner is None:
        with cloner_lock:
            if voice_cloner is None:
                started_at = time.time()
                estimated_seconds = COLD_START_MODEL_SECONDS
                warmup_stop_event = threading.Event()
                warmup_progress_thread = threading.Thread(
                    target=_track_model_warmup_progress,
                    args=(warmup_stop_event, estimated_seconds),
                    daemon=True,
                )
                _update_model_state(
                    status="warming",
                    progress=10,
                    message="Loading model weights",
                    loaded=False,
                    started_at=started_at,
                    completed_at=None,
                    error="",
                )
                warmup_progress_thread.start()
                try:
                    from voice_cloner import VoiceCloner

                    _update_model_state(progress=35, message="Initializing XTTS engine")
                    use_gpu = os.getenv("VOICE_CLONER_GPU", "0").strip() in {"1", "true", "True"}
                    voice_cloner = VoiceCloner(gpu=use_gpu)
                    warmup_stop_event.set()
                    warmup_progress_thread.join(timeout=1)
                    _update_model_state(
                        status="ready",
                        progress=100,
                        message="Model ready",
                        loaded=True,
                        completed_at=time.time(),
                    )
                except Exception as exc:
                    warmup_stop_event.set()
                    warmup_progress_thread.join(timeout=1)
                    _update_model_state(
                        status="failed",
                        progress=100,
                        message="Model warmup failed",
                        loaded=False,
                        completed_at=time.time(),
                        error=str(exc),
                    )
                    raise
    return voice_cloner


def preload_cloner() -> None:
    """Warm the TTS model once when the server starts."""
    print("[voice-cloner] Preloading model into memory...")
    get_cloner()
    print("[voice-cloner] Model warm and ready for reuse.")


def _warmup_model_async() -> None:
    """Warm the model in a background thread."""
    try:
        get_cloner()
    except Exception as exc:
        print(f"[voice-cloner] Warmup failed: {exc}")


@app.route("/model-status", methods=["GET"])
def get_model_status():
    """Read the current model warmup status."""
    with model_state_lock:
        response = dict(model_state)
    if response.get("started_at") and not response.get("completed_at") and response["status"] == "warming":
        response["elapsed_seconds"] = round(time.time() - response["started_at"], 2)
    else:
        response["elapsed_seconds"] = 0
    return jsonify(response)


@app.route("/model/warmup", methods=["POST"])
def warmup_model():
    """Start one-time model loading if it is not already ready."""
    global voice_cloner

    with model_state_lock:
        current_status = model_state["status"]
        loaded = bool(model_state["loaded"])

    if loaded or voice_cloner is not None:
        _update_model_state(status="ready", progress=100, message="Model ready", loaded=True)
        return jsonify({"status": "ready", "message": "Model already loaded"})

    if current_status == "warming":
        return jsonify({"status": "warming", "message": "Model warmup already in progress"})

    warmup_thread = threading.Thread(target=_warmup_model_async, daemon=True)
    warmup_thread.start()
    return jsonify({"status": "warming", "message": "Model warmup started"})


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "voice-cloner"})


@app.route("/generate", methods=["POST"])
def generate_speech():
    """Generate cloned voice speech (sync endpoint)."""
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text", "") or "").strip()
        character = (data.get("character", "madara") or "madara").lower()

        if not text:
            return jsonify({"error": "Text is required"}), 400

        if character not in CHARACTERS:
            return (
                jsonify({"error": f"Character not found. Available: {list(CHARACTERS.keys())}"}),
                400,
            )

        if len(text) > 500:
            return jsonify({"error": "Text too long (max 500 chars)"}), 400

        char_config = CHARACTERS[character]

        if not char_config["voice_sample"].exists():
            return jsonify({"error": f"Voice sample for {character} not found"}), 500

        output_file = CACHE_DIR / f"{uuid.uuid4()}.wav"

        cloner = get_cloner()
        success = cloner.clone_voice_in_chunks(
            reference_audio_path=str(char_config["voice_sample"]),
            text=text,
            output_path=str(output_file),
            language=char_config["language"],
            chunk_prefix=output_file.stem,
        )

        if not success:
            return jsonify({"error": "Failed to generate speech"}), 500

        return send_file(str(output_file), mimetype="audio/wav", as_attachment=False)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _slugify_name(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or f"character-{uuid.uuid4().hex[:8]}"


@app.route("/characters", methods=["GET"])
def get_characters():
    """Get available characters."""
    characters = {}
    for key, config in CHARACTERS.items():
        characters[key] = {
            "name": config["name"],
            "language": config["language"],
            "voice_sample_exists": config["voice_sample"].exists(),
        }
    return jsonify(characters)


@app.route("/characters", methods=["POST"])
def add_character():
    """Upload custom character voice sample."""
    try:
        name = (request.form.get("name", "") or "").strip()
        language = (request.form.get("language", "en") or "en").strip().lower()
        file = request.files.get("voice_sample")

        if not name:
            return jsonify({"error": "Character name is required"}), 400
        if file is None or not file.filename:
            return jsonify({"error": "voice_sample file is required"}), 400

        extension = Path(file.filename).suffix.lower()
        if extension not in app.config["UPLOAD_EXTENSIONS"]:
            return jsonify({"error": f"Unsupported file type: {extension}"}), 400

        slug = _slugify_name(name)
        key = f"custom-{slug}"
        safe_filename = secure_filename(f"{key}{extension}")
        destination = CUSTOM_VOICE_DIR / safe_filename
        file.save(destination)

        CHARACTERS[key] = {
            "name": name,
            "voice_sample": destination,
            "language": language or "en",
        }

        return jsonify(
            {
                "message": "Character added",
                "character_key": key,
                "character": {
                    "name": name,
                    "language": language or "en",
                    "voice_sample_exists": destination.exists(),
                },
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _run_job(job_id: str, text: str, character: str, output_file: Path) -> None:
    started_at = time.time()
    text_length = len(text)
    model_load_seconds = COLD_START_MODEL_SECONDS if voice_cloner is None else WARM_START_MODEL_SECONDS
    synthesis_seconds = _estimate_synthesis_seconds(text_length)
    estimated_total_seconds = model_load_seconds + VOICE_PROFILE_SECONDS + synthesis_seconds
    model_stop_event: threading.Event | None = None
    model_progress_thread: threading.Thread | None = None

    _update_job(
        job_id,
        status="running",
        progress=8,
        message=MODEL_PREP_MESSAGE,
        started_at=started_at,
        estimated_total_seconds=round(estimated_total_seconds, 2),
    )

    try:
        char_config = CHARACTERS[character]
        model_stop_event = threading.Event()
        model_progress_thread = threading.Thread(
            target=_track_stage_progress,
            args=(job_id,),
            kwargs={
                "start_progress": 8,
                "end_progress": 28,
                "message": MODEL_PREP_MESSAGE,
                "estimated_seconds": model_load_seconds,
                "stop_event": model_stop_event,
            },
            daemon=True,
        )
        model_progress_thread.start()
        cloner = get_cloner()
        model_stop_event.set()
        model_progress_thread.join(timeout=1)

        _update_job(job_id, progress=32, message=VOICE_PROFILE_MESSAGE)
        time.sleep(VOICE_PROFILE_SECONDS)

        chunks = cloner.split_into_sentence_chunks(text)
        total_chunks = len(chunks)
        if total_chunks == 0:
            raise ValueError("Unable to split text into audio chunks")

        _update_job(
            job_id,
            progress=45,
            message=f"Generating chunk 0/{total_chunks}",
            total_chunks=total_chunks,
            completed_chunks=0,
        )

        def on_chunk_complete(completed_chunks: int, chunk_total: int, _chunk_path: str) -> None:
            _update_job(
                job_id,
                progress=_progress_from_chunks(completed_chunks, chunk_total),
                message=f"Generating chunk {completed_chunks}/{chunk_total}",
                completed_chunks=completed_chunks,
                total_chunks=chunk_total,
            )

        success = cloner.clone_voice_in_chunks(
            reference_audio_path=str(char_config["voice_sample"]),
            text=text,
            output_path=str(output_file),
            language=char_config["language"],
            chunk_prefix=job_id,
            on_chunk_complete=on_chunk_complete,
        )
        _update_job(job_id, progress=98, message=FINALIZING_MESSAGE)

        elapsed = max(0.001, time.time() - started_at)
        chars_per_second = round(len(text) / elapsed, 2)

        if success:
            _update_job(
                job_id,
                status="completed",
                progress=100,
                message=COMPLETED_MESSAGE,
                elapsed_seconds=round(elapsed, 2),
                speed_chars_per_second=chars_per_second,
                output_file=str(output_file),
                completed_at=time.time(),
                completed_chunks=total_chunks,
                total_chunks=total_chunks,
            )
        else:
            _update_job(
                job_id,
                status="failed",
                progress=100,
                message="Generation failed",
                elapsed_seconds=round(elapsed, 2),
                total_chunks=total_chunks,
            )
    except Exception as e:
        _update_job(
            job_id,
            status="failed",
            progress=100,
            message=str(e),
            elapsed_seconds=round(max(0.001, time.time() - started_at), 2),
        )
    finally:
        if model_stop_event is not None:
            model_stop_event.set()
        if model_progress_thread is not None:
            model_progress_thread.join(timeout=1)


@app.route("/jobs", methods=["POST"])
def create_job():
    """Create async generation job with progress polling."""
    try:
        data = request.get_json(silent=True) or {}
        text = (data.get("text", "") or "").strip()
        character = (data.get("character", "madara") or "madara").lower()

        if not text:
            return jsonify({"error": "Text is required"}), 400
        if character not in CHARACTERS:
            return jsonify({"error": f"Character not found: {character}"}), 400
        if len(text) > 2500:
            return jsonify({"error": "Text too long (max 2500 chars)"}), 400

        char_config = CHARACTERS[character]
        if not char_config["voice_sample"].exists():
            return jsonify({"error": "Character voice sample not found"}), 500

        job_id = uuid.uuid4().hex
        output_file = CACHE_DIR / f"{job_id}.wav"
        now = time.time()
        job = {
            "job_id": job_id,
            "status": "queued",
            "progress": 0,
            "message": "Queued",
            "character": character,
            "text_length": len(text),
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "elapsed_seconds": 0,
            "speed_chars_per_second": 0,
            "estimated_total_seconds": 0,
            "completed_chunks": 0,
            "total_chunks": 0,
            "output_file": str(output_file),
        }

        with jobs_lock:
            jobs[job_id] = job

        thread = threading.Thread(
            target=_run_job,
            args=(job_id, text, character, output_file),
            daemon=True,
        )
        thread.start()

        return jsonify({"job_id": job_id, "status": "queued"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/jobs/<job_id>", methods=["GET"])
def job_status(job_id: str):
    """Read current job status."""
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return jsonify({"error": "Job not found"}), 404
        response = dict(job)

    if response["status"] in {"queued", "running"}:
        response["elapsed_seconds"] = round(time.time() - response["created_at"], 2)
        if response["elapsed_seconds"] > 0:
            response["speed_chars_per_second"] = round(
                response["text_length"] / max(1, response["elapsed_seconds"]),
                2,
            )
        total_chunks = int(response.get("total_chunks", 0) or 0)
        completed_chunks = int(response.get("completed_chunks", 0) or 0)
        if total_chunks > 0 and completed_chunks > 0:
            avg_chunk_seconds = response["elapsed_seconds"] / completed_chunks
            estimated_total_seconds = avg_chunk_seconds * total_chunks + VOICE_PROFILE_SECONDS
        else:
            estimated_total_seconds = max(
                response["elapsed_seconds"],
                float(response.get("estimated_total_seconds", 0) or 0),
            )
        response["eta_seconds"] = round(max(0.0, estimated_total_seconds - response["elapsed_seconds"]), 2)
    else:
        response["eta_seconds"] = 0

    response["audio_ready"] = response["status"] == "completed" and Path(response.get("output_file", "")).exists()
    return jsonify(response)


@app.route("/jobs/<job_id>/audio", methods=["GET"])
def job_audio(job_id: str):
    """Download/stream audio for a completed job."""
    with jobs_lock:
        job = jobs.get(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job.get("status") != "completed":
        return jsonify({"error": "Job not completed"}), 400

    output_file = Path(job.get("output_file", ""))
    if not output_file.exists():
        return jsonify({"error": "Output file missing"}), 404

    return send_file(str(output_file), mimetype="audio/wav", as_attachment=False)


@app.route("/setup-status", methods=["GET"])
def setup_status():
    """Check if voice samples are properly configured."""
    status = {}
    for key, config in CHARACTERS.items():
        status[key] = {
            "name": config["name"],
            "ready": config["voice_sample"].exists(),
            "voice_sample_path": str(config["voice_sample"]),
        }
    return jsonify(status)


def main() -> None:
    """Run the Flask server."""
    print("Voice Cloner API Server Starting...")
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Voice samples dir: {VOICE_SAMPLES_DIR}")
    print(f"Output dir: {OUTPUT_DIR}")
    preload_on_start = os.getenv("VOICE_CLONER_PRELOAD", "1").strip() not in {"0", "false", "False"}
    flask_debug = os.getenv("VOICE_CLONER_DEBUG", "0").strip() in {"1", "true", "True"}

    if preload_on_start:
        preload_cloner()

    print("\nServer will start on http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /health - Health check")
    print("  GET  /characters - List available characters")
    print("  POST /characters - Upload custom character")
    print("  GET  /setup-status - Check voice sample setup")
    print("  POST /generate - Generate cloned voice speech (sync)")
    print("  POST /jobs - Start async job with progress")
    print("  GET  /jobs/<id> - Read job progress")
    print("  GET  /jobs/<id>/audio - Get generated audio")
    print("\n" + "=" * 60)

    app.run(debug=flask_debug, use_reloader=False, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
