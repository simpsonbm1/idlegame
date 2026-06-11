let gold = 50;
let goldEarned = 0;
let goldPerSecond = 0;
let kingdomHpRegen = 0;
let kingdomHP = 1000;
let kingdomLevel = 0;
let raidsStarted = false;
let raidTierIndex = 0;
let tierWave = 0;
let raidWinStreak = 0;
let invasionTimer = 0;
let currentInvasion = null;
let lastVictory = null;
let kingdomFallRecord = null;
let recruitPool = [];
let poolTimer = 0;
let nextRecruitId = 0;
let heroSquad = new Array(6).fill(null);
let heroRecruitPool = [];
let heroPoolTimer = 0;
let nextHeroRecruitId = 0;
let confirmingReset = false;
let buyQuantity = 1;
let autoRecruitRarity = null;
const buildingExpanded = {};
let gameSpeed = 1;
let tickInterval = null;
let isDraggingHero = false;
let armedHeroSlot = null;
let armedHeroSlotTime = 0;

const rarityOrder = ['common', 'rare', 'epic', 'legendary'];

const POOL_SIZE = 5;
const POOL_REFRESH_INTERVAL = 10;

const HERO_POOL_SIZE = 3;
const HERO_POOL_REFRESH_INTERVAL = 15;

const KINGDOM_HP_MAX = 1000;
const KINGDOM_DEFENSE = 15;

const ARM_TIMEOUT_MS = 3000;

const RAID_INTERVAL = 20;
const RAID_TRIGGER_LEVEL = 2;
const RAID_TRIGGER_GOLD = 12000;

const BASE_ATTACK_INTERVAL = 2500;
const DEFAULT_BACKLINE_CHANCE = 0.15;

const RAID_TIERS = [
    { minLevel: 2, name: 'Goblin Raid',  powerMult: 1,   defenseGrowth: 1.15, baseLoot: 200000,    lootGrowth: 1.30,
        roster: { brute: 'Goblin Brute',    skirmisher: 'Goblin Skulker',   caster: 'Goblin Slinger',  shaman: 'Goblin Shaman' } },
    { minLevel: 3, name: 'Orc Warband',  powerMult: 1.6, defenseGrowth: 1.15, baseLoot: 1000000,   lootGrowth: 1.30,
        roster: { brute: 'Orc Brute',       skirmisher: 'Orc Berserker',    caster: 'Orc Warcaster',   shaman: 'Orc Witch Doctor' } },
    { minLevel: 4, name: 'Bandit Horde', powerMult: 2.4, defenseGrowth: 1.15, baseLoot: 5000000,   lootGrowth: 1.32,
        roster: { brute: 'Bandit Enforcer', skirmisher: 'Bandit Cutthroat', caster: 'Bandit Marksman', shaman: 'Bandit Medic' } },
    { minLevel: 5, name: 'Dark Army',    powerMult: 3.6, defenseGrowth: 1.15, baseLoot: 25000000,  lootGrowth: 1.34,
        roster: { brute: 'Death Knight',    skirmisher: 'Shadow Reaver',    caster: 'Necromancer',     shaman: 'Bone Priest' } },
    { minLevel: 6, name: 'Dragon Siege', powerMult: 5.5, defenseGrowth: 1.15, baseLoot: 120000000, lootGrowth: 1.36,
        roster: { brute: 'Dragon Guard',    skirmisher: 'Wyrmling',         caster: 'Dragon Mage',     shaman: 'Dragonpriest' } }
];

const ENEMY_ARCHETYPES = {
    brute:      { base: { defense: 20, hp: 120, attack: { power: 14, speed: 0.7 } } },
    skirmisher: { base: { defense: 8,  hp: 70,  attack: { power: 18, speed: 1.1 }, backlineChance: 0.4 } },
    caster:     { base: { defense: 5,  hp: 55,  attack: { power: 20, speed: 0.9 } } },
    shaman:     { base: { defense: 8,  hp: 60,  heal: { power: 15, speed: 0.7 } } }
};

const HERO_ARCHETYPES = {
    guardian: { names: ['Knight', 'Sentinel', 'Vanguard', 'Paragon'],   baseCost: 1000, base: { defense: 35, hp: 140, attack: { power: 8,  speed: 0.7 } } },
    ranged:   { names: ['Archer', 'Sharpshooter', 'Hunter', 'Marksman'], baseCost: 800,  base: { defense: 5,  hp: 60,  attack: { power: 18, speed: 1.3 } } },
    mender:   { names: ['Acolyte', 'Cleric', 'Druid', 'Saint'],          baseCost: 900,  base: { defense: 5,  hp: 55,  heal:   { power: 20, speed: 0.7 } } }
};

function getRaidTierIndex(level) {
    let idx = 0;
    for (let i = 0; i < RAID_TIERS.length; i++) {
        if (level >= RAID_TIERS[i].minLevel) idx = i;
    }
    return idx;
}

function getInvasionName(tierIndex, wave) {
    const tier = RAID_TIERS[tierIndex];
    return wave === 0 ? tier.name : `${tier.name} (Wave ${wave + 1})`;
}

function getInvasionLoot(tierIndex, streak) {
    const tier = RAID_TIERS[tierIndex];
    return Math.floor(tier.baseLoot * Math.pow(tier.lootGrowth, streak));
}

