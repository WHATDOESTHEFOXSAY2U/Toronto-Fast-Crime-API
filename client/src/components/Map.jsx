import React, { useEffect } from 'react';
import { MapContainer, TileLayer, useMap, useMapEvents, Marker, Circle, Polygon } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { TORONTO_BOUNDARY } from './TorontoBoundary';
import HeatmapLayer from './HeatmapLayer';

// Component to handle map clicks and movement
function MapController({ onLocationSelect, center }) {
    const map = useMap();

    useEffect(() => {
        if (center) {
            // map.flyTo(center, map.getZoom(), {
            //     duration: 1.5,
            //     easeLinearity: 0.25
            // });
        }
    }, [center, map]);

    useMapEvents({
        click(e) {
            onLocationSelect(e.latlng);
            // Don't flyTo here. Let the parent update the 'center' prop, 
            // which triggers the useEffect above. This prevents double-movement glitches.
        },
    });

    return null;
}

export default function Map({ center, onLocationSelect }) {
    return (
        <MapContainer
            center={center || [43.6532, -79.3832]}
            zoom={13}
            zoomControl={false}
            className="w-full h-full z-0"
            style={{ background: '#0f172a' }}
        >
            {/* Dark Matter Tiles for Premium Look */}
            <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
                url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            />

            {/* Heatmap Layer */}
            <HeatmapLayer />

            {/* Toronto City Boundary */}
            <Polygon
                positions={TORONTO_BOUNDARY}
                pathOptions={{
                    color: '#3b82f6',
                    fillColor: '#3b82f6',
                    fillOpacity: 0.05,
                    weight: 2,
                    dashArray: '5, 10',
                    lineCap: 'round'
                }}
            />

            {/* Selected Location Marker & Radius */}
            {center && (
                <>
                    <Marker
                        key={`${center[0]}-${center[1]}`}
                        position={center}
                    />
                    <Circle
                        key={`circle-${center[0]}-${center[1]}`}
                        center={center}
                        radius={800} // 800m default radius
                        pathOptions={{
                            color: '#3b82f6',
                            fillColor: '#3b82f6',
                            fillOpacity: 0.1,
                            weight: 1
                        }}
                    />
                </>
            )}

            <MapController onLocationSelect={onLocationSelect} center={center} />
        </MapContainer>
    );
}
