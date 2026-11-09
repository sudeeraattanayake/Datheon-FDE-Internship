
"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  ArrowRight,
  Database,
  FileText,
  Layers3,
  Search,
  ShieldCheck,
  UploadCloud,
} from "lucide-react";

import { api } from "@/lib/api";
import type { SystemStats } from "@/types";

export default function Home() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [online, setOnline] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadDashboard() {
      try {
        const [health, data] = await Promise.all([
          api.health(),
          api.stats(),
        ]);

        setOnline(health.status === "healthy");
        setStats(data);
      } catch {
        setOnline(false);
      } finally {
        setLoading(false);
      }
    }

    loadDashboard();
  }, []);

  const cards = [
    {
      title: "Indexed Chunks",
      value: stats?.indexed_chunks?.toLocaleString() ?? "—",
      icon: Layers3,
      color: "text-cyan-400",
    },
    {
      title: "Vector Database",
      value: stats?.vector_database ?? "—",
      icon: Database,
      color: "text-blue-400",
    },
    {
      title: "Embedding Model",
      value: stats?.embedding_model ?? "—",
      icon: Activity,
      color: "text-violet-400",
    },
    {
      title: "API Status",
      value: loading ? "Checking" : online ? "Online" : "Offline",
      icon: ShieldCheck,
      color: online ? "text-emerald-400" : "text-amber-400",
    },
  ];

  return (
    <div className="min-h-screen bg-[#070c18] text-white">
      <header className="border-b border-white/10 bg-[#0c1424]/90">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 p-3">
              <Database className="h-6 w-6" />
            </div>

            <div>
              <h1 className="text-lg font-bold tracking-tight">
                DATHEON
              </h1>
              <p className="text-xs text-slate-400">
                Enterprise Vector ETL
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-2 text-sm">
            <span
              className={`h-2 w-2 rounded-full ${online ? "bg-emerald-400" : "bg-amber-400"
                }`}
            />
            {loading
              ? "Connecting..."
              : online
                ? "System Operational"
                : "Backend Offline"}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-12">
        <div className="mb-12">
          <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-xs font-medium text-cyan-300">
            <Activity className="h-4 w-4" />
            Enterprise AI Infrastructure
          </div>

          <h2 className="gradient-text max-w-3xl text-4xl font-bold tracking-tight md:text-6xl">
            Vector Intelligence
            <br />
            Command Center
          </h2>

          <p className="mt-6 max-w-2xl text-base leading-8 text-slate-400">
            Manage document ingestion, semantic embeddings,
            vector indexing and intelligent enterprise search
            from one unified workspace.
          </p>
        </div>

        <div className="mb-12 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          {cards.map((card) => {
            const Icon = card.icon;

            return (
              <div
                key={card.title}
                className="glass-panel p-6 transition hover:border-cyan-500/30"
              >
                <div className="mb-6 flex items-center justify-between">
                  <p className="text-sm text-slate-400">
                    {card.title}
                  </p>

                  <Icon className={`h-5 w-5 ${card.color}`} />
                </div>

                <p className="break-words text-2xl font-bold">
                  {card.value}
                </p>
              </div>
            );
          })}
        </div>

        <div className="mb-8 flex items-center justify-between">
          <div>
            <h3 className="text-2xl font-semibold">
              Workspace
            </h3>
            <p className="mt-2 text-sm text-slate-400">
              Access your enterprise vector operations.
            </p>
          </div>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {[
            {
              title: "Document Ingestion",
              description:
                "Upload PDF, CSV and Markdown documents into the vector pipeline.",
              href: "/upload",
              icon: UploadCloud,
              color: "from-cyan-500/20 to-blue-500/10",
            },
            {
              title: "Semantic Search",
              description:
                "Discover relevant knowledge using vector similarity and metadata filters.",
              href: "/search",
              icon: Search,
              color: "from-blue-500/20 to-violet-500/10",
            },
            {
              title: "Analytics",
              description:
                "Explore ingestion benchmarks and vector processing performance.",
              href: "/analytics",
              icon: FileText,
              color: "from-violet-500/20 to-fuchsia-500/10",
            },
          ].map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.title}
                href={item.href}
                className="glass-panel group overflow-hidden transition hover:-translate-y-1 hover:border-cyan-500/40"
              >
                <div className={`bg-gradient-to-br ${item.color} p-7`}>
                  <Icon className="h-9 w-9 text-cyan-300" />
                </div>

                <div className="p-7">
                  <h4 className="text-xl font-semibold">
                    {item.title}
                  </h4>

                  <p className="mt-3 min-h-20 text-sm leading-7 text-slate-400">
                    {item.description}
                  </p>

                  <div className="mt-5 flex items-center gap-2 text-sm font-semibold text-cyan-400">
                    Open Workspace
                    <ArrowRight className="h-4 w-4 transition group-hover:translate-x-1" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>

        <footer className="mt-16 border-t border-white/10 pt-6 text-center text-xs text-slate-500">
          Datheon Enterprise Vector ETL · Forward Deployed Engineering
        </footer>
      </main>
    </div>
  );
}
