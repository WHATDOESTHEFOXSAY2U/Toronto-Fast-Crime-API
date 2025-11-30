import React from 'react';

export default function InsightCard({ title, value, icon: Icon, color }) {
    const colorClasses = {
        amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
        rose: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
        blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        emerald: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    };

    const activeClass = colorClasses[color] || colorClasses.blue;

    return (
        <div className={`p-4 rounded-xl border ${activeClass} flex flex-col gap-2`}>
            <div className="flex items-center gap-2 opacity-80">
                {Icon && <Icon size={16} />}
                <span className="text-xs font-medium uppercase tracking-wider">{title}</span>
            </div>
            <div className="text-lg font-bold">{value}</div>
        </div>
    );
}
