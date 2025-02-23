const PRESETS = {
    'zinc_copper': {
        anode: 'Zn',
        cathode: 'Cu',
        conc_anode: '1.0',
        conc_cathode: '1.0',
        moles_reactant: '1.0',
        temperature: '25',
        pressure: '1.0',
        solvent: 'Water',
        catalyst: '',
        ph: '7'
    },
    'silver_lead': {
        anode: 'Pb',
        cathode: 'Ag',
        conc_anode: '0.5',
        conc_cathode: '0.5',
        moles_reactant: '1.0',
        temperature: '25',
        pressure: '1.0',
        solvent: 'Water',
        catalyst: '',
        ph: '7'
    }
};

function loadPreset(presetName) {
    const preset = PRESETS[presetName];
    if (!preset) return;
    
    Object.keys(preset).forEach(key => {
        const element = document.getElementById(key);
        if (element) element.value = preset[key];
    });
}

document.addEventListener('DOMContentLoaded', function() {
    const inputParams = document.getElementById('inputParameters');
    inputParams.style.display = 'none';
});

document.getElementById('startBtn').addEventListener('click', function() {
    const mode = document.getElementById('mode').value;
    const inputParams = document.getElementById('inputParameters');
    
    // Hide results and diagram when starting new calculation
    const results = document.getElementById('results');
    const diagram = document.getElementById('galvanicCellDiagram');
    results.classList.remove('visible');
    diagram.classList.remove('visible');
    
    switch(mode) {
        case '2': // Auto mode
            inputParams.style.display = 'block';
            document.getElementById('conc_anode').value = '1.0';
            document.getElementById('conc_cathode').value = '1.0';
            document.getElementById('moles_reactant').value = '1.0';
            document.getElementById('temperature').value = '25';
            document.getElementById('pressure').value = '1';
            document.getElementById('ph').value = '7';
            break;
        case '3': // Mixed mode
            inputParams.style.display = 'block';
            document.getElementById('temperature').value = '25';
            document.getElementById('pressure').value = '1';
            document.getElementById('ph').value = '7';
            break;
        default: // Manual mode
            inputParams.style.display = 'block';
    }
});

document.getElementById('toggleEnvSettings').addEventListener('click', function() {
    const envSettings = document.getElementById('environmentalSettings');
    if (envSettings.style.display === 'none') {
        envSettings.style.display = 'block';
        this.textContent = 'Hide Environmental Settings';
    } else {
        envSettings.style.display = 'none';
        this.textContent = 'Show Environmental Settings';
    }
});

function validateInput(input, min, max, name) {
    const value = parseFloat(input.value);
    if (isNaN(value) || value < min || value > max) {
        input.setCustomValidity(`${name} must be between ${min} and ${max}`);
        return false;
    }
    input.setCustomValidity('');
    return true;
}

function addTooltip(input, text) {
    const tooltip = document.createElement('div');
    tooltip.className = 'tooltip';
    tooltip.textContent = text;
    input.parentElement.appendChild(tooltip);
}

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    addTooltip(document.getElementById('conc_anode'), 'Enter concentration (0.001 - 10.0 M)');
    addTooltip(document.getElementById('conc_cathode'), 'Enter concentration (0.001 - 10.0 M)');
    addTooltip(document.getElementById('temperature'), 'Enter temperature (0 - 100°C)');
    addTooltip(document.getElementById('pressure'), 'Enter pressure (0.1 - 10.0 atm)');
});

