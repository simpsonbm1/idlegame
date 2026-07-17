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
};

// Enemy attack multiplier after s seconds of one battle (mirror of game.js
// escalationMult — applies to enemy attacks only, never heals).
function escMultAt(s) {
    const past = s - CFG.SIEGE_ESCALATION_GRACE;
    return past > 0 ? 1 + past * CFG.SIEGE_ESCALATION_RATE : 1;
}

// waveCount includes the boss wave (last index). powerMult chains from the
// previous tier's boss multiplier; growth 1.088/wave, continuous ladder.
const RAID_TIERS = [
    { name: 'Goblin Raid',  powerMult: 1.0,  growth: 1.088, waveCount: 5,  raidInterval: 45, baseLoot: 1200,    lootGrowth: 1.10,
      boss: { name: 'Goblin Warmaster', powerMult: 1.8, hpMult: 4.0 } },
    { name: 'Orc Warband',  powerMult: 1.52, growth: 1.088, waveCount: 8,  raidInterval: 45, baseLoot: 5000,   lootGrowth: 1.10,
      boss: { name: 'Orc Warlord', powerMult: 1.8, hpMult: 4.0 } },
    { name: 'Bandit Horde', powerMult: 3.0,  growth: 1.088, waveCount: 11, raidInterval: 40, baseLoot: 30000,  lootGrowth: 1.10,
      boss: { name: 'Bandit King', powerMult: 1.8, hpMult: 4.0 } },
    { name: 'Dark Army',    powerMult: 7.6,  growth: 1.088, waveCount: 14, raidInterval: 35, baseLoot: 120000, lootGrowth: 1.10,
      boss: { name: 'Lich Commander', powerMult: 1.8, hpMult: 4.0 } },
    { name: 'Dragon Siege', powerMult: 24.7, growth: 1.088, waveCount: 17, raidInterval: 30, baseLoot: 500000, lootGrowth: 1.10,
      boss: { name: 'Dragon Empress', powerMult: 1.8, hpMult: 4.0 } },
];

// ~30% softer than live values: the tutorial wave must be winnable by a few
// commons; the ladder growth carries the difficulty.
const ENEMY_ARCHETYPES = {
    brute:      { defense: 20, hp: 90, attack: { power: 10, speed: 0.7 } },
    skirmisher: { defense: 8,  hp: 55, attack: { power: 13, speed: 1.1 }, backlineChance: 0.4 },
    caster:     { defense: 5,  hp: 45, attack: { power: 14, speed: 0.9 } },
    shaman:     { defense: 8,  hp: 50, heal: { power: 10, speed: 0.7 } },
};

