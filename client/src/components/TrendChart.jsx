import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function TrendChart({ data }) {
    if (!data || data.length === 0) return null;

    // Reverse data to show Oldest -> Newest (Left -> Right)
    const chartData = [...data].reverse();

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={chartData} margin={{ bottom: 0, left: 0, right: 0, top: 5 }}>
                    <defs>
                        {/* Gradient for the Line Stroke (Solid) */}
                        <linearGradient id="colorScoreStroke" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#10b981" stopOpacity={1} />   {/* 100: Emerald */}
                            <stop offset="50%" stopColor="#f59e0b" stopOpacity={1} />  {/* 50: Amber */}
                            <stop offset="100%" stopColor="#f43f5e" stopOpacity={1} /> {/* 0: Rose */}
                        </linearGradient>

                        {/* Gradient for the Area Fill (Transparent) */}
                        <linearGradient id="colorScoreFill" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="0%" stopColor="#10b981" stopOpacity={0.4} />
                            <stop offset="50%" stopColor="#f59e0b" stopOpacity={0.2} />
                            <stop offset="100%" stopColor="#f43f5e" stopOpacity={0.05} />
                        </linearGradient>
                    </defs>
                    <XAxis
                        dataKey="year"
                        hide={false}
                        axisLine={false}
                        tickLine={false}
                        tick={{ fill: '#64748b', fontSize: 9, fontFamily: 'Inter' }}
                        dy={5}
                        interval="preserveStartEnd"
                    />
                    <YAxis domain={[0, 100]} hide={true} />
                    <Tooltip
                        contentStyle={{
                            backgroundColor: '#0f172a',
                            borderColor: '#334155',
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontFamily: 'Inter, sans-serif',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                        }}
                        itemStyle={{ color: '#e2e8f0' }}
                        labelStyle={{ color: '#94a3b8', marginBottom: '0.25rem' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="safety_score"
                        stroke="url(#colorScoreStroke)"
                        strokeWidth={3}
                        fillOpacity={1}
                        fill="url(#colorScoreFill)"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    );
}
