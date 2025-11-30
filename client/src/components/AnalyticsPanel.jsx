import React from 'react';
import TrendChart from './TrendChart';
import RiskBreakdown from './RiskBreakdown';
import SafetyClock from './SafetyClock';
import InsightCard from './InsightCard';
import { TrendingUp, Clock, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function AnalyticsPanel({ data }) {
    if (!data) return null;

    return (
        <div className="space-y-4 w-full max-w-sm">
            {/* Key Insights Grid */}
            <div className="grid grid-cols-2 gap-3">
                <InsightCard
                    title="Peak Risk"
                    value={data.insights.peak_hour}
                    icon={Clock}
                    color="amber"
                />
                <InsightCard
                    title="Primary Risk"
                    value={data.insights.primary_risk}
                    icon={AlertTriangle}
                    color="rose"
                />
            </div>

            {/* Historical Trend */}
            <div className="glass-panel p-4">
                <h3 className="text-sm text-slate-400 font-medium mb-4 flex items-center gap-2">
                    <TrendingUp size={16} className="text-blue-400" />
                    10-Year Safety Trend
                </h3>
                <TrendChart data={data.history} />
            </div>

            {/* Risk Breakdown */}
            <div className="glass-panel p-4">
                <h3 className="text-sm text-slate-400 font-medium mb-4 flex items-center gap-2">
                    <AlertTriangle size={16} className="text-red-400" />
                    Top Risk Factors
                </h3>
                <RiskBreakdown data={data.category_breakdown} />
            </div>

            {/* Safety Clock */}
            <div className="glass-panel p-4">
                <h3 className="text-sm text-slate-400 font-medium mb-4 flex items-center gap-2">
                    <Clock size={16} className="text-emerald-400" />
                    24-Hour Safety Clock
                </h3>
                <SafetyClock data={data.insights.safety_clock} />
            </div>
        </div>
    );
}