function getFailureLoot(tierIndex) {
    const tier = RAID_TIERS[tierIndex];
    return Math.floor(tier.baseLoot * 0.5);
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
        caps: { cottage: 10, tavern: 0, smithy: 0, library: 0, workshop: 0, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Village',
        cost: 500,
        unlocks: ['tavern', 'workshop'],
        caps: { cottage: 25, tavern: 8, smithy: 0, library: 0, workshop: 1, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Town',
        cost: 5000,
        unlocks: ['smithy'],
        caps: { cottage: 50, tavern: 20, smithy: 8, library: 0, workshop: 5, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'City',
        cost: 35000,
        unlocks: ['library'],
        caps: { cottage: 75, tavern: 35, smithy: 20, library: 8, workshop: 8, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Kingdom',
        cost: 200000,
        unlocks: [],
        caps: { cottage: 100, tavern: 60, smithy: 35, library: 20, workshop: 12, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Empire',
        cost: 1000000,
        unlocks: ['apothecary', 'keep'],
        caps: { cottage: 150, tavern: 90, smithy: 55, library: 30, workshop: 18, apothecary: 8, tower: 0, cathedral: 0, keep: 3 }
    },
    {
        name: 'Dynasty',
        cost: 8000000,
        unlocks: ['tower'],
        caps: { cottage: 200, tavern: 120, smithy: 75, library: 50, workshop: 25, apothecary: 15, tower: 6, cathedral: 0, keep: 6 }
    },
    {
        name: 'Realm',
        cost: 60000000,
        unlocks: ['cathedral'],
        caps: { cottage: 250, tavern: 160, smithy: 100, library: 70, workshop: 35, apothecary: 25, tower: 12, cathedral: 5, keep: 10 }
    }
];

const buildings = {
    cottage:  { name: 'Cottage',  cost: 10,    count: 0, slotsPerBuilding: 3, costGrowth: 1.10, type: 'gold',    residents: [] },
    tavern:   { name: 'Tavern',   cost: 300,   count: 0, slotsPerBuilding: 4, costGrowth: 1.09, type: 'gold',    residents: [] },
    smithy:   { name: 'Smithy',   cost: 2500,  count: 0, slotsPerBuilding: 3, costGrowth: 1.10, type: 'gold',    residents: [] },
    library:  { name: 'Library',  cost: 15000, count: 0, slotsPerBuilding: 5, costGrowth: 1.11, type: 'gold',    residents: [] },
    workshop: { name: 'Workshop', cost: 400,    count: 0, slotsPerBuilding: 4, costGrowth: 1.12, type: 'hpregen', residents: [] },
    keep:     { name: 'Keep',     cost: 500000, count: 0, slotsPerBuilding: 0, costGrowth: 1.16, residents: [] },
    apothecary: { name: 'Apothecary',           cost: 80000,    count: 0, slotsPerBuilding: 8, costGrowth: 1.18, type: 'gold',    residents: [] },
    tower:    { name: "Wizard's Tower",       cost: 600000,   count: 0, slotsPerBuilding: 10, costGrowth: 1.21, type: 'gold',    residents: [] },
    cathedral:{ name: 'Cathedral',            cost: 5000000,  count: 0, slotsPerBuilding: 14, costGrowth: 1.25, type: 'gold',    residents: [] }
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
    builder:      { name: 'Builder',      buildingId: 'workshop',  baseCost: 200,     incomeMin: 0.3,  incomeMax: 1.0  },
    alchemist:    { name: 'Alchemist',    buildingId: 'apothecary',  baseCost: 25000,   incomeMin: 190,  incomeMax: 440  },
    mage:         { name: 'Mage',         buildingId: 'tower',     baseCost: 150000,  incomeMin: 650,  incomeMax: 1450 },
    priest:       { name: 'High Priest',  buildingId: 'cathedral', baseCost: 1000000, incomeMin: 2050, incomeMax: 5150 }
};

const buildingToTypeId = {
    cottage: 'villager', tavern: 'tavernkeeper', smithy: 'blacksmith',
    library: 'scholar',  workshop: 'builder',
    apothecary: 'alchemist', tower: 'mage', cathedral: 'priest'
};

function getBuildingCap(id) {
    return levels[kingdomLevel].caps[id];
}

function setBuyQuantity(qty) {
    buyQuantity = qty;
    updateUI();
}

function toggleBuilding(id) {
    buildingExpanded[id] = !buildingExpanded[id];
    updateUI();
}

function setGameSpeed(speed) {
    gameSpeed = speed;
    clearInterval(tickInterval);
    tickInterval = setInterval(tick, Math.floor(1000 / speed));
    [1, 10, 50, 100].forEach(s => {
        document.getElementById(`speed-${s}`).classList.toggle('btn-speed--active', s === speed);
    });
}

function bulkBuildingCost(id, n) {
    const b = buildings[id];
    const r = b.costGrowth;
    return Math.floor(b.cost * (Math.pow(r, n) - 1) / (r - 1));
}

function maxAffordableBuildings(id) {
    const b = buildings[id];
    const r = b.costGrowth;
    const cap = getBuildingCap(id);
    const remaining = cap - b.count;
    if (remaining <= 0 || b.cost > gold) return 0;
    const maxByGold = Math.floor(Math.log(gold * (r - 1) / b.cost + 1) / Math.log(r));
    return Math.min(maxByGold, remaining);
}

const RARITY_WEIGHT_TABLE = [
    [{ r: 'common', w: 85 }, { r: 'rare', w: 15 }],
    [{ r: 'common', w: 75 }, { r: 'rare', w: 25 }],
    [{ r: 'common', w: 60 }, { r: 'rare', w: 30 }, { r: 'epic', w: 10 }],
    [{ r: 'common', w: 45 }, { r: 'rare', w: 35 }, { r: 'epic', w: 15 }, { r: 'legendary', w: 5 }],
    [{ r: 'common', w: 30 }, { r: 'rare', w: 35 }, { r: 'epic', w: 25 }, { r: 'legendary', w: 10 }],
    [{ r: 'common', w: 20 }, { r: 'rare', w: 30 }, { r: 'epic', w: 35 }, { r: 'legendary', w: 15 }],
    [{ r: 'common', w: 15 }, { r: 'rare', w: 25 }, { r: 'epic', w: 40 }, { r: 'legendary', w: 20 }],
    [{ r: 'common', w: 10 }, { r: 'rare', w: 20 }, { r: 'epic', w: 40 }, { r: 'legendary', w: 30 }]
];

function weightedRarityRoll(weights) {
    const total = weights.reduce((sum, w) => sum + w.w, 0);
    let roll = Math.random() * total;
    for (const { r, w } of weights) {
        roll -= w;
        if (roll <= 0) return r;
    }
    return 'common';
}

function getRarityWeights() {
    return RARITY_WEIGHT_TABLE[Math.min(kingdomLevel, RARITY_WEIGHT_TABLE.length - 1)];
}

function getHeroRarityWeights() {
    return RARITY_WEIGHT_TABLE[Math.min(kingdomLevel + buildings.keep.count, RARITY_WEIGHT_TABLE.length - 1)];
}

function rollRarity() {
    return weightedRarityRoll(getRarityWeights());
}

function rollHeroRarity() {
    return weightedRarityRoll(getHeroRarityWeights());
}

function generateRecruit() {
    const availableTypeIds = Object.keys(recruitTypes).filter(typeId =>
        getBuildingCap(recruitTypes[typeId].buildingId) > 0
    );
    if (availableTypeIds.length === 0) return null;

    const typeId = availableTypeIds[Math.floor(Math.random() * availableTypeIds.length)];
    const type = recruitTypes[typeId];
    const b = buildings[type.buildingId];
    const rarity = rollRarity();
    const tier = rarityTiers[rarity];

    let income;
    if (b.type === 'hpregen') {
        const baseIncome = type.incomeMin + Math.random() * (type.incomeMax - type.incomeMin);
        income = Math.max(0.1, Math.round(baseIncome * tier.incomeMult * 10) / 10);
    } else {
        const baseIncome = type.incomeMin + Math.floor(Math.random() * (type.incomeMax - type.incomeMin + 1));
        income = Math.max(1, Math.floor(baseIncome * tier.incomeMult));
    }
    const cost = Math.floor(type.baseCost * tier.costMult);

    return { id: nextRecruitId++, typeId, buildingId: type.buildingId, name: type.name, rarity, income, cost };
}

function refreshPool() {
    recruitPool = [];
    for (let i = 0; i < POOL_SIZE; i++) {
        const r = generateRecruit();
        if (r) recruitPool.push(r);
    }
    return autoRecruit();
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

        if (b.type === 'hpregen') kingdomHpRegen += recruit.income;
        else goldPerSecond += recruit.income;

        anyHired = true;
    }

    if (anyHired) {
        saveGame();
    }
    return anyHired;
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

    if (b.type === 'hpregen') {
        kingdomHpRegen += recruit.income;
    } else {
        goldPerSecond += recruit.income;
    }

    saveGame();
    updateUI();
}

function fireResident(buildingId, index) {
    const b = buildings[buildingId];
    const r = b.residents[index];
    if (b.type === 'hpregen') {
        kingdomHpRegen -= r.income;
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

// --- Combat engine ---
// A unit's attack and heal are independent actions, each with its own
// power/speed and cooldown, so a unit can attack only, heal only, or do both
// on staggered timers.
function attackAction(power, speed) {
    return { power, speed, cooldown: BASE_ATTACK_INTERVAL / speed };
}
function healAction(power, speed) {
    return { power, speed, cooldown: BASE_ATTACK_INTERVAL / speed };
}

function makeUnit(name, defense, hp, row, col, side, attack = null, heal = null, backlineChance = DEFAULT_BACKLINE_CHANCE) {
    return { name, defense, hp, maxHp: hp, row, col, side, attack, heal, backlineChance, alive: true };
}

function randomFrom(list) {
    return list[Math.floor(Math.random() * list.length)];
}

// Frontline is favored but not absolute — each attacker rolls against its own
// backlineChance to decide which row it goes after.
function pickTarget(attacker, enemySquad) {
    const front = enemySquad.filter(u => u && u.row === 0 && u.alive);
    const back = enemySquad.filter(u => u && u.row === 1 && u.alive);
    if (front.length === 0 && back.length === 0) return null;
    if (front.length === 0) return randomFrom(back);
    if (back.length === 0) return randomFrom(front);

    const wantsBackline = Math.random() < attacker.backlineChance;
    return randomFrom(wantsBackline ? back : front);
}

// Healers always tend to whoever's lowest on HP%, ignoring full-health allies.
function pickHealTarget(friendlySquad) {
    const wounded = friendlySquad.filter(u => u && u.alive && u.hp < u.maxHp);
    if (wounded.length === 0) return null;
    wounded.sort((a, b) => (a.hp / a.maxHp) - (b.hp / b.maxHp));
    return wounded[0];
}

function resolveHeal(healer, target) {
    target.hp = Math.min(target.maxHp, target.hp + healer.heal.power);
}

function resolveAttack(attacker, defender) {
    const dmg = Math.max(1, Math.round(attacker.attack.power * (1 - defender.defense / 100)));
    defender.hp -= dmg;
    if (defender.hp <= 0) {
        defender.hp = 0;
        defender.alive = false;
    }
}

function squadAlive(squad) {
    return squad.some(u => u && u.alive);
}

// Once the hero squad is wiped, nothing stands between the enemy and the
// Kingdom itself — enemies attack Kingdom HP directly until it falls or the
// raid is repelled some other way.
function attackKingdom(attacker) {
    const dmg = Math.max(1, Math.round(attacker.attack.power * (1 - KINGDOM_DEFENSE / 100)));
    kingdomHP = Math.max(0, kingdomHP - dmg);
}

// Advances combat by deltaMs. Each unit's attack and heal cooldowns tick down
// independently.
function combatTick(deltaMs) {
    const enemySide = currentInvasion.enemies;
    for (const unit of [...heroSquad, ...enemySide]) {
        if (!unit || !unit.alive) continue;

        if (unit.attack) {
            unit.attack.cooldown -= deltaMs;
            if (unit.attack.cooldown <= 0) {
                if (unit.side === 'hero') {
                    const target = pickTarget(unit, enemySide);
                    if (target) resolveAttack(unit, target);
                } else if (squadAlive(heroSquad)) {
                    const target = pickTarget(unit, heroSquad);
                    if (target) resolveAttack(unit, target);
                } else {
                    attackKingdom(unit);
                }
                unit.attack.cooldown += BASE_ATTACK_INTERVAL / unit.attack.speed;
            }
        }

        if (unit.heal) {
            unit.heal.cooldown -= deltaMs;
            if (unit.heal.cooldown <= 0) {
                const friendlySquad = unit.side === 'hero' ? heroSquad : enemySide;
                const target = pickHealTarget(friendlySquad);
                if (target) {
                    resolveHeal(unit, target);
                    unit.heal.cooldown += BASE_ATTACK_INTERVAL / unit.heal.speed;
                }
                // Nobody wounded yet — hold the heal ready and check again next tick.
            }
        }
    }
}

// --- Enemy & hero generation ---
function generateEnemy(tierIndex, archetypeKey, row, col, wave) {
    const tier = RAID_TIERS[tierIndex];
    const archetype = ENEMY_ARCHETYPES[archetypeKey];
    const base = archetype.base;
    const mult = tier.powerMult * Math.pow(tier.defenseGrowth, wave);
    const scalePower = v => Math.round(v * mult);
    const scaleHp = v => Math.round(v * Math.sqrt(mult));

    const attack = base.attack ? attackAction(scalePower(base.attack.power), base.attack.speed) : null;
    const heal = base.heal ? healAction(scalePower(base.heal.power), base.heal.speed) : null;
    const backlineChance = base.backlineChance !== undefined ? base.backlineChance : DEFAULT_BACKLINE_CHANCE;

    return makeUnit(tier.roster[archetypeKey], base.defense, scaleHp(base.hp), row, col, 'enemy', attack, heal, backlineChance);
}

function generateHero(archetypeKey, rarity, row, col) {
    const archetype = HERO_ARCHETYPES[archetypeKey];
    const tier = rarityTiers[rarity];
    const rarityIndex = rarityOrder.indexOf(rarity);
    const scalePower = v => Math.round(v * tier.incomeMult);
    const scaleHp = v => Math.round(v * Math.sqrt(tier.incomeMult));

    const base = archetype.base;
    const attack = base.attack ? attackAction(scalePower(base.attack.power), base.attack.speed) : null;
    const heal = base.heal ? healAction(scalePower(base.heal.power), base.heal.speed) : null;

    const unit = makeUnit(archetype.names[rarityIndex], base.defense, scaleHp(base.hp), row, col, 'hero', attack, heal);
    unit.rarity = rarity;
    unit.archetypeKey = archetypeKey;
    return unit;
}

function generateEnemySquad(tierIndex, wave) {
    return [
        generateEnemy(tierIndex, 'brute', 0, 0, wave),
        generateEnemy(tierIndex, 'skirmisher', 0, 1, wave),
        null,
        generateEnemy(tierIndex, 'caster', 1, 0, wave),
        generateEnemy(tierIndex, 'shaman', 1, 1, wave),
        null
    ];
}

// --- Hero recruiting & squad management ---
function generateHeroRecruit() {
    const archetypeKeys = Object.keys(HERO_ARCHETYPES);
    const archetypeKey = archetypeKeys[Math.floor(Math.random() * archetypeKeys.length)];
    const archetype = HERO_ARCHETYPES[archetypeKey];
    const rarity = rollHeroRarity();
    const rarityIndex = rarityOrder.indexOf(rarity);
    const tier = rarityTiers[rarity];

    return {
        id: nextHeroRecruitId++,
        archetypeKey,
        name: archetype.names[rarityIndex],
        rarity,
        cost: Math.floor(archetype.baseCost * tier.costMult)
    };
}

function refreshHeroPool() {
    heroRecruitPool = [];
    for (let i = 0; i < HERO_POOL_SIZE; i++) {
        heroRecruitPool.push(generateHeroRecruit());
    }
}

function hireHero(recruitId) {
    const index = heroRecruitPool.findIndex(r => r.id === recruitId);
    if (index === -1) return;
    const recruit = heroRecruitPool[index];

    const slotIndex = heroSquad.findIndex(h => h === null);
    if (slotIndex === -1 || gold < recruit.cost) return;

    gold -= recruit.cost;
    heroRecruitPool.splice(index, 1);
    heroSquad[slotIndex] = generateHero(recruit.archetypeKey, recruit.rarity, Math.floor(slotIndex / 3), slotIndex % 3);

    saveGame();
    updateUI();
}

function fireHero(slotIndex) {
    if (!heroSquad[slotIndex]) return;
    heroSquad[slotIndex] = null;
    saveGame();
    updateUI();
}

// --- Drag-and-drop hero repositioning ---
// Re-rendering mid-drag would yank the dragged element out from under the
// browser's drag session, so renderBattleSquads is suppressed while a drag is
// active and forced once on drop/dragend.
function attachHeroDragHandlers(slot, index) {
    const unit = heroSquad[index];
    if (unit && unit.alive) {
        slot.draggable = true;
        slot.addEventListener('dragstart', e => {
            isDraggingHero = true;
            if (armedHeroSlot === index) armedHeroSlot = null;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', String(index));
        });
        slot.addEventListener('dragend', () => {
            isDraggingHero = false;
            renderBattleSquads();
        });
    }

    slot.addEventListener('dragover', e => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    slot.addEventListener('dragenter', e => {
        e.preventDefault();
        slot.classList.add('drag-over');
    });
    slot.addEventListener('dragleave', () => slot.classList.remove('drag-over'));
    slot.addEventListener('drop', e => {
        e.preventDefault();
        slot.classList.remove('drag-over');
        const sourceIndex = parseInt(e.dataTransfer.getData('text/plain'), 10);
        swapHeroes(sourceIndex, index);
    });
}

function swapHeroes(sourceIndex, targetIndex) {
    if (sourceIndex === targetIndex || isNaN(sourceIndex)) return;
    const rowOf = idx => Math.floor(idx / 3);
    const colOf = idx => idx % 3;

    const a = heroSquad[sourceIndex];
    const b = heroSquad[targetIndex];
    if (a) { a.row = rowOf(targetIndex); a.col = colOf(targetIndex); }
    if (b) { b.row = rowOf(sourceIndex); b.col = colOf(sourceIndex); }
    heroSquad[sourceIndex] = b;
    heroSquad[targetIndex] = a;

    saveGame();
    renderBattleSquads();
}

// --- Invasions ---
function startInvasion() {
    const newTierIndex = getRaidTierIndex(kingdomLevel);
    if (newTierIndex !== raidTierIndex) {
        raidTierIndex = newTierIndex;
        tierWave = 0;
        raidWinStreak = 0;
    }

    // Heroes "respawn" at full HP each battle — the kingdom absorbs losses
    // via Kingdom HP, not permanent hero death.
    for (const hero of heroSquad) {
        if (!hero) continue;
        hero.hp = hero.maxHp;
        hero.alive = true;
        if (hero.attack) hero.attack.cooldown = BASE_ATTACK_INTERVAL / hero.attack.speed;
        if (hero.heal) hero.heal.cooldown = BASE_ATTACK_INTERVAL / hero.heal.speed;
    }

    currentInvasion = {
        name: getInvasionName(raidTierIndex, tierWave),
        enemies: generateEnemySquad(raidTierIndex, tierWave)
    };
}

function endInvasion() {
    const won = !squadAlive(currentInvasion.enemies);
    let loot;
    if (won) {
        loot = getInvasionLoot(raidTierIndex, raidWinStreak);
        raidWinStreak++;
    } else {
        loot = getFailureLoot(raidTierIndex);
        raidWinStreak = 0;
    }

    const kingdomFell = !won && kingdomHP <= 0;
    if (kingdomFell) {
        kingdomFallRecord = { name: currentInvasion.name, level: kingdomLevel };
    }

    lastVictory = { name: currentInvasion.name, loot, won, kingdomFell };
    gold += loot;
    tierWave++;
    currentInvasion = null;
    invasionTimer = RAID_INTERVAL;

    // Heroes that died this battle are gone for good — auto-fire them so
    // their slot is immediately free for a new recruit.
    for (let i = 0; i < heroSquad.length; i++) {
        if (heroSquad[i] && !heroSquad[i].alive) heroSquad[i] = null;
    }
}

function saveGame() {
    const state = {
        gold, goldEarned, kingdomLevel, raidsStarted, raidTierIndex, tierWave, raidWinStreak, invasionTimer, currentInvasion, lastVictory, kingdomFallRecord, autoRecruitRarity,
        recruitPool, poolTimer, nextRecruitId,
        kingdomHP, heroSquad, heroRecruitPool, heroPoolTimer, nextHeroRecruitId,
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
    if (state.raidTierIndex !== undefined) {
        raidTierIndex = state.raidTierIndex;
        tierWave = state.tierWave ?? 0;
        raidWinStreak = state.raidWinStreak ?? 0;
    } else {
        raidTierIndex = getRaidTierIndex(kingdomLevel);
        tierWave = 0;
        raidWinStreak = 0;
    }
    invasionTimer = state.invasionTimer ?? 0;
    currentInvasion = (state.currentInvasion && state.currentInvasion.enemies) ? state.currentInvasion : null;
    lastVictory = state.lastVictory ?? null;
    kingdomFallRecord = state.kingdomFallRecord ?? null;
    autoRecruitRarity = state.autoRecruitRarity ?? null;
    recruitPool = state.recruitPool ?? [];
    poolTimer = state.poolTimer ?? 0;
    nextRecruitId = state.nextRecruitId ?? 0;

    kingdomHP = state.kingdomHP ?? KINGDOM_HP_MAX;
    heroSquad = state.heroSquad ?? new Array(6).fill(null);
    heroRecruitPool = state.heroRecruitPool ?? [];
    heroPoolTimer = state.heroPoolTimer ?? 0;
    nextHeroRecruitId = state.nextHeroRecruitId ?? 0;

    for (const id in (state.buildings || {})) {
        if (!buildings[id]) continue;
        buildings[id].cost = state.buildings[id].cost;
        buildings[id].count = state.buildings[id].count;

        if (id === 'keep') {
            buildings[id].residents = [];
            continue;
        }

        buildings[id].residents = (state.buildings[id].residents || []).map(r => {
            let typeId = r.typeId || buildingToTypeId[id] || 'villager';
            let income = r.income;
            let name = r.name;
            if (id === 'workshop' && typeId === 'guard') {
                typeId = 'builder';
                name = 'Builder';
                income = Math.max(0.1, Math.round((income / 25) * 10) / 10);
            }
            return {
                income,
                rarity: r.rarity || 'common',
                typeId,
                name: name || (recruitTypes[typeId] || {}).name || 'Resident'
            };
        });
    }

    goldPerSecond = 0;
    kingdomHpRegen = 0;
    for (const id in buildings) {
        for (const r of buildings[id].residents) {
            if (buildings[id].type === 'hpregen') kingdomHpRegen += r.income;
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
    kingdomHP = Math.min(KINGDOM_HP_MAX, kingdomHP + kingdomHpRegen);

    poolTimer++;
    if (poolTimer >= POOL_REFRESH_INTERVAL) {
        poolTimer = 0;
        const hired = refreshPool();
        renderRecruitPool();
        if (hired) renderBuildings();
    }

    if (kingdomLevel >= RAID_TRIGGER_LEVEL) {
        heroPoolTimer++;
        if (heroPoolTimer >= HERO_POOL_REFRESH_INTERVAL) {
            heroPoolTimer = 0;
            refreshHeroPool();
            renderHeroRecruitPool();
        }
    }

    checkRaidTrigger();
    if (raidsStarted) {
        if (currentInvasion) {
            combatTick(1000);
            if (!squadAlive(currentInvasion.enemies) || kingdomHP <= 0) {
                endInvasion();
            }
        } else {
            invasionTimer--;
            if (invasionTimer <= 0) startInvasion();
        }
    }

    saveGame();
    tickRender();
}

function levelUpKingdom() {
    const next = levels[kingdomLevel + 1];
    if (!next || gold < next.cost) return;
    gold -= next.cost;
    kingdomLevel += 1;
    if (kingdomLevel >= RAID_TRIGGER_LEVEL && heroRecruitPool.length === 0) refreshHeroPool();
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
    b.cost = Math.floor(b.cost * Math.pow(b.costGrowth, affordable));
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
        <span class="pool-timer" id="pool-timer-text">New arrivals in ${timeUntilRefresh}s</span>
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
            const isHpregen = b.type === 'hpregen';
            const type = recruitTypes[recruit.typeId];
            const tier = rarityTiers[recruit.rarity];
            let valueLabel;
            if (isHpregen) {
                const minVal = Math.max(0.1, Math.round(type.incomeMin * tier.incomeMult * 10) / 10);
                const maxVal = Math.max(0.1, Math.round(type.incomeMax * tier.incomeMult * 10) / 10);
                valueLabel = `${minVal}-${maxVal} hp/s`;
            } else {
                const minVal = Math.max(1, Math.floor(type.incomeMin * tier.incomeMult));
                const maxVal = Math.floor(type.incomeMax * tier.incomeMult);
                valueLabel = `${minVal}-${maxVal} g/s`;
            }
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

        const isHpregen = b.type === 'hpregen';
        const hasSlots = b.slotsPerBuilding > 0;
        const totalSlots = b.count * b.slotsPerBuilding;
        const n = buyQuantity === 'max' ? maxAffordableBuildings(id) : Math.min(buyQuantity, cap - b.count);
        const totalCost = n > 0 ? bulkBuildingCost(id, n) : 0;
        const canAffordBuilding = n > 0 && gold >= totalCost;
        const costLabel = buyQuantity === 'max'
            ? (n > 0 ? `${totalCost.toLocaleString()} gold (×${n})` : 'At cap')
            : buyQuantity === 1
            ? `${b.cost.toLocaleString()} gold`
            : `${totalCost.toLocaleString()} gold (×${n})`;

        const isExpanded = buildingExpanded[id] || false;
        const buildingTotal = b.residents.reduce((sum, r) => sum + r.income, 0);
        const totalLabel = buildingTotal > 0
            ? `${isHpregen ? Math.round(buildingTotal * 10) / 10 : buildingTotal.toLocaleString()} ${isHpregen ? 'hp/s' : 'g/s'}`
            : '';

        const descLabel = id === 'keep' ? 'Improves hero recruit rarity' : `Adds ${b.slotsPerBuilding} resident slots`;

        html += `<div class="building-card ${isHpregen ? 'building-card--hpregen' : ''}">
            <div class="building-row">
                <button class="btn-building" onclick="buyBuilding('${id}')" ${canAffordBuilding ? '' : 'disabled'}>
                    <span class="building-name">${b.name}</span>
                    <span class="building-meta">
                        <span class="building-cost">Cost: ${costLabel}</span>
                        <span class="building-desc">${descLabel}</span>
                    </span>
                    <span class="building-stats">
                        <span class="building-owned">${b.count} / ${cap} buildings</span>
                        ${b.count > 0 && hasSlots ? `<span class="building-owned">${b.residents.length} / ${totalSlots} residents</span>` : ''}
                        ${id === 'keep' && b.count > 0 ? `<span class="building-income-total">+${b.count} hero rarity bias</span>` : ''}
                        ${totalLabel ? `<span class="building-income-total ${isHpregen ? 'building-income-total--hpregen' : ''}">${totalLabel}</span>` : ''}
                    </span>
                </button>
                ${b.count > 0 && hasSlots ? `<button class="btn-expand" onclick="toggleBuilding('${id}')" title="${isExpanded ? 'Collapse' : 'Expand residents'}">${isExpanded ? '▲' : '▼'}</button>` : ''}
            </div>`;

        if (b.count > 0 && hasSlots && isExpanded) {
            html += `<div class="slot-grid">`;

            const sorted = b.residents
                .map((r, i) => ({ ...r, originalIndex: i }))
                .sort((a, b) => a.income - b.income);

            sorted.forEach((r) => {
                const letter = r.name ? r.name[0].toUpperCase() : '?';
                const valueLabel = isHpregen ? `${r.income} hp/s` : `${r.income} g/s`;
                const rarityInfo = rarityTiers[r.rarity] || rarityTiers.common;
                html += `<div class="portrait portrait--${r.rarity || 'common'}" data-type="${r.typeId || 'villager'}"
                    title="${r.name} (${rarityInfo.name}) — ${valueLabel}&#10;Click to dismiss"
                    onclick="fireResident('${id}', ${r.originalIndex})">
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

function renderKingdomHP() {
    const pct = Math.max(0, Math.min(100, (kingdomHP / KINGDOM_HP_MAX) * 100));
    const html = `<div class="panel-label">Kingdom HP</div>
        <div class="hp-bar-track"><div class="hp-bar-fill" style="width:${pct}%"></div></div>
        <div class="hp-bar-caption">${Math.round(kingdomHP).toLocaleString()} / ${KINGDOM_HP_MAX.toLocaleString()}</div>
        ${kingdomHP <= 0 ? '<div class="kingdom-falling">Kingdom Falling!</div>' : ''}
        ${kingdomFallRecord ? `<div class="kingdom-fall-record">Fell at: ${kingdomFallRecord.name} (Kingdom Lv ${kingdomFallRecord.level})</div>` : ''}`;
    document.getElementById('kingdom-hp').innerHTML = html;
}

function renderRaidStatusBar() {
    let html = '';

    if (currentInvasion) {
        html += `<div class="raid-status-name">${currentInvasion.name}</div>
            <div class="raid-status-timer">Battle in progress</div>`;
        if (!squadAlive(heroSquad)) {
            html += `<div class="raid-status-siege">The Kingdom is under siege!</div>`;
        }
    } else if (raidsStarted) {
        const previewTierIndex = getRaidTierIndex(kingdomLevel);
        const previewWave = previewTierIndex === raidTierIndex ? tierWave : 0;
        const nextName = getInvasionName(previewTierIndex, previewWave);
        html += `<div class="raid-status-name">Next: ${nextName}</div>
            <div class="raid-status-timer">Arrives in ${formatTimer(invasionTimer)}</div>`;
    } else {
        html += `<div class="raid-status-name">No raids yet</div>`;
    }

    if (lastVictory) {
        const verb = lastVictory.won ? 'Repelled' : (lastVictory.kingdomFell ? 'Overrun' : 'Survived');
        html += `<div class="victory-inline">${verb}: ${lastVictory.name} +${lastVictory.loot.toLocaleString()}g</div>`;
    }

    document.getElementById('raid-status-bar').innerHTML = html;
}

// Heroes: backline column first, frontline second (frontline sits nearest the
// Enemies area). Enemies: frontline first, backline second (frontline sits
// nearest the Defenders area). This keeps both frontlines next to each other.
function renderSquad(containerId, squad, sideClass, columnOrder, interactive) {
    const el = document.getElementById(containerId);
    el.innerHTML = '';
    for (const colDef of columnOrder) {
        const colEl = document.createElement('div');
        colEl.className = 'battle-column';

        const label = document.createElement('div');
        label.className = 'battle-row-label';
        label.textContent = colDef.label;
        colEl.appendChild(label);

        for (let i = 0; i < 3; i++) {
            const index = colDef.row * 3 + i;
            const unit = squad[index];
            const slot = document.createElement('div');
            if (!unit) {
                slot.className = 'battle-slot empty';
            } else {
                slot.className = 'battle-slot' + (unit.alive ? '' : ' dead');
                const pct = Math.max(0, (unit.hp / unit.maxHp) * 100);
                const statParts = [];
                if (unit.attack) statParts.push(`ATK ${unit.attack.power}`);
                if (unit.heal) statParts.push(`HLR ${unit.heal.power}`);
                statParts.push(`DEF ${unit.defense}%`);
                slot.innerHTML = `
                    <div class="battle-unit-name">${unit.name}</div>
                    <div class="battle-unit-stats">${statParts.join(' &middot; ')}</div>
                    <div class="battle-hp-track"><div class="battle-hp-fill ${sideClass}" style="width:${pct}%"></div></div>
                    <div class="battle-hp-text">${Math.max(0, Math.round(unit.hp))} / ${unit.maxHp}</div>
                `;
                if (interactive) {
                    slot.classList.add('dismissable');
                    const armed = armedHeroSlot === index && Date.now() - armedHeroSlotTime < ARM_TIMEOUT_MS;
                    if (armed) {
                        slot.classList.add('armed');
                        slot.title = 'Click again to dismiss';
                    } else {
                        slot.title = 'Click to dismiss';
                    }
                    slot.addEventListener('click', () => {
                        if (armed) {
                            armedHeroSlot = null;
                            fireHero(index);
                        } else {
                            armedHeroSlot = index;
                            armedHeroSlotTime = Date.now();
                            renderBattleSquads();
                        }
                    });
                }
            }
            if (interactive) attachHeroDragHandlers(slot, index);
            colEl.appendChild(slot);
        }
        el.appendChild(colEl);
    }
}

function renderBattleSquads() {
    if (isDraggingHero) return;
    const enemies = currentInvasion ? currentInvasion.enemies : new Array(6).fill(null);
    renderSquad('heroSquad', heroSquad, '', [{ label: 'Backline', row: 1 }, { label: 'Frontline', row: 0 }], true);
    renderSquad('enemySquad', enemies, 'enemy', [{ label: 'Frontline', row: 0 }, { label: 'Backline', row: 1 }], false);
}

function renderHeroRecruitPool() {
    if (kingdomLevel < RAID_TRIGGER_LEVEL) {
        document.getElementById('hero-recruit-pool').innerHTML =
            `<div class="pool-empty">Unlocks at ${levels[RAID_TRIGGER_LEVEL].name}</div>`;
        return;
    }

    let html = '';

    if (heroRecruitPool.length === 0) {
        html += `<div class="pool-empty">No heroes seeking work right now.</div>`;
    } else {
        const hasSlot = heroSquad.some(h => h === null);
        heroRecruitPool.forEach(recruit => {
            const archetype = HERO_ARCHETYPES[recruit.archetypeKey];
            const tier = rarityTiers[recruit.rarity];
            const base = archetype.base;
            const statParts = [];
            if (base.attack) statParts.push(`ATK ${Math.round(base.attack.power * tier.incomeMult)}`);
            if (base.heal) statParts.push(`HLR ${Math.round(base.heal.power * tier.incomeMult)}`);
            statParts.push(`DEF ${base.defense}%`);

            const canAfford = gold >= recruit.cost;
            const canHire = canAfford && hasSlot;
            const letter = recruit.name[0].toUpperCase();

            let hint = '';
            if (!hasSlot) hint = 'Squad full';

            html += `<div class="recruit-card recruit-card--${recruit.rarity}">
                <div class="portrait portrait--${recruit.rarity}" data-type="${recruit.archetypeKey}">
                    <span class="portrait-letter">${letter}</span>
                </div>
                <div class="recruit-info">
                    <div class="recruit-name">${recruit.name}</div>
                    <div class="recruit-rarity" style="color:${tier.color}">${tier.name}</div>
                    <div class="recruit-stat">${statParts.join(' &middot; ')}</div>
                    ${hint ? `<div class="recruit-hint">${hint}</div>` : ''}
                </div>
                <div class="recruit-action">
                    <div class="recruit-cost">${recruit.cost.toLocaleString()}g</div>
                    <button class="btn-hire-recruit" onclick="hireHero(${recruit.id})" ${canHire ? '' : 'disabled'}>Hire</button>
                </div>
            </div>`;
        });
    }

    document.getElementById('hero-recruit-pool').innerHTML = html;
}

function tickRender() {
    document.getElementById('gold-display').textContent = Math.floor(gold).toLocaleString();
    const actualGps = currentInvasion ? Math.floor(goldPerSecond * 0.25) : goldPerSecond;
    document.getElementById('gps-display').textContent = actualGps.toLocaleString();
    document.getElementById('siege-indicator').textContent = currentInvasion ? ' (siege)' : '';

    renderKingdomHP();
    renderLeftPanel();
    renderRaidStatusBar();
    renderBattleSquads();
    renderHeroRecruitPool();

    const poolTimerEl = document.getElementById('pool-timer-text');
    if (poolTimerEl) poolTimerEl.textContent = `New arrivals in ${POOL_REFRESH_INTERVAL - poolTimer}s`;
}

function updateUI() {
    tickRender();
    renderRecruitPool();
    renderBuildings();
}

loadGame();
if (recruitPool.length === 0) refreshPool();
if (kingdomLevel >= RAID_TRIGGER_LEVEL && heroRecruitPool.length === 0) refreshHeroPool();
updateUI();
tickInterval = setInterval(tick, 1000);
