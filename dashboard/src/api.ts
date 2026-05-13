export type Character = {
  key: string;
  name: string;
  language: string;
  voice_sample_exists?: boolean;
};

export type JobState = {
  job_id: string;
  status: "queued" | "running" | "completed" | "failed";
  progress: number;
  message: string;
  elapsed_seconds: number;
  eta_seconds: number;
  speed_chars_per_second: number;
  audio_ready: boolean;
  completed_chunks?: number;
  total_chunks?: number;
};

export type HealthState = {
  status: string;
  service: string;
};

export type SetupCharacterState = {
  name: string;
  ready: boolean;
  voice_sample_path: string;
};

export type ModelStatusState = {
  status: "idle" | "warming" | "ready" | "failed";
  progress: number;
  message: string;
  loaded: boolean;
  started_at: number | null;
  completed_at: number | null;
  elapsed_seconds: number;
  error: string;
};

const API = (import.meta.env.VITE_API_BASE_URL as string) || "http://localhost:5000";

export async function fetchCharacters(): Promise<Character[]> {
  const res = await fetch(`${API}/characters`);
  if (!res.ok) throw new Error("Failed to load characters");
  const data = await res.json();
  return Object.entries(data).map(([key, value]: any) => ({
    key,
    name: value.name,
    language: value.language,
    voice_sample_exists: value.voice_sample_exists
  }));
}

export async function fetchHealth(): Promise<HealthState> {
  const res = await fetch(`${API}/health`);
  if (!res.ok) throw new Error("Backend health check failed");
  return res.json();
}

export async function fetchSetupStatus(): Promise<Record<string, SetupCharacterState>> {
  const res = await fetch(`${API}/setup-status`);
  if (!res.ok) throw new Error("Failed to load setup status");
  return res.json();
}

export async function fetchModelStatus(): Promise<ModelStatusState> {
  const res = await fetch(`${API}/model-status`);
  if (!res.ok) throw new Error("Failed to load model status");
  return res.json();
}

export async function startModelWarmup(): Promise<{ status: string; message: string }> {
  const res = await fetch(`${API}/model/warmup`, { method: "POST" });
  if (!res.ok) throw new Error((await res.json()).error || "Failed to start model warmup");
  return res.json();
}

export async function createJob(text: string, character: string): Promise<{ job_id: string }> {
  const res = await fetch(`${API}/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, character })
  });
  if (!res.ok) throw new Error((await res.json()).error || "Failed to create job");
  return res.json();
}

export async function generateSync(text: string, character: string): Promise<Blob> {
  const res = await fetch(`${API}/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, character })
  });

  if (!res.ok) throw new Error((await res.json()).error || "Sync generate failed");
  return res.blob();
}

export async function getJob(jobId: string): Promise<JobState> {
  const res = await fetch(`${API}/jobs/${jobId}`);
  if (!res.ok) throw new Error("Failed to fetch job status");
  return res.json();
}

export function getAudioUrl(jobId: string): string {
  return `${API}/jobs/${jobId}/audio`;
}

export async function uploadCharacter(name: string, file: File): Promise<void> {
  const formData = new FormData();
  formData.append("name", name);
  formData.append("language", "en");
  formData.append("voice_sample", file);

  const res = await fetch(`${API}/characters`, { method: "POST", body: formData });
  if (!res.ok) throw new Error((await res.json()).error || "Failed to upload character");
}
