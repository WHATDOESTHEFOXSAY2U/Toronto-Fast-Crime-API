import React from 'react';
import { motion } from 'framer-motion';

export default function SafetyGauge({ score, loading }) {
    const getColor = (s) => {
        if (s >= 80) return '#10b981'; // Emerald
        if (s >= 60) return '#f59e0b'; // Amber
        return '#ef4444'; // Red
    };

    const displayScore = loading ? 0 : (score || 0);
    const color = getColor(displayScore);
    const circumference = 2 * Math.PI * 90;
    const strokeDashoffset = circumference - (displayScore / 100) * circumference;

    return (
        <div className="relative w-full h-full flex items-center justify-center">
            {/* SVG Gauge */}
            <svg className="w-full h-full" viewBox="0 0 200 200">
                {/* Background Circle */}
                <circle
                    cx="100"
                    cy="100"
                    r="90"
                    stroke="#1e293b"
                    strokeWidth="10"
                    fill="transparent"
                    transform="rotate(-90 100 100)"
                />
                {/* Progress Circle */}
                {!loading && (
                    <motion.circle
                        initial={{ strokeDashoffset: circumference }}
                        animate={{ strokeDashoffset }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        cx="100"
                        cy="100"
                        r="90"
                        stroke={color}
                        strokeWidth="10"
                        fill="transparent"
                        strokeDasharray={circumference}
                        strokeLinecap="round"
                        transform="rotate(-90 100 100)"
                        style={{ filter: 'drop-shadow(0 0 8px rgba(59, 130, 246, 0.4))' }}
                    />
                )}

                {/* Center Score Text */}
                <text
                    x="100"
                    y="100"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    className="fill-white font-bold"
                    style={{ fontSize: '48px', fontFamily: 'Inter, sans-serif' }}
                >
                    {loading ? '-' : Math.round(displayScore)}
                </text>
            </svg>
        </div>
    );
}
