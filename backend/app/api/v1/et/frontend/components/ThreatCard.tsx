import React from "react";

export default function ThreatCard() {
  return (
    <div className="rounded-xl bg-slate-900 p-6 border border-white/5">
      <div className="mb-3 text-sm text-slate-400">Incoming message</div>
      <div className="rounded-lg bg-black/40 p-4">
        <p className="text-white font-medium">You won a lottery! Click the link to claim your prize.</p>
        <div className="mt-3 text-xs text-red-400">Threat Detected</div>
      </div>
      <div className="mt-4 text-sm text-slate-300">Scroll to see how SatyaSetu analyzes and verifies this message.</div>
    </div>
  );
}
