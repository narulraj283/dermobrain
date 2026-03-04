/**
 * DermoBrain Cost Comparison Tool
 * Compare procedure costs across different cities
 */
(function() {
    'use strict';

    let procedureData = [];
    let cityData = [];

    async function init() {
        try {
            const [procRes, cityRes] = await Promise.all([
                fetch('/data/procedure_costs.json'),
                fetch('/data/cities.json')
            ]);
            procedureData = await procRes.json();
            cityData = await cityRes.json();
            populateSelect();
        } catch (e) {
            console.error('Failed to load data:', e);
        }
    }

    function populateSelect() {
        const select = document.getElementById('compare-procedure');
        if (!select) return;

        const procedures = [...new Set(procedureData.map(p => p.procedure || p.name))].sort();
        procedures.forEach(proc => {
            const opt = document.createElement('option');
            opt.value = proc;
            opt.textContent = proc;
            select.appendChild(opt);
        });

        select.addEventListener('change', showComparison);
    }

    function showComparison() {
        const proc = document.getElementById('compare-procedure').value;
        const resultsDiv = document.getElementById('comparison-results');
        const tableDiv = document.getElementById('comparison-table');

        if (!proc) {
            resultsDiv.style.display = 'none';
            return;
        }

        const match = procedureData.find(p => (p.procedure || p.name) === proc);
        if (!match) return;

        const avgCost = match.average_cost || match.avg_cost || 500;
        const lowCost = match.low_cost || Math.round(avgCost * 0.6);
        const highCost = match.high_cost || Math.round(avgCost * 1.5);

        // Build comparison table with top cities
        const topCities = cityData.slice(0, 30).sort((a, b) => {
            const modA = a.cost_modifier || a.cost_index || 1.0;
            const modB = b.cost_modifier || b.cost_index || 1.0;
            return modA - modB;
        });

        let tableHTML = `
        <table style="width:100%; border-collapse:collapse; font-size:0.95rem;">
            <thead>
                <tr style="border-bottom:2px solid #1A6B54; text-align:left;">
                    <th style="padding:12px 8px;">City</th>
                    <th style="padding:12px 8px;">Estimated Cost</th>
                    <th style="padding:12px 8px;">Range</th>
                    <th style="padding:12px 8px;">vs National Avg</th>
                </tr>
            </thead>
            <tbody>`;

        topCities.forEach((city, i) => {
            const mod = city.cost_modifier || city.cost_index || 1.0;
            const cityAvg = Math.round(avgCost * mod);
            const cityLow = Math.round(lowCost * mod);
            const cityHigh = Math.round(highCost * mod);
            const diff = Math.round((mod - 1) * 100);
            const diffStr = diff > 0 ? `+${diff}%` : diff < 0 ? `${diff}%` : 'Average';
            const diffColor = diff > 0 ? '#e74c3c' : diff < 0 ? '#27ae60' : '#666';
            const bgColor = i % 2 === 0 ? '#fff' : '#f8f9fa';

            tableHTML += `
                <tr style="background:${bgColor}; border-bottom:1px solid #eee;">
                    <td style="padding:10px 8px; font-weight:500;">${city.name || city.city}, ${city.state}</td>
                    <td style="padding:10px 8px; font-weight:700;">$${cityAvg.toLocaleString()}</td>
                    <td style="padding:10px 8px; color:#666;">$${cityLow.toLocaleString()} - $${cityHigh.toLocaleString()}</td>
                    <td style="padding:10px 8px; color:${diffColor}; font-weight:600;">${diffStr}</td>
                </tr>`;
        });

        tableHTML += '</tbody></table>';
        tableHTML += '<p style="margin-top:12px; color:#999; font-size:0.8rem;">* Costs are estimates based on national averages adjusted by regional cost of living. Actual prices may vary.</p>';

        tableDiv.innerHTML = tableHTML;
        resultsDiv.style.display = 'block';
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
