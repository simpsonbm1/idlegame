let gold = 50;
let goldEarned = 0;
let goldPerSecond = 0;
let totalDefense = 0;
let kingdomLevel = 0;
let invasionIndex = 0;
let currentInvasion = null;
let lastVictory = null;

const invasions = [
    {
        name: 'Goblin Raid',
        triggerLevel: 2,
        triggerGoldEarned: 12000,
        defenseRequired: 500,
        loot: 4000
    },
    {
        name: 'Orc Warband',
        triggerLevel: 4,
        triggerGoldEarned: 150000,
        defenseRequired: 2000,
        loot: 40000
    }
];

const levels = [
    {
        name: 'Hamlet',
        cost: 0,
        unlocks: ['cottage'],
        caps: { cottage: 10, tavern: 0, smithy: 0, library: 0, barracks: 0 }
    },
    {
        name: 'Village',
        cost: 500,
        unlocks: ['tavern', 'barracks'],
        caps: { cottage: 25, tavern: 8, smithy: 0, library: 0, barracks: 1 }
    },
    {
        name: 'Town',
        cost: 5000,
        unlocks: ['smithy'],
        caps: { cottage: 50, tavern: 20, smithy: 8, library: 0, barracks: 5 }
    },
    {
        name: 'City',
        cost: 35000,
        unlocks: ['library'],
        caps: { cottage: 75, tavern: 35, smithy: 20, library: 8, barracks: 8 }
    },
    {
        name: 'Kingdom',
        cost: 200000,
        unlocks: [],
        caps: { cottage: 100, tavern: 60, smithy: 35, library: 20, barracks: 12 }
    }
];

const buildings = {
    cottage: {
        name: 'Cottage', cost: 10, count: 0, slotsPerBuilding: 3,
        residentName: 'Villager', hireCost: 25,
        incomeMin: 1, incomeMax: 5, luckyChance: 0.10, luckyMin: 8, luckyMax: 15,
        residents: [], type: 'gold'
    },
    tavern: {
        name: 'Tavern', cost: 300, count: 0, slotsPerBuilding: 4,
        residentName: 'Tavernkeeper', hireCost: 120,
        incomeMin: 5, incomeMax: 12, luckyChance: 0.10, luckyMin: 20, luckyMax: 35,
        residents: [], type: 'gold'
    },
    smithy: {
        name: 'Smithy', cost: 2500, count: 0, slotsPerBuilding: 3,
        residentName: 'Blacksmith', hireCost: 700,
        incomeMin: 15, incomeMax: 40, luckyChance: 0.10, luckyMin: 70, luckyMax: 120,
        residents: [], type: 'gold'
    },
    library: {
        name: 'Library', cost: 15000, count: 0, slotsPerBuilding: 5,
        residentName: 'Scholar', hireCost: 3500,
        incomeMin: 50, incomeMax: 130, luckyChance: 0.10, luckyMin: 220, luckyMax: 380,
        residents: [], type: 'gold'
    },
    barracks: {
        name: 'Barracks', cost: 400, count: 0, slotsPerBuilding: 4,
        residentName: 'Guard', hireCost: 200,
        incomeMin: 10, incomeMax: 30, luckyChance: 0.10, luckyMin: 60, luckyMax: 100,
        residents: [], type: 'defense'
    }
};

function getBuildingCap(id) {
    return levels[kingdomLevel].caps[id];
}

function rollIncome(b) {
    if (Math.random() < b.luckyChance) {
        return {
            income: b.luckyMin + Math.floor(Math.random() * (b.luckyMax - b.luckyMin + 1)),
            lucky: true
        };
    }
    return {
        income: b.incomeMin + Math.floor(Math.random() * (b.incomeMax - b.incomeMin + 1)),
        lucky: false
    };
}

function checkInvasion() {
    if (currentInvasion !== null) {
        if (totalDefense >= currentInvasion.defenseRequired) {
            repelInvasion();
        }
        return;
    }
    if (invasionIndex >= invasions.length) return;
    const next = invasions[invasionIndex];
    if (kingdomLevel >= next.triggerLevel && goldEarned >= next.triggerGoldEarned) {
        currentInvasion = invasions[invasionIndex];
        invasionIndex++;
    }
}

function repelInvasion() {
    lastVictory = { name: currentInvasion.name, loot: currentInvasion.loot };
    gold += currentInvasion.loot;
    currentInvasion = null;
}

function tick() {
    const income = currentInvasion ? goldPerSecond * 0.25 : goldPerSecond;
    gold += income;
    goldEarned += goldPerSecond;
    checkInvasion();
    updateUI();
}

function levelUpKingdom() {
    const next = levels[kingdomLevel + 1];
    if (!next || gold < next.cost) return;
    gold -= next.cost;
    kingdomLevel += 1;
    updateUI();
}

function buyBuilding(id) {
    const b = buildings[id];
    const cap = getBuildingCap(id);
    if (gold < b.cost || b.count >= cap) return;
    gold -= b.cost;
    b.count += 1;
    b.cost = Math.floor(b.cost * 1.15);
    updateUI();
}

function hireResident(id) {
    const b = buildings[id];
    const slots = b.count * b.slotsPerBuilding;
    if (gold < b.hireCost || b.residents.length >= slots) return;
    gold -= b.hireCost;
    const result = rollIncome(b);
    b.residents.push(result);
    if (b.type === 'defense') {
        totalDefense += result.income;
    } else {
        goldPerSecond += result.income;
    }
    checkInvasion();
    updateUI();
}

