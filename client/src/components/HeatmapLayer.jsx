import React, { useEffect } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet.heat';

export default function HeatmapLayer() {
    const map = useMap();

    useEffect(() => {
        // Fetch heatmap data
        fetch('/heatmap')
            .then(res => res.json())
            .then(data => {
                if (!data || data.length === 0) return;

                // Create heat layer
                // Data format: [lat, lon, intensity]
                // L.heatLayer should be available now via the import
                if (!L.heatLayer) {
                    console.error("L.heatLayer is not defined even after import");
                    return;
                }

                const heat = L.heatLayer(data, {
                    radius: 15,
                    blur: 12,
                    maxZoom: 17,
                    max: 1000, // Drastically reduced max to ensure Red zones appear (was 4000)
                    minOpacity: 0.0, // Allow full transparency
                    gradient: {
                        0.00: 'rgba(0, 255, 0, 0)',      // Transparent Start
                        0.05: 'rgba(0, 255, 0, 0.9)',    // Deep Green (Very Safe - Opaque)
                        0.20: 'rgba(144, 238, 144, 0.6)',// Light Green (Safe - Semi-Transparent)
                        0.35: 'rgba(255, 255, 0, 0.2)',  // Yellow (Transition - Transparent)
                        0.50: 'rgba(255, 165, 0, 0.6)',  // Orange (Danger Start - Semi-Opaque)
                        0.65: 'rgba(255, 69, 0, 0.8)',   // Red-Orange (High Danger - Opaque)
                        0.85: 'rgba(139, 0, 0, 1.0)'     // Dark Red (Extreme Danger - Opaque)
                    }
                }).addTo(map);

                // Cleanup
                return () => {
                    map.removeLayer(heat);
                };
            })
            .catch(err => console.error("Error loading heatmap data:", err));
    }, [map]);

    return null;
}

