/* ═══════════════════════════════════════════════════════════
   SALES ANALYTICS DASHBOARD — APPLICATION LOGIC
   Loads CSV, computes KPIs, renders Chart.js visualisations
   ═══════════════════════════════════════════════════════════ */

// ── Global State ────────────────────────────────────────────
let rawData = [];
let filteredData = [];
let charts = {};

// ── Chart.js Defaults ───────────────────────────────────────
Chart.defaults.color = '#94a3b8';
Chart.defaults.font.family = "'Inter', sans-serif";
Chart.defaults.font.size = 12;
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.pointStyleWidth = 10;

const COLORS = {
    blue: '#667eea',
    purple: '#764ba2',
    green: '#2ecc71',
    red: '#e74c3c',
    gold: '#f39c12',
    cyan: '#06b6d4',
    pink: '#ec4899',
    orange: '#f97316',
    teal: '#14b8a6',
    indigo: '#6366f1',
};

const REGION_COLORS = {
    'West': COLORS.blue,
    'East': COLORS.green,
    'Central': COLORS.gold,
    'South': COLORS.red,
};

const CATEGORY_COLORS = {
    'Technology': COLORS.blue,
    'Furniture': COLORS.purple,
    'Office Supplies': COLORS.green,
    'Clothing': COLORS.gold,
};

// ── Data Loading ────────────────────────────────────────────
async function loadData() {
    try {
        const response = await fetch('../data/cleaned_sales_data.csv');
        const csvText = await response.text();
        const parsed = Papa.parse(csvText, {
            header: true,
            dynamicTyping: true,
            skipEmptyLines: true,
        });
        rawData = parsed.data;
        filteredData = [...rawData];

        populateFilters();
        updateDashboard();
    } catch (err) {
        console.error('Failed to load CSV:', err);
        document.querySelector('.kpi-sub').textContent = 'Error loading data';
    }
}

// ── Filter Population ───────────────────────────────────────
function populateFilters() {
    const years = [...new Set(rawData.map(d => d.Year))].sort();
    const categories = [...new Set(rawData.map(d => d.Category))].sort();
    const regions = [...new Set(rawData.map(d => d.Region))].sort();
    const segments = [...new Set(rawData.map(d => d.Segment))].sort();

    fillSelect('filter-year', years);
    fillSelect('filter-category', categories);
    fillSelect('filter-region', regions);
    fillSelect('filter-segment', segments);
}

function fillSelect(id, values) {
    const select = document.getElementById(id);
    values.forEach(v => {
        if (v != null && v !== '') {
            const opt = document.createElement('option');
            opt.value = v;
            opt.textContent = v;
            select.appendChild(opt);
        }
    });
}

// ── Filter Logic ────────────────────────────────────────────
function applyFilters() {
    const year = document.getElementById('filter-year').value;
    const category = document.getElementById('filter-category').value;
    const region = document.getElementById('filter-region').value;
    const segment = document.getElementById('filter-segment').value;

    filteredData = rawData.filter(d => {
        if (year !== 'all' && d.Year != year) return false;
        if (category !== 'all' && d.Category !== category) return false;
        if (region !== 'all' && d.Region !== region) return false;
        if (segment !== 'all' && d.Segment !== segment) return false;
        return true;
    });

    updateDashboard();
}

function resetFilters() {
    document.getElementById('filter-year').value = 'all';
    document.getElementById('filter-category').value = 'all';
    document.getElementById('filter-region').value = 'all';
    document.getElementById('filter-segment').value = 'all';
    filteredData = [...rawData];
    updateDashboard();
}

// ── KPI Computation ─────────────────────────────────────────
function formatCurrency(n) {
    if (Math.abs(n) >= 1e6) return '$' + (n / 1e6).toFixed(2) + 'M';
    if (Math.abs(n) >= 1e3) return '$' + (n / 1e3).toFixed(1) + 'K';
    return '$' + n.toFixed(2);
}

function formatNumber(n) {
    return n.toLocaleString('en-US');
}

function updateKPIs() {
    const totalSales = filteredData.reduce((s, d) => s + (d.Sales || 0), 0);
    const totalProfit = filteredData.reduce((s, d) => s + (d.Profit || 0), 0);
    const totalOrders = filteredData.length;
    const avgOrderValue = totalOrders > 0 ? totalSales / totalOrders : 0;
    const profitMargin = totalSales > 0 ? (totalProfit / totalSales) * 100 : 0;

    // Quantities
    const totalQty = filteredData.reduce((s, d) => s + (d.Quantity || 0), 0);

    animateKPI('kpi-sales-value', formatCurrency(totalSales));
    animateKPI('kpi-profit-value', formatCurrency(totalProfit));
    animateKPI('kpi-orders-value', formatNumber(totalOrders));
    animateKPI('kpi-aov-value', formatCurrency(avgOrderValue));
    animateKPI('kpi-margin-value', profitMargin.toFixed(1) + '%');

    document.getElementById('kpi-sales-sub').textContent = `${formatNumber(totalQty)} units sold`;
    document.getElementById('kpi-profit-sub').textContent = profitMargin >= 0 ? '↗ Positive' : '↘ Negative';
    document.getElementById('kpi-orders-sub').textContent = `Avg qty: ${(totalQty / Math.max(totalOrders, 1)).toFixed(1)}`;
    document.getElementById('kpi-aov-sub').textContent = `Per transaction`;
    document.getElementById('kpi-margin-sub').textContent = totalProfit >= 0 ? '✓ Healthy' : '⚠ Loss';
}

