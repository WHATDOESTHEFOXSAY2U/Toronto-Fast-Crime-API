import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export default function ForecastCard({ forecast, currentScore }) {
    if (!forecast) return null;

    const { predicted_score, trend_direction, model_used, confidence_interval } = forecast;

    // Calculate delta if currentScore is available
    const delta = currentScore ? predicted_score - currentScore : 0;
    const absDelta = Math.abs(delta).toFixed(1);
    const isPositive = delta >= 0; // Higher score is better/safer

    // Determine colors based on safety trend (Positive delta = Safer = Green)
    const trendColor = isPositive ? 'text-emerald-400' : 'text-rose-400';
    const trendBg = isPositive ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-rose-500/10 border-rose-500/20';
    const glowColor = isPositive ? 'bg-emerald-500' : 'bg-rose-500';

    return (
        <div className="relative group">
            {/* Subtle Ambient Glow */}
            <div className={`absolute -inset-0.5 rounded-xl blur opacity-20 group-hover:opacity-40 transition duration-700 ${glowColor}`} />

            <div className="relative glass-card p-5 rounded-xl bg-slate-900/80 backdrop-blur-xl border border-white/5 flex flex-col justify-between overflow-hidden">
                {/* Decorative Background Element */}
                <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full blur-3xl opacity-10 ${glowColor}`} />

                <div className="flex justify-between items-start mb-4 relative z-10">
                    <div>
                        <div className="text-[9px] text-slate-400 font-bold uppercase tracking-widest mb-1">2026 Projection</div>
                        <div className="flex items-baseline gap-2">
                            <span className={`text-4xl font-light tracking-tighter ${trendColor}`}>
                                {Math.round(predicted_score)}
                            </span>
                            <span className="text-sm text-slate-500 font-medium">/100</span>
                        </div>
                    </div>

                    {/* Delta Badge */}
                    <div className={`flex flex-col items-end ${trendColor}`}>
                        <div className={`flex items-center gap-1.5 px-2.5 py-1 rounded-lg border ${trendBg} backdrop-blur-md`}>
                            {isPositive ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                            <span className="text-xs font-bold">{isPositive ? '+' : '-'}{absDelta}</span>
                        </div>
                        <span className="text-[9px] font-medium uppercase tracking-wide mt-1 opacity-80">
                            {isPositive ? 'Improving' : 'Declining'}
                        </span>
                    </div>
                </div>

                {/* Footer Info */}
                <div className="flex items-center justify-between pt-3 border-t border-white/5 relative z-10">
                    <div className="flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full ${isPositive ? 'bg-emerald-500' : 'bg-rose-500'}`} />
                        <span className="text-[10px] text-slate-400 font-medium">{model_used}</span>
                    </div>
                    <div className="text-[9px] text-slate-500 font-mono bg-slate-800/50 px-2 py-0.5 rounded border border-white/5">
                        ±{confidence_interval} margin
                    </div>
                </div>
            </div>
        </div>
    );
}
