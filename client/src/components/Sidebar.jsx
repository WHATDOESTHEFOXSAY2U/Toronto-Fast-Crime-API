import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Shield, TrendingUp, AlertTriangle, Clock, MapPin, Building } from 'lucide-react';
import SearchOverlay from './SearchOverlay';
import SafetyGauge from './SafetyGauge';
import TrendChart from './TrendChart';
import RiskBreakdown from './RiskBreakdown';
import DailyTimeline from './DailyTimeline';
import SeasonalityChart from './SeasonalityChart';
import WeeklyPattern from './WeeklyPattern';
import ForecastCard from './ForecastCard';
import PremisesChart from './PremisesChart';

export default function Sidebar({ scoreData, loading, error, onSearch }) {
    // Helper to format time to 12h
    const formatTimeRange = (range) => {
        if (!range) return '--';
        // Assuming range is like "16:00-19:00" or "10:00-13:00"
        try {
            const [start, end] = range.split('-');
            const formatHour = (h) => {
                const hour = parseInt(h.split(':')[0]);
                const ampm = hour >= 12 ? 'PM' : 'AM';
                const h12 = hour % 12 || 12;
                return `${h12}${ampm}`;
            };
            return `${formatHour(start)} - ${formatHour(end)}`;
        } catch (e) {
            return range;
        }
    };

    return (
        <motion.div
            initial={{ x: -400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            className="h-full w-full max-w-md flex flex-col pointer-events-auto p-3"
        >
            {/* Header (Fixed) */}
            <div className="glass-panel p-3 backdrop-blur-2xl bg-slate-900/90 border-slate-700/50 shadow-2xl shrink-0 mb-3">
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <div className="p-1.5 rounded-lg bg-blue-500/10 border border-blue-500/20 shadow-[0_0_10px_rgba(59,130,246,0.2)]">
                            <Shield className="text-blue-400" size={16} />
                        </div>
                        <h1 className="text-sm font-bold text-white tracking-tight">TORONTO SAFETY</h1>
                    </div>
                </div>
                <SearchOverlay onSearch={onSearch} loading={loading} compact={true} />
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col gap-3 min-h-0 overflow-y-auto custom-scrollbar pr-1">
                {error && (
                    <div className="glass-panel p-3 border-red-500/30 bg-red-500/10 text-red-200 text-xs flex items-center gap-2">
                        <AlertTriangle size={14} />
                        {error}
                    </div>
                )}

                {!scoreData && !loading && !error && (
                    <div className="glass-panel p-8 text-center text-slate-500 flex-1 flex flex-col justify-center items-center">
                        <Shield className="mb-4 opacity-20" size={48} />
                        <p className="text-sm font-light">Select a location to begin analysis</p>
                    </div>
                )}

                <AnimatePresence mode="wait">
                    {(scoreData || loading) && (
                        <motion.div
                            key="dashboard"
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            exit={{ opacity: 0, y: -10 }}
                            className="flex flex-col gap-3"
                        >
                            {/* 1. Current Safety & Percentile */}
                            <div className="glass-panel p-4 relative overflow-hidden">
                                <div className={`absolute top-0 right-0 w-64 h-64 rounded-full blur-[80px] opacity-20 pointer-events-none ${scoreData?.current_score >= 80 ? 'bg-emerald-500' :
                                    scoreData?.current_score >= 60 ? 'bg-amber-500' : 'bg-rose-600'
                                    }`} />

                                <div className="relative z-10 flex justify-between items-end">
                                    <div>
                                        <div className="text-[9px] text-slate-400 font-bold uppercase tracking-widest mb-1">Current Safety</div>
                                        <div className="flex items-baseline gap-2">
                                            <span className={`text-6xl font-light tracking-tighter ${scoreData?.current_score >= 80 ? 'text-emerald-400 neon-text-safe' :
                                                scoreData?.current_score >= 60 ? 'text-amber-400' : 'text-rose-400 neon-text-unsafe'
                                                }`}>
                                                {scoreData ? Math.round(scoreData.current_score) : '--'}
                                            </span>
                                            <span className="text-xl text-slate-500 font-thin">/100</span>
                                        </div>
                                        <div className={`text-[10px] font-bold uppercase mt-1 ${scoreData?.current_score >= 80 ? 'text-emerald-500' :
                                            scoreData?.current_score >= 60 ? 'text-amber-500' : 'text-rose-500'
                                            }`}>
                                            {scoreData?.benchmark?.status || 'Unknown'}
                                        </div>
                                    </div>

                                    <div className="bg-slate-800/40 rounded-xl p-3 border border-slate-700/30 backdrop-blur-md flex flex-col justify-center min-w-[120px]">
                                        <div className="text-[9px] text-slate-400 font-bold uppercase tracking-widest mb-1">Safer Than</div>
                                        <div className="flex items-baseline gap-1">
                                            <span className={`text-3xl font-light tracking-tighter ${(100 - (scoreData?.overall_percentile || 0)) >= 80 ? 'text-emerald-400' :
                                                (100 - (scoreData?.overall_percentile || 0)) >= 50 ? 'text-blue-400' :
                                                    'text-rose-400'
                                                }`}>
                                                {Math.round(100 - (scoreData?.overall_percentile || 0))}%
                                            </span>
                                            <span className="text-[10px] text-slate-500 font-medium uppercase tracking-wide">of City</span>
                                        </div>
                                        {/* Visual Indicator Bar */}
                                        <div className="w-full h-1 bg-slate-700/50 rounded-full mt-2 overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${(100 - (scoreData?.overall_percentile || 0)) >= 80 ? 'bg-gradient-to-r from-emerald-600 to-emerald-400' :
                                                    (100 - (scoreData?.overall_percentile || 0)) >= 50 ? 'bg-gradient-to-r from-blue-600 to-blue-400' :
                                                        'bg-gradient-to-r from-rose-600 to-rose-400'
                                                    }`}
                                                style={{ width: `${100 - (scoreData?.overall_percentile || 0)}%` }}
                                            />
                                        </div>
                                    </div>
                                </div>

                                {/* Trend Chart with Timeline */}
                                <div className="h-24 w-full mt-2 -mb-2">
                                    <TrendChart data={scoreData?.history} />
                                </div>
                            </div>

                            {/* 2. Forecast */}
                            {scoreData?.forecast && (
                                <ForecastCard
                                    forecast={scoreData.forecast}
                                    currentScore={scoreData.current_score}
                                />
                            )}

                            {/* 3. Risk Context (Peak Time & Primary Risk) */}
                            <div className="grid grid-cols-2 gap-3">
                                {/* Peak Risk Time */}
                                <div className="glass-panel p-3 flex flex-col justify-center items-center text-center">
                                    <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1">Riskiest Time</div>
                                    <div className="text-lg font-bold text-rose-300 flex items-center gap-2">
                                        <Clock size={14} />
                                        {formatTimeRange(scoreData?.insights?.peak_time_range)}
                                    </div>
                                </div>

                                {/* Primary Risk */}
                                <div className="glass-panel p-3 flex flex-col justify-center items-center text-center">
                                    <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-1">Top Crime Type</div>
                                    {(() => {
                                        const riskName = scoreData?.insights?.primary_risk;
                                        const riskStats = scoreData?.category_breakdown?.[riskName];
                                        const riskScore = riskStats?.safety_score;

                                        let colorClass = 'text-slate-200';
                                        if (riskScore !== undefined) {
                                            if (riskScore >= 80) colorClass = 'text-emerald-400';
                                            else if (riskScore >= 60) colorClass = 'text-amber-400';
                                            else colorClass = 'text-rose-400';
                                        }

                                        return (
                                            <div className="flex flex-col items-center">
                                                <div className={`text-lg font-bold ${colorClass}`}>
                                                    {riskName || '--'}
                                                </div>
                                                {riskScore !== undefined && (
                                                    <div className="text-[10px] text-slate-500 font-mono mt-0.5">
                                                        Score: <span className={colorClass}>{Math.round(riskScore)}</span>
                                                    </div>
                                                )}
                                            </div>
                                        );
                                    })()}
                                </div>
                            </div>

                            {/* 4. Charts (Seasonality & Weekly) */}
                            <div className="grid grid-cols-2 gap-3">
                                <div className="glass-panel p-3">
                                    <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-2 text-center">Monthly Trend</div>
                                    <div className="h-20">
                                        <SeasonalityChart data={scoreData?.insights?.monthly_pattern} />
                                    </div>
                                </div>
                                <div className="glass-panel p-3">
                                    <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-2 text-center">Weekly Trend</div>
                                    <div className="h-20">
                                        <WeeklyPattern data={scoreData?.insights?.weekly_pattern} />
                                    </div>
                                </div>
                            </div>

                            {/* 5. Location Context (Neighbourhood & Premises) */}
                            <div className="grid grid-cols-2 gap-3">
                                {/* Neighbourhood Card */}
                                <div className="glass-panel p-3 flex flex-col justify-center items-center text-center">
                                    <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-2">Neighbourhood</div>
                                    <div className="flex flex-col items-center gap-1">
                                        <div className="p-2 rounded-full bg-blue-500/10 text-blue-400 mb-1">
                                            <MapPin size={16} />
                                        </div>
                                        <div className="text-xs font-bold text-slate-200 leading-tight line-clamp-2">
                                            {scoreData?.insights?.neighbourhood || 'Unknown'}
                                        </div>
                                    </div>
                                </div>

                                {/* Premises Breakdown */}
                                <div className="glass-panel p-3 flex flex-col">
                                    <div className="text-[9px] text-slate-500 font-bold uppercase tracking-widest mb-2 text-center">Where is Crime Happening?</div>
                                    <PremisesChart data={scoreData?.insights?.premises_breakdown} />
                                </div>
                            </div>

                            {/* 5. Detailed Risk List */}
                            <div className="glass-panel p-4">
                                <h3 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest flex items-center gap-2 mb-4">
                                    <AlertTriangle size={12} /> Full Breakdown
                                </h3>
                                <RiskBreakdown data={scoreData?.category_breakdown} />
                            </div>
                        </motion.div>
                    )}
                </AnimatePresence>
            </div>
        </motion.div>
    );
}

// Helper component for compact stat badges
function StatBadge({ label, value, color = 'slate', icon }) {
    const colorClasses = {
        emerald: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-300',
        amber: 'bg-amber-500/10 border-amber-500/30 text-amber-300',
        rose: 'bg-rose-500/10 border-rose-500/30 text-rose-300',
        blue: 'bg-blue-500/10 border-blue-500/30 text-blue-300',
        slate: 'bg-slate-700/20 border-slate-600/30 text-slate-300'
    };

    return (
        <div className={`rounded-lg p-1.5 border ${colorClasses[color]}`}>
            <div className="text-[8px] text-slate-500 uppercase tracking-wide mb-0.5 flex items-center gap-1">
                {icon}
                {label}
            </div>
            <div className="text-[11px] font-bold truncate">{value}</div>
        </div>
    );
}
