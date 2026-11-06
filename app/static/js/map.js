/**
 * map.js — Leaflet.js integration for CivicPulse
 *
 * Two public functions:
 *   initAdminMap(complaints, defaultLat, defaultLng)
 *   initPickerMap(mapId, latInputId, lngInputId, textInputId)
 */

// Status → marker color
const STATUS_COLORS = {
  'Pending':    '#e74c3c',   // red
  'In Progress':'#e67e22',   // orange
  'Resolved':   '#27ae60',   // green
  'Archived':   '#95a5a6',   // grey
};

function makeIcon(color) {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:14px;height:14px;
      background:${color};
      border:2px solid #fff;
      border-radius:50%;
      box-shadow:0 1px 4px rgba(0,0,0,.4);
    "></div>`,
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    popupAnchor: [0, -10],
  });
}

/**
 * Admin map — renders all complaint markers.
 * @param {Array}  complaints  Array of complaint objects from /admin/map/data
 * @param {number} defaultLat
 * @param {number} defaultLng
 */
function initAdminMap(complaints, defaultLat, defaultLng) {
  const mapEl = document.getElementById('admin-map');
  if (!mapEl) return;

  const map = L.map('admin-map').setView([defaultLat, defaultLng], 12);

  // Tile layer with graceful fallback
  const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 19,
  });

  tiles.on('tileerror', function() {
    const fb = document.getElementById('map-fallback');
    if (fb) fb.style.display = 'block';
  });

  tiles.addTo(map);

  if (!complaints || complaints.length === 0) return;

  complaints.forEach(function(c) {
    if (!c.latitude || !c.longitude) return;
    const color = STATUS_COLORS[c.status] || '#95a5a6';
    const marker = L.marker([c.latitude, c.longitude], { icon: makeIcon(color) });
    marker.bindPopup(`
      <div style="min-width:200px;font-size:13px;">
        <strong>${escHtml(c.title)}</strong><br>
        <span style="color:#888;font-size:12px;">${escHtml(c.category)}</span><br>
        <hr style="margin:6px 0;">
        <b>Location:</b> ${escHtml(c.location_text)}<br>
        <b>Status:</b> <span style="color:${color};font-weight:600;">${escHtml(c.status)}</span><br>
        <b>Priority:</b> ${escHtml(c.priority)}<br>
        <a href="/admin/complaints/${c.id}" style="display:inline-block;margin-top:6px;color:#1a5276;">
          View Details &rarr;
        </a>
      </div>
    `);
    marker.addTo(map);
  });

  // Auto-fit map to markers
  const coords = complaints
    .filter(c => c.latitude && c.longitude)
    .map(c => [c.latitude, c.longitude]);
  if (coords.length > 1) {
    map.fitBounds(coords, { padding: [40, 40] });
  }
}

/**
 * Location-picker map for the citizen submission form.
 * Clicking the map drops a pin and fills hidden lat/lng inputs
 * and (optionally) reverse-geocodes to fill the text input.
 */
function initPickerMap(mapId, latInputId, lngInputId, textInputId, defaultLat, defaultLng) {
  const mapEl = document.getElementById(mapId);
  if (!mapEl) return;

  const map = L.map(mapId).setView([defaultLat, defaultLng], 12);

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map);

  let marker = null;

  map.on('click', function(e) {
    const lat = e.latlng.lat.toFixed(6);
    const lng = e.latlng.lng.toFixed(6);

    document.getElementById(latInputId).value = lat;
    document.getElementById(lngInputId).value = lng;

    if (marker) {
      marker.setLatLng(e.latlng);
    } else {
      marker = L.marker(e.latlng).addTo(map);
    }
    marker.bindPopup('Selected location').openPopup();

    // Reverse geocode via Nominatim (rate-limited to user clicks only)
    if (textInputId) {
      fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lng}&format=json`)
        .then(r => r.json())
        .then(data => {
          if (data && data.display_name) {
            const textEl = document.getElementById(textInputId);
            if (textEl && !textEl.value) {
              textEl.value = data.display_name.substring(0, 200);
            }
          }
        })
        .catch(() => {}); // silently ignore network errors
    }
  });
}

function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
