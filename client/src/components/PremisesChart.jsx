import React from 'react';
import { Building, Home, ShoppingBag, Map, Train } from 'lucide-react';

const PREMISES_ICONS = {
    'Apartment': Home,
    'House': Home,
    'Commercial': ShoppingBag,
    'Outside': Map,
    'Transit': Train,
    'Educational': Building,
    'Other': Building
};

export default function PremisesChart({ data }) {
    if (!data || Object.keys(data).length === 0) return null;

    // Convert to array and sort by count
    const items = Object.entries(data)
        .map(([name, count]) => ({ name, count }))
        .sort((a, b) => b.count - a.count);

    // Limit to top 4 for compact view
    const topItems = items.slice(0, 4);
    const maxCount = Math.max(...topItems.map(i => i.count));

    return (
        <div className="flex flex-col gap-1.5">
            {topItems.map((item, index) => {
                const Icon = PREMISES_ICONS[item.name] || Building;
                const percent = (item.count / maxCount) * 100;

                return (
                    <div key={item.name} className="relative">
                        <div className="flex items-center justify-between text-[8px] text-slate-400 mb-0.5">
                            <div className="flex items-center gap-1">
                                <Icon size={8} />
                                <span className="truncate max-w-[60px]">{item.name}</span>
                            </div>
                            <span className="font-mono opacity-70">{item.count}</span>
                        </div>
                        <div className="h-1 w-full bg-slate-800/50 rounded-full overflow-hidden">
                            <div
                                className="h-full bg-blue-500/50 rounded-full"
                                style={{ width: `${percent}%` }}
                            />
                        </div>
                    </div>
                );
            })}
        </div>
    );
}
