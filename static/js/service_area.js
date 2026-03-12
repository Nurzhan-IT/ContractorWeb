// service_area.js — Leaflet map + ZIP coverage check
// getCookie() is defined globally in base.html

document.addEventListener('DOMContentLoaded', function () {

  var cfg = window.SERVICE_AREA;

  // ── Init map ───────────────────────────────────────────────────────────────
  var map = L.map('map', { zoomControl: true }).setView(
    [cfg.centerLat, cfg.centerLng], 10
  );

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    maxZoom: 18,
  }).addTo(map);

  // ── Service zone circle ────────────────────────────────────────────────────
  L.circle([cfg.centerLat, cfg.centerLng], {
    radius: cfg.radiusMeters,
    color: '#16a34a',
    fillColor: '#16a34a',
    fillOpacity: 0.12,
    weight: 2,
  }).addTo(map);

  // Center marker (subtle)
  L.circleMarker([cfg.centerLat, cfg.centerLng], {
    radius: 6,
    color: '#15803d',
    fillColor: '#16a34a',
    fillOpacity: 1,
    weight: 2,
  }).addTo(map).bindPopup('<b>Our HQ</b><br>Atlanta, GA');

  // ── Completed-job markers ──────────────────────────────────────────────────
  var JOBS = [
    { lat: 33.9526, lng: -84.5499, text: '<b>Roof Repair</b><br>Marietta — saved client $1,400' },
    { lat: 33.7748, lng: -84.2963, text: '<b>Emergency Pipe Burst</b><br>Decatur — fixed same day' },
    { lat: 33.9304, lng: -84.3733, text: '<b>Electrical Panel Upgrade</b><br>Sandy Springs — full rewire' },
    { lat: 33.8840, lng: -84.5144, text: '<b>HVAC Replacement</b><br>Smyrna — 5-star review' },
    { lat: 33.9412, lng: -84.2135, text: '<b>Kitchen Plumbing Remodel</b><br>Norcross — 3-week project' },
    { lat: 33.6400, lng: -84.4499, text: '<b>Flat Roof Replacement</b><br>College Park — 30-year warranty' },
  ];

  var starIcon = L.divIcon({
    html: '<div style="font-size:18px;line-height:1;filter:drop-shadow(0 1px 3px rgba(0,0,0,0.4))">⭐</div>',
    className: '',
    iconSize: [22, 22],
    iconAnchor: [11, 11],
    popupAnchor: [0, -14],
  });

  JOBS.forEach(function (job) {
    L.marker([job.lat, job.lng], { icon: starIcon })
      .addTo(map)
      .bindPopup(job.text, { maxWidth: 200 });
  });

  // ── ZIP form ───────────────────────────────────────────────────────────────
  var form       = document.getElementById('zip-form');
  var zipInput   = document.getElementById('zip-input');
  var checkBtn   = document.getElementById('check-btn');
  var zipError   = document.getElementById('zip-error');
  var resultBlock  = document.getElementById('result-block');
  var inZoneEl     = document.getElementById('in-zone');
  var outZoneEl    = document.getElementById('out-of-zone');
  var userMarker   = null;

  form.addEventListener('submit', function (e) {
    e.preventDefault();

    var zip = zipInput.value.trim();
    zipError.classList.add('hidden');
    zipError.textContent = '';

    if (!/^\d{5}$/.test(zip)) {
      zipError.textContent = 'Please enter a valid 5-digit ZIP code.';
      zipError.classList.remove('hidden');
      zipInput.focus();
      return;
    }

    // Spinner
    checkBtn.disabled = true;
    checkBtn.innerHTML =
      '<svg class="animate-spin h-4 w-4 inline mr-1" xmlns="http://www.w3.org/2000/svg" ' +
      'fill="none" viewBox="0 0 24 24">' +
      '<circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>' +
      '<path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path>' +
      '</svg>Checking...';

    fetch('/api/service-area/check/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ zip: zip }),
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        checkBtn.disabled = false;
        checkBtn.textContent = 'Check Now \u2192';

        if (data.error) {
          zipError.textContent = data.error;
          zipError.classList.remove('hidden');
          return;
        }

        showResult(data);
        updateMap(data);
      })
      .catch(function () {
        checkBtn.disabled = false;
        checkBtn.textContent = 'Check Now \u2192';
        zipError.textContent = 'Connection error. Please try again.';
        zipError.classList.remove('hidden');
      });
  });

  function showResult(data) {
    resultBlock.classList.remove('hidden');

    // Reset animation by re-adding class
    [inZoneEl, outZoneEl].forEach(function (el) {
      el.classList.remove('result-animate');
      void el.offsetWidth; // reflow
      el.classList.add('result-animate');
    });

    if (data.in_zone) {
      inZoneEl.classList.remove('hidden');
      outZoneEl.classList.add('hidden');

      var cityLabel = data.city + (data.state ? ', ' + data.state : '');
      document.getElementById('result-city').textContent = cityLabel;
      document.getElementById('result-eta').textContent  = data.eta_range || '';
    } else {
      outZoneEl.classList.remove('hidden');
      inZoneEl.classList.add('hidden');

      document.getElementById('result-distance').textContent = data.distance_miles;
    }
  }

  function updateMap(data) {
    // Remove previous user marker
    if (userMarker) {
      map.removeLayer(userMarker);
      userMarker = null;
    }

    var color = data.in_zone ? '#16a34a' : '#dc2626';
    var label = data.in_zone
      ? '<b>' + data.city + '</b><br>In service zone ✅'
      : '<b>' + data.city + '</b><br>Outside service zone ❌<br>' +
        data.distance_miles + ' miles from our zone';

    var icon = L.divIcon({
      html: '<div style="width:18px;height:18px;border-radius:50%;background:' + color +
            ';border:3px solid white;box-shadow:0 2px 6px rgba(0,0,0,0.35)"></div>',
      className: '',
      iconSize: [18, 18],
      iconAnchor: [9, 9],
      popupAnchor: [0, -12],
    });

    userMarker = L.marker([data.lat, data.lng], { icon: icon })
      .addTo(map)
      .bindPopup(label, { maxWidth: 200 })
      .openPopup();

    map.flyTo([data.lat, data.lng], 11, { duration: 1.5 });
  }

  // ── Cities accordion ───────────────────────────────────────────────────────
  var citiesToggle = document.getElementById('cities-toggle');
  var citiesList   = document.getElementById('cities-list');

  citiesToggle.addEventListener('click', function () {
    var isOpen = !citiesList.classList.contains('hidden');
    citiesList.classList.toggle('hidden', isOpen);
    citiesToggle.classList.toggle('accordion-open', !isOpen);
  });

});