function animateKPI(id, value) {
    const el = document.getElementById(id);
    el.style.opacity = 0;
    el.textContent = value;
    requestAnimationFrame(() => {
        el.style.transition = 'opacity 0.4s ease';
        el.style.opacity = 1;
    });
}

// ── Chart Helpers ───────────────────────────────────────────
function groupBy(data, key) {
    const map = {};
    data.forEach(d => {
        const k = d[key];
        if (!map[k]) map[k] = [];
        map[k].push(d);
    });
    return map;
}

function sumField(arr, field) {
    return arr.reduce((s, d) => s + (d[field] || 0), 0);
}

function destroyChart(name) {
    if (charts[name]) {
        charts[name].destroy();
        delete charts[name];
    }
}

// ── Sales Trend Chart ───────────────────────────────────────
function renderSalesTrend() {
    destroyChart('salesTrend');
    const ctx = document.getElementById('salesTrendChart').getContext('2d');

    // Group by Year-Month
    const monthly = {};
    filteredData.forEach(d => {
        const key = d['Order Date']?.substring(0, 7); // YYYY-MM
        if (key) {
            if (!monthly[key]) monthly[key] = { sales: 0, profit: 0 };
            monthly[key].sales += d.Sales || 0;
            monthly[key].profit += d.Profit || 0;
        }
    });

    const labels = Object.keys(monthly).sort();
    const salesValues = labels.map(k => monthly[k].sales);
    const profitValues = labels.map(k => monthly[k].profit);

    // Short labels
    const shortLabels = labels.map(l => {
        const [y, m] = l.split('-');
        const months = ['', 'Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
        return months[parseInt(m)] + ' ' + y.slice(2);
    });

    charts.salesTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels: shortLabels,
            datasets: [
                {
                    label: 'Sales',
                    data: salesValues,
                    borderColor: COLORS.blue,
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2.5,
                    pointRadius: 0,
                    pointHoverRadius: 6,
                    pointHoverBackgroundColor: COLORS.blue,
                },
                {
                    label: 'Profit',
                    data: profitValues,
                    borderColor: COLORS.green,
                    backgroundColor: 'rgba(46, 204, 113, 0.05)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 5,
                    pointHoverBackgroundColor: COLORS.green,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: ctx => ctx.dataset.label + ': ' + formatCurrency(ctx.parsed.y)
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(45,55,72,0.4)' },
                    ticks: { maxTicksLimit: 12 }
                },
                y: {
                    grid: { color: 'rgba(45,55,72,0.4)' },
                    ticks: {
                        callback: v => formatCurrency(v)
                    }
                }
            }
        }
    });
}

