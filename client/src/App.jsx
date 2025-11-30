import React, { useState } from 'react';
import Map from './components/Map';
import Sidebar from './components/Sidebar';
import { motion, AnimatePresence } from 'framer-motion';

function App() {
    const [scoreData, setScoreData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [mapCenter, setMapCenter] = useState([43.6532, -79.3832]); // Toronto default

    const fetchScore = async (lat, lon) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`/score/coords?lat=${lat}&lon=${lon}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error('Failed to fetch safety score');
            }

            const data = await response.json();
            setScoreData({ ...data, coordinates: { lat, lon } });
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleLocationSelect = (latlng) => {
        setMapCenter([latlng.lat, latlng.lng]);
        fetchScore(latlng.lat, latlng.lng);
    };

    const handleSearch = async (query) => {
        setLoading(true);
        try {
            const response = await fetch(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query + ', Toronto')}`);
            const data = await response.json();

            if (data && data.length > 0) {
                const { lat, lon } = data[0];
                const newCenter = [parseFloat(lat), parseFloat(lon)];
                setMapCenter(newCenter);
                fetchScore(parseFloat(lat), parseFloat(lon));
            } else {
                setError("Location not found");
                setLoading(false);
            }
        } catch (err) {
            console.error("Geocoding error:", err);
            setError("Failed to search location");
            setLoading(false);
        }
    };

    return (
        <div className="relative w-full h-screen overflow-hidden bg-slate-900 font-inter">
            {/* Map Background Layer */}
            <div className="absolute inset-0 z-0">
                <Map
                    center={mapCenter}
                    onLocationSelect={handleLocationSelect}
                    scoreData={scoreData}
                />
            </div>

            {/* Main UI Overlay */}
            <div className="absolute inset-0 z-10 pointer-events-none flex p-4 md:p-6 lg:p-8">
                <Sidebar
                    scoreData={scoreData}
                    loading={loading}
                    error={error}
                    onSearch={handleSearch}
                />
            </div>
        </div>
    );
}

export default App;
