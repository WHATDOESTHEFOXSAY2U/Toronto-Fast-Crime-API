import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp } from 'lucide-react';

export default function RiskBreakdown({ data }) {
    if (!data || typeof data !== 'object') return null;

    const [expanded, setExpanded] = useState(null);
    const toggleExpand = (category) => setExpanded(expanded === category ? null : category);

    // Sort by risk (lowest safety = highest risk)
    const sortedCategories = Object.entries(data).sort(([, a], [, b]) => a.safety_score - b.safety_score);

    return (
        <div className="space-y-2">
            {sortedCategories.map(([category, stats]) => {
                const isExpanded = expanded === category;
                const riskColor = stats.safety_score >= 80 ? 'bg-emerald-500' :
                    stats.safety_score >= 60 ? 'bg-amber-500' : 'bg-rose-500';
                const riskText = stats.safety_score >= 80 ? 'text-emerald-400' :
                    stats.safety_score >= 60 ? 'text-amber-400' : 'text-rose-400';

                return (
                    <div key={category} className="bg-slate-800/40 rounded-lg border border-slate-700/30 overflow-hidden hover:border-slate-600/50 transition-colors">
                        {/* Header */}
                        <div
                            onClick={() => toggleExpand(category)}
                            className="p-3 cursor-pointer hover:bg-slate-800/60 transition-colors flex items-center justify-between group"
                        >
                            <div className="flex items-center gap-3">
                                <div className={`w-1 h-8 rounded-full ${riskColor}`} />
                                <div>
                                    <div className="text-xs font-bold text-slate-200 mb-1">{category}</div>
                                    <div className="inline-flex items-center px-1.5 py-0.5 rounded bg-slate-700/30 border border-slate-600/30">
                                        <span className="text-[9px] font-mono text-slate-400">
                                            <span className="text-slate-300 font-bold">{stats.incident_count}</span> cases
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="flex items-center gap-4">
                                <div className="text-right">
                                    <div className={`text-lg font-light tracking-tighter leading-none ${riskText}`}>
                                        {Math.round(stats.safety_score)}<span className="text-[10px] text-slate-500 font-normal ml-0.5">/100</span>
                                    </div>
                                </div>
                                {isExpanded ?
                                    <ChevronUp size={14} className="text-slate-500" /> :
                                    <ChevronDown size={14} className="text-slate-600 group-hover:text-slate-400 transition-colors" />
                                }
                            </div>
                        </div>

                        {/* Expanded Details */}
                        <AnimatePresence>
                            {isExpanded && (
                                <motion.div
                                    initial={{ height: 0, opacity: 0 }}
                                    animate={{ height: 'auto', opacity: 1 }}
                                    exit={{ height: 0, opacity: 0 }}
                                    transition={{ duration: 0.2 }}
                                    className="border-t border-slate-700/30 bg-slate-900/30"
                                >
                                    <div className="p-3 space-y-2">
                                        <div className="flex justify-between text-[9px] uppercase tracking-wider text-slate-500 font-bold">
                                            <span>Subtype</span>
                                            <span>Count</span>
                                        </div>
                                        {stats.top_subtypes && stats.top_subtypes.length > 0 ? (
                                            stats.top_subtypes.map((sub, idx) => (
                                                <div key={idx} className="flex justify-between items-center text-[11px] py-1 border-b border-slate-800/50 last:border-0">
                                                    <span className="text-slate-300">{sub.type}</span>
                                                    <span className="font-mono text-slate-500">{sub.count}</span>
                                                </div>
                                            ))
                                        ) : (
                                            <div className="text-[11px] text-slate-500 italic">No details available</div>
                                        )}
                                    </div>
                                </motion.div>
                            )}
                        </AnimatePresence>
                    </div>
                );
            })}
        </div>
    );
}
