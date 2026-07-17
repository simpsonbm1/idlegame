// Balance simulator: models a sensible player at 1x speed using a mirror of
// game.js constants and a port of its combat rules. Used to tune M9; rerun
// for any balance pass (M14). KEEP THE TABLES BELOW IN SYNC WITH game.js.
// Usage: node tools/balance-sim.js

// ---------- Constants (mirror of game.js values) ----------
const CFG = {
    RAID_TRIGGER_LEVEL: 2,
    RAID_TRIGGER_GOLD: 4000, FIRST_RAID_GRACE: 75,
    KINGDOM_HP_MAX: 1000,
    KINGDOM_DEFENSE: 15,
    BASE_ATTACK_INTERVAL: 2500,
    DEFAULT_BACKLINE_CHANCE: 0.15,
    SIEGE_ESCALATION_GRACE: 60,  // game-seconds of battle before escalation begins
    SIEGE_ESCALATION_RATE: 0.01, // +1% enemy attack power per second past the grace
    AOE_POWER_FACTOR: 0.65,      // row-AoE hits everyone in the row at a discount
};

// Enemy attack multiplier after s seconds of one battle (mirror of game.js
// escalationMult — applies to enemy attacks only, never heals).
function escMultAt(s) {
    const past = s - CFG.SIEGE_ESCALATION_GRACE;
    return past > 0 ? 1 + past * CFG.SIEGE_ESCALATION_RATE : 1;
}

// waveCount includes the boss wave (last index). powerMult chains from the
// previous tier's boss multiplier; growth 1.088/wave, continuous ladder.
// M11: grid + traits + boss signature traits mirror game.js exactly.
const RAID_TIERS = [
    { name: 'Goblin Raid',  powerMult: 1.0,  growth: 1.088, waveCount: 5,  raidInterval: 45, baseLoot: 1200,    lootGrowth: 1.10,
      grid: { rows: 2, cols: 3 }, traits: {},
      boss: { name: 'Goblin Warmaster', powerMult: 1.8, hpMult: 4.0, traits: { aura: { power: 0.15, range: 'all' } } } },
    { name: 'Orc Warband',  powerMult: 1.52, growth: 1.088, waveCount: 8,  raidInterval: 45, baseLoot: 5000,   lootGrowth: 1.10,
      grid: { rows: 2, cols: 3 }, traits: { brute: { enrage: { speed: 1.5, power: 1 } } },
      boss: { name: 'Orc Warlord', powerMult: 1.8, hpMult: 4.0, traits: { enrage: { speed: 1.75, power: 1.25 } } } },
    { name: 'Bandit Horde', powerMult: 3.0,  growth: 1.088, waveCount: 11, raidInterval: 40, baseLoot: 30000,  lootGrowth: 1.10,
      grid: { rows: 3, cols: 4 }, traits: { caster: { backlineChance: 0.7 } },
      boss: { name: 'Bandit King', powerMult: 1.8, hpMult: 4.0, traits: { backlineChance: 0.85 } } },
    { name: 'Undead Legion', powerMult: 7.6, growth: 1.088, waveCount: 14, raidInterval: 35, baseLoot: 120000, lootGrowth: 1.10,
      grid: { rows: 3, cols: 4 }, traits: { caster: { reviveCharges: 1 } },
      boss: { name: 'Lich Commander', powerMult: 1.8, hpMult: 4.0, traits: { reviveCharges: 2 } } },
    { name: 'Infernal Siege', powerMult: 24.7, growth: 1.088, waveCount: 17, raidInterval: 30, baseLoot: 500000, lootGrowth: 1.10,
      grid: { rows: 4, cols: 4 }, traits: { caster: { aoe: 'row' } },
      boss: { name: 'Demon Empress', powerMult: 1.8, hpMult: 4.0, traits: { aoe: 'row', enrage: { speed: 1, power: 1.25 } } } },
];

// ~30% softer than live values: the tutorial wave must be winnable by a few
// commons; the ladder growth carries the difficulty.
const ENEMY_ARCHETYPES = {
    brute:      { defense: 20, hp: 90, attack: { power: 10, speed: 0.7 } },
    skirmisher: { defense: 8,  hp: 55, attack: { power: 13, speed: 1.1 }, backlineChance: 0.4 },
    caster:     { defense: 5,  hp: 45, attack: { power: 14, speed: 0.9 } },
    shaman:     { defense: 8,  hp: 50, heal: { power: 10, speed: 0.7 } },
    sapper:     { defense: 10, hp: 65, attack: { power: 8, speed: 0.8 }, targetsKingdom: true },
};