const HERO_ARCHETYPES = {
    guardian: { baseCost: 1000, defense: 35, hp: 140, attack: { power: 8,  speed: 0.7 } },
    ranged:   { baseCost: 750, defense: 5,  hp: 60,  attack: { power: 18, speed: 1.3 } },
    mender:   { baseCost: 850, defense: 5,  hp: 55,  heal:   { power: 20, speed: 0.7 } },
    // M10 unlockable archetypes
    paladin:  { baseCost: 1300, defense: 25, hp: 120, attack: { power: 9, speed: 0.7 }, heal: { power: 11, speed: 0.55 } },
    assassin: { baseCost: 950,  defense: 3,  hp: 45,  attack: { power: 26, speed: 1.2 }, backlineChance: 0.9 },
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

// ---------- Combat engine (ported from game.js) ----------
function makeUnit(name, defense, hp, row, side, attack, heal, backlineChance) {
    return {
        name, defense, hp, maxHp: hp, row, side,
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

function generateEnemySquad(tierIdx, wave) {
    const t = RAID_TIERS[tierIdx];
    const mult = waveMult(tierIdx, wave);
    const mk = (key, row, pMult = 1, hMult = 1) => {
        const a = ENEMY_ARCHETYPES[key];
        const attack = a.attack ? { power: Math.round(a.attack.power * mult * pMult), speed: a.attack.speed } : null;
        const heal = a.heal ? { power: Math.round(a.heal.power * mult * pMult), speed: a.heal.speed } : null;
        return makeUnit(key, a.defense, Math.round(a.hp * Math.sqrt(mult) * hMult), row, 'enemy', attack, heal, a.backlineChance);
    };
    const isBoss = wave === t.waveCount - 1;
    if (isBoss) {
        const b = mk('brute', 0, t.boss.powerMult, t.boss.hpMult);
        b.name = t.boss.name;
        return [b, mk('brute', 0), mk('skirmisher', 0), mk('shaman', 1)];
    }
    return [mk('brute', 0), mk('skirmisher', 0), mk('caster', 1), mk('shaman', 1)];
}

function makeHero(key, rarityMult, treePower = 1, treeHp = 1) {
    const a = HERO_ARCHETYPES[key];
    const attack = a.attack ? { power: Math.round(a.attack.power * rarityMult * treePower), speed: a.attack.speed } : null;
    const heal = a.heal ? { power: Math.round(a.heal.power * rarityMult * treePower), speed: a.heal.speed } : null;
    const row = (key === 'guardian' || key === 'paladin') ? 0 : 1;
    return makeUnit(key, a.defense, Math.round(a.hp * Math.sqrt(rarityMult) * treeHp), row, 'hero', attack, heal, a.backlineChance);
}

// Mirror of game.js pickTarget (generalized to N rows in M10): frontmost
// occupied row is the front, everything behind is the backline pool.
function pickTarget(attacker, squad) {
    const alive = squad.filter(u => u && u.alive);
    if (!alive.length) return null;
    const frontRow = Math.min(...alive.map(u => u.row));
    const front = alive.filter(u => u.row === frontRow);
    const back = alive.filter(u => u.row > frontRow);
    if (!back.length) return front[Math.floor(Math.random() * front.length)];
    const pool = Math.random() < attacker.backlineChance ? back : front;
    return pool[Math.floor(Math.random() * pool.length)];
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

// Runs one game-second of combat. Returns kingdom damage dealt this tick.
// escMult scales enemy attack power only (siege escalation).
function combatTick(heroes, enemies, kingdomAlive, escMult = 1) {
    let kingdomDmg = 0;
    for (const u of [...heroes, ...enemies]) {
        if (!u || !u.alive) continue;
        if (u.attack) {
            u.attack.cooldown -= 1000;
            while (u.attack.cooldown <= 0) {
                if (u.side === 'hero') {
                    const t = pickTarget(u, enemies);
                    if (t) { t.hp -= dmg(u.attack.power, t.defense); if (t.hp <= 0) { t.hp = 0; t.alive = false; } }
                } else if (heroes.some(h => h && h.alive)) {
                    const t = pickTarget(u, heroes);
                    if (t) { t.hp -= dmg(u.attack.power * escMult, t.defense); if (t.hp <= 0) { t.hp = 0; t.alive = false; } }
                } else if (kingdomAlive()) {
                    kingdomDmg += dmg(u.attack.power * escMult, CFG.KINGDOM_DEFENSE);
                }
                u.attack.cooldown += CFG.BASE_ATTACK_INTERVAL / u.attack.speed;
            }
        }
        if (u.heal) {
            u.heal.cooldown -= 1000;
            if (u.heal.cooldown <= 0) {
                const t = pickHealTarget(u.side === 'hero' ? heroes : enemies);
                if (t) { t.hp = Math.min(t.maxHp, t.hp + u.heal.power); u.heal.cooldown += CFG.BASE_ATTACK_INTERVAL / u.heal.speed; }
            }
        }
        // dead heroes free their slot at moment of death (M8 rule) -- modeled
        // by the alive flag; slot reuse handled by the hire logic outside.
    }
    return kingdomDmg;
}

// ---------- Run-1 player simulation ----------
function simulateRun({ treeIncome = 1, treePower = 1, treeHp = 1, startGold = 50, rarityMult = 1, verbose = true } = {}) {
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
    const heroCost = key => HERO_ARCHETYPES[key].baseCost * (rarityMult === 1 ? 1 : rarityMult === 2.5 ? 3 : rarityMult === 5 ? 8 : 20);
    const wantHeroes = ['guardian', 'ranged', 'mender', 'guardian', 'ranged', 'mender'];
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
                kingdomHP -= combatTick(heroes, battle, () => kingdomHP > 0, escMultAt(battleT));
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
                    for (const h of heroes) { h.hp = h.maxHp; h.alive = true; if (h.attack) h.attack.cooldown = CFG.BASE_ATTACK_INTERVAL / h.attack.speed; if (h.heal) h.heal.cooldown = CFG.BASE_ATTACK_INTERVAL / h.heal.speed; }
                }
            }
        }
    }
    return { t, tierIdx, wave, waves, legacy, income, log, timeout: true };
}

function fmt(s) { return `${String(Math.floor(s / 60)).padStart(3)}m${String(s % 60).padStart(2, '0')}`; }

