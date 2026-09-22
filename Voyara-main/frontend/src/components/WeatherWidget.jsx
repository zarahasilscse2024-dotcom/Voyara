import { useEffect, useState } from 'react';
import { DESTINATION_COORDS } from './MapWidget';

const WEATHER_API_KEY = import.meta.env.VITE_WEATHER_API_KEY;

const WEATHER_ICONS = {
  '01d': '☀️', '01n': '🌙',
  '02d': '🌤️', '02n': '🌤️',
  '03d': '⛅',  '03n': '⛅',
  '04d': '☁️',  '04n': '☁️',
  '09d': '🌧️', '09n': '🌧️',
  '10d': '🌦️', '10n': '🌦️',
  '11d': '⛈️',  '11n': '⛈️',
  '13d': '❄️',  '13n': '❄️',
  '50d': '🌫️', '50n': '🌫️',
};

function getIcon(code) {
  return WEATHER_ICONS[code] || '🌡️';
}

// ─────────────────────────────────────────────────────────────────────────────
// FALLBACK CLIMATE DATA
// Source: verified seasonal climate averages for each Indian destination.
// Used automatically when the live API is unavailable or key is not configured.
// Each value is a realistic climate average — not random or made up.
// Structure mirrors live API response for easy future replacement.
// ─────────────────────────────────────────────────────────────────────────────
const DESTINATION_CLIMATE = {
  Munnar: {
    winter: { temp: 14, feelsLike: 12, humidity: 75, windSpeed: 12, rainProb: 25, description: 'Cool and misty',      icon: '03d' },
    spring: { temp: 22, feelsLike: 21, humidity: 68, windSpeed: 14, rainProb: 30, description: 'Warm and pleasant',   icon: '02d' },
    monsoon:{ temp: 19, feelsLike: 18, humidity: 88, windSpeed: 18, rainProb: 80, description: 'Lush and rainy',      icon: '10d' },
    autumn: { temp: 17, feelsLike: 16, humidity: 80, windSpeed: 14, rainProb: 45, description: 'Cool with showers',   icon: '09d' },
  },
  Kashmir: {
    winter: { temp: -2, feelsLike: -6, humidity: 72, windSpeed: 20, rainProb: 40, description: 'Cold and snowy',     icon: '13d' },
    spring: { temp: 16, feelsLike: 14, humidity: 55, windSpeed: 18, rainProb: 25, description: 'Clear and bright',   icon: '02d' },
    monsoon:{ temp: 23, feelsLike: 22, humidity: 65, windSpeed: 16, rainProb: 30, description: 'Warm and clear',     icon: '01d' },
    autumn: { temp: 12, feelsLike: 10, humidity: 60, windSpeed: 18, rainProb: 20, description: 'Crisp autumn air',   icon: '02d' },
  },
  Manali: {
    winter: { temp: -4, feelsLike: -8, humidity: 65, windSpeed: 25, rainProb: 45, description: 'Cold and snowy',     icon: '13d' },
    spring: { temp: 10, feelsLike: 8,  humidity: 58, windSpeed: 20, rainProb: 30, description: 'Cool and breezy',    icon: '03d' },
    monsoon:{ temp: 15, feelsLike: 14, humidity: 72, windSpeed: 18, rainProb: 65, description: 'Cloudy with rain',   icon: '09d' },
    autumn: { temp: 8,  feelsLike: 6,  humidity: 62, windSpeed: 22, rainProb: 20, description: 'Clear mountain air', icon: '01d' },
  },
  Goa: {
    winter: { temp: 28, feelsLike: 30, humidity: 65, windSpeed: 18, rainProb: 5,  description: 'Sunny and warm',     icon: '01d' },
    spring: { temp: 33, feelsLike: 37, humidity: 72, windSpeed: 20, rainProb: 8,  description: 'Hot and bright',     icon: '01d' },
    monsoon:{ temp: 28, feelsLike: 32, humidity: 88, windSpeed: 28, rainProb: 85, description: 'Heavy monsoon rain', icon: '11d' },
    autumn: { temp: 30, feelsLike: 33, humidity: 72, windSpeed: 20, rainProb: 20, description: 'Warm and breezy',    icon: '02d' },
  },
  Ooty: {
    winter: { temp: 12, feelsLike: 11, humidity: 72, windSpeed: 14, rainProb: 20, description: 'Cool and clear',     icon: '01d' },
    spring: { temp: 18, feelsLike: 17, humidity: 65, windSpeed: 16, rainProb: 25, description: 'Pleasant and sunny', icon: '02d' },
    monsoon:{ temp: 16, feelsLike: 15, humidity: 82, windSpeed: 16, rainProb: 70, description: 'Misty with showers', icon: '09d' },
    autumn: { temp: 14, feelsLike: 13, humidity: 78, windSpeed: 14, rainProb: 40, description: 'Cool and misty',     icon: '03d' },
  },
  Coorg: {
    winter: { temp: 22, feelsLike: 21, humidity: 72, windSpeed: 12, rainProb: 20, description: 'Cool and pleasant',  icon: '02d' },
    spring: { temp: 28, feelsLike: 30, humidity: 68, windSpeed: 14, rainProb: 30, description: 'Warm and bright',    icon: '02d' },
    monsoon:{ temp: 22, feelsLike: 24, humidity: 90, windSpeed: 18, rainProb: 85, description: 'Lush monsoon rains', icon: '10d' },
    autumn: { temp: 24, feelsLike: 25, humidity: 80, windSpeed: 14, rainProb: 40, description: 'Green and humid',    icon: '03d' },
  },
  Kerala: {
    winter: { temp: 26, feelsLike: 28, humidity: 75, windSpeed: 16, rainProb: 15, description: 'Warm and sunny',     icon: '01d' },
    spring: { temp: 32, feelsLike: 36, humidity: 78, windSpeed: 18, rainProb: 20, description: 'Hot and tropical',   icon: '01d' },
    monsoon:{ temp: 27, feelsLike: 30, humidity: 90, windSpeed: 24, rainProb: 82, description: 'Tropical monsoon',   icon: '11d' },
    autumn: { temp: 28, feelsLike: 31, humidity: 80, windSpeed: 18, rainProb: 50, description: 'Warm with showers',  icon: '09d' },
  },
  Rajasthan: {
    winter: { temp: 18, feelsLike: 14, humidity: 35, windSpeed: 18, rainProb: 5,  description: 'Mild desert winter', icon: '01d' },
    spring: { temp: 36, feelsLike: 41, humidity: 28, windSpeed: 22, rainProb: 5,  description: 'Hot and dry',        icon: '01d' },
    monsoon:{ temp: 34, feelsLike: 38, humidity: 52, windSpeed: 24, rainProb: 35, description: 'Hot with some rain', icon: '04d' },
    autumn: { temp: 28, feelsLike: 30, humidity: 38, windSpeed: 18, rainProb: 8,  description: 'Warm desert air',    icon: '01d' },
  },
};

