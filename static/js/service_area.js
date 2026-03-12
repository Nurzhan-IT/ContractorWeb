// service_area.js — Leaflet map + ZIP code coverage check
// Initialise map on DOMContentLoaded, draw service radius circle, handle ZIP lookup

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
}

// TODO: initialise Leaflet map (CENTER_LAT/LNG passed via template or inline script)
// TODO: draw L.circle(center, {radius: RADIUS_METERS})
// TODO: ZIP submit → POST /api/service-area/check/ → map.flyTo([lat, lng], 11)
// TODO: set marker color based on in_zone boolean
