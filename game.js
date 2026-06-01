let gold = 50;
let goldEarned = 0;
let goldPerSecond = 0;
let totalDefense = 0;
let kingdomLevel = 0;
let raidsStarted = false;
let invasionCount = 0;
let invasionTimer = 0;
let currentInvasion = null;
let lastVictory = null;
let recruitPool = [];
let poolTimer = 0;
let nextRecruitId = 0;
let confirmingReset = false;
let buyQuantity = 1;
let autoRecruitRarity = null;

const rarityOrder = ['common', 'rare', 'epic', 'legendary'];

const POOL_SIZE = 5;
const POOL_REFRESH_INTERVAL = 10;

const RAID_INTERVAL = 300;
const RAID_TRIGGER_LEVEL = 2;
const RAID_TRIGGER_GOLD = 12000;
const INVASION_NAMES = ['Goblin Raid', 'Orc Warband', 'Bandit Horde', 'Dark Army', 'Dragon Siege'];

function getInvasionName(count) {
    if (count < INVASION_NAMES.length) return INVASION_NAMES[count];
    return `Dragon Siege (Wave ${count - INVASION_NAMES.length + 2})`;
}

function getRequiredDefense(count) {
    return Math.floor(500 * Math.pow(1.5, count));
}

function getInvasionLoot(count) {
    return Math.floor(4000 * Math.pow(1.3, count));
}

function formatTimer(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
}