function fireResident(id, index) {
    const b = buildings[id];
    const r = b.residents[index];
    if (b.type === 'defense') {
        totalDefense -= r.income;
    } else {
        goldPerSecond -= r.income;
    }
    b.residents.splice(index, 1);
    updateUI();
}

function renderLeftPanel() {
    let html = '';

    if (getBuildingCap('barracks') > 0 || totalDefense > 0) {
        html += `<div class="panel-section">
            <div class="panel-label">Defense Power</div>
            <div class="stat-value">${totalDefense.toLocaleString()}</div>
        </div>`;
    }

    if (currentInvasion) {
        html += `<div class="panel-section invasion-panel">
            <div class="panel-label">Under Siege</div>
            <div class="invasion-name">${currentInvasion.name}</div>
            <div class="invasion-progress">${totalDefense.toLocaleString()} / ${currentInvasion.defenseRequired.toLocaleString()} defense</div>
            <div class="invasion-note">Income reduced to 25%</div>
        </div>`;
    } else if (lastVictory) {
        html += `<div class="panel-section">
            <div class="panel-label">Last Victory</div>
            <div class="victory-name">${lastVictory.name}</div>
            <div class="victory-loot">+${lastVictory.loot.toLocaleString()} gold looted</div>
        </div>`;
    }

    const current = levels[kingdomLevel];
    const next = levels[kingdomLevel + 1];

    html += `<div class="panel-section">
        <div class="panel-label">Kingdom</div>
        <div class="kingdom-name">${current.name}</div>`;

    if (next) {
        const canAfford = gold >= next.cost;
        const unlockNames = next.unlocks.map(id => buildings[id].name).join(', ');
        html += `<div class="levelup-block">
            <div class="levelup-cost">Level up: ${next.cost.toLocaleString()} gold</div>
            ${unlockNames ? `<div class="levelup-unlocks">Unlocks: ${unlockNames}</div>` : ''}
            <button class="btn-levelup" onclick="levelUpKingdom()" ${canAfford ? '' : 'disabled'}>
                Become a ${next.name}
            </button>
        </div>`;
    } else {
        html += `<div class="kingdom-maxed">Maximum level reached</div>`;
    }

    html += `</div>`;

    document.getElementById('left-panel-dynamic').innerHTML = html;
}

function renderBuildings() {
    let html = '';
    for (const id in buildings) {
        const b = buildings[id];
        const cap = getBuildingCap(id);
        const isUnlocked = cap > 0;

        if (!isUnlocked) {
            const unlocksAtLevel = levels.find(l => l.caps[id] > 0);
            html += `<div class="building-card">
                <div class="btn-building btn-building--locked">
                    <span class="building-name">${b.name}</span>
                    <span class="building-locked-hint">Unlocks at ${unlocksAtLevel ? unlocksAtLevel.name : '???'}</span>
                </div>
            </div>`;
            continue;
        }

        const isDefense = b.type === 'defense';
        const atCap = b.count >= cap;
        const canAffordBuilding = gold >= b.cost && !atCap;
        const slots = b.count * b.slotsPerBuilding;
        const canAffordHire = gold >= b.hireCost && b.residents.length < slots;
        const valueLabel = isDefense ? 'defense' : 'gold/sec';

        html += `<div class="building-card ${isDefense ? 'building-card--defense' : ''}">
            <button class="btn-building" onclick="buyBuilding('${id}')" ${canAffordBuilding ? '' : 'disabled'}>
                <span class="building-name">${b.name}</span>
                <span class="building-meta">
                    <span class="building-cost">Cost: ${b.cost.toLocaleString()} gold</span>
                    <span class="building-desc">Adds ${b.slotsPerBuilding} resident slots</span>
                </span>
                <span class="building-owned">${b.count} / ${cap}</span>
            </button>`;

        if (b.count > 0) {
            html += `<div class="building-roster">
                <div class="roster-header">
                    <button class="btn-hire" onclick="hireResident('${id}')" ${canAffordHire ? '' : 'disabled'}>
                        Hire ${b.residentName} — ${b.hireCost.toLocaleString()} gold
                    </button>
                    <span class="slot-count">${b.residents.length} / ${slots} residents</span>
                </div>
                <div class="resident-list">`;

            b.residents.forEach((r, i) => {
                html += `<div class="resident ${isDefense ? 'resident--defense' : ''}">
                    <span class="resident-name">${b.residentName}</span>
                    <span class="resident-income">${r.income} ${valueLabel}</span>
                    ${r.lucky ? '<span class="resident-lucky">&#9733; Lucky</span>' : ''}
                    <button class="btn-fire" onclick="fireResident('${id}', ${i})">Fire</button>
                </div>`;
            });

            html += `</div></div>`;
        }

        html += `</div>`;
    }

    document.getElementById('building-list').innerHTML = html;
}

function updateUI() {
    document.getElementById('gold-display').textContent = Math.floor(gold).toLocaleString();

    const actualGps = currentInvasion ? Math.floor(goldPerSecond * 0.25) : goldPerSecond;
    document.getElementById('gps-display').textContent = actualGps.toLocaleString();
    document.getElementById('siege-indicator').textContent = currentInvasion ? ' (siege)' : '';

    renderLeftPanel();
    renderBuildings();
}

setInterval(tick, 1000);
