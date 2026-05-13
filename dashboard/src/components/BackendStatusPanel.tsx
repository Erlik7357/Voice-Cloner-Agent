import { LoaderCircle, Server, ShieldCheck, ShieldX } from "lucide-react";
import { ModelStatusState, SetupCharacterState } from "../api";

type Props = {
  backendUp: boolean;
  serviceName: string;
  setupStatus: Record<string, SetupCharacterState>;
  modelStatus: ModelStatusState;
  onWarmModel: () => Promise<void>;
  warmingModel: boolean;
};

export default function BackendStatusPanel({
  backendUp,
  serviceName,
  setupStatus,
  modelStatus,
  onWarmModel,
  warmingModel
}: Props) {
  const entries = Object.entries(setupStatus);
  const canWarmModel = backendUp && modelStatus.status !== "warming" && !modelStatus.loaded && !warmingModel;

  return (
    <section className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-electric">
        <Server size={18} />
        <h3 className="text-lg font-semibold">Backend Status</h3>
      </div>

      <div className="rounded-xl bg-slate-900/60 border border-slate-700 p-3 text-sm">
        <p className="text-slate-300">Service: <span className="text-white">{serviceName || "voice-cloner"}</span></p>
        <p className={backendUp ? "text-emerald-300" : "text-red-300"}>
          API: {backendUp ? "Online" : "Offline"}
        </p>
      </div>

      <div className="rounded-xl bg-slate-900/60 border border-slate-700 p-3 space-y-3">
        <div className="flex items-center justify-between gap-3">
          <div>
            <p className="text-slate-100 font-semibold">Model Status</p>
            <p className="text-sm text-slate-300">{modelStatus.message}</p>
          </div>
          <button
            className="inline-flex items-center gap-2 rounded-lg bg-electric px-3 py-2 text-xs font-semibold text-black disabled:cursor-not-allowed disabled:opacity-50"
            disabled={!canWarmModel}
            onClick={() => void onWarmModel()}
          >
            {(warmingModel || modelStatus.status === "warming") && <LoaderCircle size={14} className="animate-spin" />}
            {modelStatus.loaded ? "Model Ready" : modelStatus.status === "warming" ? "Warming..." : "Start Loading"}
          </button>
        </div>

        <div className="h-3 w-full overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full bg-gradient-to-r from-emerald-400 via-cyan-400 to-electric transition-all duration-500"
            style={{ width: `${modelStatus.progress}%` }}
          />
        </div>

        <div className="flex items-center justify-between text-xs text-slate-400">
          <span>Status: {modelStatus.status}</span>
          <span>{modelStatus.progress}%</span>
        </div>

        {modelStatus.error && <p className="text-xs text-red-300">{modelStatus.error}</p>}
      </div>

      <div className="space-y-2">
        {entries.map(([key, value]) => (
          <div key={key} className="rounded-xl bg-slate-900/60 border border-slate-700 p-3">
            <div className="flex items-center justify-between">
              <p className="font-semibold text-slate-100">{value.name}</p>
              <span className={value.ready ? "text-emerald-300" : "text-red-300"}>
                {value.ready ? <ShieldCheck size={16} /> : <ShieldX size={16} />}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1 break-all">{value.voice_sample_path}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
