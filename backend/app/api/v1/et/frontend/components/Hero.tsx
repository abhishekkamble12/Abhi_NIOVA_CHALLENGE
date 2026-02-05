import React from "react";

export default function Hero() {
  return (
    <section className="h-[70vh] flex flex-col items-center justify-center text-center">
      <div className="w-full max-w-2xl">
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white">SatyaSetu: Defense for the Next Billion</h1>
        <p className="mt-4 text-slate-300">Real-time AI protection at the edge — mobile-first, voice-enabled.</p>
        <div className="mt-6 flex items-center justify-center">
          <button className="rounded-lg bg-cyan-500 px-6 py-3 font-semibold text-black">Try Voice</button>
        </div>
      </div>
    </section>
  );
}
