import { Mic2, Upload } from "lucide-react";
import { useState } from "react";

type Props = {
  onUpload: (name: string, file: File) => Promise<void>;
  disabled?: boolean;
};

export default function UploadPanel({ onUpload, disabled = false }: Props) {
  const [name, setName] = useState("");
  const [file, setFile] = useState<File | null>(null);

  return (
    <section className="glass rounded-2xl p-5 space-y-4">
      <div className="flex items-center gap-2 text-accent">
        <Mic2 size={18} />
        <h3 className="text-lg font-semibold">Clone New Anime Voice</h3>
      </div>

      <input
        className="w-full rounded-lg bg-slate-900/70 border border-slate-700 px-3 py-2"
        placeholder="Character name (e.g. Itachi Uchiha)"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      <input
        className="w-full text-sm"
        type="file"
        accept=".wav,.mp3,.m4a,.flac,.ogg"
        onChange={(e) => setFile(e.target.files?.[0] ?? null)}
      />

      <button
        className="inline-flex items-center gap-2 rounded-lg bg-accent px-4 py-2 text-black font-semibold hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
        disabled={disabled || !name || !file}
        onClick={async () => {
          if (!name || !file) return;
          await onUpload(name, file);
          setName("");
          setFile(null);
        }}
      >
        <Upload size={16} /> Upload Voice Sample
      </button>

      {disabled && (
        <p className="text-xs text-amber-200">
          Confirm the consent and legal statements before uploading a voice sample.
        </p>
      )}
    </section>
  );
}
