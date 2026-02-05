"use client";

import React from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Zap,
  BookOpen,
  Film,
  ArrowRight,
  BarChart3,
  Sparkles,
} from "lucide-react";

export default function Dashboard() {
  const modules = [
    {
      title: "Social Media Engine",
      description:
        "Generate, schedule, and optimize social media content with AI-powered captions, hashtags, and engagement analysis.",
      icon: Zap,
      href: "/social",
      color: "from-blue-500 to-blue-600",
      features: [
        "AI Caption Generation",
        "Multi-platform Scheduling",
        "Engagement Analytics",
        "Auto-optimization",
      ],
    },
    {
      title: "News Feed",
      description:
        "Curated, personalized news feed powered by NLP and recommendations that adapts to your interests.",
      icon: BookOpen,
      href: "/feed",
      color: "from-purple-500 to-purple-600",
      features: [
        "Personalized Recommendations",
        "NLP Tagging",
        "Interest Tracking",
        "Trending Articles",
      ],
    },
    {
      title: "Video Editor",
      description:
        "Turn raw footage into platform-ready videos with AI scene detection, captions, and smart exports.",
      icon: Film,
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700 bg-slate-900/50 backdrop-blur">
        <div className="mx-auto max-w-7xl px-6 py-12">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <h1 className="text-4xl font-bold text-white">
              AI Media & Content Platform
            </h1>
            <p className="mt-2 text-lg text-slate-400">
              Automate content creation, personalize information delivery, and
              optimize digital assets with AI
            </p>
          </motion.div>
        </div>
      </header>

      {/* Stats */}
      <div className="border-b border-slate-700 bg-slate-800/30">
        <div className="mx-auto max-w-7xl px-6 py-8">
          <div className="grid grid-cols-3 gap-4">
            {stats.map(({ label, value, icon: Icon }) => (
              <motion.div
                key={label}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="flex items-center gap-4 rounded-lg border border-slate-700 bg-slate-800/50 p-4"
              >
                <Icon className="h-6 w-6 text-blue-400" />
                <div>
                  <p className="text-sm text-slate-400">{label}</p>
                  <p className="text-2xl font-bold text-white">{value}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Modules Grid */}
      <main className="mx-auto max-w-7xl px-6 py-12">
        <div className="grid gap-6 md:grid-cols-3">
          {modules.map((module, index) => {
            const Icon = module.icon;

            return (
              <motion.div
                key={module.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                whileHover={{ y: -5 }}
              >
                <Link href={module.href}>
                  <div className="group relative h-full overflow-hidden rounded-lg border border-slate-700 bg-slate-800/50 p-6 backdrop-blur transition hover:border-slate-600 hover:bg-slate-800/70">
                    {/* Background Gradient */}
                    <div
                      className={`absolute inset-0 opacity-0 transition group-hover:opacity-10 bg-gradient-to-br ${module.color}`}
                    />

                    {/* Content */}
                    <div className="relative z-10 space-y-4">
                      {/* Icon */}
                      <div
                        className={`inline-flex rounded-lg bg-gradient-to-br ${module.color} p-3`}
                      >
                        <Icon className="h-6 w-6 text-white" />
                      </div>

                      {/* Title & Description */}
                      <div>
                        <h2 className="text-xl font-bold text-white group-hover:text-blue-400 transition">
                          {module.title}
                        </h2>
                        <p className="mt-2 text-sm text-slate-400">
                          {module.description}
                        </p>
                      </div>

                      {/* Features */}
                      <div className="space-y-2 pt-4 border-t border-slate-700">
                        {module.features.map((feature) => (
                          <div
                            key={feature}
                            className="flex items-center gap-2 text-sm text-slate-300"
                          >
                            <div className="h-1.5 w-1.5 rounded-full bg-blue-400" />
                            {feature}
                          </div>
                        ))}
                      </div>

                      {/* CTA */}
                      <div className="flex items-center gap-2 pt-4 text-blue-400 group-hover:gap-3 transition">
                        <span className="text-sm font-semibold">
                          Explore Module
                        </span>
                        <ArrowRight className="h-4 w-4" />
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>

        {/* System Architecture Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mt-12 rounded-lg border border-slate-700 bg-slate-800 p-8"
        >
          <h2 className="mb-6 text-2xl font-bold text-white">
            System Architecture
          </h2>

          <div className="space-y-6">
            {/* Data Flow */}
            <div>
              <h3 className="mb-3 font-semibold text-blue-400">Data Flow</h3>
              <div className="flex flex-wrap items-center gap-2 text-sm text-slate-300">
                <span className="rounded bg-slate-900 px-3 py-1">
                  User Input
                </span>
                <span className="text-blue-400">→</span>
                <span className="rounded bg-slate-900 px-3 py-1">
                  AI Pipeline
                </span>
                <span className="text-blue-400">→</span>
                <span className="rounded bg-slate-900 px-3 py-1">
                  Content Gen
                </span>
                <span className="text-blue-400">→</span>
                <span className="rounded bg-slate-900 px-3 py-1">
                  Distribution
                </span>
                <span className="text-blue-400">→</span>
                <span className="rounded bg-slate-900 px-3 py-1">
                  Analytics
                </span>
              </div>
            </div>

            {/* Tech Stack */}
            <div>
              <h3 className="mb-3 font-semibold text-blue-400">Tech Stack</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-xs text-slate-400 font-medium">Backend</p>
                  <p className="mt-1 text-slate-300">
                    FastAPI, Python, PostgreSQL
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-400 font-medium">Frontend</p>
                  <p className="mt-1 text-slate-300">
                    Next.js 14, TypeScript, Tailwind
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-400 font-medium">AI/ML</p>
                  <p className="mt-1 text-slate-300">
                    OpenAI, NLP, Computer Vision
                  </p>
                </div>
                <div>
                  <p className="text-xs text-slate-400 font-medium">Database</p>
                  <p className="mt-1 text-slate-300">
                    PostgreSQL, Redis, Vector DB
                  </p>
                </div>
              </div>
            </div>

            {/* Key Features */}
            <div>
              <h3 className="mb-3 font-semibold text-blue-400">Key Features</h3>
              <ul className="grid grid-cols-2 gap-2 text-sm text-slate-300">
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Real-time processing
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Feedback loops
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Multi-platform support
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Self-optimizing
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Scalable architecture
                </li>
                <li className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400" />
                  Privacy-focused
                </li>
              </ul>
            </div>
          </div>
        </motion.div>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          className="mt-12 rounded-lg bg-gradient-to-r from-blue-600 to-blue-700 p-8 text-center"
        >
          <h2 className="mb-2 text-2xl font-bold text-white">
            Ready to Transform Your Content?
          </h2>
          <p className="mb-6 text-slate-100">
            Start with any module and unlock the power of AI-driven content
            automation
          </p>
          <Link href="/social">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="rounded-lg bg-white px-8 py-3 font-semibold text-blue-600 hover:bg-slate-50"
            >
              Get Started
            </motion.button>
          </Link>
        </motion.div>
      </main>
    </div>
  );
}
            Empowering rural communities with AI-driven cybersecurity
          </p>
          <div className="flex justify-center space-x-6">
            <Link href="/voice" className="text-gray-300 hover:text-white transition-colors">
              Voice Assistant
            </Link>
            <Link href="/admin" className="text-gray-300 hover:text-white transition-colors">
              Dashboard
            </Link>
          </div>
        </div>
      </footer>
    </div>
  )
}