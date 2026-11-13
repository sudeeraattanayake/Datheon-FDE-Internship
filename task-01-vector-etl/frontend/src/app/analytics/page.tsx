import Link from "next/link";
import { ArrowLeft, BarChart3, Database, Gauge, Timer } from "lucide-react";
import BenchmarkChart from "@/components/analytics/benchmark-chart";

export default function AnalyticsPage() {
    return (
        <main className="mx-auto max-w-6xl px-5 py-10 md:py-16">
            <Link href="/" className="mb-8 inline-flex items-center gap-2 text-sm text-slate-400 hover:text-cyan-300">
                <ArrowLeft size={17} /> Back to Dashboard
            </Link>

            <div className="mb-10">
                <span className="text-sm font-medium text-cyan-400">
                    PERFORMANCE INTELLIGENCE
                </span>
                <h1 className="mt-3 text-4xl font-bold md:text-5xl">
                    Pipeline <span className="text-cyan-400">Analytics</span>
                </h1>
                <p className="mt-4 text-slate-400">
                    Historical batch ingestion benchmarks from the Task 01 ETL pipeline.
                </p>
            </div>

            <div className="mb-8 grid gap-4 sm:grid-cols-3">
                {[
                    { label: "Benchmark Runs", value: "12", icon: BarChart3 },
                    { label: "Balanced Batch Size", value: "32", icon: Database },
                    { label: "Peak Throughput", value: "24.38/s", icon: Gauge },
                ].map((card) => {
                    const Icon = card.icon;
                    return (
                        <div key={card.label} className="glass-panel p-6">
                            <Icon className="mb-5 text-cyan-400" size={24} />
                            <p className="text-sm text-slate-400">{card.label}</p>
                            <p className="mt-2 text-3xl font-bold">{card.value}</p>
                        </div>
                    );
                })}
            </div>

            <BenchmarkChart />

            <div className="glass-panel mt-6 flex items-start gap-3 p-5 text-sm text-slate-400">
                <Timer className="shrink-0 text-cyan-400" size={20} />
                <p>
                    Benchmark dataset: 100 synthetic CSV records. Four batch sizes,
                    three repetitions each. Results are historical measurements,
                    not live API telemetry. Batch size 32 is the balanced default.
                </p>
            </div>
        </main>
    );
}
