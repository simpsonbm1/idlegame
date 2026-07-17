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
let confirmingNewAge = false;
let runEnded = false;
let runSummary = null;
let runLegacyEarned = 0;
let runWavesCleared = 0;
let buyQuantity = 1;
let autoRecruitRarity = null;
let runTime = 0; // game-seconds since this Age began — the clock resident injuries expire against
let finalSiegeCountdown = -1; // -1 inactive · 3..1 raids remaining · 0 the Final Siege is due
let victoryPending = false;   // campaign won, victory screen up, world frozen until Endless
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

const RAID_TRIGGER_LEVEL = 2;
const RAID_TRIGGER_GOLD = 4000;
// Extra breathing room before the very first raid ever arrives — the player
// needs time to hire their first heroes. Later raids use the tier's interval.
const FIRST_RAID_GRACE = 75;

// Bump when a rebalance makes old saves meaningless; mismatched saves are
// discarded on load (fresh start).
const SAVE_VERSION = 4;

// Dev build flag: keeps testing conveniences (auto-hire without the Steward's
// Ledger upgrade, dev speed buttons) always available. Flip to false for a
// release build.
const DEV_MODE = true;

const BASE_ATTACK_INTERVAL = 2500;
const DEFAULT_BACKLINE_CHANCE = 0.15;

// Siege escalation: past the grace period, enemy attacks grow stronger every
// second the battle drags on, so an unwinnable siege eventually overwhelms the
// Kingdom instead of stalemating forever. (2026-07-17 playtest: enemy healers
// + cheap rehires + Builder regen made wall waves a permanent stalemate inside
// one endless battle — neither Repelled nor Overrun could ever occur.)
const SIEGE_ESCALATION_GRACE = 60;  // game-seconds of battle before escalation begins
const SIEGE_ESCALATION_RATE = 0.01; // +1% enemy attack power per second past the grace

// Sappers (M11): each hit they land on the Kingdom has a chance to injure a
// random staffed resident — income/regen paused until they recover. Residents
// are never killed (losing a lucky roll permanently would be brutal).
const SAPPER_INJURY_CHANCE = 0.25;
const INJURY_DURATION = 90; // game-seconds until an injured resident recovers

// Row-AoE attacks (Battlemage, dragon breath) hit every unit in the row at a
// discount — otherwise AoE is strictly multiplicative and the deep ladder
// becomes unwinnable (sim: 16 legendaries scored 0% on the final boss at 1.0).
const AOE_POWER_FACTOR = 0.65;

// Tiers form one continuous 55-wave ladder: each tier's powerMult picks up
// where the previous tier's boss left off (defenseGrowth 1.088/wave, so the
// final boss lands ~95x goblin wave 1 — no stat cliffs at tier transitions).
// waveCount includes the boss wave (the tier's last wave); killing the boss
// advances to the next tier. Tiers are climbed by boss-kill only — kingdom
// level no longer selects the raid tier.
// M11: each tier carries its battle grid, per-archetype trait overrides (the
// tier's tactical lesson), and a boss with a signature ability (boss.traits).
const RAID_TIERS = [
    { name: 'Goblin Raid',  powerMult: 1.0,  defenseGrowth: 1.088, waveCount: 5,  raidInterval: 45, baseLoot: 1200,   lootGrowth: 1.10,
        grid: { rows: 2, cols: 3 }, traits: {},
        boss: { name: 'Goblin Warmaster', powerMult: 1.8, hpMult: 4.0, traits: { aura: { power: 0.15, range: 'all' } } },
        roster: { brute: 'Goblin Brute',    skirmisher: 'Goblin Skulker',   caster: 'Goblin Slinger',  shaman: 'Goblin Shaman',  sapper: 'Goblin Tunneler' } },
    { name: 'Orc Warband',  powerMult: 1.52, defenseGrowth: 1.088, waveCount: 8,  raidInterval: 45, baseLoot: 5000,   lootGrowth: 1.10,
        grid: { rows: 2, cols: 3 }, traits: { brute: { enrage: { speed: 1.5, power: 1 } } },
        boss: { name: 'Orc Warlord', powerMult: 1.8, hpMult: 4.0, traits: { enrage: { speed: 1.75, power: 1.25 } } },
        roster: { brute: 'Orc Brute',       skirmisher: 'Orc Berserker',    caster: 'Orc Warcaster',   shaman: 'Orc Witch Doctor', sapper: 'Orc Saboteur' } },
    { name: 'Bandit Horde', powerMult: 3.0,  defenseGrowth: 1.088, waveCount: 11, raidInterval: 40, baseLoot: 30000,  lootGrowth: 1.10,
        grid: { rows: 3, cols: 4 }, traits: { caster: { backlineChance: 0.7 } },
        boss: { name: 'Bandit King', powerMult: 1.8, hpMult: 4.0, traits: { backlineChance: 0.85 } },
        roster: { brute: 'Bandit Enforcer', skirmisher: 'Bandit Cutthroat', caster: 'Bandit Marksman', shaman: 'Bandit Medic',   sapper: 'Bandit Torchman' } },
    { name: 'Dark Army',    powerMult: 7.6,  defenseGrowth: 1.088, waveCount: 14, raidInterval: 35, baseLoot: 120000, lootGrowth: 1.10,
        grid: { rows: 3, cols: 4 }, traits: { caster: { reviveCharges: 1 } },
        boss: { name: 'Lich Commander', powerMult: 1.8, hpMult: 4.0, traits: { reviveCharges: 2 } },
        roster: { brute: 'Death Knight',    skirmisher: 'Shadow Reaver',    caster: 'Necromancer',     shaman: 'Bone Priest',    sapper: 'Grave Digger' } },
    { name: 'Dragon Siege', powerMult: 24.7, defenseGrowth: 1.088, waveCount: 17, raidInterval: 30, baseLoot: 500000, lootGrowth: 1.10,
        grid: { rows: 4, cols: 4 }, traits: { caster: { aoe: 'row' } },
        boss: { name: 'Dragon Empress', powerMult: 1.8, hpMult: 4.0, traits: { aoe: 'row', enrage: { speed: 1, power: 1.25 } } },
        roster: { brute: 'Dragon Guard',    skirmisher: 'Wyrmling',         caster: 'Dragon Mage',     shaman: 'Dragonpriest',   sapper: 'Cinder Imp' } }
];

