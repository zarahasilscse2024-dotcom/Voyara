import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, ZoomControl } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

/**
 * Destination coordinates — real verified coordinates for all Voyara destinations.
 * Exported so WeatherWidget can reuse them for precise lat/lon API calls.
 */
export const DESTINATION_COORDS = {
  Munnar:    { lat: 10.0889, lng: 77.0595, label: 'Munnar, Kerala',                  state: 'Kerala' },
  Kashmir:   { lat: 34.0837, lng: 74.7973, label: 'Srinagar, Kashmir',               state: 'Jammu & Kashmir' },
  Manali:    { lat: 32.2396, lng: 77.1887, label: 'Manali, Himachal Pradesh',         state: 'Himachal Pradesh' },
  Goa:       { lat: 15.2993, lng: 74.1240, label: 'Goa, India',                       state: 'Goa' },
  Ooty:      { lat: 11.4102, lng: 76.6950, label: 'Ooty, Tamil Nadu',                 state: 'Tamil Nadu' },
  Coorg:     { lat: 12.3375, lng: 75.8069, label: 'Coorg, Karnataka',                 state: 'Karnataka' },
  Kerala:    { lat: 9.4981,  lng: 76.9493, label: 'Alleppey, Kerala',                 state: 'Kerala' },
  Rajasthan: { lat: 26.9124, lng: 75.7873, label: 'Jaipur, Rajasthan',               state: 'Rajasthan' },
};

/**
 * Custom Voyara map marker — styled to match the Voyara design system.
 * Uses a CSS DivIcon to avoid Leaflet's default PNG marker asset issues.
 */
function createVoyaraMarker() {
  return L.divIcon({
    className: '',
    html: `
      <div class="voyara-map-pin">
        <div class="voyara-map-pin-dot"></div>
        <div class="voyara-map-pin-ring"></div>
      </div>
    `,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -18],
  });
}

/**
 * Inner map — a separate component so that changing the `key` prop
 * on MapWidget fully re-mounts Leaflet when the destination changes.
 */
function LeafletMap({ coords }) {
  const marker = createVoyaraMarker();

  return (
    <MapContainer
      center={[coords.lat, coords.lng]}
      zoom={11}
      style={{ width: '100%', height: '100%' }}
      scrollWheelZoom={false}
      zoomControl={false}
      attributionControl={true}
    >
      {/* Carto Voyager tiles — free, no API key, beautiful cartographic style */}
      <TileLayer
        url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        subdomains="abcd"
        maxZoom={20}
      />
      <ZoomControl position="bottomright" />
      <Marker position={[coords.lat, coords.lng]} icon={marker}>
        <Popup className="voyara-map-popup">
          <strong>📍 {coords.label}</strong>
          <br />
          <span style={{ fontSize: 11, color: '#68736d' }}>
            {coords.lat.toFixed(4)}°N, {coords.lng.toFixed(4)}°E
          </span>
        </Popup>
      </Marker>
    </MapContainer>
  );
}

/**
 * MapWidget — interactive map powered by Leaflet + OpenStreetMap/CARTO.
 * ✅ 100% free — no API key required, no Google Cloud, no billing.
 * ✅ Destination-specific — each destination shows its own real location.
 * ✅ Interactive — zoom, pan, marker popup.
 */
export default function MapWidget({ destination }) {
  const coords = DESTINATION_COORDS[destination];

  if (!coords) {
    return (
      <div className="map-card map-config-notice">
        <div className="map-config-icon">📍</div>
        <div>
          <strong>Location not available</strong>
          <p>Location data for "{destination}" is not yet in our system.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="map-card">
      <div className="map-location-label">
        <span className="map-pin">📍</span>
        <span>{coords.label}</span>
        <span className="map-coords">
          {coords.lat.toFixed(2)}°N · {coords.lng.toFixed(2)}°E
        </span>
      </div>
      {/* key forces full remount when destination changes */}
      <div className="map-iframe-wrapper" key={destination}>
        <LeafletMap coords={coords} />
      </div>
    </div>
  );
}