document.getElementById('galvaSimForm').addEventListener('submit', function(event) {
    event.preventDefault();
    
    try {
        // Validate inputs
        const validations = [
            {elem: 'conc_anode', min: 0.001, max: 10, name: 'Anode concentration'},
            {elem: 'conc_cathode', min: 0.001, max: 10, name: 'Cathode concentration'},
            {elem: 'temperature', min: 0, max: 100, name: 'Temperature'},
            {elem: 'pressure', min: 0.1, max: 10, name: 'Pressure'}
        ];

        const isValid = validations.every(v => 
            validateInput(document.getElementById(v.elem), v.min, v.max, v.name)
        );
        
        if (!isValid) {
            throw new Error('Validation failed');
        }

        const mode = document.getElementById('mode').value;
    const anode = document.getElementById('anode').value;
    const cathode = document.getElementById('cathode').value;
    const concAnode = parseFloat(document.getElementById('conc_anode').value);
    const concCathode = parseFloat(document.getElementById('conc_cathode').value);
    const molesReactant = parseFloat(document.getElementById('moles_reactant').value);
    const temperature = parseFloat(document.getElementById('temperature').value);
    const pressure = parseFloat(document.getElementById('pressure').value);
    const solvent = document.getElementById('solvent').value;
    const catalyst = document.getElementById('catalyst').value || null;
    const ph = parseFloat(document.getElementById('ph').value);

    const environment = new EnvironmentSettings(temperature, pressure, solvent, catalyst, ph);
    const params = new SimulationParameters(anode, cathode, concAnode, concCathode, molesReactant, environment);
    const cell = new AdvancedElectrochemicalCell(environment);

    const cellPotential = cell.calculateCellPotential(params);
    const halfReactions = cell.getHalfReactions(anode, cathode);
    const reactionSummary = cell.getReactionSummary(anode, cathode, molesReactant, (molesReactant * concAnode) / concCathode);

    const results = document.getElementById('results');
    results.innerHTML = `
        <p>Calculated Cell Potential: ${cellPotential} V</p>
        <p>Anode Half-Reaction: ${halfReactions[0]}</p>
        <p>Cathode Half-Reaction: ${halfReactions[1]}</p>
        <p>Overall Reaction: ${halfReactions[2]}</p>
        <p>${reactionSummary}</p>
    `;
    
    drawGalvanicCell(anode, cathode, cellPotential);
        
        // Show results and diagram with animation
        results.classList.add('visible');
        document.getElementById('galvanicCellDiagram').classList.add('visible');
    } catch (error) {
        console.error('Simulation error:', error);
        alert('Error during simulation: ' + error.message);
    }
});

class EnvironmentSettings {
    constructor(temperature, pressure, solvent, catalyst, ph) {
        this.temperature = temperature;
        this.pressure = pressure;
        this.solvent = solvent;
        this.catalyst = catalyst;
        this.ph = ph;
    }

    modifyPotential(basePotential) {
        const temperatureK = this.temperature + 273.15;
        const tempFactor = temperatureK / 298.15;
        const pressureFactor = Math.log(this.pressure);
        const phFactor = -0.059 * (this.ph - 7);
        const solventFactors = {
            "Water": 1.0,
            "Methanol": 0.95,
            "Ethanol": 0.90,
            "DMSO": 1.1,
            "Acetonitrile": 1.05
        };
        const solventFactor = solventFactors[this.solvent] || 1.0;
        const catalystBoost = this.catalyst ? 0.05 : 0.0;
        return (basePotential * tempFactor * solventFactor + pressureFactor * 0.01 + phFactor + catalystBoost).toFixed(3);
    }
}

class SimulationParameters {
    constructor(anode, cathode, concAnode, concCathode, molesReactant, environment) {
        this.anode = anode;
        this.cathode = cathode;
        this.concAnode = concAnode;
        this.concCathode = concCathode;
        this.molesReactant = molesReactant;
        this.environment = environment;
    }
}

class AdvancedElectrochemicalCell {
    constructor(environment) {
        this.environment = environment;
    }

    calculateCellPotential(params) {
        try {
            if (!STANDARD_REDUCTION_POTENTIALS[params.anode] || !STANDARD_REDUCTION_POTENTIALS[params.cathode]) {
                throw new Error('Invalid electrode materials');
            }

            const E0_anode = parseFloat(this.environment.modifyPotential(STANDARD_REDUCTION_POTENTIALS[params.anode].potential));
            const E0_cathode = parseFloat(this.environment.modifyPotential(STANDARD_REDUCTION_POTENTIALS[params.cathode].potential));
            const E0_cell = E0_cathode - E0_anode;
            
            const temperatureK = this.environment.temperature + 273.15;
            const F = 96485.3321233100184; // Faraday constant (C/mol)
            const R = 8.31446261815324; // Gas constant (J/K⋅mol)
            const RT_nF = (temperatureK * R) / (2 * F);
            
            if (params.concCathode === 0) {
                throw new Error('Cathode concentration cannot be zero');
            }
            
            const Q = params.concAnode / params.concCathode;
            const result = E0_cell - RT_nF * Math.log(Q);
            return Number(result).toFixed(4);
        } catch (error) {
            console.error('Cell potential calculation error:', error);
            throw error;
        }
    }

