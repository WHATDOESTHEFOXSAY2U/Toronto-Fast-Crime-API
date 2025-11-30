import React, { useState } from 'react';
import { motion } from 'framer-motion';

export default function SafetyClock({ data }) {
    if (!data || data.length === 0) return null;

    const [hoveredHour, setHoveredHour] = useState(null);

    const radius = 80;
    const center = 100;

    return (
        <div className="relative w-full h-full aspect-square max-w-[240px] mx-auto">
            <svg viewBox="0 0 200 200" className="w-full h-full transform -rotate-90">
                {/* Hour markers */}
                {data.map((score, i) => {
                    const angle = (i / 24) * 360;
                    const isSafe = score >= 70;
                    const color = isSafe ? '#10b981' : (score >= 50 ? '#f59e0b' : '#ef4444');

                    // Bar length
                    const barLength = 25 + (score / 100) * 35;

                    return (
                        <g
                            key={i}
                            transform={`rotate(${angle} ${center} ${center})`}
                            onMouseEnter={() => setHoveredHour({ hour: i, score })}
                            onMouseLeave={() => setHoveredHour(null)}
                            className="cursor-pointer"
                        >
                            {/* Invisible hit area for easier hovering */}
                            <line
                                x1={center + radius + 10}
                                y1={center}
                                x2={center + 20}
                                y2={center}
                                stroke="transparent"
                                strokeWidth="12"
                            />
                            {/* Visible Bar */}
                            <motion.line
                                initial={{ scaleX: 0 }}
                                animate={{ scaleX: 1 }}
                                transition={{ delay: i * 0.02 }}
                                x1={center + 40} // Start from inner circle
                                y1={center}
                                x2={center + 40 + barLength}
                                y2={center}
                                stroke={color}
                                strokeWidth={hoveredHour?.hour === i ? "6" : "4"}
                                strokeLinecap="round"
                                className="transition-all duration-200"
                            />
                        </g>
                    );
                })}

                {/* Inner Circle (Sun/Moon) */}
                <circle cx={center} cy={center} r="35" fill="#1e293b" stroke="#334155" strokeWidth="2" />
            </svg>

            {/* Center Text (Hovered Info) */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                {hoveredHour !== null ? (
                    <>
                        <div className="text-lg font-bold text-white leading-none">
                            {hoveredHour.hour}:00
                        </div>
                        <div className={`text-xs font-medium ${hoveredHour.score >= 70 ? 'text-emerald-400' :
                                hoveredHour.score >= 50 ? 'text-amber-400' : 'text-rose-400'
                            }`}>
                            {Math.round(hoveredHour.score)}
                        </div>
                    </>
                ) : (
                    <div className="text-xs text-slate-500 font-mono">24H</div>
                )}
            </div>

            {/* Labels */}
            <div className="absolute top-0 left-1/2 -translate-x-1/2 text-[10px] text-slate-500 font-medium">12 PM</div>
            <div className="absolute bottom-0 left-1/2 -translate-x-1/2 text-[10px] text-slate-500 font-medium">12 AM</div>
            <div className="absolute left-0 top-1/2 -translate-y-1/2 text-[10px] text-slate-500 font-medium">6 AM</div>
            <div className="absolute right-0 top-1/2 -translate-y-1/2 text-[10px] text-slate-500 font-medium">6 PM</div>
        </div>
    );
}