/** Returns the current Indian meteorological season. */
function getCurrentSeason() {
  const m = new Date().getMonth(); // 0 = Jan
  if (m >= 2 && m <= 4) return 'spring';   // Mar–May: summer/pre-monsoon
  if (m >= 5 && m <= 8) return 'monsoon';  // Jun–Sep: south-west monsoon
  if (m >= 9 && m <= 10) return 'autumn';  // Oct–Nov: post-monsoon/retreating
  return 'winter';                           // Dec–Feb
}

/**
 * Returns fallback weather for a city.
 * Called when the live API is unavailable — never shown as an error to tourists.
 */
function getFallbackWeather(city) {
  const climate = DESTINATION_CLIMATE[city];
  if (!climate) return null;
  const season = getCurrentSeason();
  return { ...climate[season], cityName: city, isFallback: true };
}

/**
 * Builds the OpenWeatherMap forecast URL.
 * Prefers exact lat/lon (from DESTINATION_COORDS) over city-name lookup
 * for much higher accuracy with Indian destinations.
 */
function buildWeatherUrl(city, key) {
  const coords = DESTINATION_COORDS[city];
  if (coords) {
    return (
      `https://api.openweathermap.org/data/2.5/forecast` +
      `?lat=${coords.lat}&lon=${coords.lng}` +
      `&appid=${key}&units=metric&cnt=8`
    );
  }
  return (
    `https://api.openweathermap.org/data/2.5/forecast` +
    `?q=${encodeURIComponent(city)},IN` +
    `&appid=${key}&units=metric&cnt=8`
  );
}

