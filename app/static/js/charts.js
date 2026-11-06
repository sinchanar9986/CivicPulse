/**
 * charts.js — Chart.js dashboard charts for CivicPulse admin
 *
 * Usage: initDashboardCharts('/admin/stats')
 */

const CHART_COLORS = {
  High:        '#e74c3c',
  Medium:      '#e67e22',
  Low:         '#27ae60',
  Pending:     '#e74c3c',
  'In Progress':'#e67e22',
  Resolved:    '#27ae60',
  Archived:    '#95a5a6',
  Garbage:     '#8e44ad',
  'Road Damage':'#2980b9',
  Drainage:    '#16a085',
  'Water Leakage':'#2471a3',
  Streetlight: '#f39c12',
  Other:       '#7f8c8d',
};

function getColor(label) {
  return CHART_COLORS[label] || '#3498db';
}

function initDashboardCharts(statsUrl) {
  fetch(statsUrl)
    .then(r => r.json())
    .then(data => {
      renderDoughnut('chart-status',   data.by_status,   'Complaints by Status');
      renderBar      ('chart-category', data.by_category, 'Complaints by Category');
      renderLine     ('chart-date',     data.by_date,     'Submissions (last 30 days)');
      renderHBar     ('chart-priority', data.by_priority, 'Complaints by Priority');
    })
    .catch(err => console.error('Failed to load chart data:', err));
}

function renderDoughnut(canvasId, dataObj, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj);
  new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data: values,
        backgroundColor: labels.map(getColor),
        borderWidth: 2,
        borderColor: '#fff',
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { position: 'bottom', labels: { font: { size: 12 } } },
        title:  { display: true, text: label, font: { size: 14, weight: '600' } },
      },
    },
  });
}

function renderBar(canvasId, dataObj, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj);
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Complaints',
        data: values,
        backgroundColor: labels.map(getColor),
        borderRadius: 5,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title:  { display: true, text: label, font: { size: 14, weight: '600' } },
      },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
}

function renderLine(canvasId, dataObj, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj);
  new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [{
        label: 'Submissions',
        data: values,
        borderColor: '#1a5276',
        backgroundColor: 'rgba(26,82,118,0.12)',
        borderWidth: 2,
        pointRadius: 3,
        fill: true,
        tension: 0.3,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        title:  { display: true, text: label, font: { size: 14, weight: '600' } },
      },
      scales: { y: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
}

function renderHBar(canvasId, dataObj, label) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const labels = Object.keys(dataObj);
  const values = Object.values(dataObj);
  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Complaints',
        data: values,
        backgroundColor: labels.map(getColor),
        borderRadius: 5,
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      plugins: {
        legend: { display: false },
        title:  { display: true, text: label, font: { size: 14, weight: '600' } },
      },
      scales: { x: { beginAtZero: true, ticks: { stepSize: 1 } } },
    },
  });
}
