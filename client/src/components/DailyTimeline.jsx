import React from 'react';
import { Clock } from 'lucide-react';

export default function DailyTimeline({ data, peakRange }) {
    if (!data || data.length !== 24) return null;

    // Normalize data for opacity (0.2 to 1.0)
    const minScore = Math.min(...data);
    const maxScore = Math.max(...data);
    const range = maxScore - minScore;

    const getOpacity = (score) => {
        // Lower score = Higher Risk = Higher Opacity
        // Invert score because data is safety score (100=safe, 0=unsafe)
        // We want to highlight RISK (low safety)
        const risk = 100 - score;
        return 0.2 + (risk / 100) * 0.8;
    };

    const getColor = (score) => {
        if (score >= 80) return '#10b981'; // Emerald
        if (score >= 60) return '#22c55e'; // Green
        if (score >= 40) return '#f59e0b'; // Amber
        if (score >= 20) return '#f97316'; // Orange
        return '#ef4444'; // Red
    };

    return (
        <div className="w-full h-full flex flex-col justify-center">
            {/* Timeline Bar */}
            <div className="flex w-full h-8 rounded-lg overflow-hidden relative">
                {data.map((score, hour) => (
                    <div
                        key={hour}
                        className="flex-1 h-full transition-all duration-300 hover:scale-y-110 origin-bottom"
                        style={{
                            backgroundColor: getColor(score),
                            opacity: getOpacity(score)
                        }}
                        title={`${hour}:00 - Safety: ${score}`}
                    />
                ))}

                {/* Peak Range Marker (Overlay) */}
                {/* This is a bit complex to position absolutely without exact pixel math, 
                    so we'll just use the visual density for now. 
                    Or we could add a border to the peak hours. */}
            </div>

            {/* Labels */}
            <div className="flex justify-between text-[9px] text-slate-500 mt-1 font-medium uppercase tracking-wider">
                <span>12am</span>
                <span>6am</span>
                <span>12pm</span>
                <span>6pm</span>
                <span>11pm</span>
            </div>

            {/* Peak Indicator */}
            {peakRange && (
                <div className="flex items-center gap-1.5 mt-2 justify-end">
                    <div className="text-[9px] text-slate-400 uppercase tracking-wide">Peak Risk</div>
                    <div className="px-1.5 py-0.5 rounded bg-rose-500/20 border border-rose-500/30 text-[10px] font-bold text-rose-300 flex items-center gap-1">
                        <Clock size={10} />
                        {peakRange}
                    </div>
                </div>
            )}
        </div>
    );
}