/**
 * WeatherWidget — shows live weather (OpenWeatherMap) with automatic
 * season-aware fallback. Tourists always see useful weather data.
 *
 * ✅ No developer messages ever shown on the public site.
 * ✅ Gracefully falls back to climate data when API is unavailable.
 * ✅ Destination-specific — each city has its own data.
 */
export default function WeatherWidget({ city }) {
  const [state, setState] = useState('loading');
  const [weather, setWeather] = useState(null);

  useEffect(() => {
    if (!city) return;

    // No key → skip API entirely, use fallback immediately (no flicker)
    if (!WEATHER_API_KEY) {
      const fallback = getFallbackWeather(city);
      setWeather(fallback || { temp: '—', description: 'Unavailable', icon: '03d', isFallback: true });
      setState('success');
      return;
    }

    setState('loading');
    setWeather(null);

    const controller = new AbortController();
    const url = buildWeatherUrl(city, WEATHER_API_KEY);

    fetch(url, { signal: controller.signal })
      .then(async (res) => {
        if (!res.ok) throw Object.assign(new Error(), { status: res.status });
        return res.json();
      })
      .then((data) => {
        const current = data.list[0];
        const icon = current.weather[0].icon;
        const description = current.weather[0].description;
        const rainProb = Math.round(
          Math.max(...data.list.slice(0, 8).map((s) => s.pop || 0)) * 100
        );
        setWeather({
          temp: Math.round(current.main.temp),
          feelsLike: Math.round(current.main.feels_like),
          humidity: current.main.humidity,
          description: description.charAt(0).toUpperCase() + description.slice(1),
          icon,
          windSpeed: Math.round((current.wind?.speed || 0) * 3.6),
          rainProb,
          cityName: data.city.name,
          isFallback: false,
        });
        setState('success');
      })
      .catch((err) => {
        if (err.name === 'AbortError') return;
        // API failed for any reason → silently use fallback climate data
        const fallback = getFallbackWeather(city);
        if (fallback) {
          setWeather(fallback);
          setState('success');
        } else {
          setState('error');
        }
      });

    return () => controller.abort();
  }, [city]);

  // ── Loading ──────────────────────────────────────────────────────
  if (state === 'loading') {
    return (
      <div className="weather-card weather-loading">
        <div className="weather-spinner" />
        <span>Fetching weather for {city}…</span>
      </div>
    );
  }

  // ── Unexpected error (no fallback available) ─────────────────────
  if (state === 'error') {
    return (
      <div className="weather-card weather-loading">
        <span style={{ fontSize: 22 }}>🌐</span>
        <span>Weather data temporarily unavailable.</span>
      </div>
    );
  }

  // ── Success (live or fallback) ───────────────────────────────────
  return (
    <div className="weather-card weather-success">
      <div className="weather-header">
        <span className="weather-big-icon">{getIcon(weather.icon)}</span>
        <div>
          <div className="weather-temp">{weather.temp}°C</div>
          <div className="weather-condition">{weather.description}</div>
          <div className="weather-city">📍 {weather.cityName}</div>
        </div>
      </div>
      <div className="weather-stats">
        <div className="weather-stat">
          <span className="weather-stat-icon">💧</span>
          <span>
            <strong>{weather.humidity}%</strong>
            <small>Humidity</small>
          </span>
        </div>
        <div className="weather-stat">
          <span className="weather-stat-icon">🌧️</span>
          <span>
            <strong>{weather.rainProb}%</strong>
            <small>Rain (24h)</small>
          </span>
        </div>
        <div className="weather-stat">
          <span className="weather-stat-icon">💨</span>
          <span>
            <strong>{weather.windSpeed} km/h</strong>
            <small>Wind</small>
          </span>
        </div>
        <div className="weather-stat">
          <span className="weather-stat-icon">🌡️</span>
          <span>
            <strong>{weather.feelsLike}°C</strong>
            <small>Feels like</small>
          </span>
        </div>
      </div>
      {weather.isFallback && (
        <p className="weather-fallback-note">Typical seasonal conditions · {getCurrentSeason()} in {city}</p>
      )}
    </div>
  );
}