const levels = [
    {
        name: 'Hamlet',
        cost: 0,
        unlocks: ['cottage'],
        caps: { cottage: 10, tavern: 0, smithy: 0, library: 0, barracks: 0, workshop: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Village',
        cost: 500,
        unlocks: ['tavern', 'barracks'],
        caps: { cottage: 25, tavern: 8, smithy: 0, library: 0, barracks: 1, workshop: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Town',
        cost: 5000,
        unlocks: ['smithy'],
        caps: { cottage: 50, tavern: 20, smithy: 8, library: 0, barracks: 5, workshop: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'City',
        cost: 35000,
        unlocks: ['library'],
        caps: { cottage: 75, tavern: 35, smithy: 20, library: 8, barracks: 8, workshop: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Kingdom',
        cost: 200000,
        unlocks: [],
        caps: { cottage: 100, tavern: 60, smithy: 35, library: 20, barracks: 12, workshop: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Empire',
        cost: 1000000,
        unlocks: ['workshop', 'keep'],
        caps: { cottage: 150, tavern: 90, smithy: 55, library: 30, barracks: 18, workshop: 8, tower: 0, cathedral: 0, keep: 3 }
    },
    {
        name: 'Dynasty',
        cost: 8000000,
        unlocks: ['tower'],
        caps: { cottage: 200, tavern: 120, smithy: 75, library: 50, barracks: 25, workshop: 15, tower: 6, cathedral: 0, keep: 6 }
    },
    {
        name: 'Realm',
        cost: 60000000,
        unlocks: ['cathedral'],
        caps: { cottage: 250, tavern: 160, smithy: 100, library: 70, barracks: 35, workshop: 25, tower: 12, cathedral: 5, keep: 10 }
    }
];

const buildings = {
    cottage:  { name: 'Cottage',  cost: 10,    count: 0, slotsPerBuilding: 3, type: 'gold',    residents: [] },
    tavern:   { name: 'Tavern',   cost: 300,   count: 0, slotsPerBuilding: 4, type: 'gold',    residents: [] },
    smithy:   { name: 'Smithy',   cost: 2500,  count: 0, slotsPerBuilding: 3, type: 'gold',    residents: [] },
    library:  { name: 'Library',  cost: 15000, count: 0, slotsPerBuilding: 5, type: 'gold',    residents: [] },
    barracks: { name: 'Barracks', cost: 400,    count: 0, slotsPerBuilding: 4, type: 'defense', residents: [] },
    keep:     { name: 'Keep',     cost: 500000, count: 0, slotsPerBuilding: 3, type: 'defense', residents: [] },
    workshop: { name: "Alchemist's Workshop", cost: 80000,    count: 0, slotsPerBuilding: 4, type: 'gold',    residents: [] },
    tower:    { name: "Wizard's Tower",       cost: 600000,   count: 0, slotsPerBuilding: 3, type: 'gold',    residents: [] },
    cathedral:{ name: 'Cathedral',            cost: 5000000,  count: 0, slotsPerBuilding: 5, type: 'gold',    residents: [] }
};

const rarityTiers = {
    common:    { name: 'Common',    color: '#888888', costMult: 1,  incomeMult: 1   },
    rare:      { name: 'Rare',      color: '#4488ff', costMult: 3,  incomeMult: 2.5 },
    epic:      { name: 'Epic',      color: '#aa44ff', costMult: 8,  incomeMult: 5   },
    legendary: { name: 'Legendary', color: '#ffaa00', costMult: 20, incomeMult: 10  }
};

const recruitTypes = {
    villager:     { name: 'Villager',     buildingId: 'cottage',  baseCost: 25,   incomeMin: 1,  incomeMax: 5   },
    tavernkeeper: { name: 'Tavernkeeper', buildingId: 'tavern',   baseCost: 120,  incomeMin: 5,  incomeMax: 12  },
    blacksmith:   { name: 'Blacksmith',   buildingId: 'smithy',   baseCost: 700,  incomeMin: 15, incomeMax: 40  },
    scholar:      { name: 'Scholar',      buildingId: 'library',  baseCost: 3500, incomeMin: 50, incomeMax: 130 },
    guard:        { name: 'Guard',        buildingId: 'barracks',  baseCost: 200,     incomeMin: 10,   incomeMax: 30   },
    knight:       { name: 'Knight',       buildingId: 'keep',      baseCost: 5000,    incomeMin: 50,   incomeMax: 120  },
    alchemist:    { name: 'Alchemist',    buildingId: 'workshop',  baseCost: 25000,   incomeMin: 150,  incomeMax: 350  },
    mage:         { name: 'Mage',         buildingId: 'tower',     baseCost: 150000,  incomeMin: 400,  incomeMax: 900  },
    priest:       { name: 'High Priest',  buildingId: 'cathedral', baseCost: 1000000, incomeMin: 1000, incomeMax: 2500 }
};

const buildingToTypeId = {
    cottage: 'villager', tavern: 'tavernkeeper', smithy: 'blacksmith',
    library: 'scholar',  barracks: 'guard',
    workshop: 'alchemist', tower: 'mage', cathedral: 'priest', keep: 'knight'
};

function getBuildingCap(id) {
    return levels[kingdomLevel].caps[id];
}

function setBuyQuantity(qty) {
    buyQuantity = qty;
    updateUI();
}

function bulkBuildingCost(id, n) {
    const b = buildings[id];
    return Math.floor(b.cost * (Math.pow(1.15, n) - 1) / 0.15);
}

function maxAffordableBuildings(id) {
    const b = buildings[id];
    const cap = getBuildingCap(id);
    const remaining = cap - b.count;
    if (remaining <= 0 || b.cost > gold) return 0;
    const maxByGold = Math.floor(Math.log(gold * 0.15 / b.cost + 1) / Math.log(1.15));
    return Math.min(maxByGold, remaining);
}

function getRarityWeights() {
    const table = [
        [{ r: 'common', w: 85 }, { r: 'rare', w: 15 }],
        [{ r: 'common', w: 75 }, { r: 'rare', w: 25 }],
        [{ r: 'common', w: 60 }, { r: 'rare', w: 30 }, { r: 'epic', w: 10 }],
        [{ r: 'common', w: 45 }, { r: 'rare', w: 35 }, { r: 'epic', w: 15 }, { r: 'legendary', w: 5 }],
        [{ r: 'common', w: 30 }, { r: 'rare', w: 35 }, { r: 'epic', w: 25 }, { r: 'legendary', w: 10 }],
        [{ r: 'common', w: 20 }, { r: 'rare', w: 30 }, { r: 'epic', w: 35 }, { r: 'legendary', w: 15 }],
        [{ r: 'common', w: 15 }, { r: 'rare', w: 25 }, { r: 'epic', w: 40 }, { r: 'legendary', w: 20 }],
        [{ r: 'common', w: 10 }, { r: 'rare', w: 20 }, { r: 'epic', w: 40 }, { r: 'legendary', w: 30 }]
    ];
    return table[Math.min(kingdomLevel, table.length - 1)];
}

function rollRarity() {
    const weights = getRarityWeights();
    const total = weights.reduce((sum, w) => sum + w.w, 0);
    let roll = Math.random() * total;
    for (const { r, w } of weights) {
        roll -= w;
        if (roll <= 0) return r;
    }
    return 'common';
}

function generateRecruit() {
    const availableTypeIds = Object.keys(recruitTypes).filter(typeId =>
        getBuildingCap(recruitTypes[typeId].buildingId) > 0
    );
    if (availableTypeIds.length === 0) return null;

    const typeId = availableTypeIds[Math.floor(Math.random() * availableTypeIds.length)];
    const type = recruitTypes[typeId];
    const rarity = rollRarity();
    const tier = rarityTiers[rarity];

    const baseIncome = type.incomeMin + Math.floor(Math.random() * (type.incomeMax - type.incomeMin + 1));
    const income = Math.max(1, Math.floor(baseIncome * tier.incomeMult));
    const cost = Math.floor(type.baseCost * tier.costMult);

    return { id: nextRecruitId++, typeId, buildingId: type.buildingId, name: type.name, rarity, income, cost };
}

function refreshPool() {
    recruitPool = [];
    for (let i = 0; i < POOL_SIZE; i++) {
        const r = generateRecruit();
        if (r) recruitPool.push(r);
    }
    autoRecruit();
}

function setAutoRecruit(rarity) {
    autoRecruitRarity = rarity;
    autoRecruit();
    saveGame();
    updateUI();
}

function autoRecruit() {
    if (!autoRecruitRarity) return;
    const threshold = rarityOrder.indexOf(autoRecruitRarity);
    let anyHired = false;

    for (let i = recruitPool.length - 1; i >= 0; i--) {
        const recruit = recruitPool[i];
        if (rarityOrder.indexOf(recruit.rarity) < threshold) continue;

        const b = buildings[recruit.buildingId];
        const slots = b.count * b.slotsPerBuilding;
        if (getBuildingCap(recruit.buildingId) <= 0) continue;
        if (b.residents.length >= slots) continue;
        if (gold < recruit.cost) continue;

        gold -= recruit.cost;
        recruitPool.splice(i, 1);
        b.residents.push({ typeId: recruit.typeId, name: recruit.name, rarity: recruit.rarity, income: recruit.income });

        if (b.type === 'defense') totalDefense += recruit.income;
        else goldPerSecond += recruit.income;

        anyHired = true;
    }

    if (anyHired) {
        checkRepel();
        saveGame();
    }
}

function hireRecruit(recruitId) {
    const index = recruitPool.findIndex(r => r.id === recruitId);
    if (index === -1) return;
    const recruit = recruitPool[index];

    const b = buildings[recruit.buildingId];
    const slots = b.count * b.slotsPerBuilding;
    if (gold < recruit.cost || b.residents.length >= slots) return;

    gold -= recruit.cost;
    recruitPool.splice(index, 1);
    b.residents.push({ typeId: recruit.typeId, name: recruit.name, rarity: recruit.rarity, income: recruit.income });

    if (b.type === 'defense') {
        totalDefense += recruit.income;
    } else {
        goldPerSecond += recruit.income;
    }

    checkRepel();
    saveGame();
    updateUI();
}

function fireResident(buildingId, index) {
    const b = buildings[buildingId];
    const r = b.residents[index];
    if (b.type === 'defense') {
        totalDefense -= r.income;
    } else {
        goldPerSecond -= r.income;
    }
    b.residents.splice(index, 1);
    saveGame();
    updateUI();
}

function checkRaidTrigger() {
    if (raidsStarted) return;
    if (kingdomLevel >= RAID_TRIGGER_LEVEL && goldEarned >= RAID_TRIGGER_GOLD) {
        raidsStarted = true;
        invasionTimer = RAID_INTERVAL;
    }
}

function startInvasion() {
    currentInvasion = {
        name: getInvasionName(invasionCount),
        defenseRequired: getRequiredDefense(invasionCount),
        loot: getInvasionLoot(invasionCount)
    };
}

function checkRepel() {
    if (currentInvasion && totalDefense >= currentInvasion.defenseRequired) {
        repelInvasion();
    }
}

function repelInvasion() {
    lastVictory = { name: currentInvasion.name, loot: currentInvasion.loot };
    gold += currentInvasion.loot;
    invasionCount++;
    currentInvasion = null;
    invasionTimer = RAID_INTERVAL;
}

function saveGame() {
    const state = {
        gold, goldEarned, kingdomLevel, raidsStarted, invasionCount, invasionTimer, currentInvasion, lastVictory, autoRecruitRarity,
        recruitPool, poolTimer, nextRecruitId,
        buildings: {}
    };
    for (const id in buildings) {
        state.buildings[id] = { cost: buildings[id].cost, count: buildings[id].count, residents: buildings[id].residents };
    }
    localStorage.setItem('idleKingdomSave', JSON.stringify(state));
}

function loadGame() {
    const saved = localStorage.getItem('idleKingdomSave');
    if (!saved) return;
    const state = JSON.parse(saved);

    gold = state.gold ?? 50;
    goldEarned = state.goldEarned ?? 0;
    kingdomLevel = state.kingdomLevel ?? 0;
    raidsStarted = state.raidsStarted ?? false;
    invasionCount = state.invasionCount ?? 0;
    invasionTimer = state.invasionTimer ?? 0;
    currentInvasion = state.currentInvasion ?? null;
    lastVictory = state.lastVictory ?? null;
    autoRecruitRarity = state.autoRecruitRarity ?? null;
    recruitPool = state.recruitPool ?? [];
    poolTimer = state.poolTimer ?? 0;
    nextRecruitId = state.nextRecruitId ?? 0;

    for (const id in (state.buildings || {})) {
        if (!buildings[id]) continue;
        buildings[id].cost = state.buildings[id].cost;
        buildings[id].count = state.buildings[id].count;
        buildings[id].residents = (state.buildings[id].residents || []).map(r => ({
            income: r.income,
            rarity: r.rarity || 'common',
            typeId: r.typeId || buildingToTypeId[id] || 'villager',
            name: r.name || (recruitTypes[buildingToTypeId[id]] || {}).name || 'Resident'
        }));
    }

    goldPerSecond = 0;
    totalDefense = 0;
    for (const id in buildings) {
        for (const r of buildings[id].residents) {
            if (buildings[id].type === 'defense') totalDefense += r.income;
            else goldPerSecond += r.income;
        }
    }
}

function showResetConfirm() {
    confirmingReset = true;
    updateUI();
}

function cancelReset() {
    confirmingReset = false;
    updateUI();
}

function doResetGame() {
    localStorage.removeItem('idleKingdomSave');
    location.reload();
}

function tick() {
    const income = currentInvasion ? goldPerSecond * 0.25 : goldPerSecond;
    gold += income;
    goldEarned += goldPerSecond;

    poolTimer++;
    if (poolTimer >= POOL_REFRESH_INTERVAL) {
        poolTimer = 0;
        refreshPool();
    }

    checkRaidTrigger();
    if (raidsStarted) {
        if (currentInvasion) {
            checkRepel();
        } else {
            invasionTimer--;
            if (invasionTimer <= 0) startInvasion();
        }
    }

    saveGame();
    updateUI();
}

function levelUpKingdom() {
    const next = levels[kingdomLevel + 1];
    if (!next || gold < next.cost) return;
    gold -= next.cost;
    kingdomLevel += 1;
    saveGame();
    updateUI();
}

function buyBuilding(id) {
    const b = buildings[id];
    const cap = getBuildingCap(id);
    const n = buyQuantity === 'max' ? maxAffordableBuildings(id) : buyQuantity;
    const affordable = Math.min(n, cap - b.count);
    if (affordable <= 0) return;
    const totalCost = bulkBuildingCost(id, affordable);
    if (gold < totalCost) return;
    gold -= totalCost;
    b.cost = Math.floor(b.cost * Math.pow(1.15, affordable));
    b.count += affordable;
    saveGame();
    updateUI();
}

function renderRecruitPool() {
    const timeUntilRefresh = POOL_REFRESH_INTERVAL - poolTimer;

    const autoOptions = [
        { value: null,        label: 'Off'       },
        { value: 'common',    label: 'Common+'   },
        { value: 'rare',      label: 'Rare+'     },
        { value: 'epic',      label: 'Epic+'     },
        { value: 'legendary', label: 'Legendary' }
    ];

    let html = `<div class="pool-header">
        <span class="pool-timer">New arrivals in ${timeUntilRefresh}s</span>
        <div class="auto-recruit">
            <span class="auto-recruit-label">Auto-hire:</span>
            ${autoOptions.map(({ value, label }) => {
                const active = autoRecruitRarity === value;
                const arg = value === null ? 'null' : `'${value}'`;
                const rarityClass = value ? `btn-auto--${value}` : '';
                return `<button class="btn-auto ${rarityClass} ${active ? 'btn-auto--active' : ''}" onclick="setAutoRecruit(${arg})">${label}</button>`;
            }).join('')}
        </div>
    </div><div class="pool-cards">`;

    if (recruitPool.length === 0) {
        html += `<div class="pool-empty">No one seeking work right now.</div>`;
    } else {
        recruitPool.forEach(recruit => {
            const b = buildings[recruit.buildingId];
            const slots = b.count * b.slotsPerBuilding;
            const hasSlot = b.residents.length < slots;
            const canAfford = gold >= recruit.cost;
            const buildingUnlocked = getBuildingCap(recruit.buildingId) > 0;
            const canHire = canAfford && hasSlot && buildingUnlocked;
            const isDefense = b.type === 'defense';
            const type = recruitTypes[recruit.typeId];
            const tier = rarityTiers[recruit.rarity];
            const minVal = Math.max(1, Math.floor(type.incomeMin * tier.incomeMult));
            const maxVal = Math.floor(type.incomeMax * tier.incomeMult);
            const valueLabel = isDefense ? `${minVal}-${maxVal} def` : `${minVal}-${maxVal} g/s`;
            const rarityInfo = rarityTiers[recruit.rarity];
            const letter = recruit.name[0].toUpperCase();

            let hint = '';
            if (!buildingUnlocked) hint = `Needs ${b.name}`;
            else if (!hasSlot) hint = `No open slots`;

            html += `<div class="recruit-card recruit-card--${recruit.rarity}">
                <div class="portrait portrait--${recruit.rarity}" data-type="${recruit.typeId}">
                    <span class="portrait-letter">${letter}</span>
                </div>
                <div class="recruit-info">
                    <div class="recruit-name">${recruit.name}</div>
                    <div class="recruit-rarity" style="color:${rarityInfo.color}">${rarityInfo.name}</div>
                    <div class="recruit-stat">${valueLabel}</div>
                    ${hint ? `<div class="recruit-hint">${hint}</div>` : ''}
                </div>
                <div class="recruit-action">
                    <div class="recruit-cost">${recruit.cost.toLocaleString()}g</div>
                    <button class="btn-hire-recruit" onclick="hireRecruit(${recruit.id})" ${canHire ? '' : 'disabled'}>Hire</button>
                </div>
            </div>`;
        });
    }

    html += `</div>`;
    document.getElementById('recruit-pool').innerHTML = html;
}

function renderBuildings() {
    const qtys = [1, 5, 10, 'max'];
    let html = `<div class="buy-mode">
        <span class="buy-mode-label">Buy:</span>
        ${qtys.map(q => `<button class="btn-qty ${buyQuantity === q ? 'btn-qty--active' : ''}" onclick="setBuyQuantity(${q === 'max' ? "'max'" : q})">×${q}</button>`).join('')}
    </div>`;

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
        const totalSlots = b.count * b.slotsPerBuilding;
        const n = buyQuantity === 'max' ? maxAffordableBuildings(id) : Math.min(buyQuantity, cap - b.count);
        const totalCost = n > 0 ? bulkBuildingCost(id, n) : 0;
        const canAffordBuilding = n > 0 && gold >= totalCost;
        const costLabel = buyQuantity === 'max'
            ? (n > 0 ? `${totalCost.toLocaleString()} gold (×${n})` : 'At cap')
            : buyQuantity === 1
            ? `${b.cost.toLocaleString()} gold`
            : `${totalCost.toLocaleString()} gold (×${n})`;

        html += `<div class="building-card ${isDefense ? 'building-card--defense' : ''}">
            <button class="btn-building" onclick="buyBuilding('${id}')" ${canAffordBuilding ? '' : 'disabled'}>
                <span class="building-name">${b.name}</span>
                <span class="building-meta">
                    <span class="building-cost">Cost: ${costLabel}</span>
                    <span class="building-desc">Adds ${b.slotsPerBuilding} resident slots</span>
                </span>
                <span class="building-owned">${b.count} / ${cap}</span>
            </button>`;

        if (b.count > 0) {
            html += `<div class="slot-grid">`;

            b.residents.forEach((r, i) => {
                const letter = r.name ? r.name[0].toUpperCase() : '?';
                const valueLabel = isDefense ? `${r.income} def` : `${r.income} g/s`;
                const rarityInfo = rarityTiers[r.rarity] || rarityTiers.common;
                html += `<div class="portrait portrait--${r.rarity || 'common'}" data-type="${r.typeId || 'villager'}"
                    title="${r.name} (${rarityInfo.name}) — ${valueLabel}&#10;Click to dismiss"
                    onclick="fireResident('${id}', ${i})">
                    <span class="portrait-letter">${letter}</span>
                    <span class="portrait-stat">${r.income}</span>
                </div>`;
            });

            for (let i = b.residents.length; i < totalSlots; i++) {
                html += `<div class="portrait portrait--empty" title="Empty slot">
                    <span class="portrait-letter">·</span>
                </div>`;
            }

            html += `</div>`;
        }

        html += `</div>`;
    }
    document.getElementById('building-list').innerHTML = html;
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
    } else if (raidsStarted) {
        const nextName = getInvasionName(invasionCount);
        const nextDefense = getRequiredDefense(invasionCount);
        html += `<div class="panel-section">
            <div class="panel-label">Next Raid</div>
            <div class="invasion-name invasion-name--warning">${nextName}</div>
            <div class="invasion-preview">Needs ${nextDefense.toLocaleString()} defense</div>
            <div class="invasion-timer">Arrives in ${formatTimer(invasionTimer)}</div>
        </div>`;
        if (lastVictory) {
            html += `<div class="victory-inline">
                Last: ${lastVictory.name} +${lastVictory.loot.toLocaleString()}g
            </div>`;
        }
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

    if (confirmingReset) {
        html += `<div class="panel-section">
            <div class="panel-label" style="color:#8a4040">Reset all progress?</div>
            <div class="reset-confirm-buttons">
                <button class="btn-reset btn-reset--confirm" onclick="doResetGame()">Yes, reset</button>
                <button class="btn-reset" onclick="cancelReset()">Cancel</button>
            </div>
        </div>`;
    } else {
        html += `<div class="panel-section">
            <button class="btn-reset" onclick="showResetConfirm()">Reset game</button>
        </div>`;
    }

    document.getElementById('left-panel-dynamic').innerHTML = html;
}

function updateUI() {
    document.getElementById('gold-display').textContent = Math.floor(gold).toLocaleString();

    const actualGps = currentInvasion ? Math.floor(goldPerSecond * 0.25) : goldPerSecond;
    document.getElementById('gps-display').textContent = actualGps.toLocaleString();
    document.getElementById('siege-indicator').textContent = currentInvasion ? ' (siege)' : '';

    renderLeftPanel();
    renderRecruitPool();
    renderBuildings();
}

loadGame();
if (recruitPool.length === 0) refreshPool();
updateUI();
setInterval(tick, 1000);