// KEEP IN SYNC with game.js TIER_WAVES (hand-authored compositions).
// NOTE: resident-injury economics from sappers is NOT modeled here — sapper
// kingdom damage is; injury income loss is a real-play tax the sim understates.
const TIER_WAVES = [
    [
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1', 'caster 1 2'],
        ['BOSS 0 1', 'brute 0 0', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1']
    ],
    [
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'shaman 1 1'],
        ['skirmisher 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'caster 1 2', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'shaman 1 0', 'caster 1 1', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1', 'shaman 1 2'],
        ['BOSS 0 1', 'brute 0 0', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1', 'shaman 1 2']
    ],
    [
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 1', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'caster 1 0', 'caster 1 2', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 1', 'shaman 1 2', 'sapper 2 0', 'sapper 2 3'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 1', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 1', 'shaman 1 0', 'shaman 1 3'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'sapper 2 2'],
        ['skirmisher 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 1', 'caster 1 2', 'shaman 1 0', 'shaman 1 3'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 1', 'shaman 1 0', 'shaman 1 2', 'sapper 2 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2', 'sapper 2 0', 'sapper 2 3'],
        ['BOSS 0 1', 'brute 0 0', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2', 'sapper 2 2']
    ],
    [
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 1', 'shaman 1 2'],
        ['brute 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'sapper 2 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 1', 'shaman 1 0', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'sapper 2 0'],
        ['skirmisher 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3', 'sapper 2 3'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'caster 1 1', 'caster 1 3', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2', 'sapper 2 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3', 'sapper 2 0', 'sapper 2 3'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2', 'sapper 2 2'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'shaman 1 1', 'caster 1 2', 'shaman 1 3', 'sapper 2 0', 'sapper 2 3'],
        ['BOSS 0 1', 'brute 0 0', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3', 'sapper 2 2']
    ],
    [
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 1', 'shaman 1 2'],
        ['skirmisher 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'skirmisher 1 0', 'skirmisher 1 3', 'caster 1 1', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'sapper 2 0'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 1', 'shaman 1 0', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3', 'sapper 2 1'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'skirmisher 1 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'sapper 2 0', 'sapper 2 3'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3', 'sapper 2 1'],
        ['skirmisher 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'skirmisher 1 0', 'skirmisher 1 2', 'caster 1 1', 'caster 1 3', 'shaman 2 0', 'shaman 2 3'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'brute 0 3', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3', 'sapper 2 0', 'sapper 2 2'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 1', 'caster 1 3', 'shaman 1 2', 'shaman 2 0', 'sapper 2 3'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 1', 'caster 1 2', 'shaman 1 3', 'shaman 2 1', 'sapper 2 2'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'brute 0 3', 'skirmisher 1 3', 'caster 1 1', 'caster 1 2', 'shaman 2 0', 'shaman 2 3', 'sapper 2 2'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'skirmisher 0 3', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2', 'sapper 2 0', 'sapper 2 3'],
        ['brute 0 0', 'brute 0 1', 'brute 0 2', 'brute 0 3', 'caster 1 0', 'caster 1 2', 'shaman 1 1', 'shaman 1 3', 'sapper 2 1', 'sapper 2 2'],
        ['BOSS 0 1', 'brute 0 0', 'brute 0 2', 'brute 0 3', 'caster 1 0', 'shaman 1 1', 'shaman 1 3', 'sapper 2 1', 'sapper 2 2']
    ]
];

// M14.1 rebalance (playtest feedback): the GUARD SPECTRUM — guard = targeting
// tickets within the unit's row pool (unset = 1): guardian 3, paladin/banneret
// 2, fighter 1.5, assassin 0.5 (slippery). Fighter debuts (frontline DPS, base
// roster); paladin heal 11->9 (stack was dominant); mender buffed 22/65/8.
const HERO_COST_TIER_GROWTH = 1.4; // hero hire cost x1.4 per raid tier reached
const HERO_ARCHETYPES = {
    guardian: { baseCost: 1000, defense: 35, hp: 140, attack: { power: 8,  speed: 0.7 }, guard: 3 },
    fighter:  { baseCost: 1100, defense: 18, hp: 95,  attack: { power: 14, speed: 1.0 }, guard: 1.5 },
    ranged:   { baseCost: 750, defense: 5,  hp: 60,  attack: { power: 18, speed: 1.3 } },
    mender:   { baseCost: 850, defense: 8,  hp: 65,  heal:   { power: 22, speed: 0.7 } },
    // M10 unlockable archetypes
    paladin:  { baseCost: 1300, defense: 25, hp: 120, attack: { power: 9, speed: 0.7 }, heal: { power: 9, speed: 0.55 }, guard: 2 },
    assassin: { baseCost: 950,  defense: 3,  hp: 45,  attack: { power: 26, speed: 1.2 }, backlineChance: 0.9, guard: 0.5 },
    // M11 unlockable archetypes (aura/chill are fixed effects; rarity scales stats)
    battlemage: { baseCost: 1600, defense: 8,  hp: 70,  attack: { power: 12, speed: 0.8, aoe: 'row' } },
    banneret:   { baseCost: 1500, defense: 25, hp: 110, attack: { power: 6, speed: 0.6 }, aura: { power: 0.15, range: 'adjacent' }, guard: 2 },
    frostadept: { baseCost: 1400, defense: 6,  hp: 65,  attack: { power: 10, speed: 1.0, chill: { mult: 1.35, duration: 6 } } },
};

// Hall of Legends (Military tree, costs 50/750/5000 Legacy): hero rarity is
// CAPPED at common/rare/epic/legendary by rank 0-3 — in-run gold cannot buy
// past it. This is the run-depth gate; the ceiling-mapped win-rate table at
// the bottom is what verifies each cap's wall lands on the difficulty arc.

// Proposed economy (buildings: cost, growth, slots; residents: cost, avg g/s)
// Resident ROI stretched to ~60-190s so income ramps over minutes, not seconds.
const BUILDINGS = {
    cottage:  { cost: 10,     growth: 1.30, slots: 2, hire: 25,     inc: 2.0 },
    tavern:   { cost: 250,    growth: 1.30, slots: 2, hire: 300,    inc: 6.0 },
    smithy:   { cost: 1500,   growth: 1.35, slots: 2, hire: 1200,   inc: 15 },
    library:  { cost: 6000,   growth: 1.35, slots: 2, hire: 4500,   inc: 45 },
    workshop: { cost: 400,    growth: 1.35, slots: 2, hire: 250,    inc: 0,  hp: 0.55 },
    apothecary:{ cost: 25000, growth: 1.40, slots: 3, hire: 15000,  inc: 120 },
    tower:    { cost: 100000, growth: 1.45, slots: 3, hire: 60000,  inc: 375 },
    cathedral:{ cost: 400000, growth: 1.50, slots: 3, hire: 200000, inc: 1050 },
};

const LEVELS = [
    { name: 'Hamlet',  cost: 0,       caps: { cottage: 3 } },
    { name: 'Village', cost: 400,     caps: { cottage: 5,  tavern: 2, workshop: 1 } },
    { name: 'Town',    cost: 3000,    caps: { cottage: 7,  tavern: 3, smithy: 2, workshop: 2 } },
    { name: 'City',    cost: 20000,   caps: { cottage: 9,  tavern: 4, smithy: 3, library: 2, workshop: 2 } },
    { name: 'Kingdom', cost: 80000,   caps: { cottage: 11, tavern: 5, smithy: 4, library: 3, workshop: 3 } },
    { name: 'Empire',  cost: 300000,  caps: { cottage: 13, tavern: 6, smithy: 5, library: 4, workshop: 3, apothecary: 2 } },
    { name: 'Dynasty', cost: 1000000,  caps: { cottage: 15, tavern: 7, smithy: 6, library: 5, workshop: 4, apothecary: 3, tower: 2 } },
    { name: 'Realm',   cost: 3000000, caps: { cottage: 16, tavern: 8, smithy: 7, library: 6, workshop: 4, apothecary: 4, tower: 3, cathedral: 2 } },
];

// ---------- Combat engine (ported from game.js, M11 feature-complete) ----------
function makeUnit(name, defense, hp, row, col, side, attack, heal, backlineChance) {
    return {
        name, defense, hp, maxHp: hp, row, col, side,
        attack: attack ? { ...attack, cooldown: CFG.BASE_ATTACK_INTERVAL / attack.speed } : null,
        heal: heal ? { ...heal, cooldown: CFG.BASE_ATTACK_INTERVAL / heal.speed } : null,
        backlineChance: backlineChance ?? CFG.DEFAULT_BACKLINE_CHANCE,
        alive: true,
    };
}

function waveMult(tierIdx, wave) {
    const t = RAID_TIERS[tierIdx];
    return t.powerMult * Math.pow(t.growth, wave);
}

// Mirror of game.js: builds the wave from its hand-authored composition and
// applies tier traits (+ boss signature traits on the boss unit).
function generateEnemySquad(tierIdx, wave) {
    const t = RAID_TIERS[tierIdx];
    const mult = waveMult(tierIdx, wave);
    const comp = TIER_WAVES[tierIdx][Math.min(wave, TIER_WAVES[tierIdx].length - 1)];
    const squad = [];
    for (const entry of comp) {
        const [key, r, c] = entry.split(' ');
        const isBoss = key === 'BOSS';
        const aKey = isBoss ? 'brute' : key;
        const a = ENEMY_ARCHETYPES[aKey];
        const pMult = mult * (isBoss ? t.boss.powerMult : 1);
        const hMult = Math.sqrt(mult) * (isBoss ? t.boss.hpMult : 1);
        const attack = a.attack ? { power: Math.round(a.attack.power * pMult), speed: a.attack.speed } : null;
        const heal = a.heal ? { power: Math.round(a.heal.power * pMult), speed: a.heal.speed } : null;
        const unit = makeUnit(isBoss ? t.boss.name : aKey, a.defense, Math.round(a.hp * hMult), Number(r), Number(c), 'enemy', attack, heal, a.backlineChance);
        if (a.targetsKingdom) unit.targetsKingdom = true;
        const traits = { ...(t.traits[aKey] || {}), ...(isBoss ? t.boss.traits : {}) };
        if (traits.backlineChance !== undefined) unit.backlineChance = traits.backlineChance;
        if (traits.enrage) unit.enrage = traits.enrage;
        if (traits.reviveCharges) unit.reviveCharges = traits.reviveCharges;
        if (traits.aura) unit.aura = traits.aura;
        if (traits.aoe && unit.attack) unit.attack.aoe = traits.aoe;
        squad.push(unit);
    }
    return squad;
}

function makeHero(key, rarityMult, treePower = 1, treeHp = 1) {
    const a = HERO_ARCHETYPES[key];
    const attack = a.attack ? { power: Math.round(a.attack.power * rarityMult * treePower), speed: a.attack.speed } : null;
    const heal = a.heal ? { power: Math.round(a.heal.power * rarityMult * treePower), speed: a.heal.speed } : null;
    if (attack && a.attack.aoe) attack.aoe = a.attack.aoe;
    if (attack && a.attack.chill) attack.chill = a.attack.chill;
    const row = (key === 'guardian' || key === 'paladin' || key === 'banneret' || key === 'fighter') ? 0 : 1;
    const unit = makeUnit(key, a.defense, Math.round(a.hp * Math.sqrt(rarityMult) * treeHp), row, 0, 'hero', attack, heal, a.backlineChance);
    if (a.aura) unit.aura = a.aura;
    if (a.guard) unit.guard = a.guard;
    return unit;
}

// Assign columns within each row (needed for aura adjacency). Call after any
// squad change.
function assignHeroCols(heroes) {
    const counts = {};
    for (const h of heroes) {
        if (!h) continue;
        counts[h.row] = counts[h.row] || 0;
        h.col = counts[h.row]++;
    }
}

// Mirror of game.js pickTarget (generalized to N rows in M10; M14.1 taunt):
// frontmost occupied row is the front, everything behind is the backline pool.
// Within the chosen pool, a unit with guard > 1 draws that many targeting
// "tickets" (guardians tank for whoever shares their pool).
function weightedPick(pool) {
    let total = 0;
    for (const u of pool) total += u.guard || 1;
    let roll = Math.random() * total;
    for (const u of pool) { roll -= u.guard || 1; if (roll <= 0) return u; }
    return pool[pool.length - 1];
}
function pickTarget(attacker, squad) {
    const alive = squad.filter(u => u && u.alive);
    if (!alive.length) return null;
    const frontRow = Math.min(...alive.map(u => u.row));
    const front = alive.filter(u => u.row === frontRow);
    const back = alive.filter(u => u.row > frontRow);
    if (!back.length) return weightedPick(front);
    const pool = Math.random() < attacker.backlineChance ? back : front;
    return weightedPick(pool);
}

function pickHealTarget(squad) {
    const wounded = squad.filter(u => u && u.alive && u.hp < u.maxHp);
    if (!wounded.length) return null;
    wounded.sort((a, b) => a.hp / a.maxHp - b.hp / b.maxHp);
    return wounded[0];
}

function dmg(power, defense) {
    return Math.max(1, Math.round(power * (1 - defense / 100)));
}

// --- M12 doctrines (mirror of game.js; set per scenario, applied to heroes) ---
// attack: Smithy Forgework mult; speed: Library Tactics mult; salves: fraction
// of maxHp regen/s (Apothecary); blessing: first hero death revives at 30%.
let DOCTRINES = { attack: 1, speed: 1, salves: 0, blessing: false };
let blessingUsed = false; // reset at each battle start

// --- M11 modifier layer (mirror of game.js) ---
function isEnraged(u) { return u.enrage && u.alive && u.hp / u.maxHp < 0.5; }

function auraBonus(unit, squad) {
    let bonus = 0;
    for (const ally of squad) {
        if (!ally || !ally.alive || ally === unit || !ally.aura) continue;
        const adjacent = (ally.row === unit.row && Math.abs(ally.col - unit.col) === 1)
            || (ally.col === unit.col && Math.abs(ally.row - unit.row) === 1);
        if (ally.aura.range === 'all' || adjacent) bonus += ally.aura.power;
    }
    return bonus;
}

function effPower(unit, squad) {
    let p = unit.attack.power;
    if (isEnraged(unit)) p *= unit.enrage.power || 1;
    p *= 1 + auraBonus(unit, squad);
    if (unit.side === 'hero') p *= DOCTRINES.attack;
    return p;
}

function effInterval(unit, action, battleT) {
    let interval = CFG.BASE_ATTACK_INTERVAL / action.speed;
    if (isEnraged(unit)) interval /= unit.enrage.speed || 1;
    if (unit.chilledUntil !== undefined && battleT < unit.chilledUntil) interval *= unit.chillMult || 1;
    if (unit.side === 'hero') interval /= DOCTRINES.speed;
    return interval;
}

function onUnitDeath(unit, enemies) {
    if (unit.side === 'hero') {
        if (DOCTRINES.blessing && !blessingUsed) {
            blessingUsed = true;
            unit.alive = true;
            unit.hp = Math.max(1, Math.round(unit.maxHp * 0.3));
            if (unit.attack) unit.attack.cooldown = CFG.BASE_ATTACK_INTERVAL / unit.attack.speed;
            if (unit.heal) unit.heal.cooldown = CFG.BASE_ATTACK_INTERVAL / unit.heal.speed;
        }
        return;
    }
    for (const ally of enemies) {
        if (!ally || !ally.alive || !(ally.reviveCharges > 0)) continue;
        ally.reviveCharges--;
        unit.alive = true;
        unit.hp = Math.round(unit.maxHp * 0.5);
        if (unit.attack) unit.attack.cooldown = CFG.BASE_ATTACK_INTERVAL / unit.attack.speed;
        if (unit.heal) unit.heal.cooldown = CFG.BASE_ATTACK_INTERVAL / unit.heal.speed;
        return;
    }
}

// Runs one game-second of combat. Returns kingdom damage dealt this tick.
// escMult scales enemy attack power only (siege escalation); battleT is the
// battle clock in seconds (chill expiry).
function combatTick(heroes, enemies, kingdomAlive, escMult = 1, battleT = 0) {
    let kingdomDmg = 0;
    const strike = (attacker, defender, friendly, powerScale = 1) => {
        let p = effPower(attacker, friendly) * powerScale;
        if (attacker.side === 'enemy') p *= escMult;
        defender.hp -= dmg(p, defender.defense);
        if (attacker.attack.chill && defender.hp > 0) {
            defender.chilledUntil = battleT + attacker.attack.chill.duration;
            defender.chillMult = attacker.attack.chill.mult;
        }
        if (defender.hp <= 0) { defender.hp = 0; defender.alive = false; onUnitDeath(defender, enemies); }
    };
    for (const u of [...heroes, ...enemies]) {
        if (!u || !u.alive) continue;
        if (u.attack) {
            u.attack.cooldown -= 1000;
            while (u.attack.cooldown <= 0) {
                if (u.side === 'enemy' && (u.targetsKingdom || !heroes.some(h => h && h.alive))) {
                    if (kingdomAlive()) kingdomDmg += dmg(effPower(u, enemies) * escMult, CFG.KINGDOM_DEFENSE);
                } else {
                    const friendly = u.side === 'hero' ? heroes : enemies;
                    const opposing = u.side === 'hero' ? enemies : heroes;
                    const t = pickTarget(u, opposing);
                    if (t) {
                        if (u.attack.aoe === 'row') {
                            for (const v of opposing.filter(x => x && x.alive && x.row === t.row)) strike(u, v, friendly, CFG.AOE_POWER_FACTOR);
                        } else strike(u, t, friendly);
                    }
                }
                u.attack.cooldown += effInterval(u, u.attack, battleT);
            }
        }
        if (u.heal) {
            u.heal.cooldown -= 1000;
            if (u.heal.cooldown <= 0) {
                const friendly = u.side === 'hero' ? heroes : enemies;
                const t = pickHealTarget(friendly);
                if (t) {
                    t.hp = Math.min(t.maxHp, t.hp + u.heal.power * (1 + auraBonus(u, friendly)));
                    u.heal.cooldown += effInterval(u, u.heal, battleT);
                }
            }
        }
        // dead heroes free their slot at moment of death (M8 rule) -- modeled
        // by the alive flag; slot reuse handled by the hire logic outside.
    }
    // Apothecary Salves (M12): heroes regenerate during battle.
    if (DOCTRINES.salves > 0) {
        for (const h of heroes) {
            if (h && h.alive && h.hp < h.maxHp) h.hp = Math.min(h.maxHp, h.hp + h.maxHp * DOCTRINES.salves);
        }
    }
    return kingdomDmg;
}

// ---------- Run-1 player simulation ----------
function simulateRun({ treeIncome = 1, treePower = 1, treeHp = 1, startGold = 75, rarityMult = 1, verbose = true } = {}) {
    let gold = startGold, earned = 0, income = 0, hpRegen = 0;
    let level = 0, kingdomHP = CFG.KINGDOM_HP_MAX;
    const owned = {}, staffed = {};
    for (const id in BUILDINGS) { owned[id] = 0; staffed[id] = 0; }
    const costNow = {};
    for (const id in BUILDINGS) costNow[id] = BUILDINGS[id].cost;

    let raids = false, tierIdx = 0, wave = 0, streak = 0, timer = 0;
    let battle = null, heroes = [], battleT = 0;
    let legacy = 0, waves = 0, hireCooldown = 0, t = 0;
    const log = [];

    const cap = id => (LEVELS[level].caps[id] || 0);
    const heroCost = key => HERO_ARCHETYPES[key].baseCost * (rarityMult === 1 ? 1 : rarityMult === 2.5 ? 3 : rarityMult === 5 ? 8 : 20)
        * Math.pow(HERO_COST_TIER_GROWTH, tierIdx);
    // Role coverage first, then double up — the cheap 2nd/3rd hires matter for
    // surviving the knife-edge first battle (the model spends down to ~0 gold
    // at the trigger).
    const wantHeroes = ['guardian', 'ranged', 'mender', 'fighter', 'ranged', 'mender'];
    const maxSquad = 6;

    while (t < 3 * 3600) {
        t++;
        gold += income * treeIncome;
        earned += income * treeIncome;
        kingdomHP = Math.min(CFG.KINGDOM_HP_MAX, kingdomHP + hpRegen);
        if (hireCooldown > 0) hireCooldown--;

        // --- player decisions ---
        // Heroes: emergency-rehire during a battle with nobody standing;
        // otherwise build toward a 6-slot squad when gold is comfortable.
        heroes = heroes.filter(x => x.alive || battle); // dead slots free instantly
        const aliveHeroes = heroes.filter(h => h.alive).length;
        const need = wantHeroes[aliveHeroes % wantHeroes.length];
        const emergency = battle && aliveHeroes === 0;
        const wantMore = level >= CFG.RAID_TRIGGER_LEVEL && aliveHeroes < maxSquad &&
            (emergency ? gold >= heroCost(need) : gold >= heroCost(need) * 1.5);
        if (wantMore && hireCooldown === 0) {
            gold -= heroCost(need);
            heroes = heroes.filter(x => x.alive);
            heroes.push(makeHero(need, rarityMult, treePower, treeHp));
            assignHeroCols(heroes);
            hireCooldown = 8; // pool RNG / refresh delay
        } else if (!emergency) {
            // level up when affordable
            if (level + 1 < LEVELS.length && gold >= LEVELS[level + 1].cost && (level < CFG.RAID_TRIGGER_LEVEL || aliveHeroes >= 6)) {
                gold -= LEVELS[level + 1].cost; level++;
                log.push(`${fmt(t)}  -> ${LEVELS[level].name} (income ${income.toFixed(1)} g/s)`);
            }
            // hire into any open slot (throttled to model the pool)
            if (hireCooldown === 0) {
                let best = null;
                for (const id in BUILDINGS) {
                    const b = BUILDINGS[id];
                    if (staffed[id] < owned[id] * b.slots && gold >= b.hire) {
                        if (!best || b.inc / b.hire > BUILDINGS[best].inc / BUILDINGS[best].hire) best = id;
                    }
                }
                if (best) {
                    gold -= BUILDINGS[best].hire; staffed[best]++;
                    income += BUILDINGS[best].inc; hpRegen += BUILDINGS[best].hp || 0;
                    hireCooldown = 2;
                }
            }
            // buy a building when everything is staffed
            const allStaffed = Object.keys(BUILDINGS).every(id => staffed[id] >= owned[id] * BUILDINGS[id].slots);
            if (allStaffed) {
                let bestB = null;
                for (const id in BUILDINGS) {
                    if (owned[id] < cap(id) && gold >= costNow[id]) {
                        if (!bestB || costNow[id] < costNow[bestB]) bestB = id;
                    }
                }
                if (bestB) { gold -= costNow[bestB]; owned[bestB]++; costNow[bestB] = Math.floor(costNow[bestB] * BUILDINGS[bestB].growth); }
            }
        }

        // --- raids ---
        if (!raids && level >= CFG.RAID_TRIGGER_LEVEL && earned >= CFG.RAID_TRIGGER_GOLD) {
            raids = true; timer = CFG.FIRST_RAID_GRACE;
            log.push(`${fmt(t)}  RAIDS TRIGGERED (income ${income.toFixed(1)} g/s, gold ${Math.floor(gold)})`);
        }
        if (raids) {
            if (battle) {
                battleT++;
                for (const h of heroes) if (!h.alive) heroes = heroes.filter(x => x.alive);
                kingdomHP -= combatTick(heroes, battle, () => kingdomHP > 0, escMultAt(battleT), battleT);
                if (kingdomHP <= 0) {
                    log.push(`${fmt(t)}  OVERRUN at ${RAID_TIERS[tierIdx].name} wave ${wave + 1} -- RUN ENDS`);
                    return { t, tierIdx, wave, waves, legacy, income, log };
                }
                if (!battle.some(e => e.alive)) {
                    const tier = RAID_TIERS[tierIdx];
                    const loot = Math.floor(tier.baseLoot * Math.pow(tier.lootGrowth, streak));
                    const isBoss = wave === tier.waveCount - 1;
                    const lp = [10, 50, 250, 1250, 6250][tierIdx] * (isBoss ? 4 : 1);
                    gold += loot; legacy += lp; waves++; streak++;
                    log.push(`${fmt(t)}  WIN ${tier.name} w${wave + 1}${isBoss ? ' BOSS' : ''} +${loot}g (${(loot / (income * treeIncome) / 60).toFixed(1)} min inc) +${lp}LP | heroes ${heroes.filter(h => h.alive).length} | KHP ${Math.round(kingdomHP)}`);
                    if (isBoss && tierIdx < RAID_TIERS.length - 1) { tierIdx++; wave = 0; streak = 0; }
                    else wave++;
                    battle = null; timer = RAID_TIERS[tierIdx].raidInterval;
                }
            } else {
                timer--;
                if (timer <= 0) {
                    battle = generateEnemySquad(tierIdx, wave);
                    battleT = 0;
                    blessingUsed = false;
                    for (const h of heroes) { h.hp = h.maxHp; h.alive = true; delete h.chilledUntil; if (h.attack) h.attack.cooldown = CFG.BASE_ATTACK_INTERVAL / h.attack.speed; if (h.heal) h.heal.cooldown = CFG.BASE_ATTACK_INTERVAL / h.heal.speed; }
                }
            }
        }
    }
    return { t, tierIdx, wave, waves, legacy, income, log, timeout: true };
}

function fmt(s) { return `${String(Math.floor(s / 60)).padStart(3)}m${String(s % 60).padStart(2, '0')}`; }

// ---------- Squad-vs-wave win-rate table (deeper-run sanity check) ----------
function winRate(squadSpec, tierIdx, wave, trials = 40, doctrines = null) {
    let wins = 0;
    const winTimes = [];
    const saved = DOCTRINES;
    if (doctrines) DOCTRINES = { ...saved, ...doctrines };
    for (let i = 0; i < trials; i++) {
        blessingUsed = false;
        const heroes = squadSpec.map(([k, r, tp, th]) => makeHero(k, r, tp, th));
        assignHeroCols(heroes);
        const enemies = generateEnemySquad(tierIdx, wave);
        let khp = CFG.KINGDOM_HP_MAX, ticks = 0;
        while (ticks++ < 600) {
            khp -= combatTick(heroes, enemies, () => khp > 0, escMultAt(ticks), ticks);
            if (khp <= 0) break;
            if (!enemies.some(e => e.alive)) { wins++; winTimes.push(ticks); break; }
        }
    }
    DOCTRINES = saved;
    winTimes.sort((a, b) => a - b);
    return { rate: wins / trials, medWin: winTimes.length ? winTimes[Math.floor(winTimes.length / 2)] : null };
}

// ---------- Stalemate/grind check (the 2026-07-17 playtest scenario) ----------
// One endless siege: a 6-slot squad continuously refilled from income while
// the Kingdom regenerates behind it. Without escalation, a healer-led wave the
// squad can't out-damage stalemates forever (the playtest soft-lock); with it,
// the siege must resolve as WIN or OVERRUN.
function grindBattle({ tierIdx, wave, rarityMult = 1, income = 400, regen = 6, hireDelay = 6, escalation = true, maxSeconds = 3600 }) {
    const costMult = (rarityMult === 1 ? 1 : rarityMult === 2.5 ? 3 : rarityMult === 5 ? 8 : 20)
        * Math.pow(HERO_COST_TIER_GROWTH, tierIdx);
    const want = ['guardian', 'fighter', 'ranged', 'mender'];
    // Real walls are hit with a full squad standing and a deep wallet — the
    // previous wave was just won. Rehires then drip in against attrition.
    let gold = 20000, khp = CFG.KINGDOM_HP_MAX, cd = 0, hired = 0;
    blessingUsed = false;
    let heroes = [0, 1, 2, 3, 4, 5].map(i => makeHero(want[i % want.length], rarityMult));
    assignHeroCols(heroes);
    const enemies = generateEnemySquad(tierIdx, wave);
    for (let t = 1; t <= maxSeconds; t++) {
        gold += income;
        khp = Math.min(CFG.KINGDOM_HP_MAX, khp + regen);
        if (cd > 0) cd--;
        heroes = heroes.filter(h => h.alive);
        const key = want[hired % want.length];
        const cost = HERO_ARCHETYPES[key].baseCost * costMult;
        if (heroes.length < 6 && cd === 0 && gold >= cost) {
            gold -= cost; heroes.push(makeHero(key, rarityMult)); hired++; cd = hireDelay;
            assignHeroCols(heroes);
        }
        khp -= combatTick(heroes, enemies, () => khp > 0, escalation ? escMultAt(t) : 1, t);
        if (khp <= 0) return { outcome: 'OVERRUN', t, hired };
        if (!enemies.some(e => e.alive)) return { outcome: 'WIN', t, hired };
    }
    return { outcome: 'STALEMATE', t: maxSeconds, hired };
}

// ---------- Report ----------
console.log('=== Ladder multipliers (continuous check) ===');
let prev = null;
for (let ti = 0; ti < RAID_TIERS.length; ti++) {
    const t = RAID_TIERS[ti];
    const first = waveMult(ti, 0), boss = waveMult(ti, t.waveCount - 1);
    console.log(`${t.name.padEnd(14)} w1 x${first.toFixed(2)}  boss x${boss.toFixed(2)}${prev ? `  (jump from prev boss: ${(first / prev * 100 - 100).toFixed(0)}%)` : ''}`);
    prev = boss;
}
console.log(`Final boss vs goblin w1: x${(waveMult(4, 16) / waveMult(0, 0)).toFixed(0)} (target 80-100, boss unit adds x1.6 power on top)\n`);

console.log('=== RUN 1 (no upgrades, common heroes) ===');
const r1 = simulateRun({});
for (const line of r1.log) console.log(line);
console.log(`Result: ${fmt(r1.t)} | wall ${RAID_TIERS[r1.tierIdx].name} w${r1.wave + 1} | ${r1.waves} waves | ${r1.legacy} LP\n`);

console.log('=== RUN 2-3 (Rare ceiling; income x1.5, hero x1.2/x1.2, start 1000g) ===');
const r3 = simulateRun({ treeIncome: 1.5, treePower: 1.2, treeHp: 1.2, startGold: 1000, rarityMult: 2.5 });
for (const line of r3.log.slice(-12)) console.log(line);
console.log(`Result: ${fmt(r3.t)} | wall ${RAID_TIERS[r3.tierIdx].name} w${r3.wave + 1} | ${r3.waves} waves | ${r3.legacy} LP\n`);

console.log('=== Squad-vs-wave win rates (full 6-hero squads G/F front + 2R/2M) ===');
const six = (r, tp, th) => [['guardian', r, tp, th], ['fighter', r, tp, th], ['ranged', r, tp, th], ['ranged', r, tp, th], ['mender', r, tp, th], ['mender', r, tp, th]];
const specs = [
    ['3 commons (run 1 early)', [['guardian', 1, 1, 1], ['ranged', 1, 1, 1], ['mender', 1, 1, 1]]],
    ['6 commons, no tree',      six(1, 1, 1)],
    ['run2: 4C+2R, tree x1.15', [['guardian', 2.5, 1.15, 1.15], ['guardian', 1, 1.15, 1.15], ['ranged', 2.5, 1.15, 1.15], ['ranged', 1, 1.15, 1.15], ['mender', 1, 1.15, 1.15], ['mender', 1, 1.15, 1.15]]],
    ['6 rares, tree x1.2',      six(2.5, 1.2, 1.2)],
    ['run4: 2R+4E, tree x1.4',  [['guardian', 5, 1.4, 1.4], ['guardian', 2.5, 1.4, 1.4], ['ranged', 5, 1.4, 1.4], ['ranged', 5, 1.4, 1.4], ['mender', 5, 1.4, 1.4], ['mender', 2.5, 1.4, 1.4]]],
    ['6 epics, tree x1.6',      six(5, 1.6, 1.6)],
    ['6 legendaries x2.0',      six(10, 2, 2)],
    // Hall of Legends ceiling-mapped rows: the BEST squad money can buy at each
    // cap (min/maxer), with tree ranks plausible for the runs that cap spans.
    // Each row's wall should land ~where the difficulty-arc table expects.
    ['capC r1: 6 com, no tree', six(1, 1, 1)],
    ['capR r2-3: 6 rare x1.2',  six(2.5, 1.2, 1.2)],
    ['capE r4-5: 6 epic x1.5',  six(5, 1.5, 1.5)],
    ['capL r6+: 6 leg x1.8',    six(10, 1.8, 1.8)],
];

// M10 expanded squads (War Banners 12/16 slots + Paladin/Assassin): compare
// against the 6-slot cap rows above to price the expansion nodes on the arc.
const twelve = (r, tp, th) => [
    ['guardian', r, tp, th], ['fighter', r, tp, th], ['paladin', r, tp, th], ['paladin', r, tp, th],
    ['ranged', r, tp, th], ['ranged', r, tp, th], ['assassin', r, tp, th], ['assassin', r, tp, th],
    ['mender', r, tp, th], ['mender', r, tp, th], ['ranged', r, tp, th], ['mender', r, tp, th],
];
const sixteen = (r, tp, th) => [...twelve(r, tp, th),
    ['banneret', r, tp, th], ['battlemage', r, tp, th], ['frostadept', r, tp, th], ['assassin', r, tp, th]];
specs.push(
    ['r3-4: 12 rare+PA x1.3',  twelve(2.5, 1.3, 1.3)],
    ['r5-6: 12 epic+PA x1.5',  twelve(5, 1.5, 1.5)],
    ['r7-8: 16 epic+PA x1.7',  sixteen(5, 1.7, 1.7)],
    ['r9+: 16 leg+PA x2.0',    sixteen(10, 2.0, 2.0)],
);
for (const [label, spec] of specs) {
    const cells = [];
    for (let ti = 0; ti < RAID_TIERS.length; ti++) {
        const t = RAID_TIERS[ti];
        for (const w of [0, Math.floor(t.waveCount / 2), t.waveCount - 1]) {
            const wr = winRate(spec, ti, w);
            cells.push(`${t.name.split(' ')[0].slice(0, 4)}w${w + 1}${w === t.waveCount - 1 ? 'B' : ''}:${Math.round(wr.rate * 100)}%`);
        }
    }
    console.log(label.padEnd(20) + cells.join(' '));
}

// ---------- Final Siege gauntlet (M13 mirror) ----------
// One battle, three phases at waves 18/19/20 of the Infernal tier: hero HP
// carries between phases, the escalation clock resets per phase, blessing
// fires once across the whole gauntlet. Kingdom HP is the carry-over buffer.
const FINAL_SIEGE_PHASES = [
    { wave: 14, comp: ['brute 0 0', 'brute 0 1', 'brute 0 2', 'brute 0 3', 'skirmisher 1 0', 'skirmisher 1 3', 'caster 1 1', 'shaman 1 2', 'shaman 2 1', 'sapper 2 2'] },
    { wave: 16, comp: ['brute 0 0', 'brute 0 1', 'brute 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2', 'sapper 2 0', 'sapper 2 3'] },
    { wave: 18, comp: ['BOSS 0 1', 'brute 0 0', 'brute 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1', 'shaman 1 2', 'sapper 2 1', 'sapper 2 2'] },
];

function siegePhaseSquad(phaseDef) {
    const t = RAID_TIERS[4];
    const mult = waveMult(4, phaseDef.wave);
    const squad = [];
    for (const entry of phaseDef.comp) {
        const [key, r, c] = entry.split(' ');
        const isBoss = key === 'BOSS';
        const aKey = isBoss ? 'brute' : key;
        const a = ENEMY_ARCHETYPES[aKey];
        const pMult = mult * (isBoss ? t.boss.powerMult : 1);
        const hMult = Math.sqrt(mult) * (isBoss ? t.boss.hpMult : 1);
        const attack = a.attack ? { power: Math.round(a.attack.power * pMult), speed: a.attack.speed } : null;
        const heal = a.heal ? { power: Math.round(a.heal.power * pMult), speed: a.heal.speed } : null;
        const unit = makeUnit(isBoss ? t.boss.name : aKey, a.defense, Math.round(a.hp * hMult), Number(r), Number(c), 'enemy', attack, heal, a.backlineChance);
        if (a.targetsKingdom) unit.targetsKingdom = true;
        const traits = { ...(t.traits[aKey] || {}), ...(isBoss ? t.boss.traits : {}) };
        if (traits.backlineChance !== undefined) unit.backlineChance = traits.backlineChance;
        if (traits.enrage) unit.enrage = traits.enrage;
        if (traits.reviveCharges) unit.reviveCharges = traits.reviveCharges;
        if (traits.aura) unit.aura = traits.aura;
        if (traits.aoe && unit.attack) unit.attack.aoe = traits.aoe;
        squad.push(unit);
    }
    return squad;
}

// Endgame kingdom defaults: Reinforced Walls maxed (2000 HP, and since M14.1
// +3 Kingdom defense per rank -> 15+12=27) and a Realm-level Builder corps
// (8 slots, uncapped rarity, Master Builders) ~25 hp/s regen.
function finalSiegeRate(squadSpec, trials = 60, doctrines = null, regen = 25, khpMax = 2000, kdef = 27) {
    let wins = 0;
    const saved = DOCTRINES;
    const savedKdef = CFG.KINGDOM_DEFENSE;
    CFG.KINGDOM_DEFENSE = kdef;
    if (doctrines) DOCTRINES = { ...saved, ...doctrines };
    for (let i = 0; i < trials; i++) {
        blessingUsed = false;
        const heroes = squadSpec.map(([k, r, tp, th]) => makeHero(k, r, tp, th));
        assignHeroCols(heroes);
        let khp = khpMax, dead = false;
        for (const phase of FINAL_SIEGE_PHASES) {
            const enemies = siegePhaseSquad(phase);
            let ticks = 0;
            while (ticks++ < 600) {
                khp = Math.min(khpMax, khp + regen);
                khp -= combatTick(heroes, enemies, () => khp > 0, escMultAt(ticks), ticks);
                if (khp <= 0) { dead = true; break; }
                if (!enemies.some(e => e.alive)) break;
            }
            if (dead || ticks >= 600) { dead = true; break; }
        }
        if (!dead) wins++;
    }
    DOCTRINES = saved;
    CFG.KINGDOM_DEFENSE = savedKdef;
    return wins / trials;
}

// Realm-level doctrine values: 7 Smithies x1.5% = x1.105 attack, 6 Libraries
// x1% = x1.06 speed, 4 Apothecaries x0.3% = 1.2%/s salves, blessing on.
const REALM_DOCTRINES = { attack: 1.105, speed: 1.06, salves: 0.012, blessing: true };

// M12 verification: doctrines must open the final boss for the endgame squad.
console.log('\n=== M12 doctrine check (16-slot squads + Realm doctrines) ===');
for (const [label, spec, ti, w] of [
    ['16 epic x1.7 vs Undead boss',   sixteen(5, 1.7, 1.7), 3, 13],
    ['16 epic x1.7 vs Inf w9',     sixteen(5, 1.7, 1.7), 4, 8],
    ['16 leg x2.0 vs Inf w9',      sixteen(10, 2, 2), 4, 8],
    ['16 leg x2.0 vs Inf w17 BOSS', sixteen(10, 2, 2), 4, 16],
]) {
    const bare = winRate(spec, ti, w, 60);
    const doc = winRate(spec, ti, w, 60, REALM_DOCTRINES);
    console.log(`${label.padEnd(28)} no doctrines: ${String(Math.round(bare.rate * 100)).padStart(3)}%   with doctrines: ${String(Math.round(doc.rate * 100)).padStart(3)}%`);
}

// ---------- Campaign-arc verification (M14) ----------
// For each run's arc-expected squad, walk the ladder to the first wave under
// a 50% win rate ("the wall") and compare to the difficulty-arc table target.
// Rows are strictly stronger than their predecessors, so each scan starts at
// the previous wall.
function findWall(spec, doctrines, startTier = 0, startWave = 0, trials = 16) {
    for (let ti = startTier; ti < RAID_TIERS.length; ti++) {
        const start = ti === startTier ? startWave : 0;
        for (let w = start; w < RAID_TIERS[ti].waveCount; w++) {
            const wr = winRate(spec, ti, w, trials, doctrines);
            if (wr.rate < 0.5) return { tier: ti, wave: w, rate: wr.rate };
        }
    }
    return null; // cleared the entire ladder
}

console.log('\n=== M14 campaign-arc check (wall = first wave under 50%) ===');
const fourC2R = tp => [['guardian', 2.5, tp, tp], ['fighter', 1, tp, tp], ['ranged', 2.5, tp, tp], ['ranged', 1, tp, tp], ['mender', 1, tp, tp], ['mender', 1, tp, tp]];
const ARC_RUNS = [
    ['run 1',  'Goblin boss-Orc w5',   six(1, 1, 1), null],
    ['run 2',  'Orc w3-5',             fourC2R(1.15), null],
    ['run 3',  'Orc boss-Bandit w2',   six(2.5, 1.2, 1.2), null],
    ['run 4',  'Bandit w6-8',          twelve(2.5, 1.3, 1.3), { attack: 1.06 }],
    ['run 5',  'Bandit boss-Undead w3',  twelve(5, 1.4, 1.4), { attack: 1.06 }],
    ['run 6',  'Undead w7-10',           twelve(5, 1.5, 1.5), { attack: 1.06, speed: 1.05 }],
    ['run 7',  'Undead boss-Infernal w4', sixteen(5, 1.6, 1.6), { attack: 1.08, speed: 1.05, blessing: true }],
    ['run 8',  'Infernal w9-13',       sixteen(10, 1.8, 1.8), { attack: 1.09, speed: 1.06, salves: 0.009, blessing: true }],
    ['run 9',  'Infernal boss (w17)',  sixteen(10, 2, 2), REALM_DOCTRINES],
];
let scanTier = 0, scanWave = 0;
for (const [run, target, spec, doc] of ARC_RUNS) {
    const wall = findWall(spec, doc, scanTier, scanWave);
    if (wall) {
        const t = RAID_TIERS[wall.tier];
        const isBoss = wall.wave === t.waveCount - 1;
        console.log(`${run.padEnd(7)} target: ${target.padEnd(22)} sim wall: ${t.name} w${wall.wave + 1}${isBoss ? ' BOSS' : ''} (${Math.round(wall.rate * 100)}%)`);
        scanTier = wall.tier; scanWave = wall.wave;
    } else {
        console.log(`${run.padEnd(7)} target: ${target.padEnd(22)} sim wall: NONE — clears the ladder`);
    }
}

console.log('\n=== M13 Final Siege gauntlet (3 phases, HP carries, blessing once) ===');
for (const [label, spec, doc] of [
    ['16 epic x1.7 + doctrines', sixteen(5, 1.7, 1.7), REALM_DOCTRINES],
    ['16 leg x2.0, no doctrines', sixteen(10, 2, 2), null],
    ['16 leg x2.0 + doctrines',  sixteen(10, 2, 2), REALM_DOCTRINES],
]) {
    console.log(`${label.padEnd(28)} win ${Math.round(finalSiegeRate(spec, 60, doc) * 100)}%`);
}

console.log('\n=== Fair-fight win durations (median s; must sit under the ' + CFG.SIEGE_ESCALATION_GRACE + 's escalation grace) ===');
const fairFights = [
    ['3 commons vs Gobl w1',   [['guardian', 1, 1, 1], ['ranged', 1, 1, 1], ['mender', 1, 1, 1]], 0, 0],
    ['6 commons vs Gobl boss', six(1, 1, 1), 0, 4],
    ['6 commons vs Orc w4',    six(1, 1, 1), 1, 3],
    ['6 rares vs Orc boss',    six(2.5, 1.2, 1.2), 1, 7],
    ['6 rares vs Band w6',     six(2.5, 1.2, 1.2), 2, 5],
    ['6 epics vs Band boss',   six(5, 1.5, 1.5), 2, 10],
    ['6 epics vs Undead w7',     six(5, 1.5, 1.5), 3, 6],
    ['6 legs vs Undead boss',    six(10, 1.8, 1.8), 3, 13],
    ['6 legs vs Inf w9',      six(10, 1.8, 1.8), 4, 8],
];
for (const [label, spec, ti, w] of fairFights) {
    const wr = winRate(spec, ti, w, 60);
    console.log(`${label.padEnd(24)} win ${String(Math.round(wr.rate * 100)).padStart(3)}%  median win ${wr.medWin === null ? '  --' : String(wr.medWin).padStart(4)}s`);
}

console.log('\n=== Stalemate/grind check (endless siege + continuous rehires) ===');
console.log('Playtest scenario: common-capped heroes, Empire-grade economy (400 g/s, 6 hp/s regen).');
const grinds = [
    ['Orc boss   (w8)',  1, 7],
    ['Bandit w1',        2, 0],
    ['Bandit w3',        2, 2],
    ['Bandit w6',        2, 5],
    ['Bandit boss (w11)', 2, 10],
];
for (const [label, ti, w] of grinds) {
    const off = grindBattle({ tierIdx: ti, wave: w, escalation: false });
    const on = grindBattle({ tierIdx: ti, wave: w, escalation: true });
    console.log(`common vs ${label.padEnd(18)} esc OFF: ${off.outcome.padEnd(9)} ${fmt(off.t)} (${off.hired} hires) | esc ON: ${on.outcome.padEnd(9)} ${fmt(on.t)} (${on.hired} hires)`);
}
console.log('Rare-capped squad, same economy:');
for (const [label, ti, w] of [['Bandit w6', 2, 5], ['Bandit boss (w11)', 2, 10], ['Undead w3', 3, 2]]) {
    const on = grindBattle({ tierIdx: ti, wave: w, rarityMult: 2.5, escalation: true });
    console.log(`rare   vs ${label.padEnd(18)} esc ON: ${on.outcome.padEnd(9)} ${fmt(on.t)} (${on.hired} hires)`);
}
