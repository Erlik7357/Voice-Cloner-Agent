import { PlayCircle, Wand2 } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import {
  Character,
  createJob,
  fetchCharacters,
  fetchHealth,
  fetchModelStatus,
  fetchSetupStatus,
  generateSync,
  getAudioUrl,
  getJob,
  JobState,
  ModelStatusState,
  SetupCharacterState,
  startModelWarmup,
  uploadCharacter
} from "./api";
import BackendStatusPanel from "./components/BackendStatusPanel";
import ConsentChecklist, { type ConsentState } from "./components/ConsentChecklist";
import ProgressPanel from "./components/ProgressPanel";
import UploadPanel from "./components/UploadPanel";

const starterScript = `In this world, every soul carries a story. Today, we carve ours with fire and conviction.`;
const initialModelStatus: ModelStatusState = {
  status: "idle",
  progress: 0,
  message: "Model not loaded",
  loaded: false,
  started_at: null,
  completed_at: null,
  elapsed_seconds: 0,
  error: ""
};

export default function App() {
  const [consent, setConsent] = useState<ConsentState>({
    ownsSample: false,
    noImpersonation: false,
    understandsLegalRisk: false
  });
  const [characters, setCharacters] = useState<Character[]>([]);
  const [selected, setSelected] = useState("madara");
  const [script, setScript] = useState(starterScript);
  const [job, setJob] = useState<JobState | null>(null);
  const [audio, setAudio] = useState<string>("");
  const [syncAudio, setSyncAudio] = useState<string>("");
  const [error, setError] = useState("");
  const [backendUp, setBackendUp] = useState(false);
  const [serviceName, setServiceName] = useState("voice-cloner");
  const [setupStatus, setSetupStatus] = useState<Record<string, SetupCharacterState>>({});
  const [modelStatus, setModelStatus] = useState<ModelStatusState>(initialModelStatus);
  const [warmingModel, setWarmingModel] = useState(false);

  async function loadCharacters() {
    const items = await fetchCharacters();
    setCharacters(items);
    if (!items.find((item) => item.key === selected) && items[0]) {
      setSelected(items[0].key);
    }
  }

  async function loadBackendStatus() {
    try {
      const health = await fetchHealth();
      setBackendUp(health.status === "ok");
      setServiceName(health.service || "voice-cloner");
    } catch {
      setBackendUp(false);
    }

    try {
      const setup = await fetchSetupStatus();
      setSetupStatus(setup);
    } catch {
      setSetupStatus({});
    }

    try {
      const model = await fetchModelStatus();
      setModelStatus(model);
    } catch {
      setModelStatus(initialModelStatus);
    }
  }

  async function handleWarmModel() {
    try {
      setError("");
      setWarmingModel(true);
      await startModelWarmup();
      const nextStatus = await fetchModelStatus();
      setModelStatus(nextStatus);
    } catch (e: any) {
      setError(e.message || "Failed to start model warmup");
    } finally {
      setWarmingModel(false);
    }
  }

  useEffect(() => {
    Promise.all([loadCharacters(), loadBackendStatus()]).catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!backendUp || modelStatus.status !== "warming") return;
    const timer = setInterval(async () => {
      try {
        const nextStatus = await fetchModelStatus();
        setModelStatus(nextStatus);
      } catch {
        clearInterval(timer);
      }
    }, 700);
    return () => clearInterval(timer);
  }, [backendUp, modelStatus.status]);

  useEffect(() => {
    if (!job || job.status === "completed" || job.status === "failed") return;
    const timer = setInterval(async () => {
      try {
        const next = await getJob(job.job_id);
        setJob(next);
        if (next.status === "completed") {
          setAudio(getAudioUrl(next.job_id));
        }
      } catch {
        clearInterval(timer);
      }
    }, 500);
    return () => clearInterval(timer);
  }, [job]);

  const charCount = useMemo(() => script.trim().length, [script]);
  const consentConfirmed = useMemo(
    () => Object.values(consent).every(Boolean),
    [consent]
  );

  return (
    <main className="min-h-screen px-4 py-8 text-slate-100">
      <div className="mx-auto max-w-6xl space-y-6">
        <header className="glass rounded-2xl p-6">
          <p className="text-electric text-xs uppercase tracking-widest">Voice Cloner Localhost Dashboard</p>
          <h1 className="text-3xl md:text-4xl font-bold mt-2">Anime Voice Forge</h1>
          <p className="text-slate-300 mt-2">Paste your 1-2 minute script, choose voice, track generation speed and completion in real time.</p>
        </header>

        <section className="grid lg:grid-cols-3 gap-5">
          <div className="lg:col-span-2 glass rounded-2xl p-5 space-y-4">
            <div className="flex items-center gap-2 text-electric">
              <Wand2 size={18} />
              <h2 className="text-lg font-semibold">Script To Voice</h2>
            </div>

            <select
              className="w-full rounded-lg bg-slate-900/70 border border-slate-700 px-3 py-2"
              value={selected}
              onChange={(e) => setSelected(e.target.value)}
            >
              {characters.map((c) => (
                <option key={c.key} value={c.key}>{c.name}</option>
              ))}
            </select>

            <textarea
              className="h-52 w-full rounded-xl bg-slate-900/70 border border-slate-700 p-3"
              value={script}
              onChange={(e) => setScript(e.target.value)}
              placeholder="Paste your 1-2 min script here"
            />

            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Length: {charCount} chars</span>
              <span>Recommended: 600-2000 chars for 1-2 mins</span>
            </div>

            <ConsentChecklist value={consent} onChange={setConsent} />

            <button
              className="inline-flex items-center gap-2 rounded-lg bg-electric px-4 py-2 text-black font-semibold hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!consentConfirmed}
              onClick={async () => {
                try {
                  setError("");
                  const created = await createJob(script, selected);
                  setAudio("");
                  setJob({
                    job_id: created.job_id,
                    status: "queued",
                    progress: 0,
                    message: "Queued",
                    elapsed_seconds: 0,
                    eta_seconds: 0,
                    speed_chars_per_second: 0,
                    audio_ready: false,
                    completed_chunks: 0,
                    total_chunks: 0
                  });
                } catch (e: any) {
                  setError(e.message || "Failed to generate audio");
                }
              }}
            >
              <PlayCircle size={16} /> Generate Voice
            </button>

            <button
              className="ml-2 inline-flex items-center gap-2 rounded-lg bg-slate-200 px-4 py-2 text-slate-900 font-semibold hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
              disabled={!consentConfirmed}
              onClick={async () => {
                try {
                  setError("");
                  if (syncAudio) URL.revokeObjectURL(syncAudio);
                  const blob = await generateSync(script, selected);
                  setSyncAudio(URL.createObjectURL(blob));
                } catch (e: any) {
                  setError(e.message || "Sync generation failed");
                }
              }}
            >
              <PlayCircle size={16} /> Sync Generate Test
            </button>

            {!consentConfirmed && (
              <p className="text-sm text-amber-200">
                Confirm all three statements before generating or uploading cloned voice content.
              </p>
            )}

            {audio && (
              <audio controls className="w-full">
                <source src={audio} type="audio/wav" />
              </audio>
            )}

            {syncAudio && (
              <audio controls className="w-full">
                <source src={syncAudio} type="audio/wav" />
              </audio>
            )}
          </div>

          <div className="space-y-5">
            <BackendStatusPanel
              backendUp={backendUp}
              serviceName={serviceName}
              setupStatus={setupStatus}
              modelStatus={modelStatus}
              onWarmModel={handleWarmModel}
              warmingModel={warmingModel}
            />
            <ProgressPanel job={job} />
            <UploadPanel
              disabled={!consentConfirmed}
              onUpload={async (name, file) => {
                try {
                  await uploadCharacter(name, file);
                  await loadCharacters();
                  await loadBackendStatus();
                } catch (e: any) {
                  setError(e.message || "Upload failed");
                }
              }}
            />
          </div>
        </section>

        {error && <p className="text-red-300 text-sm">{error}</p>}
      </div>
    </main>
  );
}
