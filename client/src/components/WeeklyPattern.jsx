import React from 'react';
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function WeeklyPattern({ data }) {
    if (!data || data.length !== 7) return null;

    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    const chartData = data.map((score, index) => ({
        day: days[index],
        score: score
    }));

    const getColorForScore = (score) => {
        if (score >= 80) return '#10b981'; // Emerald-500
        if (score >= 60) return '#f59e0b'; // Amber-500
        return '#f43f5e'; // Rose-500
    };

    return (
        <div className="w-full h-full">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                    <XAxis
                        dataKey="day"
                        stroke="#64748b"
                        fontSize={9}
                        tickLine={false}
                        axisLine={false}
                        fontFamily="Inter, sans-serif"
                        fontWeight={500}
                    />
                    <Tooltip
                        cursor={{ fill: '#1e293b' }}
                        contentStyle={{
                            backgroundColor: '#0f172a',
                            borderColor: '#334155',
                            borderRadius: '12px',
                            fontSize: '11px',
                            fontFamily: 'Inter, sans-serif',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
                        }}
                        itemStyle={{ color: '#e2e8f0' }}
                    />
                    <Bar dataKey="score" radius={[4, 4, 0, 0]}>
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={getColorForScore(entry.score)} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
}