    getHalfReactions(anode, cathode) {
        const halfReactionAnode = `${anode}ⁿ⁺ + n e⁻ ⇌ ${anode}`;
        const halfReactionCathode = `${cathode}ᵐ⁺ + m e⁻ ⇌ ${cathode}`;
        const overallReaction = `m ${anode} + n ${cathode}ᵐ⁺ ⇌ n ${cathode} + m ${anode}ⁿ⁺`;
        return [halfReactionAnode, halfReactionCathode, overallReaction];
    }

    getReactionSummary(anode, cathode, molesAnode, molesCathode) {
        return `The overall reaction suggests that ${molesAnode} moles of ${anode} are oxidized and ${molesCathode} moles of ${cathode} ions are reduced, forming ${cathode} metal and ${anode} ions.`;
    }
}

const STANDARD_REDUCTION_POTENTIALS = {
    "Li": { "potential": -3.04 },
    "K": { "potential": -2.93 },
    "Ca": { "potential": -2.87 },
    "Na": { "potential": -2.71 },
    "Mg": { "potential": -2.37 },
    "Al": { "potential": -1.66 },
    "Zn": { "potential": -0.76 },
    "Fe": { "potential": -0.44 },
    "Ni": { "potential": -0.25 },
    "Sn": { "potential": -0.14 },
    "Pb": { "potential": -0.13 },
    "H2": { "potential": 0.00 },
    "Cu": { "potential": 0.34 },
    "Ag": { "potential": 0.80 },
    "Hg": { "potential": 0.85 },
    "Pt": { "potential": 1.20 },
    "Au": { "potential": 1.50 }
};

function drawGalvanicCell(anode, cathode, E_cell) {
    const canvas = document.getElementById('galvanicCellDiagram');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    // Set white stroke and fill
    ctx.strokeStyle = '#ffffff';
    ctx.fillStyle = '#ffffff';
    ctx.lineWidth = 2;
    
    // Draw cell containers
    ctx.beginPath();
    ctx.rect(100, 150, 150, 200);
    ctx.rect(550, 150, 150, 200);
    ctx.stroke();
    
    // Draw electrodes
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(175, 100);
    ctx.lineTo(175, 250);
    ctx.moveTo(625, 100);
    ctx.lineTo(625, 250);
    ctx.stroke();
    
    // Draw salt bridge
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(250, 200);
    ctx.lineTo(550, 200);
    ctx.stroke();
    
    // Add labels with scientific notation
    ctx.font = '16px IBM Plex Mono';
    ctx.fillText(`${anode} | ${anode}${superscript('n+')} (Anode)`, 100, 380);
    ctx.fillText(`${cathode}${superscript('m+')} | ${cathode} (Cathode)`, 550, 380);
    
    // Add potential
    ctx.font = 'bold 18px IBM Plex Mono';
    ctx.fillText(`E°cell = ${E_cell} V`, 350, 150);
    
    // Add electron flow arrow
    drawArrow(ctx, 175, 80, 625, 80);
    ctx.font = '14px IBM Plex Mono';
    ctx.fillText('e⁻', 380, 75);
}

function superscript(text) {
    return text.split('').map(char => 
        '⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻'['0123456789+-'.indexOf(char)] || char
    ).join('');
}

function drawArrow(ctx, x1, y1, x2, y2) {
    const headLength = 15;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.lineTo(x2 - headLength * Math.cos(angle - Math.PI/6), y2 - headLength * Math.sin(angle - Math.PI/6));
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLength * Math.cos(angle + Math.PI/6), y2 - headLength * Math.sin(angle + Math.PI/6));
    ctx.stroke();
}