// ── Region Donut Chart ──────────────────────────────────────
function renderRegionChart() {
    destroyChart('region');
    const ctx = document.getElementById('regionChart').getContext('2d');

    const grouped = groupBy(filteredData, 'Region');
    const labels = Object.keys(grouped).sort();
    const values = labels.map(k => sumField(grouped[k], 'Sales'));
    const colors = labels.map(k => REGION_COLORS[k] || COLORS.teal);

    charts.region = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors,
                borderColor: '#1a1f2e',
                borderWidth: 3,
                hoverOffset: 8,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 16 }
                },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.parsed / total) * 100).toFixed(1);
                            return `${ctx.label}: ${formatCurrency(ctx.parsed)} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}

// ── Category Bar Chart ──────────────────────────────────────
function renderCategoryChart() {
    destroyChart('category');
    const ctx = document.getElementById('categoryChart').getContext('2d');

    const grouped = groupBy(filteredData, 'Category');
    const labels = Object.keys(grouped).sort();
    const profitValues = labels.map(k => sumField(grouped[k], 'Profit'));
    const salesValues = labels.map(k => sumField(grouped[k], 'Sales'));
    const colors = labels.map(k => CATEGORY_COLORS[k] || COLORS.teal);

    charts.category = new Chart(ctx, {
        type: 'bar',
        data: {
            labels,
            datasets: [
                {
                    label: 'Profit',
                    data: profitValues,
                    backgroundColor: colors.map(c => c + 'cc'),
                    borderColor: colors,
                    borderWidth: 1,
                    borderRadius: 8,
                    borderSkipped: false,
                },
                {
                    label: 'Sales',
                    data: salesValues,
                    backgroundColor: colors.map(c => c + '33'),
                    borderColor: colors.map(c => c + '66'),
                    borderWidth: 1,
                    borderRadius: 8,
                    borderSkipped: false,
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { position: 'top' },
                tooltip: {
                    callbacks: {
                        label: ctx => ctx.dataset.label + ': ' + formatCurrency(ctx.parsed.x)
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(45,55,72,0.4)' },
                    ticks: { callback: v => formatCurrency(v) }
                },
                y: {
                    grid: { display: false }
                }
            }
        }
    });
}

// ── Profit Trend Chart ──────────────────────────────────────
function renderProfitTrend() {
    destroyChart('profitTrend');
    const ctx = document.getElementById('profitTrendChart').getContext('2d');

    const quarterly = {};
    filteredData.forEach(d => {
        const key = d.Year + ' ' + d.Quarter;
        if (key && d.Year) {
            if (!quarterly[key]) quarterly[key] = 0;
            quarterly[key] += d.Profit || 0;
        }
    });

    const labels = Object.keys(quarterly).sort();
    const values = labels.map(k => quarterly[k]);

    const gradient = ctx.createLinearGradient(0, 0, 0, 280);
    gradient.addColorStop(0, 'rgba(46, 204, 113, 0.4)');
    gradient.addColorStop(1, 'rgba(46, 204, 113, 0.02)');

    charts.profitTrend = new Chart(ctx, {
        type: 'line',
        data: {
            labels,
            datasets: [{
                label: 'Quarterly Profit',
                data: values,
                borderColor: COLORS.green,
                backgroundColor: gradient,
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointRadius: 4,
                pointBackgroundColor: COLORS.green,
                pointBorderColor: '#1a1f2e',
                pointBorderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => 'Profit: ' + formatCurrency(ctx.parsed.y)
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(45,55,72,0.4)' },
                    ticks: { maxTicksLimit: 8 }
                },
                y: {
                    grid: { color: 'rgba(45,55,72,0.4)' },
                    ticks: { callback: v => formatCurrency(v) }
                }
            }
        }
    });
}

// ── Sub-Category Horizontal Bar ─────────────────────────────
function renderSubCatChart() {
    destroyChart('subCat');
    const ctx = document.getElementById('subCatChart').getContext('2d');

    const grouped = groupBy(filteredData, 'Sub-Category');
    const entries = Object.entries(grouped)
        .map(([k, v]) => ({ name: k, sales: sumField(v, 'Sales') }))
        .sort((a, b) => b.sales - a.sales)
        .slice(0, 10);

    const palette = [COLORS.blue, COLORS.purple, COLORS.green, COLORS.gold,
        COLORS.red, COLORS.cyan, COLORS.pink, COLORS.orange, COLORS.teal, COLORS.indigo];

    charts.subCat = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: entries.map(e => e.name),
            datasets: [{
                label: 'Sales',
                data: entries.map(e => e.sales),
                backgroundColor: entries.map((_, i) => palette[i] + 'b3'),
                borderColor: entries.map((_, i) => palette[i]),
                borderWidth: 1,
                borderRadius: 6,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: ctx => 'Sales: ' + formatCurrency(ctx.parsed.x)
                    }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(45,55,72,0.4)' },
                    ticks: { callback: v => formatCurrency(v) }
                },
                y: { grid: { display: false } }
            }
        }
    });
}

// ── Ship Mode Pie Chart ─────────────────────────────────────
function renderShipModeChart() {
    destroyChart('shipMode');
    const ctx = document.getElementById('shipModeChart').getContext('2d');

    const grouped = groupBy(filteredData, 'Ship Mode');
    const labels = Object.keys(grouped).sort();
    const values = labels.map(k => grouped[k].length);
    const colors = [COLORS.blue, COLORS.green, COLORS.gold, COLORS.red];

    charts.shipMode = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels,
            datasets: [{
                data: values,
                backgroundColor: colors.map(c => c + '80'),
                borderColor: colors,
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { padding: 16 }
                },
                tooltip: {
                    callbacks: {
                        label: ctx => {
                            const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((ctx.parsed.r / total) * 100).toFixed(1);
                            return `${ctx.label}: ${formatNumber(ctx.parsed.r)} orders (${pct}%)`;
                        }
                    }
                }
            },
            scales: {
                r: {
                    grid: { color: 'rgba(45,55,72,0.4)' },
                    ticks: { display: false }
                }
            }
        }
    });
}

// ── Master Update ───────────────────────────────────────────
function updateDashboard() {
    updateKPIs();
    renderSalesTrend();
    renderRegionChart();
    renderCategoryChart();
    renderProfitTrend();
    renderSubCatChart();
    renderShipModeChart();
}

// ── Event Listeners ─────────────────────────────────────────
document.getElementById('filter-year').addEventListener('change', applyFilters);
document.getElementById('filter-category').addEventListener('change', applyFilters);
document.getElementById('filter-region').addEventListener('change', applyFilters);
document.getElementById('filter-segment').addEventListener('change', applyFilters);
document.getElementById('reset-filters').addEventListener('click', resetFilters);

// ── Boot ────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', loadData);
