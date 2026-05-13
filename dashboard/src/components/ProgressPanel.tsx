import { AudioLines, Clock3, Gauge, Sparkles } from "lucide-react";
import { JobState } from "../api";

type Props = {
  job: JobState | null;
};

export default function ProgressPanel({ job }: Props) {
  const progress = job?.progress ?? 0;
  const chunkLabel =
    job && (job.total_chunks ?? 0) > 0
      ? `${job.completed_chunks ?? 0}/${job.total_chunks ?? 0}`
      : "--";

  return (
    <section className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-electric">
        <Sparkles size={18} />
        <h3 className="text-lg font-semibold">Runtime Tracking</h3>
      </div>

      <div className="h-3 w-full rounded-full bg-slate-800 overflow-hidden">
        <div
          className="h-full bg-gradient-to-r from-accent to-electric transition-all duration-500"
          style={{ width: `${progress}%` }}
        />
      </div>

      <p className="text-sm text-slate-300">{job?.message ?? "Waiting for generation"}</p>

      <div className="grid grid-cols-3 gap-3 text-xs">
        <Metric icon={<AudioLines size={15} />} label="Progress" value={`${progress}%`} />
        <Metric icon={<Gauge size={15} />} label="Speed" value={`${job?.speed_chars_per_second ?? 0} ch/s`} />
        <Metric icon={<Clock3 size={15} />} label="Elapsed" value={`${job?.elapsed_seconds ?? 0}s`} />
      </div>

      <p className="text-xs text-slate-400">Chunks: {chunkLabel}</p>
      <p className="text-xs text-slate-400">ETA: {job?.eta_seconds ?? 0}s</p>
    </section>
  );
}

function Metric({ icon, label, value }: { icon: JSX.Element; label: string; value: string }) {
  return (
    <div className="rounded-xl bg-slate-900/60 border border-slate-700 p-3">
      <div className="text-slate-400 mb-1 flex items-center gap-1">{icon} {label}</div>
      <div className="text-slate-100 font-semibold">{value}</div>
    </div>
  );
}
