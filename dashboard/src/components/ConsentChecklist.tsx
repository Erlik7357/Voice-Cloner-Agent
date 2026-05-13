type ConsentState = {
  ownsSample: boolean;
  noImpersonation: boolean;
  understandsLegalRisk: boolean;
};

type Props = {
  value: ConsentState;
  onChange: (next: ConsentState) => void;
};

export type { ConsentState };

export default function ConsentChecklist({ value, onChange }: Props) {
  const items = [
    {
      key: "ownsSample" as const,
      label: "I confirm I own this voice sample or have explicit permission to use it."
    },
    {
      key: "noImpersonation" as const,
      label: "I will not impersonate real people without consent."
    },
    {
      key: "understandsLegalRisk" as const,
      label: "Generated voices may be subject to copyright, publicity, privacy, and local law."
    }
  ];

  return (
    <div className="rounded-xl border border-amber-400/30 bg-amber-300/10 p-4 text-sm text-amber-50">
      <p className="font-semibold text-amber-200">Consent and use confirmation</p>
      <div className="mt-3 space-y-3">
        {items.map((item) => (
          <label key={item.key} className="flex items-start gap-3">
            <input
              className="mt-1 h-4 w-4 accent-amber-300"
              type="checkbox"
              checked={value[item.key]}
              onChange={(e) => onChange({ ...value, [item.key]: e.target.checked })}
            />
            <span>{item.label}</span>
          </label>
        ))}
      </div>
    </div>
  );
}
