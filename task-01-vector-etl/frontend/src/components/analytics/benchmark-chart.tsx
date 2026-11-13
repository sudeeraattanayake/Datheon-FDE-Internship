"use client";

import {
    Bar,
    BarChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

const data = [
    { batch: "8", seconds: 6.095, throughput: 17.51 },
    { batch: "16", seconds: 4.52, throughput: 22.15 },
    { batch: "32", seconds: 4.11, throughput: 24.34 },
    { batch: "64", seconds: 4.131, throughput: 24.38 },
];

export default function BenchmarkChart() {
    return (
        <div className="space-y-6">
            <div className="glass-panel p-6">
                <h2 className="mb-2 text-xl font-semibold">Processing Throughput</h2>
                <p className="mb-8 text-sm text-slate-400">
                    Average chunks processed per second by batch size.
                </p>
                <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data}>
                            <CartesianGrid stroke="#243149" strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="batch" stroke="#94a3b8" />
                            <YAxis stroke="#94a3b8" />
                            <Tooltip
                                contentStyle={{
                                    background: "#101a2c",
                                    border: "1px solid #334155",
                                    borderRadius: 12,
                                    color: "#fff",
                                }}
                            />
                            <Bar
                                dataKey="throughput"
                                name="Chunks / second"
                                fill="#22d3ee"
                                radius={[7, 7, 0, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

            <div className="glass-panel p-6">
                <h2 className="mb-2 text-xl font-semibold">Average Ingestion Time</h2>
                <p className="mb-8 text-sm text-slate-400">
                    Mean processing time in seconds across three runs per batch size.
                </p>
                <div className="h-72 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data}>
                            <CartesianGrid stroke="#243149" strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="batch" stroke="#94a3b8" />
                            <YAxis stroke="#94a3b8" />
                            <Tooltip
                                contentStyle={{
                                    background: "#101a2c",
                                    border: "1px solid #334155",
                                    borderRadius: 12,
                                    color: "#fff",
                                }}
                            />
                            <Bar
                                dataKey="seconds"
                                name="Seconds"
                                fill="#818cf8"
                                radius={[7, 7, 0, 0]}
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
}