// Hand-authored wave compositions ("archetype row col"; 'BOSS r c' is the
// tier's named boss). Deterministic — a repeated wave is the same fight.
// Waves fill more of the grid as they climb, with variety mixes (double-brute,
// skirmisher swarm, twin-healer, sapper raids from Bandit tier on).
const TIER_WAVES = [
    [ // Goblin Raid (2x3)
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1', 'caster 1 2'],
        ['BOSS 0 1', 'brute 0 0', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1']
    ],
    [ // Orc Warband (2x3)
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'shaman 1 1'],
        ['skirmisher 0 0', 'skirmisher 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'caster 1 0', 'caster 1 2', 'shaman 1 1'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1'],
        ['brute 0 0', 'skirmisher 0 1', 'shaman 1 0', 'caster 1 1', 'shaman 1 2'],
        ['brute 0 0', 'brute 0 1', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1', 'shaman 1 2'],
        ['BOSS 0 1', 'brute 0 0', 'skirmisher 0 2', 'caster 1 0', 'shaman 1 1', 'shaman 1 2']
    ],
    [ // Bandit Horde (3x4) — marksmen hunt the backline, medics wall, sappers raid the town
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
    [ // Dark Army (3x4) — necromancers raise the fallen: kill order matters
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
    [ // Dragon Siege (4x4) — mages breathe on whole rows: split your formation
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

// --- The Final Siege (M13) ---
// After the Dragon Empress falls (first time only), a herald announces the
// Final Siege: 3 raids of prep, then a 3-phase gauntlet. One invasion, three
// squads: heroes do NOT reset HP between phases (menders/Blessing showcase),
// the escalation clock resets per phase, Kingdom HP is the carry-over buffer.
const FINAL_SIEGE_COUNTDOWN_RAIDS = 3;
const LESSONS_LEGACY = 25000; // once-per-campaign bonus for a LOST Final Siege attempt
// Phase waves tuned in the sim (14/16/18): the gauntlet's difficulty comes
// from being ONE battle — carried hero damage across phases — not from
// out-statting the w17 boss the player just proved they could kill. Sim: the
// endgame squad (16 legendaries + Realm doctrines) wins ~38%/attempt; without
// doctrines 0% — run 9 loses (Lessons bonus), run 10 wins, per the arc.
const FINAL_SIEGE_PHASES = [
    { name: 'The Vanguard', wave: 14, comp: [
        'brute 0 0', 'brute 0 1', 'brute 0 2', 'brute 0 3', 'skirmisher 1 0', 'skirmisher 1 3',
        'caster 1 1', 'shaman 1 2', 'shaman 2 1', 'sapper 2 2'] },
    { name: 'The Elite Guard', wave: 16, comp: [
        'brute 0 0', 'brute 0 1', 'brute 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1',
        'shaman 1 2', 'sapper 2 0', 'sapper 2 3'] },
    { name: 'The Empress Ascendant', wave: 18, comp: [
        'BOSS 0 1', 'brute 0 0', 'brute 0 2', 'caster 1 0', 'caster 1 3', 'shaman 1 1',
        'shaman 1 2', 'sapper 2 1', 'sapper 2 2'] }
];

const ENEMY_ARCHETYPES = {
    brute:      { base: { defense: 20, hp: 90, attack: { power: 10, speed: 0.7 } } },
    skirmisher: { base: { defense: 8,  hp: 55, attack: { power: 13, speed: 1.1 }, backlineChance: 0.4 } },
    caster:     { base: { defense: 5,  hp: 45, attack: { power: 14, speed: 0.9 } } },
    shaman:     { base: { defense: 8,  hp: 50, heal: { power: 10, speed: 0.7 } } },
    // Sappers ignore the hero squad entirely and attack the Kingdom itself,
    // with a chance to injure residents — the town is part of the battle.
    sapper:     { base: { defense: 10, hp: 65, attack: { power: 8, speed: 0.8 }, targetsKingdom: true } }
};

// Archetypes with an `unlock` field only appear in the hero pool once that
// Military-tree node is owned (M10: Paladin, Assassin).
const HERO_ARCHETYPES = {
    guardian: { names: ['Knight', 'Sentinel', 'Vanguard', 'Paragon'],    baseCost: 1000, base: { defense: 35, hp: 140, attack: { power: 8,  speed: 0.7 } } },
    ranged:   { names: ['Archer', 'Sharpshooter', 'Hunter', 'Marksman'], baseCost: 750,  base: { defense: 5,  hp: 60,  attack: { power: 18, speed: 1.3 } } },
    mender:   { names: ['Acolyte', 'Cleric', 'Druid', 'Saint'],          baseCost: 850,  base: { defense: 5,  hp: 55,  heal:   { power: 20, speed: 0.7 } } },
    paladin:  { names: ['Squire', 'Paladin', 'Crusader', 'Highlord'],    baseCost: 1300, unlock: 'paladin',
                base: { defense: 25, hp: 120, attack: { power: 9, speed: 0.7 }, heal: { power: 11, speed: 0.55 } } },
    assassin: { names: ['Rogue', 'Assassin', 'Nightblade', 'Phantom'],   baseCost: 950,  unlock: 'assassin',
                base: { defense: 3,  hp: 45,  attack: { power: 26, speed: 1.2 }, backlineChance: 0.9 } },
    // M11 archetypes exercising the new engine features. Banneret's aura and
    // Frost Adept's chill are fixed effects — rarity scales their own stats.
    battlemage: { names: ['Adept', 'Battlemage', 'Warmage', 'Archmage'], baseCost: 1600, unlock: 'battlemage',
                base: { defense: 8,  hp: 70,  attack: { power: 12, speed: 0.8, aoe: 'row' } } },
    banneret: { names: ['Herald', 'Banneret', 'Marshal', 'High Marshal'], baseCost: 1500, unlock: 'banneret',
                base: { defense: 25, hp: 110, attack: { power: 6, speed: 0.6 }, aura: { power: 0.15, range: 'adjacent' } } },
    frostadept: { names: ['Frost Apprentice', 'Frost Adept', 'Rimecaller', "Winter's Voice"], baseCost: 1400, unlock: 'frost',
                base: { defense: 6,  hp: 65,  attack: { power: 10, speed: 1.0, chill: { mult: 1.35, duration: 6 } } } }
};

function isBossWave(tierIndex, wave) {
    return wave === RAID_TIERS[tierIndex].waveCount - 1;
}

function getRaidInterval() {
    return RAID_TIERS[raidTierIndex].raidInterval;
}

function getInvasionName(tierIndex, wave) {
    const tier = RAID_TIERS[tierIndex];
    if (isBossWave(tierIndex, wave)) return `${tier.name} — ${tier.boss.name}`;
    return wave === 0 ? tier.name : `${tier.name} (Wave ${wave + 1})`;
}

function getInvasionLoot(tierIndex, streak) {
    const tier = RAID_TIERS[tierIndex];
    return Math.floor(tier.baseLoot * Math.pow(tier.lootGrowth, streak));
}

// --- Legacy (meta currency) & permanent upgrades ---
// Meta state lives in its own localStorage key and survives "Found a New Age"
// resets. Wiped only by the full dev reset.
const META_SAVE_KEY = 'idleKingdomMeta';

// Full first-clear value per wave, by raid tier (~5x per tier). Re-clearing an
// already-credited wave pays only the trickle fraction, so restart-farming
// early waves is pointless next to pushing the all-time frontier.
const WAVE_LEGACY_VALUES = [10, 50, 250, 1250, 6250];
const REPEAT_LEGACY_FRACTION = 0.15;
const BOSS_LEGACY_MULT = 4; // "breakthrough" bonus for boss waves

let meta = defaultMeta();

function defaultMeta() {
    return {
        age: 1,
        legacy: 0,
        // Per-tier high-water mark: number of waves ever credited at full value.
        waveCredit: RAID_TIERS.map(() => 0),
        upgrades: {},
        fallHistory: [],
        lessonsGranted: false, // Lessons of the Last Siege paid out (once per campaign)
        victory: false,        // the Final Siege has been won — endless mode unlocked
        gameSeconds: 0         // lifetime game-time across all Ages (victory-screen stat)
    };
}

function saveMeta() {
    localStorage.setItem(META_SAVE_KEY, JSON.stringify({ version: SAVE_VERSION, ...meta }));
}

function loadMeta() {
    const saved = localStorage.getItem(META_SAVE_KEY);
    if (!saved) return;
    const state = JSON.parse(saved);
    if ((state.version ?? 1) !== SAVE_VERSION) return;
    meta = {
        age: state.age ?? 1,
        legacy: state.legacy ?? 0,
        waveCredit: RAID_TIERS.map((_, i) => (state.waveCredit || [])[i] ?? 0),
        upgrades: state.upgrades ?? {},
        fallHistory: state.fallHistory ?? [],
        lessonsGranted: state.lessonsGranted ?? false,
        victory: state.victory ?? false,
        gameSeconds: state.gameSeconds ?? 0
    };
}

const UPGRADE_TREES = {
    economy: {
        label: 'Economy',
        nodes: [
            { id: 'trade',       name: 'Prosperous Trade', desc: '+25% gold income per rank',                                    maxRank: 5, costs: [15, 60, 250, 1000, 4000] },
            { id: 'treasury',    name: 'Royal Treasury',   desc: 'Begin each Age with a larger treasury (250 / 1,000 / 4,000 / 15,000 gold)', maxRank: 4, costs: [10, 40, 150, 500] },
            { id: 'builders',    name: 'Master Builders',  desc: '+50% Builder HP regen per rank',                               maxRank: 3, costs: [25, 100, 400] },
            { id: 'steward',     name: "Steward's Ledger", desc: 'Unlocks auto-hiring for townsfolk',                            maxRank: 1, costs: [150] },
            { id: 'foundations', name: 'Old Foundations',  desc: 'New Ages begin at Village level',                              maxRank: 1, costs: [400] },
            // Doctrines (M12): buildings feed the army, so town composition
            // stays a battle decision all game.
            { id: 'forgework', name: 'Smithy Forgework',    desc: '+1.5% hero attack per Smithy owned',                           maxRank: 1, costs: [2000] },
            { id: 'tactics',   name: 'Library Tactics',     desc: '+1% hero action speed per Library owned',                      maxRank: 1, costs: [3000] },
            { id: 'salves',    name: 'Apothecary Salves',   desc: 'Heroes regenerate 0.3% HP/s per Apothecary during battle',     maxRank: 1, costs: [5000] },
            { id: 'blessing',  name: 'Cathedral Blessing',  desc: 'The first hero to fall each battle revives at 30% HP (requires a Cathedral)', maxRank: 1, costs: [8000] }
        ]
    },
    military: {
        label: 'Military',
        nodes: [
            { id: 'renown',  name: 'Hall of Legends',   desc: 'Greater heroes join the recruit pool (Rare / Epic / Legendary)', maxRank: 3, costs: [50, 750, 5000] },
            { id: 'paladin', name: "Paladin's Oath",    desc: 'Unlocks the Paladin — a stalwart who attacks and heals',   maxRank: 1, costs: [250] },
            { id: 'assassin', name: 'Shadow Guild',     desc: 'Unlocks the Assassin — hunts the enemy backline',          maxRank: 1, costs: [400] },
            { id: 'battlemage', name: 'War Magics',     desc: 'Unlocks the Battlemage — strikes an entire enemy row',     maxRank: 1, costs: [800] },
            { id: 'frost', name: 'Rimecraft',           desc: 'Unlocks the Frost Adept — attacks slow the target',        maxRank: 1, costs: [1200] },
            { id: 'banneret', name: 'Standard Bearers', desc: 'Unlocks the Banneret — adjacent allies fight harder',      maxRank: 1, costs: [1500] },
            { id: 'squadsize', name: 'War Banners',     desc: 'Expand the hero squad (12 slots, then 16)',                maxRank: 2, costs: [2500, 20000] },
            { id: 'drills',  name: 'Weapon Drills',     desc: '+20% hero attack & healing per rank',        maxRank: 5, costs: [15, 60, 250, 1000, 4000] },
            { id: 'armor',   name: 'Hardened Armor',    desc: '+20% hero HP per rank',                      maxRank: 5, costs: [15, 60, 250, 1000, 4000] },
            { id: 'muster',  name: 'Muster Rolls',      desc: 'Hero hiring 15% cheaper per rank',           maxRank: 3, costs: [20, 80, 300] },
            { id: 'walls',   name: 'Reinforced Walls',  desc: '+250 max Kingdom HP per rank',               maxRank: 4, costs: [15, 60, 250, 1000] },
            { id: 'veteran', name: "Veteran's Welcome", desc: 'Each new Age begins with a free Rare Knight', maxRank: 1, costs: [100] }
        ]
    }
};

const STARTING_GOLD_BY_TREASURY_RANK = [50, 250, 1000, 4000, 15000];

function upgradeRank(id) {
    return meta.upgrades[id] || 0;
}

function findUpgrade(id) {
    for (const treeId in UPGRADE_TREES) {
        const node = UPGRADE_TREES[treeId].nodes.find(n => n.id === id);
        if (node) return node;
    }
    return null;
}

function buyUpgrade(id) {
    const def = findUpgrade(id);
    if (!def) return;
    const rank = upgradeRank(id);
    if (rank >= def.maxRank) return;
    const cost = def.costs[rank];
    if (meta.legacy < cost) return;
    meta.legacy -= cost;
    meta.upgrades[id] = rank + 1;
    if (id === 'squadsize') {
        resizeHeroSquad();
        saveGame();
    }
    saveMeta();
    renderRunSummary();
}

// Upgrade effect helpers — all run-state math routes through these so tree
// purchases apply everywhere without special cases.
function econIncomeMult()    { return 1 + 0.25 * upgradeRank('trade'); }
function builderRegenMult()  { return 1 + 0.5 * upgradeRank('builders'); }
function getStartingGold()   { return STARTING_GOLD_BY_TREASURY_RANK[upgradeRank('treasury')]; }
function getStartingLevel()  { return upgradeRank('foundations') > 0 ? 1 : 0; }
function heroPowerMult()     { return 1 + 0.2 * upgradeRank('drills'); }
function heroHpMult()        { return 1 + 0.2 * upgradeRank('armor'); }
function heroCostMult()      { return Math.pow(0.85, upgradeRank('muster')); }
// Hero rarity ceiling (index into rarityOrder): heroes above this rarity never
// appear in the pool. THE run-depth pacing gate — one rarity step is worth
// ~1.5 raid tiers of squad power, so this is what the Legacy trees meter out
// (kingdom level + Keeps only shift weights *under* the unlocked ceiling).
function heroRarityCap()     { return upgradeRank('renown'); }
function getKingdomHpMax()   { return KINGDOM_HP_MAX + 250 * upgradeRank('walls'); }

// Doctrines (M12): live multipliers from buildings owned — computed at use
// time via the M11 modifier layer, so they apply to already-hired heroes and
// track building purchases mid-run.
function doctrineAttackMult()  { return upgradeRank('forgework') ? 1 + 0.015 * buildings.smithy.count : 1; }
function doctrineSpeedMult()   { return upgradeRank('tactics')   ? 1 + 0.01  * buildings.library.count : 1; }
function doctrineSalvesRegen() { return upgradeRank('salves')    ? 0.003 * buildings.apothecary.count : 0; } // fraction of maxHp/s
function blessingAvailable()   { return upgradeRank('blessing') > 0 && buildings.cathedral.count > 0; }

// Hero grid dimensions by War Banners rank: 2x3 -> 3x4 -> 4x4 (rows x cols).
// Row 0 is the frontline; rows only ever grow, so no unit can be orphaned.
const HERO_GRID_BY_RANK = [{ rows: 2, cols: 3 }, { rows: 3, cols: 4 }, { rows: 4, cols: 4 }];
function heroGridDims()  { return HERO_GRID_BY_RANK[Math.min(upgradeRank('squadsize'), HERO_GRID_BY_RANK.length - 1)]; }
function heroSquadCap()  { const d = heroGridDims(); return d.rows * d.cols; }

// Rebuilds the squad array to the current grid dimensions, keeping every hero
// at its row/col (grids only grow, but guard against any stale position).
function resizeHeroSquad() {
    const { rows, cols } = heroGridDims();
    if (heroSquad.length === rows * cols && heroSquad.every(u => !u || (u.row < rows && u.col < cols))) return;
    const resized = new Array(rows * cols).fill(null);
    for (const unit of heroSquad) {
        if (!unit) continue;
        let idx = unit.row * cols + unit.col;
        if (unit.row >= rows || unit.col >= cols || resized[idx]) {
            idx = resized.findIndex(s => s === null);
            if (idx === -1) continue;
            unit.row = Math.floor(idx / cols);
            unit.col = idx % cols;
        }
        resized[idx] = unit;
    }
    heroSquad = resized;
}

// Archetypes whose unlock node is owned (or that never needed one).
function unlockedHeroArchetypes() {
    return Object.keys(HERO_ARCHETYPES).filter(key => {
        const unlock = HERO_ARCHETYPES[key].unlock;
        return !unlock || upgradeRank(unlock) > 0;
    });
}

// Townsfolk auto-hire is an Economy-tree purchase (Steward's Ledger); the dev
// build keeps it always-on for testing.
function autoRecruitAvailable() { return DEV_MODE || upgradeRank('steward') > 0; }

// First-ever-clear pays full value; re-clears pay the trickle. Credit is
// all-time (the high-water mark persists across Ages).
function bankWaveLegacy(tierIndex, wave) {
    let value = WAVE_LEGACY_VALUES[Math.min(tierIndex, WAVE_LEGACY_VALUES.length - 1)];
    if (isBossWave(tierIndex, wave)) value *= BOSS_LEGACY_MULT;
    let earned;
    if (wave >= meta.waveCredit[tierIndex]) {
        earned = value;
        meta.waveCredit[tierIndex] = wave + 1;
    } else {
        earned = Math.max(1, Math.round(value * REPEAT_LEGACY_FRACTION));
    }
    meta.legacy += earned;
    runLegacyEarned += earned;
    saveMeta();
    return earned;
}

function formatTimer(seconds) {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
}

// Deliberately scarce: a handful of each building, 2-3 slots each, so every
// building purchase and every staffing choice matters (M9 shrink).
const levels = [
    {
        name: 'Hamlet',
        cost: 0,
        unlocks: ['cottage'],
        caps: { cottage: 3, tavern: 0, smithy: 0, library: 0, workshop: 0, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Village',
        cost: 400,
        unlocks: ['tavern', 'workshop'],
        caps: { cottage: 5, tavern: 2, smithy: 0, library: 0, workshop: 1, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Town',
        cost: 3000,
        unlocks: ['smithy'],
        caps: { cottage: 7, tavern: 3, smithy: 2, library: 0, workshop: 2, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'City',
        cost: 20000,
        unlocks: ['library'],
        caps: { cottage: 9, tavern: 4, smithy: 3, library: 2, workshop: 2, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Kingdom',
        cost: 80000,
        unlocks: [],
        caps: { cottage: 11, tavern: 5, smithy: 4, library: 3, workshop: 3, apothecary: 0, tower: 0, cathedral: 0, keep: 0 }
    },
    {
        name: 'Empire',
        cost: 300000,
        unlocks: ['apothecary', 'keep'],
        caps: { cottage: 13, tavern: 6, smithy: 5, library: 4, workshop: 3, apothecary: 2, tower: 0, cathedral: 0, keep: 1 }
    },
    {
        name: 'Dynasty',
        cost: 1000000,
        unlocks: ['tower'],
        caps: { cottage: 15, tavern: 7, smithy: 6, library: 5, workshop: 4, apothecary: 3, tower: 2, cathedral: 0, keep: 2 }
    },
    {
        name: 'Realm',
        cost: 3000000,
        unlocks: ['cathedral'],
        caps: { cottage: 16, tavern: 8, smithy: 7, library: 6, workshop: 4, apothecary: 4, tower: 3, cathedral: 2, keep: 3 }
    }
];

const buildings = {
    cottage:  { name: 'Cottage',  cost: 10,   count: 0, slotsPerBuilding: 2, costGrowth: 1.30, type: 'gold',    residents: [] },
    tavern:   { name: 'Tavern',   cost: 250,  count: 0, slotsPerBuilding: 2, costGrowth: 1.30, type: 'gold',    residents: [] },
    smithy:   { name: 'Smithy',   cost: 1500, count: 0, slotsPerBuilding: 2, costGrowth: 1.35, type: 'gold',    residents: [] },
    library:  { name: 'Library',  cost: 6000, count: 0, slotsPerBuilding: 2, costGrowth: 1.35, type: 'gold',    residents: [] },
    workshop: { name: 'Workshop', cost: 400,   count: 0, slotsPerBuilding: 2, costGrowth: 1.35, type: 'hpregen', residents: [] },
    keep:     { name: 'Keep',     cost: 40000, count: 0, slotsPerBuilding: 0, costGrowth: 1.50, residents: [] },
    apothecary: { name: 'Apothecary',      cost: 25000,  count: 0, slotsPerBuilding: 3, costGrowth: 1.40, type: 'gold',    residents: [] },
    tower:    { name: "Wizard's Tower",  cost: 100000, count: 0, slotsPerBuilding: 3, costGrowth: 1.45, type: 'gold',    residents: [] },
    cathedral:{ name: 'Cathedral',       cost: 400000, count: 0, slotsPerBuilding: 3, costGrowth: 1.50, type: 'gold',    residents: [] }
};

// Captured before any save is loaded, so "Found a New Age" can restore
// original building prices after cost-growth inflation.
const BUILDING_BASE_COSTS = {};
for (const id in buildings) BUILDING_BASE_COSTS[id] = buildings[id].cost;

const rarityTiers = {
    common:    { name: 'Common',    color: '#888888', costMult: 1,  incomeMult: 1   },
    rare:      { name: 'Rare',      color: '#4488ff', costMult: 3,  incomeMult: 2.5 },
    epic:      { name: 'Epic',      color: '#aa44ff', costMult: 8,  incomeMult: 5   },
    legendary: { name: 'Legendary', color: '#ffaa00', costMult: 20, incomeMult: 10  }
};

// Hire costs sized for ~60-190s payback at the average roll, so income ramps
// over minutes, not seconds (M9 pacing).
const recruitTypes = {
    villager:     { name: 'Villager',     buildingId: 'cottage',  baseCost: 25,   incomeMin: 1,  incomeMax: 3  },
    tavernkeeper: { name: 'Tavernkeeper', buildingId: 'tavern',   baseCost: 300,  incomeMin: 4,  incomeMax: 8  },
    blacksmith:   { name: 'Blacksmith',   buildingId: 'smithy',   baseCost: 1200, incomeMin: 10, incomeMax: 20 },
    scholar:      { name: 'Scholar',      buildingId: 'library',  baseCost: 4500, incomeMin: 30, incomeMax: 60 },
    builder:      { name: 'Builder',      buildingId: 'workshop',  baseCost: 250,    incomeMin: 0.3, incomeMax: 0.8 },
    alchemist:    { name: 'Alchemist',    buildingId: 'apothecary', baseCost: 15000,  incomeMin: 80,  incomeMax: 160 },
    mage:         { name: 'Mage',         buildingId: 'tower',     baseCost: 60000,  incomeMin: 250, incomeMax: 500 },
    priest:       { name: 'High Priest',  buildingId: 'cathedral', baseCost: 200000, incomeMin: 700, incomeMax: 1400 }
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

// Deliberately stingy at low levels: one rarity step is worth ~1.5 raid tiers
// of squad power (sim-verified), so rarity availability is the main knob that
// paces how deep a run can push. Kingdom level loosens it for townspeople;
// for HEROES the weights are additionally clamped by the Hall of Legends
// ceiling (heroRarityCap) — in-run gold alone must never buy hero rarity,
// or a patient run 1 clears the whole ladder (2026-07-13 playtest).
const RARITY_WEIGHT_TABLE = [
    [{ r: 'common', w: 92 }, { r: 'rare', w: 8 }],
    [{ r: 'common', w: 88 }, { r: 'rare', w: 12 }],
    [{ r: 'common', w: 85 }, { r: 'rare', w: 15 }],
    [{ r: 'common', w: 78 }, { r: 'rare', w: 20 }, { r: 'epic', w: 2 }],
    [{ r: 'common', w: 65 }, { r: 'rare', w: 28 }, { r: 'epic', w: 6 }, { r: 'legendary', w: 1 }],
    [{ r: 'common', w: 50 }, { r: 'rare', w: 32 }, { r: 'epic', w: 15 }, { r: 'legendary', w: 3 }],
    [{ r: 'common', w: 35 }, { r: 'rare', w: 33 }, { r: 'epic', w: 25 }, { r: 'legendary', w: 7 }],
    [{ r: 'common', w: 25 }, { r: 'rare', w: 30 }, { r: 'epic', w: 30 }, { r: 'legendary', w: 15 }]
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
    const weights = RARITY_WEIGHT_TABLE[Math.min(kingdomLevel + buildings.keep.count, RARITY_WEIGHT_TABLE.length - 1)];
    // Clamp to the Hall of Legends ceiling; weightedRarityRoll renormalizes
    // over whatever remains (common is index 0, so this is never empty).
    return weights.filter(w => rarityOrder.indexOf(w.r) <= heroRarityCap());
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
    if (!autoRecruitRarity || !autoRecruitAvailable()) return;
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
        invasionTimer = FIRST_RAID_GRACE;
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
// Generalized to any number of rows (M10 squad expansion): the frontmost
// occupied row is "the front"; every row behind it is the backline pool.
function pickTarget(attacker, enemySquad) {
    const alive = enemySquad.filter(u => u && u.alive);
    if (alive.length === 0) return null;
    const frontRow = Math.min(...alive.map(u => u.row));
    const front = alive.filter(u => u.row === frontRow);
    const back = alive.filter(u => u.row > frontRow);
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
    const power = healer.heal.power * (1 + auraBonus(healer));
    target.hp = Math.min(target.maxHp, target.hp + power);
}

// Enemy attacks (and only enemy attacks — never heals, or the stalemate would
// get worse, not better) scale up as the current battle drags on.
function escalationMult(invasion) {
    if (!invasion) return 1;
    const past = (invasion.duration || 0) - SIEGE_ESCALATION_GRACE;
    return past > 0 ? 1 + past * SIEGE_ESCALATION_RATE : 1;
}

// --- M11 modifier layer: enrage, auras, chill ---
// Modifiers are COMPUTED from unit state each use, never stacked as effect
// objects — there is nothing to desync or forget to expire (chill, the one
// timed effect, carries its own expiry timestamp on the target).

function isEnraged(unit) {
    return unit.enrage && unit.alive && unit.hp / unit.maxHp < 0.5;
}

// Sum of aura bonuses reaching this unit from living allies (Banneret:
// adjacent only; boss war-cries: the whole squad).
function auraBonus(unit) {
    const squad = unit.side === 'hero' ? heroSquad : (currentInvasion ? currentInvasion.enemies : []);
    let bonus = 0;
    for (const ally of squad) {
        if (!ally || !ally.alive || ally === unit || !ally.aura) continue;
        const adjacent = (ally.row === unit.row && Math.abs(ally.col - unit.col) === 1)
            || (ally.col === unit.col && Math.abs(ally.row - unit.row) === 1);
        if (ally.aura.range === 'all' || adjacent) bonus += ally.aura.power;
    }
    return bonus;
}

function effectiveAttackPower(unit) {
    let power = unit.attack.power;
    if (isEnraged(unit)) power *= unit.enrage.power || 1;
    power *= 1 + auraBonus(unit);
    if (unit.side === 'hero') power *= doctrineAttackMult();
    return power;
}

function chilled(unit) {
    return unit.chilledUntil !== undefined && currentInvasion
        && (currentInvasion.duration || 0) < unit.chilledUntil;
}

// Cooldown refill for any action: enrage speeds it up, chill drags it out.
function effectiveActionInterval(unit, action) {
    let interval = BASE_ATTACK_INTERVAL / action.speed;
    if (isEnraged(unit)) interval /= unit.enrage.speed || 1;
    if (chilled(unit)) interval *= unit.chillMult || 1;
    if (unit.side === 'hero') interval /= doctrineSpeedMult();
    return interval;
}

// On-death hook (M11): enemies with reviveCharges (necromancers, the Lich
// Commander) raise a fallen ally at 50% HP — once per charge, and only while
// the reviver itself stands. Kill order is the counter.
// M12: the hero side gets Cathedral Blessing — the first hero to fall each
// battle revives at 30% HP (blessingUsed lives on currentInvasion, so it
// resets naturally with each new battle).
function onUnitDeath(unit) {
    if (!currentInvasion) return;
    if (unit.side === 'hero') {
        if (blessingAvailable() && !currentInvasion.blessingUsed) {
            currentInvasion.blessingUsed = true;
            unit.alive = true;
            unit.hp = Math.max(1, Math.round(unit.maxHp * 0.3));
            if (unit.attack) unit.attack.cooldown = effectiveActionInterval(unit, unit.attack);
            if (unit.heal) unit.heal.cooldown = effectiveActionInterval(unit, unit.heal);
        }
        return;
    }
    for (const ally of currentInvasion.enemies) {
        if (!ally || !ally.alive || !(ally.reviveCharges > 0)) continue;
        ally.reviveCharges--;
        unit.alive = true;
        unit.hp = Math.round(unit.maxHp * 0.5);
        if (unit.attack) unit.attack.cooldown = effectiveActionInterval(unit, unit.attack);
        if (unit.heal) unit.heal.cooldown = effectiveActionInterval(unit, unit.heal);
        return;
    }
}

function resolveAttack(attacker, defender, powerScale = 1) {
    let power = effectiveAttackPower(attacker) * powerScale;
    if (attacker.side === 'enemy') power *= escalationMult(currentInvasion);
    const dmg = Math.max(1, Math.round(power * (1 - defender.defense / 100)));
    defender.hp -= dmg;
    if (attacker.attack.chill && defender.hp > 0) {
        defender.chilledUntil = (currentInvasion ? currentInvasion.duration || 0 : 0) + attacker.attack.chill.duration;
        defender.chillMult = attacker.attack.chill.mult;
    }
    if (defender.hp <= 0) {
        defender.hp = 0;
        defender.alive = false;
        onUnitDeath(defender);
    }
}

function squadAlive(squad) {
    return squad.some(u => u && u.alive);
}

// Once the hero squad is wiped, nothing stands between the enemy and the
// Kingdom itself — enemies attack Kingdom HP directly until it falls or the
// raid is repelled some other way.
function attackKingdom(attacker) {
    const power = effectiveAttackPower(attacker) * escalationMult(currentInvasion);
    const dmg = Math.max(1, Math.round(power * (1 - KINGDOM_DEFENSE / 100)));
    kingdomHP = Math.max(0, kingdomHP - dmg);
}

// A sapper hit on the Kingdom can put a random staffed resident out of action
// for INJURY_DURATION game-seconds — Builders' regen and the town's income
// are part of the battle now.
function maybeInjureResident() {
    if (Math.random() >= SAPPER_INJURY_CHANCE) return;
    const staffed = [];
    for (const id in buildings) {
        for (const r of buildings[id].residents) {
            if (!isInjured(r)) staffed.push(r);
        }
    }
    if (staffed.length === 0) return;
    randomFrom(staffed).injuredUntil = runTime + INJURY_DURATION;
    recomputeIncome();
    renderBuildings();
}

function isInjured(resident) {
    return resident.injuredUntil !== undefined && resident.injuredUntil > runTime;
}

// Authoritative income recompute (skips injured residents). Called whenever
// residents change or injuries start/expire; also every tick as a safety net
// against incremental-update drift.
function recomputeIncome() {
    goldPerSecond = 0;
    kingdomHpRegen = 0;
    for (const id in buildings) {
        for (const r of buildings[id].residents) {
            if (isInjured(r)) continue;
            if (buildings[id].type === 'hpregen') kingdomHpRegen += r.income;
            else goldPerSecond += r.income;
        }
    }
}

// Advances combat by deltaMs. Each unit's attack and heal cooldowns tick down
// independently.
function combatTick(deltaMs) {
    currentInvasion.duration = (currentInvasion.duration || 0) + deltaMs / 1000;
    const enemySide = currentInvasion.enemies;
    for (const unit of [...heroSquad, ...enemySide]) {
        if (!unit || !unit.alive) continue;

        if (unit.attack) {
            unit.attack.cooldown -= deltaMs;
            if (unit.attack.cooldown <= 0) {
                if (unit.side === 'enemy' && (unit.targetsKingdom || !squadAlive(heroSquad))) {
                    // Sappers always hit the Kingdom; everyone does once no hero stands.
                    attackKingdom(unit);
                    if (unit.targetsKingdom) maybeInjureResident();
                } else {
                    const opposing = unit.side === 'hero' ? enemySide : heroSquad;
                    const target = pickTarget(unit, opposing);
                    if (target) {
                        if (unit.attack.aoe === 'row') {
                            // Row AoE (Battlemage, dragon breath): everyone in
                            // the target's row takes a discounted hit.
                            for (const u of opposing) {
                                if (u && u.alive && u.row === target.row) resolveAttack(unit, u, AOE_POWER_FACTOR);
                            }
                        } else {
                            resolveAttack(unit, target);
                        }
                    }
                }
                unit.attack.cooldown += effectiveActionInterval(unit, unit.attack);
            }
        }

        if (unit.heal) {
            unit.heal.cooldown -= deltaMs;
            if (unit.heal.cooldown <= 0) {
                const friendlySquad = unit.side === 'hero' ? heroSquad : enemySide;
                const target = pickHealTarget(friendlySquad);
                if (target) {
                    resolveHeal(unit, target);
                    unit.heal.cooldown += effectiveActionInterval(unit, unit.heal);
                }
                // Nobody wounded yet — hold the heal ready and check again next tick.
            }
        }
    }

    // Apothecary Salves (M12): heroes slowly regenerate during battle.
    const salves = doctrineSalvesRegen();
    if (salves > 0) {
        for (const hero of heroSquad) {
            if (hero && hero.alive && hero.hp < hero.maxHp) {
                hero.hp = Math.min(hero.maxHp, hero.hp + hero.maxHp * salves * (deltaMs / 1000));
            }
        }
    }

    // Dead heroes are gone for good — free their slot the moment they fall so
    // mid-battle reinforcements can be hired even after a full squad wipe.
    for (let i = 0; i < heroSquad.length; i++) {
        if (heroSquad[i] && !heroSquad[i].alive) heroSquad[i] = null;
    }
}

// --- Enemy & hero generation ---
function generateEnemy(tierIndex, archetypeKey, row, col, wave, bossPart = null) {
    const tier = RAID_TIERS[tierIndex];
    const archetype = ENEMY_ARCHETYPES[archetypeKey];
    const base = archetype.base;
    const mult = tier.powerMult * Math.pow(tier.defenseGrowth, wave);
    const powerMult = mult * (bossPart ? tier.boss.powerMult : 1);
    const hpMult = Math.sqrt(mult) * (bossPart ? tier.boss.hpMult : 1);
    const scalePower = v => Math.round(v * powerMult);
    const scaleHp = v => Math.round(v * hpMult);

    const attack = base.attack ? attackAction(scalePower(base.attack.power), base.attack.speed) : null;
    const heal = base.heal ? healAction(scalePower(base.heal.power), base.heal.speed) : null;
    const backlineChance = base.backlineChance !== undefined ? base.backlineChance : DEFAULT_BACKLINE_CHANCE;

    const name = bossPart ? tier.boss.name : tier.roster[archetypeKey];
    const unit = makeUnit(name, base.defense, scaleHp(base.hp), row, col, 'enemy', attack, heal, backlineChance);
    if (base.targetsKingdom) unit.targetsKingdom = true;

    // Tier trait overrides (the tier's tactical lesson), then boss signature
    // traits on top for the boss unit itself.
    const traits = { ...(tier.traits[archetypeKey] || {}), ...(bossPart ? tier.boss.traits : {}) };
    if (traits.backlineChance !== undefined) unit.backlineChance = traits.backlineChance;
    if (traits.enrage) unit.enrage = traits.enrage;
    if (traits.reviveCharges) unit.reviveCharges = traits.reviveCharges;
    if (traits.aura) unit.aura = traits.aura;
    if (traits.aoe && unit.attack) unit.attack.aoe = traits.aoe;
    return unit;
}

function generateHero(archetypeKey, rarity, row, col) {
    const archetype = HERO_ARCHETYPES[archetypeKey];
    const tier = rarityTiers[rarity];
    const rarityIndex = rarityOrder.indexOf(rarity);
    const scalePower = v => Math.round(v * tier.incomeMult * heroPowerMult());
    const scaleHp = v => Math.round(v * Math.sqrt(tier.incomeMult) * heroHpMult());

    const base = archetype.base;
    const attack = base.attack ? attackAction(scalePower(base.attack.power), base.attack.speed) : null;
    const heal = base.heal ? healAction(scalePower(base.heal.power), base.heal.speed) : null;
    // Carry M11 action modifiers through (AoE rows, chill-on-hit).
    if (attack && base.attack.aoe) attack.aoe = base.attack.aoe;
    if (attack && base.attack.chill) attack.chill = base.attack.chill;

    const unit = makeUnit(archetype.names[rarityIndex], base.defense, scaleHp(base.hp), row, col, 'hero', attack, heal, base.backlineChance);
    unit.rarity = rarity;
    unit.archetypeKey = archetypeKey;
    if (base.aura) unit.aura = base.aura;
    return unit;
}

// Builds the wave's squad from its hand-authored composition (TIER_WAVES).
// 'BOSS r c' places the tier's named boss (a scaled-up brute with signature
// traits); everything else is "archetype row col".
function generateEnemySquad(tierIndex, wave) {
    const tier = RAID_TIERS[tierIndex];
    const comps = TIER_WAVES[tierIndex];
    // Waves past the boss (Final Siege countdown, endless mode) reuse the last
    // NON-boss composition while their stats keep scaling with the wave number.
    const compIndex = wave < comps.length ? wave : comps.length - 2;
    const comp = comps[compIndex];
    const squad = new Array(tier.grid.rows * tier.grid.cols).fill(null);
    for (const entry of comp) {
        const [key, r, c] = entry.split(' ');
        const row = Number(r), col = Number(c);
        const unit = key === 'BOSS'
            ? generateEnemy(tierIndex, 'brute', row, col, wave, true)
            : generateEnemy(tierIndex, key, row, col, wave);
        squad[row * tier.grid.cols + col] = unit;
    }
    return squad;
}

// --- Hero recruiting & squad management ---
function generateHeroRecruit() {
    const archetypeKeys = unlockedHeroArchetypes();
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
        cost: Math.floor(archetype.baseCost * tier.costMult * heroCostMult())
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
    const cols = heroGridDims().cols;
    heroSquad[slotIndex] = generateHero(recruit.archetypeKey, recruit.rarity, Math.floor(slotIndex / cols), slotIndex % cols);

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
    const cols = heroGridDims().cols;
    const rowOf = idx => Math.floor(idx / cols);
    const colOf = idx => idx % cols;

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
    // Heroes "respawn" at full HP each battle — the kingdom absorbs losses
    // via Kingdom HP, not permanent hero death. Chill wears off between battles.
    for (const hero of heroSquad) {
        if (!hero) continue;
        hero.hp = hero.maxHp;
        hero.alive = true;
        delete hero.chilledUntil;
        delete hero.chillMult;
        if (hero.attack) hero.attack.cooldown = BASE_ATTACK_INTERVAL / hero.attack.speed;
        if (hero.heal) hero.heal.cooldown = BASE_ATTACK_INTERVAL / hero.heal.speed;
    }

    // The Final Siege is due — the gauntlet begins instead of a normal raid.
    if (finalSiegeCountdown === 0) {
        finalSiegeCountdown = -1;
        spawnFinalSiegePhase(1);
        return;
    }

    const tier = RAID_TIERS[raidTierIndex];
    currentInvasion = {
        name: getInvasionName(raidTierIndex, tierWave),
        enemies: generateEnemySquad(raidTierIndex, tierWave),
        grid: { rows: tier.grid.rows, cols: tier.grid.cols },
        duration: 0 // game-seconds of battle so far — drives siege escalation
    };
}

// Spawns a Final Siege phase into the CURRENT battle (phase 1 creates it).
// Heroes keep their HP between phases; the escalation clock resets — each
// phase is a fresh assault against an already-bloodied defense.
function spawnFinalSiegePhase(phase) {
    const def = FINAL_SIEGE_PHASES[phase - 1];
    const tierIndex = RAID_TIERS.length - 1;
    const tier = RAID_TIERS[tierIndex];
    const squad = new Array(tier.grid.rows * tier.grid.cols).fill(null);
    for (const entry of def.comp) {
        const [key, r, c] = entry.split(' ');
        const row = Number(r), col = Number(c);
        const unit = key === 'BOSS'
            ? generateEnemy(tierIndex, 'brute', row, col, def.wave, true)
            : generateEnemy(tierIndex, key, row, col, def.wave);
        squad[row * tier.grid.cols + col] = unit;
    }
    const blessingUsed = currentInvasion ? currentInvasion.blessingUsed : false;
    currentInvasion = {
        name: `The Final Siege — ${def.name}`,
        enemies: squad,
        grid: { rows: tier.grid.rows, cols: tier.grid.cols },
        duration: 0,
        finalSiege: true,
        phase,
        blessingUsed // once per gauntlet, not per phase
    };
}

// A raid has exactly two outcomes: Repelled (enemy squad wiped — handled
// here) or Overrun (kingdomHP hit 0 — handled by endRun). The wave ladder
// only climbs on wins; a lost wave re-attacks after the raid interval.
function winInvasion() {
    // Survivors leave the field fully healed. Menders don't tick between
    // battles and startInvasion resets HP anyway, so wounded bars after a
    // win were a display lie.
    for (const hero of heroSquad) {
        if (hero && hero.alive) hero.hp = hero.maxHp;
    }

    const loot = getInvasionLoot(raidTierIndex, raidWinStreak);
    raidWinStreak++;
    const legacy = bankWaveLegacy(raidTierIndex, tierWave);
    runWavesCleared++;
    lastVictory = { name: currentInvasion.name, loot, legacy, won: true };
    gold += loot;

    // Killing a tier's boss advances to the next tier's wave 1 (streak and
    // wave counter reset). Past the last tier's boss, waves keep climbing
    // (Final Siege countdown, then endless mode).
    if (isBossWave(raidTierIndex, tierWave) && raidTierIndex < RAID_TIERS.length - 1) {
        raidTierIndex++;
        tierWave = 0;
        raidWinStreak = 0;
    } else {
        // First-ever kill of the last tier's boss: the herald announces the
        // Final Siege, arriving after a handful of ordinary raids.
        if (isBossWave(raidTierIndex, tierWave) && raidTierIndex === RAID_TIERS.length - 1
            && !meta.victory && finalSiegeCountdown === -1) {
            finalSiegeCountdown = FINAL_SIEGE_COUNTDOWN_RAIDS;
        } else if (finalSiegeCountdown > 0) {
            finalSiegeCountdown--;
        }
        tierWave++;
    }

    currentInvasion = null;
    invasionTimer = getRaidInterval();
}

// Ends the current run ("Age") — either the Kingdom fell (reason 'overrun')
// or the player chose to abandon it (reason 'abandoned'). Banks nothing new
// (Legacy is banked per-wave at clear time); freezes the game and shows the
// run-summary overlay with the upgrade shop.
function endRun(reason) {
    const fellTo = currentInvasion ? currentInvasion.name : getInvasionName(raidTierIndex, tierWave);

    // Lessons of the Last Siege (M13): a LOST Final Siege attempt pays a large
    // one-time bonus — the failed attempt visibly funds the winning one.
    let lessons = 0;
    if (currentInvasion && currentInvasion.finalSiege && !meta.lessonsGranted) {
        meta.lessonsGranted = true;
        lessons = LESSONS_LEGACY;
        meta.legacy += lessons;
        runLegacyEarned += lessons;
    }

    meta.gameSeconds += runTime;
    kingdomFallRecord = { name: fellTo, level: kingdomLevel };
    meta.fallHistory.push({ age: meta.age, name: fellTo, level: kingdomLevel, waves: runWavesCleared, legacy: runLegacyEarned });
    runSummary = {
        age: meta.age,
        reason,
        fellTo,
        levelName: levels[kingdomLevel].name,
        waves: runWavesCleared,
        legacy: runLegacyEarned,
        lessons
    };
    runEnded = true;
    currentInvasion = null;
    confirmingNewAge = false;
    saveMeta();
    saveGame();
    renderRunSummary();
}

// The reset itself: back to Hamlet (or Village with Old Foundations) with
// everything run-scoped wiped. Runs when the player leaves the run-summary
// screen, so upgrades bought there apply to the new Age from second one.
function foundNewAge() {
    meta.age++;
    saveMeta();

    gold = getStartingGold();
    goldEarned = 0;
    goldPerSecond = 0;
    kingdomHpRegen = 0;
    runTime = 0;
    finalSiegeCountdown = -1;
    victoryPending = false;
    kingdomLevel = getStartingLevel();
    kingdomHP = getKingdomHpMax();
    raidsStarted = false;
    raidTierIndex = 0;
    tierWave = 0;
    raidWinStreak = 0;
    invasionTimer = 0;
    currentInvasion = null;
    lastVictory = null;
    runEnded = false;
    runSummary = null;
    runLegacyEarned = 0;
    runWavesCleared = 0;
    heroSquad = new Array(heroSquadCap()).fill(null);
    heroRecruitPool = [];
    heroPoolTimer = 0;
    recruitPool = [];
    poolTimer = 0;
    // autoRecruitRarity deliberately survives the reset (persists per design).

    for (const id in buildings) {
        buildings[id].cost = BUILDING_BASE_COSTS[id];
        buildings[id].count = 0;
        buildings[id].residents = [];
    }

    if (upgradeRank('veteran') > 0) {
        heroSquad[0] = generateHero('guardian', 'rare', 0, 0);
    }

    refreshPool();
    renderRunSummary();
    saveGame();
    updateUI();
}

// The Final Siege is broken — the campaign is won (M13). The world freezes on
// the victory screen until the player chooses to rule on in endless mode.
function campaignVictory() {
    meta.victory = true;
    meta.gameSeconds += runTime;
    victoryPending = true;
    currentInvasion = null;
    invasionTimer = getRaidInterval();
    saveMeta();
    saveGame();
    renderVictory();
}

// Endless mode: the run continues, raids keep climbing indefinitely, and
// Found a New Age still works for fresh runs. There is no second Final Siege.
function continueEndless() {
    victoryPending = false;
    document.getElementById('run-summary-overlay').classList.add('hidden');
    saveGame();
    updateUI();
}

function showNewAgeConfirm() {
    confirmingNewAge = true;
    updateUI();
}

function cancelNewAge() {
    confirmingNewAge = false;
    updateUI();
}

function confirmNewAge() {
    endRun('abandoned');
}

function saveGame() {
    const state = {
        version: SAVE_VERSION,
        gold, goldEarned, kingdomLevel, raidsStarted, raidTierIndex, tierWave, raidWinStreak, invasionTimer, currentInvasion, lastVictory, kingdomFallRecord, autoRecruitRarity, runTime, finalSiegeCountdown, victoryPending,
        runEnded, runSummary, runLegacyEarned, runWavesCleared, gameSpeed,
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
    // Pre-rebalance saves are meaningless after a version bump — discard.
    if ((state.version ?? 1) !== SAVE_VERSION) return;

    gold = state.gold ?? 50;
    goldEarned = state.goldEarned ?? 0;
    kingdomLevel = state.kingdomLevel ?? 0;
    raidsStarted = state.raidsStarted ?? false;
    raidTierIndex = state.raidTierIndex ?? 0;
    tierWave = state.tierWave ?? 0;
    raidWinStreak = state.raidWinStreak ?? 0;
    invasionTimer = state.invasionTimer ?? 0;
    currentInvasion = (state.currentInvasion && state.currentInvasion.enemies) ? state.currentInvasion : null;
    lastVictory = state.lastVictory ?? null;
    kingdomFallRecord = state.kingdomFallRecord ?? null;
    autoRecruitRarity = state.autoRecruitRarity ?? null;
    runTime = state.runTime ?? 0;
    finalSiegeCountdown = state.finalSiegeCountdown ?? -1;
    victoryPending = state.victoryPending ?? false;
    runEnded = state.runEnded ?? false;
    runSummary = state.runSummary ?? null;
    runLegacyEarned = state.runLegacyEarned ?? 0;
    runWavesCleared = state.runWavesCleared ?? 0;
    gameSpeed = [1, 10, 50, 100].includes(state.gameSpeed) ? state.gameSpeed : 1;
    recruitPool = state.recruitPool ?? [];
    poolTimer = state.poolTimer ?? 0;
    nextRecruitId = state.nextRecruitId ?? 0;

    kingdomHP = state.kingdomHP ?? getKingdomHpMax();
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
            const resident = {
                income,
                rarity: r.rarity || 'common',
                typeId,
                name: name || (recruitTypes[typeId] || {}).name || 'Resident'
            };
            if (r.injuredUntil !== undefined) resident.injuredUntil = r.injuredUntil;
            return resident;
        });
    }

    recomputeIncome();

    // Saved squads predate any War Banners rank bought this session (and a
    // missing save leaves the 6-slot default) — normalize to current dims.
    resizeHeroSquad();
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
    localStorage.removeItem(META_SAVE_KEY);
    location.reload();
}

function tick() {
    // The world is frozen while the run-summary screen is up — the next Age
    // starts when the player founds it. Same for the victory screen.
    if (runEnded || victoryPending) return;

    runTime++;
    // Authoritative recompute each tick: picks up injury expiries automatically
    // and immunizes income against incremental-update drift.
    recomputeIncome();
    const income = goldPerSecond * econIncomeMult();
    gold += income;
    goldEarned += income;
    kingdomHP = Math.min(getKingdomHpMax(), kingdomHP + kingdomHpRegen * builderRegenMult());

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
            if (kingdomHP <= 0) {
                endRun('overrun');
                return;
            }
            if (!squadAlive(currentInvasion.enemies)) {
                if (currentInvasion.finalSiege) {
                    if (currentInvasion.phase < FINAL_SIEGE_PHASES.length) {
                        spawnFinalSiegePhase(currentInvasion.phase + 1);
                    } else {
                        campaignVictory();
                        return;
                    }
                } else {
                    winInvasion();
                }
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

    const autoRecruitHtml = autoRecruitAvailable()
        ? `<div class="auto-recruit">
            <span class="auto-recruit-label">Auto-hire:</span>
            ${autoOptions.map(({ value, label }) => {
                const active = autoRecruitRarity === value;
                const arg = value === null ? 'null' : `'${value}'`;
                const rarityClass = value ? `btn-auto--${value}` : '';
                return `<button class="btn-auto ${rarityClass} ${active ? 'btn-auto--active' : ''}" onclick="setAutoRecruit(${arg})">${label}</button>`;
            }).join('')}
        </div>`
        : `<div class="auto-recruit"><span class="auto-recruit-label auto-recruit-locked">Auto-hire: unlocks with Steward's Ledger (Economy)</span></div>`;

    let html = `<div class="pool-header">
        <span class="pool-timer" id="pool-timer-text">New arrivals in ${timeUntilRefresh}s</span>
        ${autoRecruitHtml}
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
                const injured = isInjured(r);
                const injuredTitle = injured ? `&#10;INJURED — recovers in ${Math.max(0, Math.ceil(r.injuredUntil - runTime))}s (no income)` : '';
                html += `<div class="portrait portrait--${r.rarity || 'common'}${injured ? ' portrait--injured' : ''}" data-type="${r.typeId || 'villager'}"
                    title="${r.name} (${rarityInfo.name}) — ${valueLabel}${injuredTitle}&#10;Click to dismiss"
                    onclick="fireResident('${id}', ${r.originalIndex})">
                    <span class="portrait-letter">${injured ? '✚' : letter}</span>
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
        <div class="panel-label">Kingdom &middot; Age ${meta.age}</div>
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

    // Manual run-ender: for when a run's frontier attempts are spent and
    // waiting out the kingdom's actual fall would just waste time.
    if (raidsStarted && !runEnded) {
        if (confirmingNewAge) {
            html += `<div class="panel-section">
                <div class="panel-label" style="color:#8a4040">End this Age?</div>
                <div class="reset-confirm-buttons">
                    <button class="btn-reset btn-reset--confirm" onclick="confirmNewAge()">Yes, end it</button>
                    <button class="btn-reset" onclick="cancelNewAge()">Cancel</button>
                </div>
            </div>`;
        } else {
            html += `<div class="panel-section">
                <button class="btn-new-age-side" onclick="showNewAgeConfirm()">Found a New Age</button>
            </div>`;
        }
    }

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
    const hpMax = getKingdomHpMax();
    const pct = Math.max(0, Math.min(100, (kingdomHP / hpMax) * 100));
    const html = `<div class="panel-label">Kingdom HP</div>
        <div class="hp-bar-track"><div class="hp-bar-fill" style="width:${pct}%"></div></div>
        <div class="hp-bar-caption">${Math.round(kingdomHP).toLocaleString()} / ${hpMax.toLocaleString()}</div>
        ${kingdomHP <= 0 ? '<div class="kingdom-falling">Kingdom Falling!</div>' : ''}
        ${kingdomFallRecord ? `<div class="kingdom-fall-record">Fell at: ${kingdomFallRecord.name} (Kingdom Lv ${kingdomFallRecord.level})</div>` : ''}`;
    document.getElementById('kingdom-hp').innerHTML = html;
}

function renderRaidStatusBar() {
    let html = '';

    if (currentInvasion) {
        html += `<div class="raid-status-name">${currentInvasion.name}</div>
            <div class="raid-status-timer">${currentInvasion.finalSiege ? `Phase ${currentInvasion.phase} of ${FINAL_SIEGE_PHASES.length}` : 'Battle in progress'}</div>`;
        const esc = escalationMult(currentInvasion);
        if (esc > 1) {
            html += `<div class="raid-status-escalation">The siege escalates! Enemy attack +${Math.round((esc - 1) * 100)}%</div>`;
        }
        if (!squadAlive(heroSquad)) {
            html += `<div class="raid-status-siege">The Kingdom is under siege!</div>`;
        }
    } else if (raidsStarted) {
        const nextName = finalSiegeCountdown === 0 ? 'THE FINAL SIEGE' : getInvasionName(raidTierIndex, tierWave);
        html += `<div class="raid-status-name">Next: ${nextName}</div>
            <div class="raid-status-timer">Arrives in ${formatTimer(invasionTimer)}</div>`;
        if (finalSiegeCountdown > 0) {
            html += `<div class="raid-status-siege">A herald arrives: the Final Siege approaches — ${finalSiegeCountdown} raid${finalSiegeCountdown === 1 ? '' : 's'} remain${finalSiegeCountdown === 1 ? 's' : ''}!</div>`;
        }
    } else {
        html += `<div class="raid-status-name">No raids yet</div>`;
    }

    if (lastVictory) {
        const legacyPart = lastVictory.legacy ? ` &middot; +${lastVictory.legacy.toLocaleString()} Legacy` : '';
        html += `<div class="victory-inline">Repelled: ${lastVictory.name} +${lastVictory.loot.toLocaleString()}g${legacyPart}</div>`;
    }

    document.getElementById('raid-status-bar').innerHTML = html;
}

// Heroes: backline column first, frontline second (frontline sits nearest the
// Enemies area). Enemies: frontline first, backline second (frontline sits
// nearest the Defenders area). This keeps both frontlines next to each other.
function renderSquad(containerId, squad, sideClass, columnOrder, interactive, cols = 3) {
    const el = document.getElementById(containerId);
    el.innerHTML = '';
    // Expanded grids shrink their slots so the battle panel keeps its footprint.
    el.classList.toggle('grid-compact', squad.length > 6);
    for (const colDef of columnOrder) {
        const colEl = document.createElement('div');
        colEl.className = 'battle-column';

        const label = document.createElement('div');
        label.className = 'battle-row-label';
        label.textContent = colDef.label;
        colEl.appendChild(label);

        for (let i = 0; i < cols; i++) {
            const index = colDef.row * cols + i;
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
    // Between battles, show the upcoming tier's grid as the empty frame.
    const enemyGrid = currentInvasion ? currentInvasion.grid : RAID_TIERS[raidTierIndex].grid;
    const enemies = currentInvasion ? currentInvasion.enemies : new Array(enemyGrid.rows * enemyGrid.cols).fill(null);
    // Hero columns render rear-to-front so the frontline sits nearest the
    // enemy area; enemy columns front-first. Rows past the backline: Reserve.
    const dims = heroGridDims();
    const rowLabel = r => r === 0 ? 'Frontline' : r === 1 ? 'Backline' : 'Reserve';
    const heroColumns = [];
    for (let r = dims.rows - 1; r >= 0; r--) heroColumns.push({ label: rowLabel(r), row: r });
    const enemyColumns = [];
    for (let r = 0; r < enemyGrid.rows; r++) enemyColumns.push({ label: rowLabel(r), row: r });
    renderSquad('heroSquad', heroSquad, '', heroColumns, true, dims.cols);
    renderSquad('enemySquad', enemies, 'enemy', enemyColumns, false, enemyGrid.cols);
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
            if (base.attack) statParts.push(`ATK ${Math.round(base.attack.power * tier.incomeMult * heroPowerMult())}`);
            if (base.heal) statParts.push(`HLR ${Math.round(base.heal.power * tier.incomeMult * heroPowerMult())}`);
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

// --- Run summary & upgrade shop overlay ---
function renderUpgradeTree(treeId) {
    const tree = UPGRADE_TREES[treeId];
    let html = `<div class="upgrade-tree">
        <div class="upgrade-tree-title">${tree.label}</div>`;

    for (const node of tree.nodes) {
        const rank = upgradeRank(node.id);
        const maxed = rank >= node.maxRank;
        const cost = maxed ? null : node.costs[rank];
        const canAfford = !maxed && meta.legacy >= cost;

        html += `<div class="upgrade-node ${maxed ? 'upgrade-node--maxed' : ''}">
            <div class="upgrade-info">
                <div class="upgrade-name">${node.name}</div>
                <div class="upgrade-desc">${node.desc}</div>
                <div class="upgrade-rank">Rank ${rank} / ${node.maxRank}</div>
            </div>
            <div class="upgrade-action">
                ${maxed
                    ? `<div class="upgrade-maxed-label">Maxed</div>`
                    : `<div class="upgrade-cost">${cost.toLocaleString()} Legacy</div>
                       <button class="btn-upgrade" onclick="buyUpgrade('${node.id}')" ${canAfford ? '' : 'disabled'}>Buy</button>`}
            </div>
        </div>`;
    }

    html += `</div>`;
    return html;
}

function renderRunSummary() {
    const overlay = document.getElementById('run-summary-overlay');
    if (!runEnded || !runSummary) {
        overlay.classList.add('hidden');
        return;
    }
    const s = runSummary;

    let html = `<div class="summary-title">${s.reason === 'abandoned' ? `Age ${s.age} Concluded` : 'The Kingdom Has Fallen'}</div>
        <div class="summary-sub">${s.reason === 'abandoned' ? 'Abandoned during' : 'Fell to'} ${s.fellTo} at ${s.levelName} level</div>
        ${s.lessons ? `<div class="summary-lessons">Lessons of the Last Siege: the failed assault taught the realm much. <strong>+${s.lessons.toLocaleString()} Legacy</strong></div>` : ''}
        <div class="summary-stats">
            <div class="summary-stat"><span class="summary-stat-value">${s.waves}</span> wave${s.waves === 1 ? '' : 's'} repelled this Age</div>
            <div class="summary-stat"><span class="summary-stat-value">+${s.legacy.toLocaleString()}</span> Legacy earned this Age</div>
            <div class="summary-stat"><span class="summary-stat-value">${meta.legacy.toLocaleString()}</span> Legacy available</div>
        </div>
        <div class="summary-shop-heading">Spend Legacy on permanent upgrades — they carry into every future Age.</div>
        <div class="summary-trees">${renderUpgradeTree('economy')}${renderUpgradeTree('military')}</div>
        <button class="btn-new-age" onclick="foundNewAge()">Found a New Age &mdash; Age ${meta.age + 1}</button>`;

    document.getElementById('run-summary-content').innerHTML = html;
    overlay.classList.remove('hidden');
}

// Victory screen (M13): the campaign is won. Reuses the run-summary overlay.
function renderVictory() {
    if (!victoryPending) return;
    const overlay = document.getElementById('run-summary-overlay');
    const lifetimeLegacy = meta.fallHistory.reduce((sum, f) => sum + (f.legacy || 0), 0) + runLegacyEarned;
    const hours = Math.floor(meta.gameSeconds / 3600);
    const mins = Math.floor((meta.gameSeconds % 3600) / 60);
    const fallLines = meta.fallHistory.map(f =>
        `<div class="victory-age-line">Age ${f.age} — fell to ${f.name} (${f.waves} wave${f.waves === 1 ? '' : 's'})</div>`).join('');

    const html = `<div class="summary-title summary-title--victory">The Kingdom Stands Eternal</div>
        <div class="summary-sub">The Final Siege is broken. The Dragon Empress will not return.</div>
        <div class="summary-stats">
            <div class="summary-stat"><span class="summary-stat-value">${meta.age}</span> Age${meta.age === 1 ? '' : 's'} founded</div>
            <div class="summary-stat"><span class="summary-stat-value">${lifetimeLegacy.toLocaleString()}</span> Legacy earned across the campaign</div>
            <div class="summary-stat"><span class="summary-stat-value">${hours}h ${mins}m</span> of kingdom time</div>
        </div>
        ${fallLines ? `<div class="victory-history"><div class="summary-shop-heading">The Ages that came before:</div>${fallLines}</div>` : ''}
        <button class="btn-new-age" onclick="continueEndless()">Rule in Peace &mdash; Endless Mode</button>`;

    document.getElementById('run-summary-content').innerHTML = html;
    overlay.classList.remove('hidden');
}

function tickRender() {
    document.getElementById('gold-display').textContent = Math.floor(gold).toLocaleString();
    document.getElementById('gps-display').textContent = Math.round(goldPerSecond * econIncomeMult()).toLocaleString();
    document.getElementById('legacy-display').textContent = meta.legacy.toLocaleString();
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

loadMeta();
loadGame();
resizeHeroSquad(); // no-save startups still need the squad sized to War Banners rank
if (recruitPool.length === 0) refreshPool();
if (kingdomLevel >= RAID_TRIGGER_LEVEL && heroRecruitPool.length === 0) refreshHeroPool();
updateUI();
renderRunSummary(); // reshow the run-summary screen if the game was closed mid-summary
renderVictory();    // likewise the victory screen (closed mid-celebration)
setGameSpeed(gameSpeed); // also starts the tick interval
