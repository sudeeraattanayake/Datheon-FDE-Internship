"use client";

import { useState } from "react";
import Link from "next/link";
import {
    ArrowLeft,
    Database,
    FileText,
    Loader2,
    Search,
    Shield,
} from "lucide-react";
import { api } from "@/lib/api";
import type { SearchResponse } from "@/types";

export default function SearchPanel() {
    const [query, setQuery] = useState("");
    const [department, setDepartment] = useState("HR");
    const [accessTier, setAccessTier] = useState("internal");
    const [limit, setLimit] = useState(5);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [response, setResponse] = useState<SearchResponse | null>(null);

    async function submit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        if (!query.trim() || !department.trim() || loading) return;

        setLoading(true);
        setError("");
        setResponse(null);

        try {
            const result = await api.search({
                query: query.trim(),
                department: department.trim(),
                access_tier: accessTier,
                n_results: limit,
            });
            setResponse(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Search failed.");
        } finally {
            setLoading(false);
        }
    }

    return (
        <main className="mx-auto max-w-6xl px-5 py-10 md:py-16">
            <Link href="/" className="mb-8 inline-flex items-center gap-2 text-sm text-slate-400 hover:text-cyan-300">
                <ArrowLeft size={17} /> Back to Dashboard
            </Link>

            <div className="mb-9">
                <span className="text-sm font-medium text-cyan-400">VECTOR INTELLIGENCE</span>
                <h1 className="mt-3 text-4xl font-bold md:text-5xl">
                    Semantic <span className="text-cyan-400">Search</span>
                </h1>
                <p className="mt-4 text-slate-400">
                    Search indexed enterprise knowledge using vector similarity and metadata filters.
                </p>
            </div>

            <form onSubmit={submit} className="glass-panel space-y-5 p-5 md:p-7">
                <label className="block">
                    <span className="mb-2 block text-sm text-slate-300">Search Query</span>
                    <div className="relative">
                        <Search className="absolute left-4 top-4 text-cyan-400" size={20} />
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            maxLength={2000}
                            required
                            rows={3}
                            placeholder="How do employees request annual leave?"
                            className="input-field resize-y pl-12"
                        />
                    </div>
                </label>

                <div className="grid gap-4 md:grid-cols-3">
                    <label>
                        <span className="mb-2 block text-sm text-slate-300">Department</span>
                        <input
                            className="input-field"
                            value={department}
                            onChange={(e) => setDepartment(e.target.value)}
                            maxLength={100}
                            required
                        />
                    </label>

                    <label>
                        <span className="mb-2 block text-sm text-slate-300">Access Tier</span>
                        <select
                            className="input-field"
                            value={accessTier}
                            onChange={(e) => setAccessTier(e.target.value)}
                        >
                            <option value="public">Public</option>
                            <option value="internal">Internal</option>
                            <option value="confidential">Confidential</option>
                            <option value="restricted">Restricted</option>
                        </select>
                    </label>

                    <label>
                        <span className="mb-2 block text-sm text-slate-300">Max Results</span>
                        <select
                            className="input-field"
                            value={limit}
                            onChange={(e) => setLimit(Number(e.target.value))}
                        >
                            {[3, 5, 10, 20, 50].map((n) => (
                                <option key={n} value={n}>{n} results</option>
                            ))}
                        </select>
                    </label>
                </div>

                <button
                    type="submit"
                    disabled={loading || !query.trim() || !department.trim()}
                    className="gradient-button flex w-full items-center justify-center gap-2 rounded-xl px-6 py-4 font-semibold"
                >
                    {loading ? (
                        <><Loader2 size={19} className="animate-spin" /> Searching vectors...</>
                    ) : (
                        <><Search size={19} /> Run Semantic Search</>
                    )}
                </button>
            </form>

            {error && (
                <div role="alert" className="mt-6 rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-red-300">
                    {error}
                </div>
            )}

            {response && (
                <section className="mt-9" aria-live="polite">
                    <div className="mb-5 flex items-center justify-between gap-4">
                        <h2 className="text-2xl font-semibold">Search Results</h2>
                        <span className="rounded-full bg-cyan-500/10 px-4 py-2 text-sm text-cyan-300">
                            {response.total_results} matches
                        </span>
                    </div>

                    {response.results.length === 0 ? (
                        <div className="glass-panel p-10 text-center text-slate-400">
                            No matching documents found. Try another query or metadata filter.
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {response.results.map((item, index) => {
                                const similarity = Math.max(
                                    0,
                                    Math.min(100, (1 - item.cosine_distance) * 100),
                                );

                                return (
                                    <article key={`${index}-${item.metadata.source ?? ""}`} className="glass-panel p-6">
                                        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
                                            <div className="flex items-center gap-2">
                                                <FileText className="text-cyan-400" size={20} />
                                                <span className="font-semibold">
                                                    {item.metadata.source ?? "Unknown source"}
                                                </span>
                                            </div>
                                            <span className="rounded-lg bg-cyan-500/10 px-3 py-1 text-sm text-cyan-300">
                                                {similarity.toFixed(1)}% similarity
                                            </span>
                                        </div>

                                        <p className="whitespace-pre-wrap leading-7 text-slate-200">
                                            {item.text}
                                        </p>

                                        <div className="mt-5 flex flex-wrap gap-2 border-t border-white/10 pt-4">
                                            <span className="inline-flex items-center gap-1 rounded-lg bg-white/5 px-3 py-2 text-xs text-slate-300">
                                                <Database size={13} /> {item.metadata.department}
                                            </span>
                                            <span className="inline-flex items-center gap-1 rounded-lg bg-white/5 px-3 py-2 text-xs text-slate-300">
                                                <Shield size={13} /> {item.metadata.access_tier}
                                            </span>
                                            {item.metadata.section && (
                                                <span className="rounded-lg bg-white/5 px-3 py-2 text-xs text-slate-300">
                                                    {item.metadata.section}
                                                </span>
                                            )}
                                            <span className="rounded-lg bg-white/5 px-3 py-2 text-xs text-slate-300">
                                                {item.metadata.date}
                                            </span>
                                            <span className="rounded-lg bg-white/5 px-3 py-2 text-xs text-slate-300">
                                                Distance: {item.cosine_distance.toFixed(4)}
                                            </span>
                                        </div>
                                    </article>
                                );
                            })}
                        </div>
                    )}
                </section>
            )}
        </main>
    );
}
