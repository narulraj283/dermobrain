/**
 * DermoBrain Cost Calculator
 * Interactive tool to estimate dermatology procedure costs
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
            populateSelects();
        } catch (e) {
            console.error('Failed to load cost data:', e);
        }
    }

    function populateSelects() {
        const procSelect = document.getElementById('procedure-select');
        const citySelect = document.getElementById('city-select');
        if (!procSelect || !citySelect) return;

        // Populate procedures
        const procedures = [...new Set(procedureData.map(p => p.procedure || p.name))].sort();
        procedures.forEach(proc => {
            const opt = document.createElement('option');
            opt.value = proc;
            opt.textContent = proc;
            procSelect.appendChild(opt);
        });

        // Populate cities
        const cities = cityData.map(c => `${c.name || c.city}, ${c.state}`).sort();
        const uniqueCities = [...new Set(cities)];
        uniqueCities.forEach(city => {
            const opt = document.createElement('option');
            opt.value = city;
            opt.textContent = city;
            citySelect.appendChild(opt);
        });

        // Event listeners
        procSelect.addEventListener('change', calculate);
        citySelect.addEventListener('change', calculate);
        const insuranceToggle = document.getElementById('insurance-toggle');
        if (insuranceToggle) insuranceToggle.addEventListener('change', calculate);
    }

    function calculate() {
        const proc = document.getElementById('procedure-select').value;
        const cityVal = document.getElementById('city-select').value;
        const hasInsurance = document.getElementById('insurance-toggle').checked;
        const resultDiv = document.getElementById('cost-result');
        const amountDiv = document.getElementById('cost-amount');
        const rangeDiv = document.getElementById('cost-range');

        if (!proc) {
            resultDiv.style.display = 'none';
            return;
        }

        // Find matching procedure data
        const match = procedureData.find(p => (p.procedure || p.name) === proc);
        if (!match) {
            resultDiv.style.display = 'none';
            return;
        }

        let avgCost = match.average_cost || match.avg_cost || 500;
        let lowCost = match.low_cost || Math.round(avgCost * 0.6);
        let highCost = match.high_cost || Math.round(avgCost * 1.5);

        // City cost adjustment
        if (cityVal) {
            const cityName = cityVal.split(',')[0].trim();
            const cityInfo = cityData.find(c => (c.name || c.city) === cityName);
            if (cityInfo) {
                const modifier = cityInfo.cost_modifier || cityInfo.cost_index || 1.0;
                avgCost = Math.round(avgCost * modifier);
                lowCost = Math.round(lowCost * modifier);
                highCost = Math.round(highCost * modifier);
            }
        }

        // Insurance adjustment
        if (hasInsurance) {
            avgCost = Math.round(avgCost * 0.3);
            lowCost = Math.round(lowCost * 0.2);
            highCost = Math.round(highCost * 0.5);
        }

        amountDiv.textContent = `$${avgCost.toLocaleString()}`;
        rangeDiv.textContent = `Range: $${lowCost.toLocaleString()} - $${highCost.toLocaleString()}${hasInsurance ? ' (estimated with insurance copay/coinsurance)' : ' (without insurance)'}`;
        resultDiv.style.display = 'block';
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
