"use client";

import { useRef, useState } from "react";
import type { FormEvent, KeyboardEvent, DragEvent } from "react";
import Link from "next/link";
import {
    ArrowLeft,
    CheckCircle2,
    FileText,
    Loader2,
    UploadCloud,
    X,
} from "lucide-react";

import { api } from "@/lib/api";
import type { IngestionResponse } from "@/types";

const MAX_FILE_SIZE = 10 * 1024 * 1024;
const ALLOWED_EXTENSIONS = ["pdf", "csv", "md"];

export default function UploadPanel() {
    const inputRef = useRef<HTMLInputElement>(null);

    const [file, setFile] = useState<File | null>(null);
    const [department, setDepartment] = useState("HR");
    const [accessTier, setAccessTier] = useState("internal");
    const [documentDate, setDocumentDate] = useState("");
    const [batchSize, setBatchSize] = useState(32);

    const [dragging, setDragging] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [result, setResult] = useState<IngestionResponse | null>(null);

    function selectFile(nextFile: File | null) {
        setError("");
        setResult(null);

        if (!nextFile) {
            setFile(null);
            return;
        }

        const extension = nextFile.name
            .split(".")
            .pop()
            ?.toLowerCase();

        if (!ALLOWED_EXTENSIONS.includes(extension ?? "")) {
            setFile(null);
            setError(
                "Unsupported file format. Please upload PDF, CSV or Markdown."
            );
            return;
        }

        if (nextFile.size === 0) {
            setFile(null);
            setError("The selected file is empty.");
            return;
        }

        if (nextFile.size > MAX_FILE_SIZE) {
            setFile(null);
            setError("Maximum allowed file size is 10 MB.");
            return;
        }

        setFile(nextFile);
    }

    function removeFile() {
        setFile(null);
        setResult(null);
        setError("");

        if (inputRef.current) {
            inputRef.current.value = "";
        }
    }

    function handleDrop(event: DragEvent<HTMLDivElement>) {
        event.preventDefault();
        setDragging(false);

        if (!loading) {
            selectFile(event.dataTransfer.files[0] ?? null);
        }
    }

    function handleKeyboard(event: KeyboardEvent<HTMLDivElement>) {
        if (
            !loading &&
            (event.key === "Enter" || event.key === " ")
        ) {
            event.preventDefault();
            inputRef.current?.click();
        }
    }

    async function handleSubmit(event: FormEvent<HTMLFormElement>) {
        event.preventDefault();

        if (loading) return;

        if (!file) {
            setError("Please select a document.");
            return;
        }

        if (!department.trim()) {
            setError("Department is required.");
            return;
        }

        if (!documentDate) {
            setError("Please select a document date.");
            return;
        }

        setLoading(true);
        setError("");
        setResult(null);

        const formData = new FormData();

        formData.append("file", file);
        formData.append("department", department.trim());
        formData.append("access_tier", accessTier);
        formData.append("document_date", documentDate);
        formData.append("batch_size", String(batchSize));

        try {
            const response = await api.ingest(formData);
            setResult(response);
        } catch (err) {
            setError(
                err instanceof Error
                    ? err.message
                    : "Document ingestion failed. Please try again."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <main className="mx-auto max-w-5xl px-5 py-10 md:py-16">
            <Link
                href="/"
                className="mb-8 inline-flex items-center gap-2 text-sm text-slate-400 transition hover:text-cyan-300"
            >
                <ArrowLeft size={17} />
                Back to Dashboard
            </Link>

            <div className="mb-10">
                <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-cyan-500/20 bg-cyan-500/10 px-4 py-2 text-xs font-medium text-cyan-300">
                    <UploadCloud size={15} />
                    ENTERPRISE DOCUMENT PIPELINE
                </div>

                <h1 className="text-4xl font-bold tracking-tight md:text-5xl">
                    Document{" "}
                    <span className="gradient-text">Ingestion</span>
                </h1>

                <p className="mt-5 max-w-2xl leading-7 text-slate-400">
                    Upload enterprise documents, generate semantic chunks,
                    create vector embeddings and index knowledge into ChromaDB.
                </p>
            </div>

            <form
                onSubmit={handleSubmit}
                className="glass-panel space-y-7 p-5 md:p-8"
            >
                <div
                    role="button"
                    tabIndex={loading ? -1 : 0}
                    aria-label="Select a document to upload"
                    aria-disabled={loading}
                    onClick={() => {
                        if (!loading) inputRef.current?.click();
                    }}
                    onKeyDown={handleKeyboard}
                    onDragOver={(event) => {
                        event.preventDefault();
                        if (!loading) setDragging(true);
                    }}
                    onDragLeave={(event) => {
                        event.preventDefault();
                        setDragging(false);
                    }}
                    onDrop={handleDrop}
                    className={`rounded-2xl border-2 border-dashed p-10 text-center transition ${loading
                        ? "cursor-not-allowed opacity-60"
                        : "cursor-pointer"
                        } ${dragging
                            ? "border-cyan-400 bg-cyan-400/10"
                            : "border-slate-700 bg-[#0b1424] hover:border-cyan-500/60"
                        }`}
                >
                    <input
                        ref={inputRef}
                        type="file"
                        accept=".pdf,.csv,.md"
                        disabled={loading}
                        className="hidden"
                        onChange={(event) => {
                            selectFile(event.target.files?.[0] ?? null);
                            event.target.value = "";
                        }}
                    />

                    <div className="mx-auto mb-5 flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500/20 to-blue-500/10">
                        <UploadCloud className="h-10 w-10 text-cyan-400" />
                    </div>

                    <h2 className="text-xl font-semibold">
                        Drop your document here
                    </h2>

                    <p className="mt-3 text-sm text-slate-400">
                        Drag and drop or click to browse your files
                    </p>

                    <div className="mt-5 flex flex-wrap justify-center gap-2">
                        {["PDF", "CSV", "Markdown"].map((format) => (
                            <span
                                key={format}
                                className="rounded-lg border border-white/10 bg-white/5 px-3 py-1.5 text-xs text-slate-300"
                            >
                                {format}
                            </span>
                        ))}
                    </div>

                    <p className="mt-4 text-xs text-slate-500">
                        Maximum file size: 10 MB
                    </p>
                </div>

                {file && (
                    <div className="flex items-center justify-between gap-4 rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
                        <div className="flex min-w-0 items-center gap-3">
                            <div className="rounded-xl bg-cyan-500/10 p-3">
                                <FileText size={23} className="text-cyan-400" />
                            </div>

                            <div className="min-w-0">
                                <p className="truncate font-semibold">
                                    {file.name}
                                </p>

                                <p className="mt-1 text-xs text-slate-400">
                                    {(file.size / 1024).toFixed(2)} KB
                                </p>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={removeFile}
                            disabled={loading}
                            aria-label="Remove selected file"
                            className="rounded-lg p-2 text-slate-400 transition hover:bg-white/10 hover:text-white"
                        >
                            <X size={19} />
                        </button>
                    </div>
                )}

                <div>
                    <h3 className="mb-5 text-lg font-semibold">
                        Document Metadata
                    </h3>

                    <div className="grid gap-5 md:grid-cols-2">
                        <label className="block">
                            <span className="mb-2 block text-sm text-slate-300">
                                Department
                            </span>

                            <input
                                type="text"
                                value={department}
                                onChange={(event) =>
                                    setDepartment(event.target.value)
                                }
                                maxLength={100}
                                placeholder="HR, FINANCE, IT..."
                                className="input-field"
                                disabled={loading}
                                required
                            />
                        </label>

                        <label className="block">
                            <span className="mb-2 block text-sm text-slate-300">
                                Access Tier
                            </span>

                            <select
                                value={accessTier}
                                onChange={(event) =>
                                    setAccessTier(event.target.value)
                                }
                                className="input-field"
                                disabled={loading}
                            >
                                <option value="public">Public</option>
                                <option value="internal">Internal</option>
                                <option value="confidential">
                                    Confidential
                                </option>
                                <option value="restricted">
                                    Restricted
                                </option>
                            </select>
                        </label>

                        <label className="block">
                            <span className="mb-2 block text-sm text-slate-300">
                                Document Date
                            </span>

                            <input
                                type="date"
                                value={documentDate}
                                onChange={(event) =>
                                    setDocumentDate(event.target.value)
                                }
                                className="input-field"
                                disabled={loading}
                                required
                            />
                        </label>

                        <label className="block">
                            <span className="mb-2 block text-sm text-slate-300">
                                Batch Size
                            </span>

                            <select
                                value={batchSize}
                                onChange={(event) =>
                                    setBatchSize(Number(event.target.value))
                                }
                                className="input-field"
                                disabled={loading}
                            >
                                {[8, 16, 32, 64, 128].map((size) => (
                                    <option key={size} value={size}>
                                        {size} chunks
                                    </option>
                                ))}
                            </select>
                        </label>
                    </div>
                </div>

                {error && (
                    <div
                        role="alert"
                        className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
                    >
                        {error}
                    </div>
                )}

                <button
                    type="submit"
                    disabled={
                        !file ||
                        loading ||
                        !department.trim() ||
                        !documentDate
                    }
                    className="gradient-button flex w-full items-center justify-center gap-3 rounded-xl px-6 py-4 font-semibold"
                >
                    {loading ? (
                        <>
                            <Loader2
                                size={20}
                                className="animate-spin"
                            />
                            Processing Document...
                        </>
                    ) : (
                        <>
                            <UploadCloud size={20} />
                            Start Ingestion
                        </>
                    )}
                </button>

                <p className="text-center text-xs text-slate-500">
                    Semantic chunking and embedding generation may take
                    several minutes. Keep this page open while processing.
                </p>
            </form>

            {result && (
                <section
                    className="glass-panel mt-7 p-6 md:p-8"
                    aria-live="polite"
                >
                    <div className="mb-6 flex items-center gap-3">
                        <CheckCircle2
                            size={28}
                            className="text-emerald-400"
                        />

                        <div>
                            <h2 className="text-xl font-bold text-emerald-400">
                                Ingestion Successful
                            </h2>

                            <p className="mt-1 text-sm text-slate-400">
                                Your document has been processed and indexed.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-4 sm:grid-cols-3">
                        <div className="rounded-xl border border-white/5 bg-[#0b1424] p-5">
                            <p className="text-sm text-slate-400">
                                Documents Loaded
                            </p>

                            <p className="mt-3 text-3xl font-bold">
                                {result.documents_loaded}
                            </p>
                        </div>

                        <div className="rounded-xl border border-white/5 bg-[#0b1424] p-5">
                            <p className="text-sm text-slate-400">
                                Chunks Processed
                            </p>

                            <p className="mt-3 text-3xl font-bold">
                                {result.chunks_created}
                            </p>
                        </div>

                        <div className="rounded-xl border border-white/5 bg-[#0b1424] p-5">
                            <p className="text-sm text-slate-400">
                                Processing Time
                            </p>

                            <p className="mt-3 text-3xl font-bold">
                                {result.elapsed_seconds.toFixed(2)}s
                            </p>
                        </div>
                    </div>

                    <div className="mt-6 rounded-xl border border-white/10 bg-[#0b1424] p-5">
                        <p className="text-xs uppercase tracking-wider text-slate-500">
                            Indexed Source
                        </p>

                        <p className="mt-2 break-all font-medium text-white">
                            {result.source}
                        </p>

                        <p className="mt-2 text-sm text-slate-400">
                            Original file: {result.filename}
                        </p>
                    </div>

                    <Link
                        href="/search"
                        className="mt-6 inline-flex items-center gap-2 font-medium text-cyan-400 transition hover:text-cyan-300"
                    >
                        Search Indexed Documents
                        <span aria-hidden="true">→</span>
                    </Link>
                </section>
            )}
        </main>
    );
}