// ---------- Squad-vs-wave win-rate table (deeper-run sanity check) ----------
function winRate(squadSpec, tierIdx, wave, trials = 40) {
    let wins = 0;
    const winTimes = [];
    for (let i = 0; i < trials; i++) {
        const heroes = squadSpec.map(([k, r, tp, th]) => makeHero(k, r, tp, th));
        const enemies = generateEnemySquad(tierIdx, wave);
        let khp = CFG.KINGDOM_HP_MAX, ticks = 0;
        while (ticks++ < 600) {
            khp -= combatTick(heroes, enemies, () => khp > 0, escMultAt(ticks));
            if (khp <= 0) break;
            if (!enemies.some(e => e.alive)) { wins++; winTimes.push(ticks); break; }
        }
    }
    winTimes.sort((a, b) => a - b);
    return { rate: wins / trials, medWin: winTimes.length ? winTimes[Math.floor(winTimes.length / 2)] : null };
}

// ---------- Stalemate/grind check (the 2026-07-17 playtest scenario) ----------
// One endless siege: a 6-slot squad continuously refilled from income while
// the Kingdom regenerates behind it. Without escalation, a healer-led wave the
// squad can't out-damage stalemates forever (the playtest soft-lock); with it,
// the siege must resolve as WIN or OVERRUN.
function grindBattle({ tierIdx, wave, rarityMult = 1, income = 400, regen = 6, hireDelay = 6, escalation = true, maxSeconds = 3600 }) {
    const costMult = rarityMult === 1 ? 1 : rarityMult === 2.5 ? 3 : rarityMult === 5 ? 8 : 20;
    const want = ['guardian', 'ranged', 'mender'];
    // Real walls are hit with a full squad standing and a deep wallet — the
    // previous wave was just won. Rehires then drip in against attrition.
    let gold = 20000, khp = CFG.KINGDOM_HP_MAX, cd = 0, hired = 0;
    let heroes = [0, 1, 2, 3, 4, 5].map(i => makeHero(want[i % want.length], rarityMult));
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
        }
        khp -= combatTick(heroes, enemies, () => khp > 0, escalation ? escMultAt(t) : 1);
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

console.log('=== Squad-vs-wave win rates (full 6-hero squads 2G/2R/2M) ===');
const six = (r, tp, th) => [['guardian', r, tp, th], ['guardian', r, tp, th], ['ranged', r, tp, th], ['ranged', r, tp, th], ['mender', r, tp, th], ['mender', r, tp, th]];
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
    ['guardian', r, tp, th], ['guardian', r, tp, th], ['paladin', r, tp, th], ['paladin', r, tp, th],
    ['ranged', r, tp, th], ['ranged', r, tp, th], ['assassin', r, tp, th], ['assassin', r, tp, th],
    ['mender', r, tp, th], ['mender', r, tp, th], ['ranged', r, tp, th], ['mender', r, tp, th],
];
const sixteen = (r, tp, th) => [...twelve(r, tp, th),
    ['guardian', r, tp, th], ['paladin', r, tp, th], ['ranged', r, tp, th], ['assassin', r, tp, th]];
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

console.log('\n=== Fair-fight win durations (median s; must sit under the ' + CFG.SIEGE_ESCALATION_GRACE + 's escalation grace) ===');
const fairFights = [
    ['3 commons vs Gobl w1',   [['guardian', 1, 1, 1], ['ranged', 1, 1, 1], ['mender', 1, 1, 1]], 0, 0],
    ['6 commons vs Gobl boss', six(1, 1, 1), 0, 4],
    ['6 commons vs Orc w4',    six(1, 1, 1), 1, 3],
    ['6 rares vs Orc boss',    six(2.5, 1.2, 1.2), 1, 7],
    ['6 rares vs Band w6',     six(2.5, 1.2, 1.2), 2, 5],
    ['6 epics vs Band boss',   six(5, 1.5, 1.5), 2, 10],
    ['6 epics vs Dark w7',     six(5, 1.5, 1.5), 3, 6],
    ['6 legs vs Dark boss',    six(10, 1.8, 1.8), 3, 13],
    ['6 legs vs Drag w9',      six(10, 1.8, 1.8), 4, 8],
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
for (const [label, ti, w] of [['Bandit w6', 2, 5], ['Bandit boss (w11)', 2, 10], ['Dark w3', 3, 2]]) {
    const on = grindBattle({ tierIdx: ti, wave: w, rarityMult: 2.5, escalation: true });
    console.log(`rare   vs ${label.padEnd(18)} esc ON: ${on.outcome.padEnd(9)} ${fmt(on.t)} (${on.hired} hires)`);
}
