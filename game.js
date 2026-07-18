let gold = 75; // placeholder until loadGame(); kept at STARTING_GOLD_BY_TREASURY_RANK[0]
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
let lastSaveTime = 0; // wall-clock save throttle (M15 Phase 0)
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
// Hero hires cost x1.4 more per raid tier reached (M14.1): late-game income
// dwarfs flat hero costs, so a squad rebuild should stay a real purchase
// (~2-4 min of contemporaneous income) all game. Doesn't move battle outcomes
// (sim-verified — walls are attrition-bound, not gold-bound); it restores
// purchase weight.
const HERO_COST_TIER_GROWTH = 1.4;
const WALLS_DEFENSE_PER_RANK = 3; // Reinforced Walls: +3 Kingdom defense per rank (M14.1)

const ARM_TIMEOUT_MS = 3000;

const RAID_TRIGGER_LEVEL = 2;
const RAID_TRIGGER_GOLD = 4000;
// Extra breathing room before the very first raid ever arrives — the player
// needs time to hire their first heroes. Later raids use the tier's interval.
const FIRST_RAID_GRACE = 75;

// Bump when a rebalance makes old saves meaningless; mismatched saves are
// discarded on load (fresh start).
const SAVE_VERSION = 5;

// Dev build flag: keeps testing conveniences (auto-hire without the Steward's
// Ledger upgrade, dev speed buttons) always available. Flip to false for a
// release build.
const DEV_MODE = true;

// Game speed is pure wall-clock QoL: the whole engine runs on game-seconds
// (income, raid intervals, escalation), so a faster tick compresses real time
// without touching balance. Player speeds unlock via the Swift Seasons node;
// dev speeds exist only for testing.
const PLAYER_SPEEDS = [1, 2, 4];
const DEV_SPEEDS = [10, 50, 100];

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
    { name: 'Goblin Raid',  key: 'goblin', powerMult: 1.0,  defenseGrowth: 1.088, waveCount: 5,  raidInterval: 45, baseLoot: 1200,   lootGrowth: 1.10,
        grid: { rows: 2, cols: 3 }, traits: {},
        boss: { name: 'Goblin Warmaster', powerMult: 1.8, hpMult: 4.0, traits: { aura: { power: 0.15, range: 'all' } } },
        roster: { brute: 'Goblin Brute',    skirmisher: 'Goblin Skulker',   caster: 'Goblin Slinger',  shaman: 'Goblin Shaman',  sapper: 'Goblin Tunneler' } },
    { name: 'Orc Warband',  key: 'orc', powerMult: 1.52, defenseGrowth: 1.088, waveCount: 8,  raidInterval: 45, baseLoot: 5000,   lootGrowth: 1.10,
        grid: { rows: 2, cols: 3 }, traits: { brute: { enrage: { speed: 1.5, power: 1 } } },
        boss: { name: 'Orc Warlord', powerMult: 1.8, hpMult: 4.0, traits: { enrage: { speed: 1.75, power: 1.25 } } },
        roster: { brute: 'Orc Brute',       skirmisher: 'Orc Berserker',    caster: 'Orc Warcaster',   shaman: 'Orc Witch Doctor', sapper: 'Orc Saboteur' } },
    { name: 'Bandit Horde', key: 'bandit', powerMult: 3.0,  defenseGrowth: 1.088, waveCount: 11, raidInterval: 40, baseLoot: 30000,  lootGrowth: 1.10,
        grid: { rows: 3, cols: 4 }, traits: { caster: { backlineChance: 0.7 } },
        boss: { name: 'Bandit King', powerMult: 1.8, hpMult: 4.0, traits: { backlineChance: 0.85 } },
        roster: { brute: 'Bandit Enforcer', skirmisher: 'Bandit Cutthroat', caster: 'Bandit Marksman', shaman: 'Bandit Medic',   sapper: 'Bandit Torchman' } },
    { name: 'Undead Legion', key: 'undead', powerMult: 7.6, defenseGrowth: 1.088, waveCount: 14, raidInterval: 35, baseLoot: 120000, lootGrowth: 1.10,
        grid: { rows: 3, cols: 4 }, traits: { caster: { reviveCharges: 1 } },
        boss: { name: 'Lich Commander', powerMult: 1.8, hpMult: 4.0, traits: { reviveCharges: 2 } },
        roster: { brute: 'Death Knight',    skirmisher: 'Shadow Reaver',    caster: 'Necromancer',     shaman: 'Bone Priest',    sapper: 'Grave Digger' } },
    { name: 'Infernal Siege', key: 'infernal', powerMult: 24.7, defenseGrowth: 1.088, waveCount: 17, raidInterval: 30, baseLoot: 500000, lootGrowth: 1.10,
        grid: { rows: 4, cols: 4 }, traits: { caster: { aoe: 'row' } },
        boss: { name: 'Demon Empress', powerMult: 1.8, hpMult: 4.0, traits: { aoe: 'row', enrage: { speed: 1, power: 1.25 } } },
        roster: { brute: 'Pit Fiend',       skirmisher: 'Hellhound',        caster: 'Flamecaller',     shaman: 'Blood Acolyte',  sapper: 'Cinder Imp' } }
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
    [ // Undead Legion (3x4) — necromancers raise the fallen: kill order matters
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
    [ // Infernal Siege (4x4) — flamecallers scour whole rows with hellfire: split your formation
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
// After the Demon Empress falls (first time only), a herald announces the
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
// M14.1 rebalance (acceptance-playtest feedback): the GUARD SPECTRUM — each
// unit's `guard` is its targeting-ticket weight within its row pool (unset =
// 1): guardian 3, paladin/banneret 2, fighter 1.5, assassin 0.5 ("slippery").
// Tanks tank FOR whoever shares their pool; a rear-row guardian bodyguards
// the backline (sim: rewarding vs marksman tiers, punished vs front-heavy
// ones — a real placement decision). Also: fighter debuts as the base-roster
// frontline damage-dealer; paladin heal trimmed 11->9 (stacks dominated);
// mender buffed 22 heal / 65 hp / 8 def (was never worth the slot).
// Sim-verified: front composition is tier-dependent (GF beats FF vs orc
// enrage; FF beats GG vs bandit/dark heal-walls), paladin-stacks are a
// specialist choice, and slippery assassins don't go degenerate (row-AoE
// ignores guard; a full back pool still lands ~6% of its fire on them).
const HERO_ARCHETYPES = {
    guardian: { names: ['Knight', 'Sentinel', 'Vanguard', 'Paragon'],    baseCost: 1000, base: { defense: 35, hp: 140, attack: { power: 8,  speed: 0.7 }, guard: 3 } },
    fighter:  { names: ['Footman', 'Sellsword', 'Blademaster', 'Warlord'], baseCost: 1100, base: { defense: 18, hp: 95, attack: { power: 14, speed: 1.0 }, guard: 1.5 } },
    ranged:   { names: ['Archer', 'Sharpshooter', 'Hunter', 'Marksman'], baseCost: 750,  base: { defense: 5,  hp: 60,  attack: { power: 18, speed: 1.3 } } },
    mender:   { names: ['Acolyte', 'Cleric', 'Druid', 'Saint'],          baseCost: 850,  base: { defense: 8,  hp: 65,  heal:   { power: 22, speed: 0.7 } } },
    paladin:  { names: ['Squire', 'Paladin', 'Crusader', 'Highlord'],    baseCost: 1300, unlock: 'paladin',
                base: { defense: 25, hp: 120, attack: { power: 9, speed: 0.7 }, heal: { power: 9, speed: 0.55 }, guard: 2 } },
    assassin: { names: ['Rogue', 'Assassin', 'Nightblade', 'Phantom'],   baseCost: 950,  unlock: 'assassin',
                base: { defense: 3,  hp: 45,  attack: { power: 26, speed: 1.2 }, backlineChance: 0.9, guard: 0.5 } },
    // M11 archetypes exercising the new engine features. Banneret's aura and
    // Frost Adept's chill are fixed effects — rarity scales their own stats.
    battlemage: { names: ['Adept', 'Battlemage', 'Warmage', 'Archmage'], baseCost: 1600, unlock: 'battlemage',
                base: { defense: 8,  hp: 70,  attack: { power: 12, speed: 0.8, aoe: 'row' } } },
    banneret: { names: ['Herald', 'Banneret', 'Marshal', 'High Marshal'], baseCost: 1500, unlock: 'banneret',
                base: { defense: 25, hp: 110, attack: { power: 6, speed: 0.6 }, aura: { power: 0.15, range: 'adjacent' }, guard: 2 } },
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
        gameSeconds: 0,        // lifetime game-time across all Ages (victory-screen stat)
        reduceMotion: false,   // manual no-shake/no-float toggle (M15 Phase 2; additive field)
        sceneView: true        // M15 increment 4: the scene IS the game; classic is the escape hatch
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
        gameSeconds: state.gameSeconds ?? 0,
        reduceMotion: state.reduceMotion ?? false,
        sceneView: state.sceneView ?? true // M15 scene/classic choice (default: scene)
    };
}

const UPGRADE_TREES = {
    economy: {
        label: 'Economy',
        nodes: [
            { id: 'trade',       name: 'Prosperous Trade', desc: '+25% gold income per rank',                                    maxRank: 5, costs: [15, 60, 250, 1000, 6000] },
            { id: 'treasury',    name: 'Royal Treasury',   desc: 'Begin each Age with a larger treasury (250 / 1,000 / 4,000 / 15,000 gold)', maxRank: 4, costs: [10, 40, 150, 500] },
            { id: 'builders',    name: 'Master Builders',  desc: '+50% Builder HP regen per rank',                               maxRank: 3, costs: [25, 100, 400] },
            { id: 'steward',     name: "Steward's Ledger", desc: 'Unlocks auto-hiring for townsfolk',                            maxRank: 1, costs: [150] },
            { id: 'seasons',     name: 'Swift Seasons',    desc: 'Unlocks the game speed selector — rule your Ages at 1×, 2×, or 4× pace', maxRank: 1, costs: [300] },
            { id: 'foundations', name: 'Old Foundations',  desc: 'New Ages begin at Village level',                              maxRank: 1, costs: [400] },
            // Doctrines (M12): buildings feed the army, so town composition
            // stays a battle decision all game.
            { id: 'forgework', name: 'Smithy Forgework',    desc: 'Every Smithy sharpens the army: +1.5% hero attack each, on every swing (a full forge district: +10.5%)', maxRank: 1, costs: [2000] },
            { id: 'tactics',   name: 'Library Tactics',     desc: 'Every Library drills the army: heroes act +1% faster each — attacks AND heals (6 Libraries: +6%)', maxRank: 1, costs: [3000] },
            { id: 'salves',    name: 'Apothecary Salves',   desc: 'Every Apothecary tends the field: heroes regenerate 0.3% max HP/s each in battle (4 shops fight like a fifth mender)', maxRank: 1, costs: [6000] },
            { id: 'blessing',  name: 'Cathedral Blessing',  desc: 'The first hero to fall each battle revives at 30% HP (requires a Cathedral)', maxRank: 1, costs: [10000] }
        ]
    },
    military: {
        label: 'Military',
        nodes: [
            { id: 'renown',  name: 'Hall of Legends',   desc: 'Greater heroes join the recruit pool (Rare / Epic / Legendary)', maxRank: 3, costs: [50, 750, 6000] },
            { id: 'paladin', name: "Paladin's Oath",    desc: 'Unlocks the Paladin — a stalwart who attacks and heals',   maxRank: 1, costs: [250] },
            { id: 'assassin', name: 'Shadow Guild',     desc: 'Unlocks the Assassin — hunts the enemy backline',          maxRank: 1, costs: [400] },
            { id: 'battlemage', name: 'War Magics',     desc: 'Unlocks the Battlemage — strikes an entire enemy row',     maxRank: 1, costs: [800] },
            { id: 'frost', name: 'Rimecraft',           desc: 'Unlocks the Frost Adept — attacks slow the target',        maxRank: 1, costs: [1200] },
            { id: 'banneret', name: 'Standard Bearers', desc: 'Unlocks the Banneret — adjacent allies fight harder',      maxRank: 1, costs: [1500] },
            { id: 'squadsize', name: 'War Banners',     desc: 'Expand the hero squad (12 slots, then 16)',                maxRank: 2, costs: [4000, 30000] },
            { id: 'drills',  name: 'Weapon Drills',     desc: '+20% hero attack & healing per rank',        maxRank: 5, costs: [15, 60, 250, 1000, 6000] },
            { id: 'armor',   name: 'Hardened Armor',    desc: '+20% hero HP per rank',                      maxRank: 5, costs: [15, 60, 250, 1000, 6000] },
            { id: 'muster',  name: 'Muster Rolls',      desc: 'Hero hiring 15% cheaper per rank',           maxRank: 3, costs: [20, 80, 300] },
            { id: 'mustergrounds', name: 'Mustering Grounds', desc: '+1 hero per recruit-pool refresh (4, then 5) — comp-hunting stays viable as archetype unlocks widen the pool', maxRank: 2, costs: [300, 900] },
            { id: 'walls',   name: 'Reinforced Walls',  desc: '+250 max Kingdom HP and +3 Kingdom defense per rank — every siege hit lands softer', maxRank: 4, costs: [15, 60, 250, 1000] },
            { id: 'veteran', name: "Veteran's Welcome", desc: 'Each new Age begins with a free Rare Knight', maxRank: 1, costs: [100] }
        ]
    }
};

// Base 75, not 50: buying all 3 Hamlet cottages (39g) must still leave the
// 25g first Villager hire affordable — at 50g that was a hard new-save
// softlock (no income, no faucet, no escape; 2026-07-17 playtest).
const STARTING_GOLD_BY_TREASURY_RANK = [75, 250, 1000, 4000, 15000];

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
// Mustering Grounds: pool-QoL answer to archetype-unlock dilution (9 unlocked
// archetypes make a 3-slot pool a ~30% shot at any specific one per refresh).
function getHeroPoolSize()   { return HERO_POOL_SIZE + upgradeRank('mustergrounds'); }
function getKingdomDefense() { return KINGDOM_DEFENSE + WALLS_DEFENSE_PER_RANK * upgradeRank('walls'); }
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
function speedSelectorAvailable() { return DEV_MODE || upgradeRank('seasons') > 0; }
function allowedSpeeds() {
    const speeds = speedSelectorAvailable() ? [...PLAYER_SPEEDS] : [1];
    return DEV_MODE ? speeds.concat(DEV_SPEEDS) : speeds;
}

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
    if (!allowedSpeeds().includes(speed)) speed = 1;
    gameSpeed = speed;
    clearInterval(tickInterval);
    tickInterval = setInterval(tick, Math.floor(1000 / speed));
    renderSpeedButtons();
}

// Player speeds always render (locked until Swift Seasons); dev speeds append
// only in dev builds. Memoized like every panel — rebuilds only on change.
function renderSpeedButtons() {
    const unlocked = speedSelectorAvailable();
    let html = PLAYER_SPEEDS.map(s => {
        const locked = s > 1 && !unlocked;
        const active = s === gameSpeed ? ' btn-speed--active' : '';
        return locked
            ? `<button class="btn-speed btn-speed--locked" disabled title="Unlocks with Swift Seasons (Economy tree)">${s}×</button>`
            : `<button class="btn-speed${active}" data-action="setGameSpeed:${s}">${s}×</button>`;
    }).join('');
    if (DEV_MODE) {
        html += DEV_SPEEDS.map(s =>
            `<button class="btn-speed btn-speed--dev${s === gameSpeed ? ' btn-speed--active' : ''}" data-action="setGameSpeed:${s}">${s}×</button>`
        ).join('');
    }
    setPanelHtml('speed-buttons', html);
}

// Reduced-motion / no-shake toggle (M15 Phase 2). When the OS itself asks for
// reduced motion, the choice is honored unconditionally and the toggle locks.
function renderMotionToggle() {
    let html;
    if (SYSTEM_REDUCED_MOTION) {
        html = `<button class="btn-speed btn-speed--active btn-speed--locked" disabled title="Your system requests reduced motion">Reduced (system)</button>`;
    } else {
        const reduced = !!meta.reduceMotion;
        html = `<button class="btn-speed${reduced ? '' : ' btn-speed--active'}" data-action="setReduceMotion:0">Full</button>`
             + `<button class="btn-speed${reduced ? ' btn-speed--active' : ''}" data-action="setReduceMotion:1" title="No shake, flashes, or floating numbers">Reduced</button>`;
    }
    setPanelHtml('motion-toggle', html);
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

let poolGeneration = 0;     // bumped per refresh — drives the card shuffle-in animation
let heroPoolGeneration = 0;

function refreshPool() {
    recruitPool = [];
    for (let i = 0; i < POOL_SIZE; i++) {
        const r = generateRecruit();
        if (r) recruitPool.push(r);
    }
    poolGeneration++;
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
        emitFxData(b.type === 'hpregen' ? 'hireHp' : 'hireGold', { amount: recruit.income });

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
    emitFxData(b.type === 'hpregen' ? 'hireHp' : 'hireGold', { amount: recruit.income });

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
// Taunt (M14.1): within the chosen pool, a unit with guard > 1 draws that many
// targeting "tickets" — guardians (guard 3) soak hits that would land on
// whoever shares their pool. A lone unit in its pool gains nothing.
function weightedPick(pool) {
    let total = 0;
    for (const u of pool) total += u.guard || 1;
    let roll = Math.random() * total;
    for (const u of pool) {
        roll -= u.guard || 1;
        if (roll <= 0) return u;
    }
    return pool[pool.length - 1];
}

function pickTarget(attacker, enemySquad) {
    const alive = enemySquad.filter(u => u && u.alive);
    if (alive.length === 0) return null;
    const frontRow = Math.min(...alive.map(u => u.row));
    const front = alive.filter(u => u.row === frontRow);
    const back = alive.filter(u => u.row > frontRow);
    if (back.length === 0) return weightedPick(front);

    const wantsBackline = Math.random() < attacker.backlineChance;
    return weightedPick(wantsBackline ? back : front);
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
    const before = target.hp;
    target.hp = Math.min(target.maxHp, target.hp + power);
    if (target.hp > before) emitFx('heal', target, target.hp - before);
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
    emitFx('hit', defender, dmg);
    if (attacker.attack.chill && defender.hp > 0) {
        defender.chilledUntil = (currentInvasion ? currentInvasion.duration || 0 : 0) + attacker.attack.chill.duration;
        defender.chillMult = attacker.attack.chill.mult;
    }
    if (defender.hp <= 0) {
        defender.hp = 0;
        defender.alive = false;
        onUnitDeath(defender);
        // onUnitDeath may have raised them back up (necromancer / Blessing).
        if (defender.alive) emitFx('revive', defender);
        else emitFx('death', defender);
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
    const dmg = Math.max(1, Math.round(power * (1 - getKingdomDefense() / 100)));
    kingdomHP = Math.max(0, kingdomHP - dmg);
    emitFx('kingdomHit', null, dmg);
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
    emitFx('injury', null);
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
                emitFx('lunge', unit);
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
    unit.spriteKey = bossPart ? 'boss_' + tier.key : 'enemy_' + tier.key + '_' + archetypeKey;
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
    if (base.guard) unit.guard = base.guard;
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
        cost: Math.floor(archetype.baseCost * tier.costMult * heroCostMult() * Math.pow(HERO_COST_TIER_GROWTH, raidTierIndex))
    };
}

function refreshHeroPool() {
    heroRecruitPool = [];
    for (let i = 0; i < getHeroPoolSize(); i++) {
        heroRecruitPool.push(generateHeroRecruit());
    }
    heroPoolGeneration++;
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
    emitFx('raidStart', null);
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
    emitFx('repelled', null, loot);
    if (legacy > 0) emitFx('legacy', null, legacy);

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
    // The fall gets a beat before the ledger appears: the screen darkens,
    // then the summary rises through the lifting shroud. An abandoned Age
    // takes the short fade; a reload mid-summary still shows it instantly
    // (this path only runs at the moment of the fall).
    playFallTransition(reason === 'overrun');
}

function playFallTransition(dramatic) {
    if (reducedMotion() || document.getElementById('fx-fall-shroud')) return renderRunSummary();
    const v = document.createElement('div');
    v.id = 'fx-fall-shroud';
    if (!dramatic) v.classList.add('fx-fall-shroud--gentle');
    document.body.appendChild(v);
    setTimeout(() => {
        renderRunSummary();
        v.classList.add('fx-fall-shroud--lift');
        setTimeout(() => v.remove(), 800);
    }, dramatic ? 950 : 450);
}

// Dawn wash when a new Age begins — a warm light that fades as the fresh
// kingdom appears underneath.
function playDawnTransition() {
    if (reducedMotion() || document.getElementById('fx-dawn')) return;
    const v = document.createElement('div');
    v.id = 'fx-dawn';
    removeOnAnimationDone(v);
    document.body.appendChild(v);
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
    playDawnTransition();
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
    // Fresh boots (no save, or a discarded pre-rebalance one) must still
    // honor Royal Treasury; a usable save overwrites this right below.
    // Requires loadMeta() to have run first.
    gold = getStartingGold();
    const saved = localStorage.getItem('idleKingdomSave');
    if (!saved) return;
    const state = JSON.parse(saved);
    // Pre-rebalance saves are meaningless after a version bump — discard.
    if ((state.version ?? 1) !== SAVE_VERSION) return;

    gold = state.gold ?? getStartingGold();
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
    // Clamp to what this build + the player's upgrades actually allow (meta is
    // already loaded): a save carrying 4x without Swift Seasons, or a dev speed
    // in a non-dev build, falls back to 1x rather than keeping a speed the UI
    // can no longer select.
    gameSpeed = allowedSpeeds().includes(state.gameSpeed) ? state.gameSpeed : 1;
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
        refreshPool();
    }

    if (kingdomLevel >= RAID_TRIGGER_LEVEL) {
        heroPoolTimer++;
        if (heroPoolTimer >= HERO_POOL_REFRESH_INTERVAL) {
            heroPoolTimer = 0;
            refreshHeroPool();
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

    // Saves are wall-clock throttled (M15 Phase 0): at 100x dev speed a
    // per-tick localStorage write is real overhead. Critical moments
    // (endRun, purchases, upgrade buys) still save explicitly themselves.
    if (Date.now() - lastSaveTime >= 1000) {
        lastSaveTime = Date.now();
        saveGame();
    }
}

function levelUpKingdom() {
    const next = levels[kingdomLevel + 1];
    if (!next || gold < next.cost) return;
    gold -= next.cost;
    kingdomLevel += 1;
    if (kingdomLevel >= RAID_TRIGGER_LEVEL && heroRecruitPool.length === 0) refreshHeroPool();
    emitFxData('levelup', { label: levels[kingdomLevel].name });
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
    emitFxData('built', { id });
    saveGame();
    updateUI();
}

function canHireRecruit(recruit) {
    const b = buildings[recruit.buildingId];
    const hasSlot = b.residents.length < b.count * b.slotsPerBuilding;
    return gold >= recruit.cost && hasSlot && getBuildingCap(recruit.buildingId) > 0;
}

function renderRecruitPool() {
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
                const rarityClass = value ? `btn-auto--${value}` : '';
                return `<button class="btn-auto ${rarityClass} ${active ? 'btn-auto--active' : ''}" data-action="setAutoRecruit:${value === null ? 'null' : value}">${label}</button>`;
            }).join('')}
        </div>`
        : `<div class="auto-recruit"><span class="auto-recruit-label auto-recruit-locked">Auto-hire: unlocks with Steward's Ledger (Economy)</span></div>`;

    // The countdown is volatile text — it lives OUTSIDE the memoized string
    // (filled in refreshVolatileUI) so the ticking clock doesn't force a full
    // panel rebuild every game-second, which destroyed Hire buttons mid-click.
    let html = `<div class="pool-header">
        <span class="pool-timer" id="pool-timer-text"></span>
        ${autoRecruitHtml}
    </div><div class="pool-cards">`;

    if (recruitPool.length === 0) {
        html += `<div class="pool-empty">No one seeking work right now.</div>`;
    } else {
        recruitPool.forEach(recruit => {
            const b = buildings[recruit.buildingId];
            const slots = b.count * b.slotsPerBuilding;
            const hasSlot = b.residents.length < slots;
            const buildingUnlocked = getBuildingCap(recruit.buildingId) > 0;
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
                    ${portraitInner('town_' + recruit.typeId, letter)}
                </div>
                <div class="recruit-info">
                    <div class="recruit-name">${recruit.name}</div>
                    <div class="recruit-rarity" style="color:${rarityInfo.color}">${rarityInfo.name}</div>
                    <div class="recruit-stat">${valueLabel}</div>
                    ${hint ? `<div class="recruit-hint">${hint}</div>` : ''}
                </div>
                <div class="recruit-action">
                    <div class="recruit-cost">${recruit.cost.toLocaleString()}g</div>
                    <button class="btn-hire-recruit" data-recruit-id="${recruit.id}" data-action="hireRecruit:${recruit.id}">Hire</button>
                </div>
            </div>`;
        });
    }

    html += `</div>`;
    setPanelHtml('recruit-pool', html);
}

// Buy-button state for the current buy-quantity mode. Shared by the full
// render and the per-tick affordability refresh so the two can't drift.
function buildingPurchaseInfo(id) {
    const b = buildings[id];
    const cap = getBuildingCap(id);
    const atCap = cap - b.count <= 0;
    const n = buyQuantity === 'max' ? maxAffordableBuildings(id) : Math.min(buyQuantity, cap - b.count);
    const totalCost = n > 0 ? bulkBuildingCost(id, n) : 0;
    const canAfford = n > 0 && gold >= totalCost;
    const costLabel = atCap ? 'At cap'
        : buyQuantity === 1 || n <= 0
        ? `${b.cost.toLocaleString()} gold`
        : `${totalCost.toLocaleString()} gold (×${n})`;
    return { canAfford, costLabel };
}

function renderBuildings() {
    const qtys = [1, 5, 10, 'max'];
    let html = `<div class="buy-mode">
        <span class="buy-mode-label">Buy:</span>
        ${qtys.map(q => `<button class="btn-qty ${buyQuantity === q ? 'btn-qty--active' : ''}" data-action="setBuyQuantity:${q}">×${q}</button>`).join('')}
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

        const isExpanded = buildingExpanded[id] || false;
        const buildingTotal = b.residents.reduce((sum, r) => sum + r.income, 0);
        const totalLabel = buildingTotal > 0
            ? `${isHpregen ? Math.round(buildingTotal * 10) / 10 : buildingTotal.toLocaleString()} ${isHpregen ? 'hp/s' : 'g/s'}`
            : '';

        const descLabel = id === 'keep' ? 'Improves hero recruit rarity' : `Adds ${b.slotsPerBuilding} resident slots`;

        html += `<div class="building-card ${isHpregen ? 'building-card--hpregen' : ''}">
            <div class="building-row">
                <button class="btn-building" data-building-id="${id}" data-action="buyBuilding:${id}">
                    <span class="building-name">${b.name}</span>
                    <span class="building-meta">
                        <span class="building-cost"></span>
                        <span class="building-desc">${descLabel}</span>
                    </span>
                    <span class="building-stats">
                        <span class="building-owned">${b.count} / ${cap} buildings</span>
                        ${b.count > 0 && hasSlots ? `<span class="building-owned">${b.residents.length} / ${totalSlots} residents</span>` : ''}
                        ${id === 'keep' && b.count > 0 ? `<span class="building-income-total">+${b.count} hero rarity bias</span>` : ''}
                        ${totalLabel ? `<span class="building-income-total ${isHpregen ? 'building-income-total--hpregen' : ''}">${totalLabel}</span>` : ''}
                    </span>
                </button>
                ${b.count > 0 && hasSlots ? `<button class="btn-expand" data-action="toggleBuilding:${id}" title="${isExpanded ? 'Collapse' : 'Expand residents'}">${isExpanded ? '▲' : '▼'}</button>` : ''}
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
                // Injury recovery countdown is volatile — refreshVolatileUI
                // maintains the title so the ticking clock doesn't rebuild
                // the whole buildings panel every game-second.
                const injuredTitle = injured ? `&#10;INJURED — recovering (no income)` : '';
                html += `<div class="portrait portrait--${r.rarity || 'common'}${injured ? ' portrait--injured' : ''}" data-type="${r.typeId || 'villager'}"
                    title="${r.name} (${rarityInfo.name}) — ${valueLabel}${injuredTitle}&#10;Click to dismiss"
                    data-action="fireResident:${id}:${r.originalIndex}">
                    ${injured ? '<span class="portrait-letter">✚</span>' : portraitInner('town_' + (r.typeId || 'villager'), letter)}
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
    setPanelHtml('building-list', html);
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
            <button class="btn-levelup" data-action="levelUpKingdom" ${canAfford ? '' : 'disabled'}>
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
                    <button class="btn-reset btn-reset--confirm" data-action="confirmNewAge">Yes, end it</button>
                    <button class="btn-reset" data-action="cancelNewAge">Cancel</button>
                </div>
            </div>`;
        } else {
            html += `<div class="panel-section">
                <button class="btn-new-age-side" data-action="showNewAgeConfirm">Found a New Age</button>
            </div>`;
        }
    }

    if (confirmingReset) {
        html += `<div class="panel-section">
            <div class="panel-label" style="color:#8a4040">Reset all progress?</div>
            <div class="reset-confirm-buttons">
                <button class="btn-reset btn-reset--confirm" data-action="doResetGame">Yes, reset</button>
                <button class="btn-reset" data-action="cancelReset">Cancel</button>
            </div>
        </div>`;
    } else {
        html += `<div class="panel-section">
            <button class="btn-reset" data-action="showResetConfirm">Reset game</button>
        </div>`;
    }

    setPanelHtml('left-panel-dynamic', html);
}

let kingdomTrailPct = 100; // M15 Phase 1: crimson damage-trail lags behind HP losses

function renderKingdomHP() {
    const hpMax = getKingdomHpMax();
    const pct = Math.max(0, Math.min(100, (kingdomHP / hpMax) * 100));
    // Structure is memoized WITHOUT live values; widths/caption update in
    // place each frame so the trail animation isn't destroyed by rebuilds.
    const structure = `<div class="panel-label">Kingdom HP</div>
        <div class="hp-bar-track"><div class="hp-bar-trail"></div><div class="hp-bar-fill"></div></div>
        <div class="hp-bar-caption"></div>
        ${kingdomHP <= 0 ? '<div class="kingdom-falling">Kingdom Falling!</div>' : ''}
        ${kingdomFallRecord ? `<div class="kingdom-fall-record">Fell at: ${kingdomFallRecord.name} (Kingdom Lv ${kingdomFallRecord.level})</div>` : ''}`;
    setPanelHtml('kingdom-hp', structure);
    if (pct >= kingdomTrailPct) kingdomTrailPct = pct;             // heals snap the trail up
    else kingdomTrailPct = Math.max(pct, kingdomTrailPct - 0.7);   // losses drain it slowly
    const el = document.getElementById('kingdom-hp');
    el.querySelector('.hp-bar-fill').style.width = pct + '%';
    el.querySelector('.hp-bar-trail').style.width = kingdomTrailPct + '%';
    el.querySelector('.hp-bar-caption').textContent = `${Math.round(kingdomHP).toLocaleString()} / ${hpMax.toLocaleString()}`;
}

function renderRaidStatusBar() {
    let html = '';

    // Live numbers (arrival countdown, escalation %) render into fixed child
    // elements filled by refreshVolatileUI — baking them into this string
    // would rebuild the bar every game-second and restart its CSS animations.
    if (currentInvasion) {
        html += `<div class="raid-status-name">${currentInvasion.name}</div>
            <div class="raid-status-timer">${currentInvasion.finalSiege ? `Phase ${currentInvasion.phase} of ${FINAL_SIEGE_PHASES.length}` : 'Battle in progress'}</div>`;
        if (escalationMult(currentInvasion) > 1) {
            html += `<div class="raid-status-escalation" id="raid-esc-line"></div>`;
        }
        if (!squadAlive(heroSquad)) {
            html += `<div class="raid-status-siege">The Kingdom is under siege!</div>`;
        }
    } else if (raidsStarted) {
        const nextName = finalSiegeCountdown === 0 ? 'THE FINAL SIEGE' : getInvasionName(raidTierIndex, tierWave);
        html += `<div class="raid-status-name">Next: ${nextName}</div>
            <div class="raid-status-timer">Arrives in <span id="raid-timer-text"></span></div>`;
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

    setPanelHtml('raid-status-bar', html);
}

// Heroes: backline column first, frontline second (frontline sits nearest the
// Enemies area). Enemies: frontline first, backline second (frontline sits
// nearest the Defenders area). This keeps both frontlines next to each other.
// --- M15 Phase 0: persistent battle-slot DOM + FX bus ---
// Slots are BUILT once per structural change (grid shape or unit identity,
// tracked by a signature) and UPDATED in place every render frame. Persistent
// elements are what lets CSS animations (hit flashes, floating numbers)
// survive across frames — innerHTML rebuilds killed them every tick before.

let domKeyCounter = 0;
const slotElByKey = new Map(); // unit._domKey -> live slot element

function unitDomKey(unit) {
    if (unit._domKey === undefined) unit._domKey = ++domKeyCounter;
    return unit._domKey;
}

// FX bus: combat emits typed events; drainFx runs once per RENDERED frame and
// coalesces per unit (one number per unit per frame, float count capped), so
// 100x dev speed produces the same on-screen effect density as 1x.
const fxQueue = [];
const FX_MAX_FLOATS = 14; // concurrent floats in the battle overlay layer
const SYSTEM_REDUCED_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
// System preference OR the manual in-game toggle (M15 Phase 2, persisted in
// meta). JS spawns check this; CSS animations are gated by the matching
// `body.reduce-motion` class (synced in renderAll) plus the media query.
function reducedMotion() { return SYSTEM_REDUCED_MOTION || !!meta.reduceMotion; }

function emitFx(type, unit, amount) {
    // Hidden tabs don't render (rAF pauses), so a long-running battle could
    // pool events without bound — stale visuals aren't worth keeping.
    if (fxQueue.length > 2000) fxQueue.length = 0;
    fxQueue.push({
        type,
        key: unit ? unitDomKey(unit) : null,
        side: unit ? unit.side : null,
        name: unit ? unit.name : null,
        amount: amount || 0
    });
}

// Non-unit events (town/progression juice, M15 Phase 2) carry a free-form
// payload instead of a unit key.
function emitFxData(type, data) {
    if (fxQueue.length > 2000) fxQueue.length = 0;
    fxQueue.push({ type, ...data });
}

// Flashes that target content INSIDE memoized panels can't run in drainFx —
// it drains before the panel renders, and the rebuild would wipe the class.
// They queue here and fire at the END of renderAll, after panels settle.
const postRenderFlashes = [];

function flashClass(el, cls) {
    if (!el) return;
    el.classList.remove(cls);
    void el.offsetWidth; // reflow so re-adding the class restarts the animation
    el.classList.add(cls);
}

// Self-removing FX nodes must also die on `animationcancel`: flipping the
// reduce-motion toggle mid-flight sets animation:none, which cancels instead
// of ending — without this, the node would linger invisibly forever.
function removeOnAnimationDone(el, selfOnly) {
    const done = e => { if (!selfOnly || e.target === el) el.remove(); };
    el.addEventListener('animationend', done);
    el.addEventListener('animationcancel', done);
}

// Floats and death-ghosts live in an overlay layer over the battle area —
// not inside the slots — so a squad-structure rebuild the same frame (a
// death, a hire) can't destroy them mid-animation.
function fxLayer() {
    let layer = document.getElementById('fx-layer');
    if (!layer) {
        layer = document.createElement('div');
        layer.id = 'fx-layer';
        document.querySelector('.battle-squads').appendChild(layer);
    }
    return layer;
}

function spawnFloatAt(anchorEl, text, cls) {
    if (reducedMotion()) return;
    const layer = fxLayer();
    if (layer.querySelectorAll('.fx-float').length >= FX_MAX_FLOATS) return;
    const lr = layer.getBoundingClientRect();
    const ar = anchorEl.getBoundingClientRect();
    const f = document.createElement('div');
    f.className = 'fx-float ' + cls;
    f.textContent = text;
    f.style.left = (ar.left - lr.left + ar.width / 2) + 'px';
    f.style.top = (ar.top - lr.top - 4) + 'px';
    removeOnAnimationDone(f);
    layer.appendChild(f);
}

// One-at-a-time float pinned inside a stable (never innerHTML-replaced)
// container — used for the Legacy gain on the admin panel's resource row.
function spawnBadgeFloat(container, text, cls) {
    if (reducedMotion() || !container || container.querySelector('.fx-float')) return;
    const f = document.createElement('div');
    f.className = 'fx-float fx-float--badge ' + cls;
    f.textContent = text;
    removeOnAnimationDone(f);
    container.appendChild(f);
}

function spawnDeathGhost(slot, name) {
    if (reducedMotion()) return;
    const layer = fxLayer();
    const lr = layer.getBoundingClientRect();
    const sr = slot.getBoundingClientRect();
    const g = document.createElement('div');
    g.className = 'fx-ghost';
    g.textContent = name;
    g.style.left = (sr.left - lr.left) + 'px';
    g.style.top = (sr.top - lr.top) + 'px';
    g.style.width = sr.width + 'px';
    g.style.height = sr.height + 'px';
    removeOnAnimationDone(g);
    layer.appendChild(g);
}

function fxVignette() {
    let v = document.getElementById('fx-vignette');
    if (!v) {
        v = document.createElement('div');
        v.id = 'fx-vignette';
        document.body.appendChild(v);
    }
    return v;
}

function drainFx() {
    if (fxQueue.length === 0) return;
    const dmg = new Map(), heal = new Map(), lunges = new Map();
    const deaths = [], revives = [], builtIds = new Set();
    let kingdomHit = 0, injury = false, raidStart = false, repelledLoot = 0, legacyGain = 0;
    let hireGold = 0, hireHp = 0, levelUpLabel = null;
    for (const fx of fxQueue) {
        if (fx.type === 'hit') dmg.set(fx.key, (dmg.get(fx.key) || 0) + fx.amount);
        else if (fx.type === 'heal') heal.set(fx.key, (heal.get(fx.key) || 0) + fx.amount);
        else if (fx.type === 'lunge') lunges.set(fx.key, fx.side);
        else if (fx.type === 'death') deaths.push(fx);
        else if (fx.type === 'revive') revives.push(fx);
        else if (fx.type === 'kingdomHit') kingdomHit += fx.amount;
        else if (fx.type === 'injury') injury = true;
        else if (fx.type === 'raidStart') raidStart = true;
        else if (fx.type === 'repelled') repelledLoot += fx.amount;
        else if (fx.type === 'legacy') legacyGain += fx.amount;
        else if (fx.type === 'hireGold') hireGold += fx.amount;   // coalesced: auto-hire
        else if (fx.type === 'hireHp') hireHp += fx.amount;       // sprees float ONE sum
        else if (fx.type === 'built') builtIds.add(fx.id);
        else if (fx.type === 'levelup') levelUpLabel = fx.label;
    }
    fxQueue.length = 0;

    // Scene routing: when the scene view is open, the same events also land on
    // the scene's world units (sceneUnitElByKey) and chips. Classic targets
    // keep receiving theirs — they stay rendered (covered, not display:none),
    // so their animations still run and self-remove. Geometry capture rule
    // holds for the scene too: buildSceneBattle runs later in this same frame.
    const sceneEl = key => {
        if (!sceneOpen) return null;
        const el = sceneUnitElByKey.get(key);
        return el && el.isConnected ? el : null;
    };

    // Deaths first: ghosts must capture slot geometry BEFORE this frame's
    // squad render rebuilds the structure (drainFx runs at the top of
    // renderAll for exactly this reason).
    for (const fx of deaths) {
        const slot = slotElByKey.get(fx.key);
        if (slot && slot.isConnected) {
            if (fx.side === 'hero') spawnDeathGhost(slot, fx.name);
            else flashClass(slot, 'fx-death-anim');
        }
        const su = sceneEl(fx.key);
        if (su) {
            if (fx.side === 'hero') spawnSceneGhost(su);
            else flashClass(su, 'fx-death-anim');
        }
    }
    for (const fx of revives) {
        flashClass(slotElByKey.get(fx.key), 'fx-revive');
        flashClass(sceneEl(fx.key), 'fx-revive');
    }
    for (const [key, side] of lunges) {
        const slot = slotElByKey.get(key);
        if (slot && slot.isConnected) flashClass(slot, side === 'hero' ? 'fx-lunge-right' : 'fx-lunge-left');
        flashClass(sceneEl(key), side === 'hero' ? 'fx-lunge-right' : 'fx-lunge-left');
    }
    for (const [key, amount] of dmg) {
        const slot = slotElByKey.get(key);
        if (slot && slot.isConnected) {
            flashClass(slot, 'fx-hit');
            spawnFloatAt(slot, '-' + Math.round(amount).toLocaleString(), 'fx-float--dmg');
        }
        const su = sceneEl(key);
        if (su) {
            flashClass(su, 'fx-hit');
            spawnSceneFloatAt(su, '-' + Math.round(amount).toLocaleString(), 'fx-float--dmg');
        }
    }
    for (const [key, amount] of heal) {
        const slot = slotElByKey.get(key);
        if (slot && slot.isConnected) {
            flashClass(slot, 'fx-heal-glow');
            spawnFloatAt(slot, '+' + Math.round(amount).toLocaleString(), 'fx-float--heal');
        }
        const su = sceneEl(key);
        if (su) {
            flashClass(su, 'fx-heal-glow');
            spawnSceneFloatAt(su, '+' + Math.round(amount).toLocaleString(), 'fx-float--heal');
        }
    }
    if (kingdomHit > 0) {
        flashClass(document.getElementById('kingdom-hp'), 'fx-kingdom-hit');
        flashClass(document.getElementById(sceneOpen ? 'scene' : 'game'), 'fx-shake');
        flashClass(fxVignette(), 'fx-vignette-pulse');
        if (sceneOpen) flashClass(document.getElementById('hud-wall'), 'fx-kingdom-hit');
    }
    if (injury) {
        flashClass(document.getElementById('town-buildings'), 'fx-injury-flash');
        if (sceneOpen) flashClass(document.getElementById('scene-vista'), 'fx-injury-flash');
    }
    const raidBar = document.getElementById('raid-status-bar');
    if (raidStart) {
        flashClass(raidBar, 'fx-raid-slam');
        // The scene raid chip is rebuilt later this frame (state flipped to
        // battle) — flash it AFTER the panels settle, like the built-flash.
        if (sceneOpen) postRenderFlashes.push({ selector: '#scene-raid-chip', cls: 'fx-raid-slam' });
    }
    if (repelledLoot > 0) {
        flashClass(raidBar, 'fx-repelled-flash');
        spawnFloatAt(raidBar, '+' + Math.round(repelledLoot).toLocaleString() + 'g', 'fx-float--loot');
        if (sceneOpen) {
            postRenderFlashes.push({ selector: '#scene-raid-chip', cls: 'fx-repelled-flash' });
            const chip = document.getElementById('scene-raid-chip');
            if (chip) spawnSceneFloatAt(chip, '+' + Math.round(repelledLoot).toLocaleString() + 'g', 'fx-float--loot');
        }
    }
    if (legacyGain > 0) {
        const legacyEl = document.getElementById('legacy-display');
        spawnBadgeFloat(legacyEl && legacyEl.parentElement, '+' + legacyGain.toLocaleString(), 'fx-float--legacy');
        const sceneLegacy = document.getElementById('scene-legacy');
        if (sceneOpen && sceneLegacy) spawnBadgeFloat(sceneLegacy.parentElement, '+' + legacyGain.toLocaleString(), 'fx-float--legacy');
    }
    if (hireGold > 0) {
        const gpsEl = document.getElementById('gps-display');
        spawnBadgeFloat(gpsEl && gpsEl.parentElement, `+${Math.round(hireGold * 10) / 10} g/s`, 'fx-float--gps');
        const sceneGps = document.getElementById('scene-gps');
        if (sceneOpen && sceneGps) spawnBadgeFloat(sceneGps.parentElement, `+${Math.round(hireGold * 10) / 10} g/s`, 'fx-float--gps');
    }
    if (hireHp > 0) {
        spawnBadgeFloat(document.getElementById('kingdom-hp'), `+${Math.round(hireHp * 10) / 10} hp/s`, 'fx-float--gps');
        if (sceneOpen) spawnBadgeFloat(document.getElementById('hud-wall'), `+${Math.round(hireHp * 10) / 10} hp/s`, 'fx-float--gps');
    }
    // Building flash targets memoized-panel content: queue for AFTER the
    // panel render this frame (the rebuild would wipe a class set here).
    for (const id of builtIds) {
        postRenderFlashes.push({ selector: `.btn-building[data-building-id="${id}"]`, cls: 'fx-built' });
        if (sceneOpen) postRenderFlashes.push({ selector: `#scene-vista .plot[data-bldg="${id}"]`, cls: 'fx-built' });
    }
    if (levelUpLabel) spawnLevelUpBanner(levelUpLabel);
}

// Full-width fanfare for the kingdom level-up — the economic ratchet moment.
// One at a time; player-triggered, so no dev-speed budget concerns.
function spawnLevelUpBanner(levelName) {
    if (reducedMotion() || document.getElementById('fx-levelup-banner')) return;
    const b = document.createElement('div');
    b.id = 'fx-levelup-banner';
    b.innerHTML = `<div class="fx-levelup-rule"></div>
        <div class="fx-levelup-text">The realm rises &mdash; <strong>${levelName}</strong></div>
        <div class="fx-levelup-rule"></div>`;
    removeOnAnimationDone(b, true);
    document.body.appendChild(b);
}

// --- M15 sprite pipeline (runtime — no build step, per the tech-stack rule) ---
// The game loads the RAW Gemini sprites straight from assets/raw/ and runs
// the whole art pipeline at boot, in memory: key out the magenta background,
// trim to content, compute the foot anchor (weighted centroid of the bottom
// rows, weapon overhang excluded — seats sprites in future diorama slots),
// and downscale. A sprite that hasn't been generated yet is just a missing
// file: the UI falls back to letter portraits per key, so an art drop is
// "copy PNG into assets/raw, refresh". Needs http serving — canvas pixel
// access is blocked on file:// and the loader degrades to letters there.
const SPRITE_MAX_H = 160;
const sprites = {}; // key -> { url, w, h, ax, ay } (foot anchor in output px)
let spriteLoadBlocked = false; // file:// canvas taint — scene shows a serve-over-http notice

const SPRITE_SOURCES = {
    hero_guardian: 'raw_hero_knight_v3.png',
    hero_fighter: 'raw_hero_fighter.png',
    hero_ranged: 'raw_hero_ranged.png',
    hero_mender: 'raw_hero_mender.png',
    hero_paladin: 'raw_hero_paladin.png',
    hero_assassin: 'raw_hero_assassin.png',
    hero_battlemage: 'raw_hero_battlemage.png',
    hero_banneret: 'raw_hero_banneret.png',
    hero_frostadept: 'raw_hero_frostadept.png',
    town_villager: 'raw_town_villager.png',
    town_tavernkeeper: 'raw_town_tavernkeeper.png',
    town_blacksmith: 'raw_town_blacksmith.png',
    town_scholar: 'raw_town_scholar.png',
    town_builder: 'raw_town_builder.png',
    town_alchemist: 'raw_town_alchemist.png',
    town_mage: 'raw_town_mage.png',
    town_priest: 'raw_town_highpriest.png',
    enemy_goblin_brute: 'raw_enemy_goblin_brute.png',
    enemy_goblin_skirmisher: 'raw_enemy_goblin_skirmisher.png',
    enemy_goblin_caster: 'raw_enemy_goblin_caster.png',
    enemy_goblin_shaman: 'raw_enemy_goblin_shaman.png',
    enemy_goblin_sapper: 'raw_enemy_goblin_sapper.png',
    boss_goblin: 'raw_boss_goblin.png',
    enemy_orc_brute: 'raw_enemy_orc_brute.png',
    enemy_orc_skirmisher: 'raw_enemy_orc_skirmisher.png',
    enemy_orc_caster: 'raw_enemy_orc_caster.png',
    enemy_orc_shaman: 'raw_enemy_orc_shaman.png',
    enemy_orc_sapper: 'raw_enemy_orc_sapper.png',
    boss_orc: 'raw_boss_orc.png',
    enemy_bandit_brute: 'raw_enemy_bandit_brute.png',
    enemy_bandit_skirmisher: 'raw_enemy_bandit_skirmisher.png',
    enemy_bandit_caster: 'raw_enemy_bandit_caster.png',
    enemy_bandit_shaman: 'raw_enemy_bandit_shaman.png',
    enemy_bandit_sapper: 'raw_enemy_bandit_sapper.png',
    boss_bandit: 'raw_boss_bandit.png',
    enemy_undead_brute: 'raw_enemy_undead_brute.png',
    enemy_undead_skirmisher: 'raw_enemy_undead_skirmisher.png',
    enemy_undead_caster: 'raw_enemy_undead_caster.png',
    enemy_undead_shaman: 'raw_enemy_undead_shaman.png',
    enemy_undead_sapper: 'raw_enemy_undead_sapper.png',
    boss_undead: 'raw_boss_undead.png',
    enemy_infernal_brute: 'raw_enemy_infernal_brute.png',
    enemy_infernal_skirmisher: 'raw_enemy_infernal_skirmisher.png',
    enemy_infernal_caster: 'raw_enemy_infernal_caster.png',
    enemy_infernal_shaman: 'raw_enemy_infernal_shaman.png',
    enemy_infernal_sapper: 'raw_enemy_infernal_sapper.png',
    boss_infernal: 'raw_boss_infernal.png'
};

// Hero rarity variants (spec entries 56–82, generated lazily in any order):
// registered up front so a variant PNG dropped into assets/raw/ is live on
// refresh; heroSpriteKey() falls back to the base archetype sprite until then.
// 'common' included for the audit-demoted archetypes whose BASE art depicts a
// higher tier (mender = rare, paladin = epic) and so get a plain common file.
for (const a of ['guardian', 'fighter', 'ranged', 'mender', 'paladin', 'assassin', 'battlemage', 'banneret', 'frostadept']) {
    for (const r of ['common', 'rare', 'epic', 'legendary']) {
        SPRITE_SOURCES['hero_' + a + '_' + r] = 'raw_hero_' + a + '_' + r + '.png';
    }
}

// Building sprites (spec entries 47–55) for the M15 scene town vista: keyed by
// building id, so a raw_bldg_<id>.png dropped into assets/raw/ is live on
// refresh; renderVista() falls back to a schematic SVG per building until then.
for (const id of ['cottage', 'tavern', 'smithy', 'library', 'workshop', 'keep', 'apothecary', 'tower', 'cathedral']) {
    SPRITE_SOURCES['bldg_' + id] = 'raw_bldg_' + id + '.png';
}

function keyMagentaPixels(p) {
    for (let i = 0; i < p.length; i += 4) {
        const r = p[i], g = p[i + 1], b = p[i + 2];
        const m = Math.max(r, b);
        if (m > 130 && g < 0.65 * m && Math.min(r, b) > 0.45 * m) p[i + 3] = 0;
    }
}

function processSprite(img) {
    const c = document.createElement('canvas');
    c.width = img.width; c.height = img.height;
    const ctx = c.getContext('2d');
    ctx.drawImage(img, 0, 0);
    const data = ctx.getImageData(0, 0, c.width, c.height); // throws on file://
    const p = data.data;
    keyMagentaPixels(p);
    let minX = c.width, minY = c.height, maxX = -1, maxY = -1;
    for (let y = 0; y < c.height; y++) for (let x = 0; x < c.width; x++) {
        if (p[(y * c.width + x) * 4 + 3] > 8) {
            if (x < minX) minX = x; if (x > maxX) maxX = x;
            if (y < minY) minY = y; if (y > maxY) maxY = y;
        }
    }
    if (maxX < 0) return null;
    ctx.putImageData(data, 0, 0);
    const w = maxX - minX + 1, h = maxY - minY + 1;
    const bandTop = minY + Math.floor(h * 0.88);
    let sx = 0, n = 0;
    for (let y = bandTop; y <= maxY; y++) for (let x = minX; x <= maxX; x++) {
        if (p[(y * c.width + x) * 4 + 3] > 8) { sx += (x - minX); n++; }
    }
    const ax = n ? sx / n : w / 2;
    const half = w * 0.14;
    let ay = h - 1;
    outer:
    for (let y = maxY; y >= minY; y--) {
        const x0 = Math.max(minX, Math.floor(minX + ax - half));
        const x1 = Math.min(maxX + 1, Math.ceil(minX + ax + half));
        for (let x = x0; x < x1; x++) {
            if (p[(y * c.width + x) * 4 + 3] > 8) { ay = y - minY; break outer; }
        }
    }
    const scale = Math.min(1, SPRITE_MAX_H / h);
    const out = document.createElement('canvas');
    out.width = Math.max(1, Math.round(w * scale));
    out.height = Math.max(1, Math.round(h * scale));
    const octx = out.getContext('2d');
    octx.imageSmoothingEnabled = true;
    octx.imageSmoothingQuality = 'high';
    octx.drawImage(c, minX, minY, w, h, 0, 0, out.width, out.height);
    return { canvas: out, w: out.width, h: out.height, ax: Math.round(ax * scale), ay: Math.round(ay * scale) };
}

function loadSprites() {
    for (const key of Object.keys(SPRITE_SOURCES)) {
        const img = new Image();
        img.onload = () => {
            try {
                const s = processSprite(img);
                // Tiny blob: object URLs, not 40KB data: URLs — keeps style
                // attributes and the per-frame panel memo strings small.
                if (s) s.canvas.toBlob(blob => {
                    if (!blob) return;
                    sprites[key] = { url: URL.createObjectURL(blob), w: s.w, h: s.h, ax: s.ax, ay: s.ay };
                }, 'image/png');
            } catch (e) { spriteLoadBlocked = true; /* file:// canvas taint — letter portraits remain */ }
        };
        img.onerror = () => {}; // not generated yet — letter portraits remain
        img.src = 'assets/raw/' + SPRITE_SOURCES[key];
    }
}

// --- M15 T1 chrome: the generated frame texture becomes CSS border-image ---
// Same runtime idea as the sprites: load the raw magenta-margin frame from
// assets/raw/, key it transparent in memory, and hand the result to CSS as
// the --chrome-frame variable. Panels opt in via body.chrome-ready, so on
// file:// (canvas taint) or a missing file the flat CSS chrome remains.
function loadChrome() {
    const img = new Image();
    img.onload = () => {
        try {
            const c = document.createElement('canvas');
            c.width = img.width; c.height = img.height;
            const ctx = c.getContext('2d');
            ctx.drawImage(img, 0, 0);
            const data = ctx.getImageData(0, 0, c.width, c.height); // throws on file://
            keyMagentaPixels(data.data);
            ctx.putImageData(data, 0, 0);
            c.toBlob(blob => {
                if (!blob) return;
                document.documentElement.style.setProperty('--chrome-frame', `url(${URL.createObjectURL(blob)})`);
                document.body.classList.add('chrome-ready');
            }, 'image/png');
        } catch (e) { /* file:// canvas taint — flat chrome remains */ }
    };
    img.onerror = () => {}; // not generated yet — flat chrome remains
    img.src = 'assets/raw/raw_ui_frame.png';
}

// Portrait chip content: real sprite when its file exists, letter otherwise.
function portraitInner(spriteKey, letter) {
    const s = sprites[spriteKey];
    if (s) return `<span class="portrait-sprite" style="background-image:url(${s.url})"></span>`;
    return `<span class="portrait-letter">${letter}</span>`;
}

// Hero sprites: prefer the rarity variant when its file exists, else the base.
function heroSpriteKey(archetypeKey, rarity) {
    const variant = 'hero_' + archetypeKey + '_' + rarity;
    return sprites[variant] ? variant : 'hero_' + archetypeKey;
}

function unitSpriteKey(unit) {
    if (unit.side === 'hero') return unit.archetypeKey ? heroSpriteKey(unit.archetypeKey, unit.rarity) : null;
    return unit.spriteKey || null;
}

// Memoized innerHTML: only touch the DOM when the panel's content actually
// changed. Panels with embedded timers naturally refresh once per game-second.
function setPanelHtml(id, html) {
    const el = document.getElementById(id);
    if (el._memoHtml !== html) {
        el._memoHtml = html;
        el.innerHTML = html;
    }
}

function squadSignature(squad, columnOrder, cols) {
    let sig = cols + '|';
    for (const colDef of columnOrder) {
        sig += colDef.label + ':';
        for (let i = 0; i < cols; i++) {
            const unit = squad[colDef.row * cols + i];
            sig += (unit ? unitDomKey(unit) : 'e') + ',';
        }
        sig += '/';
    }
    return sig;
}

function buildSquad(el, squad, sideClass, columnOrder, interactive, cols) {
    if (el._slotKeys) for (const k of el._slotKeys) slotElByKey.delete(k);
    el._slotKeys = [];
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
                const statParts = [];
                if (unit.attack) statParts.push(`ATK ${unit.attack.power}`);
                if (unit.heal) statParts.push(`HLR ${unit.heal.power}`);
                statParts.push(`DEF ${unit.defense}%`);
                if (unit.guard) statParts.push(`GRD ×${unit.guard}`);
                slot.innerHTML = `
                    <div class="battle-unit-name">${unit.name}</div>
                    <div class="battle-unit-stats">${statParts.join(' &middot; ')}</div>
                    <div class="battle-hp-track"><div class="battle-hp-fill ${sideClass}"></div></div>
                    <div class="battle-hp-text"></div>
                `;
                slot._hpFill = slot.querySelector('.battle-hp-fill');
                slot._hpText = slot.querySelector('.battle-hp-text');
                const sKey = unitSpriteKey(unit);
                if (sKey && sprites[sKey]) {
                    slot.style.backgroundImage = `url(${sprites[sKey].url})`;
                    slot.classList.add('has-sprite');
                }
                const key = unitDomKey(unit);
                slotElByKey.set(key, slot);
                el._slotKeys.push(key);
                if (interactive) {
                    slot.classList.add('dismissable');
                    // Armed state is read at CLICK time (persistent handlers
                    // outlive the render pass that created them).
                    slot.addEventListener('click', () => {
                        const armed = armedHeroSlot === index && Date.now() - armedHeroSlotTime < ARM_TIMEOUT_MS;
                        if (armed) {
                            armedHeroSlot = null;
                            fireHero(index);
                        } else {
                            armedHeroSlot = index;
                            armedHeroSlotTime = Date.now();
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

function updateSquad(el, squad, columnOrder, interactive, cols) {
    let colEl = el.firstElementChild;
    for (const colDef of columnOrder) {
        let slot = colEl.firstElementChild.nextElementSibling; // skip the row label
        for (let i = 0; i < cols; i++) {
            const index = colDef.row * cols + i;
            const unit = squad[index];
            if (unit) {
                const pct = Math.max(0, (unit.hp / unit.maxHp) * 100);
                slot._hpFill.style.width = pct + '%';
                slot._hpText.textContent = `${Math.max(0, Math.round(unit.hp))} / ${unit.maxHp}`;
                slot.classList.toggle('dead', !unit.alive);
                slot.classList.toggle('fx-chilled', chilled(unit));
                // Sprites load async — adopt one the frame it becomes ready.
                if (!slot.classList.contains('has-sprite')) {
                    const sKey = unitSpriteKey(unit);
                    if (sKey && sprites[sKey]) {
                        slot.style.backgroundImage = `url(${sprites[sKey].url})`;
                        slot.classList.add('has-sprite');
                    }
                }
                if (interactive) {
                    const armed = armedHeroSlot === index && Date.now() - armedHeroSlotTime < ARM_TIMEOUT_MS;
                    slot.classList.toggle('armed', armed);
                    slot.title = armed ? 'Click again to dismiss' : 'Click to dismiss';
                }
            }
            slot = slot.nextElementSibling;
        }
        colEl = colEl.nextElementSibling;
    }
}

function renderSquad(containerId, squad, sideClass, columnOrder, interactive, cols = 3) {
    const el = document.getElementById(containerId);
    const sig = squadSignature(squad, columnOrder, cols);
    if (el._squadSig !== sig) {
        el._squadSig = sig;
        buildSquad(el, squad, sideClass, columnOrder, interactive, cols);
    }
    updateSquad(el, squad, columnOrder, interactive, cols);
}

function renderBattleSquads() {
    if (isDraggingHero) return;
    // Between battles, show the upcoming tier's grid as the empty frame.
    const enemyGrid = currentInvasion ? currentInvasion.grid : RAID_TIERS[raidTierIndex].grid;
    const enemies = currentInvasion ? currentInvasion.enemies : new Array(enemyGrid.rows * enemyGrid.cols).fill(null);
    // Hero columns render rear-to-front so the frontline sits nearest the
    // enemy area; enemy columns front-first. Every row behind the front is one
    // flat backline pool mechanically, so every rear row is labeled Backline.
    const dims = heroGridDims();
    const rowLabel = r => r === 0 ? 'Frontline' : 'Backline';
    const heroColumns = [];
    for (let r = dims.rows - 1; r >= 0; r--) heroColumns.push({ label: rowLabel(r), row: r });
    const enemyColumns = [];
    for (let r = 0; r < enemyGrid.rows; r++) enemyColumns.push({ label: rowLabel(r), row: r });
    renderSquad('heroSquad', heroSquad, '', heroColumns, true, dims.cols);
    renderSquad('enemySquad', enemies, 'enemy', enemyColumns, false, enemyGrid.cols);

    // Escalation reads visually: the enemy side takes on a deepening red
    // wash as the multiplier climbs (state-driven, straight from the sim).
    const esc = currentInvasion ? escalationMult(currentInvasion) : 1;
    document.getElementById('enemySquad').style.backgroundColor =
        esc > 1 ? `rgba(160, 30, 20, ${Math.min(0.35, (esc - 1) * 0.5)})` : '';
}

function renderHeroRecruitPool() {
    if (kingdomLevel < RAID_TRIGGER_LEVEL) {
        setPanelHtml('hero-recruit-pool',
            `<div class="pool-empty">Unlocks at ${levels[RAID_TRIGGER_LEVEL].name}</div>`);
        return;
    }

    let html = `<div class="pool-header">
        <span class="pool-timer" id="hero-pool-timer-text"></span>
    </div>`;

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
            if (base.guard) statParts.push(`GRD ×${base.guard}`);

            const letter = recruit.name[0].toUpperCase();

            let hint = '';
            if (!hasSlot) hint = 'Squad full';

            html += `<div class="recruit-card recruit-card--${recruit.rarity}">
                <div class="portrait portrait--${recruit.rarity}" data-type="${recruit.archetypeKey}">
                    ${portraitInner(heroSpriteKey(recruit.archetypeKey, recruit.rarity), letter)}
                </div>
                <div class="recruit-info">
                    <div class="recruit-name">${recruit.name}</div>
                    <div class="recruit-rarity" style="color:${tier.color}">${tier.name}</div>
                    <div class="recruit-stat">${statParts.join(' &middot; ')}</div>
                    ${hint ? `<div class="recruit-hint">${hint}</div>` : ''}
                </div>
                <div class="recruit-action">
                    <div class="recruit-cost">${recruit.cost.toLocaleString()}g</div>
                    <button class="btn-hire-recruit" data-hero-id="${recruit.id}" data-action="hireHero:${recruit.id}">Hire</button>
                </div>
            </div>`;
        });
    }

    setPanelHtml('hero-recruit-pool', html);
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
                       <button class="btn-upgrade" data-action="buyUpgrade:${node.id}" ${canAfford ? '' : 'disabled'}>Buy</button>`}
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
        <button class="btn-new-age" data-action="foundNewAge">Found a New Age &mdash; Age ${meta.age + 1}</button>`;

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
        <div class="summary-sub">The Final Siege is broken. The Demon Empress will not return.</div>
        <div class="summary-stats">
            <div class="summary-stat"><span class="summary-stat-value">${meta.age}</span> Age${meta.age === 1 ? '' : 's'} founded</div>
            <div class="summary-stat"><span class="summary-stat-value">${lifetimeLegacy.toLocaleString()}</span> Legacy earned across the campaign</div>
            <div class="summary-stat"><span class="summary-stat-value">${hours}h ${mins}m</span> of kingdom time</div>
        </div>
        ${fallLines ? `<div class="victory-history"><div class="summary-shop-heading">The Ages that came before:</div>${fallLines}</div>` : ''}
        <button class="btn-new-age" data-action="continueEndless">Rule in Peace &mdash; Endless Mode</button>`;

    document.getElementById('run-summary-content').innerHTML = html;
    overlay.classList.remove('hidden');
}

// Gold accrues every tick, but the Town Square and building panels only
// rebuild on events (pool refresh, purchases, expand/collapse) — so their
// baked-in disabled states go stale as gold comes in. Refresh them in place
// each tick instead of rebuilding the DOM (see the M15 perf-debt note).
// Per-frame in-place refresh of every VOLATILE piece of the UI: affordability
// (disabled states, live cost labels) and ticking countdown texts. These are
// deliberately NOT part of the memoized panel strings — baking a per-second
// value into a panel forces a full innerHTML rebuild every game-second, which
// destroys buttons mid-click (the click-eating bug, fixed 2026-07-17) and
// kills hover states / CSS animations. Runs after the panel renders in
// renderAll, so even a frame that rebuilt a panel ends with correct state.
function refreshVolatileUI() {
    document.querySelectorAll('#recruit-pool .btn-hire-recruit[data-recruit-id]').forEach(btn => {
        const recruit = recruitPool.find(r => r.id === Number(btn.dataset.recruitId));
        if (recruit) btn.disabled = !canHireRecruit(recruit);
    });
    document.querySelectorAll('#building-list .btn-building[data-building-id]').forEach(btn => {
        const info = buildingPurchaseInfo(btn.dataset.buildingId);
        btn.disabled = !info.canAfford;
        const costEl = btn.querySelector('.building-cost');
        if (costEl) costEl.textContent = `Cost: ${info.costLabel}`;
    });
    const heroHasSlot = heroSquad.some(h => h === null);
    document.querySelectorAll('#hero-recruit-pool .btn-hire-recruit[data-hero-id]').forEach(btn => {
        const recruit = heroRecruitPool.find(r => r.id === Number(btn.dataset.heroId));
        if (recruit) btn.disabled = !(gold >= recruit.cost && heroHasSlot);
    });

    const setText = (id, text) => {
        const el = document.getElementById(id);
        if (el && el.textContent !== text) el.textContent = text;
    };
    setText('pool-timer-text', `New arrivals in ${Math.max(0, POOL_REFRESH_INTERVAL - poolTimer)}s`);
    setText('hero-pool-timer-text', `New heroes in ${Math.max(0, HERO_POOL_REFRESH_INTERVAL - heroPoolTimer)}s`);
    setText('raid-timer-text', formatTimer(invasionTimer));
    if (currentInvasion) {
        setText('raid-esc-line', `The siege escalates! Enemy attack +${Math.round((escalationMult(currentInvasion) - 1) * 100)}%`);
    }
}

// --- M15 Phase 0: the render loop ---
// tick() is pure simulation; THIS is the only place the DOM gets painted.
// ==================================================================
// M15 SCENE VIEW (T2/T3 overhaul, incremental) — a real-state port of
// tools/scene-prototype.html. Increment 1: continuous backdrop + town
// vista (buildings on fixed plots, driven by real `buildings` state) +
// HUD chips. Hidden until #scene-toggle flips it on; the classic
// #layout stays the working default so the game is always playable.
// Later increments: hiring crowd as world units, the battle diorama,
// then retiring the panels. All new render goes through setPanelHtml
// (memoized) and the volatile/structure split, per Phase 0.
// ==================================================================
let sceneOpen = false;

function toggleSceneView() {
    sceneOpen = !sceneOpen;
    const scene = document.getElementById('scene');
    scene.classList.toggle('hidden', !sceneOpen);
    scene.setAttribute('aria-hidden', String(!sceneOpen));
    document.body.classList.toggle('scene-open', sceneOpen);
    document.getElementById('scene-toggle').textContent = sceneOpen ? '⛶ Classic view' : '⛶ Scene view';
    meta.sceneView = sceneOpen; // persisted choice (additive meta field)
    saveMeta();
    if (sceneOpen) { layoutScene(); updateUI(); }
}

// Backdrop: the accepted continuous widescreen scene, cover-fit with the
// painted wall (~x1318/2752) seated on the 46% seam. It's an opaque
// painting, so no canvas keying is needed — this also works on file://.
let sceneBgImg = null;
const SCENE_WALL_FRAC = 1318 / 2752;   // wall center in the source image
const TOWN_REGION_FRAC = 0.46;         // town half of the stage width
function loadScene() {
    const img = new Image();
    img.onload = () => { sceneBgImg = img; if (sceneOpen) layoutScene(); };
    img.onerror = () => {}; // absent — flat ground remains
    img.src = 'assets/raw/scenebothhalves.png';
}
function layoutScene() {
    const bg = document.getElementById('scene-bg');
    if (!sceneBgImg || !bg) return;
    const sw = window.innerWidth, sh = window.innerHeight;
    const W = sceneBgImg.width, H = sceneBgImg.height;
    const s = Math.max(sh / H, sw / W);              // cover-fit
    let ox = sw * 0.46 - SCENE_WALL_FRAC * W * s;    // seat wall on 46%
    ox = Math.min(0, Math.max(sw - W * s, ox));      // clamp: no edge gaps
    bg.style.backgroundImage = `url(${sceneBgImg.src})`;
    bg.style.backgroundSize = `${W * s}px ${H * s}px`;
    bg.style.backgroundPosition = `${ox}px ${(sh - H * s) / 2}px`;
}
window.addEventListener('resize', () => { if (sceneOpen) layoutScene(); });

// Fixed building plots (x,y in % of the town region = left 46% of the
// stage). Fixed positions — never free placement — is what keeps the
// vista affordable (spec T3). Laid out for scenebothhalves.png: the
// painted plaza + road form a belt across the town's midline (~y 50-78),
// so buildings live on the upper grass band (back rows, smaller with
// depth) and the bottom-left pocket (cottage — the first building the
// player ever buys gets the near-camera spot). Nothing stands on the
// plaza, the road, or the crowd zone (y 84+).
const BUILDING_PLOTS = {
    // back row, along the north wall (smaller with depth)
    keep:      { x: 8,  y: 26 }, library: { x: 22, y: 24 }, tower:    { x: 36, y: 22 },
    cathedral: { x: 52, y: 24 }, apothecary: { x: 68, y: 27 },
    // mid row, upper grass above the plaza — cottage leftmost (the first
    // building every run buys reads first); all bases clear of the belt
    cottage:   { x: 12, y: 41 }, tavern:  { x: 32, y: 39 }, smithy:   { x: 52, y: 41 },
    workshop:  { x: 66, y: 43 }
};

// Schematic SVG placeholders shown until raw_bldg_<id>.png lands (then
// renderVista swaps in the real sprite). Ported from the prototype.
const SBC = { wall: '#8a7a5c', wallD: '#6b5d44', roof: '#7a3f2e', roofD: '#5c2f22',
              wood: '#4a3826', glow: '#e8a850', stone: '#7d7a6e', dark: '#2a2118', gold: '#b8942f' };
function svgOpen(w, h) {
    return `<svg width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" shape-rendering="crispEdges" xmlns="http://www.w3.org/2000/svg">`;
}
const BUILDING_ART = {
    cottage: () => svgOpen(64, 54) +
        `<rect x="8" y="26" width="48" height="28" fill="${SBC.wall}"/><rect x="8" y="26" width="48" height="4" fill="${SBC.wallD}"/>
         <polygon points="4,28 32,6 60,28" fill="${SBC.roof}"/><polygon points="4,28 32,6 32,12 10,28" fill="${SBC.roofD}"/>
         <rect x="26" y="36" width="12" height="18" fill="${SBC.wood}"/><rect x="44" y="34" width="8" height="8" fill="${SBC.glow}"/></svg>`,
    tavern: () => svgOpen(84, 62) +
        `<rect x="6" y="30" width="72" height="32" fill="${SBC.wall}"/><rect x="6" y="30" width="72" height="4" fill="${SBC.wallD}"/>
         <polygon points="2,32 42,8 82,32" fill="${SBC.roof}"/><polygon points="2,32 42,8 42,14 8,32" fill="${SBC.roofD}"/>
         <rect x="16" y="40" width="14" height="22" fill="${SBC.wood}"/><rect x="40" y="40" width="10" height="10" fill="${SBC.glow}"/>
         <rect x="58" y="40" width="10" height="10" fill="${SBC.glow}"/><rect x="66" y="20" width="12" height="10" fill="${SBC.wood}"/></svg>`,
    smithy: () => svgOpen(72, 60) +
        `<rect x="6" y="30" width="60" height="30" fill="${SBC.stone}"/><rect x="6" y="30" width="60" height="4" fill="#66635a"/>
         <polygon points="2,32 36,10 70,32" fill="${SBC.roofD}"/><rect x="52" y="6" width="10" height="20" fill="${SBC.stone}"/>
         <rect x="16" y="40" width="16" height="20" fill="${SBC.dark}"/><rect x="18" y="44" width="12" height="12" fill="${SBC.glow}"/></svg>`,
    workshop: () => svgOpen(68, 52) +
        `<rect x="6" y="22" width="56" height="30" fill="${SBC.wood}"/><polygon points="2,24 34,6 66,24" fill="${SBC.wallD}"/>
         <rect x="14" y="30" width="14" height="22" fill="${SBC.dark}"/><rect x="38" y="30" width="18" height="12" fill="${SBC.wall}"/></svg>`,
    library: () => svgOpen(60, 70) +
        `<rect x="8" y="18" width="44" height="52" fill="${SBC.wall}"/><rect x="8" y="18" width="44" height="4" fill="${SBC.wallD}"/>
         <polygon points="4,20 30,4 56,20" fill="${SBC.roof}"/><rect x="22" y="28" width="16" height="18" fill="${SBC.glow}"/>
         <rect x="24" y="52" width="12" height="18" fill="${SBC.wood}"/></svg>`,
    keep: () => svgOpen(64, 76) +
        `<rect x="12" y="20" width="40" height="56" fill="${SBC.stone}"/><rect x="12" y="20" width="40" height="5" fill="#66635a"/>
         <rect x="8" y="10" width="10" height="14" fill="${SBC.stone}"/><rect x="27" y="10" width="10" height="14" fill="${SBC.stone}"/>
         <rect x="46" y="10" width="10" height="14" fill="${SBC.stone}"/><rect x="24" y="52" width="16" height="24" fill="${SBC.dark}"/></svg>`,
    apothecary: () => svgOpen(64, 58) +
        `<rect x="8" y="26" width="48" height="32" fill="${SBC.wall}"/><polygon points="4,28 32,8 60,28" fill="#4f6b3a"/>
         <rect x="24" y="38" width="12" height="20" fill="${SBC.wood}"/><circle cx="48" cy="22" r="7" fill="#6fae52"/></svg>`,
    tower: () => svgOpen(52, 82) +
        `<rect x="14" y="26" width="24" height="56" fill="${SBC.stone}"/><polygon points="8,28 26,4 44,28" fill="#5a4a8a"/>
         <rect x="20" y="38" width="12" height="14" fill="${SBC.glow}"/><rect x="22" y="64" width="10" height="18" fill="${SBC.dark}"/></svg>`,
    cathedral: () => svgOpen(76, 84) +
        `<rect x="10" y="30" width="56" height="54" fill="${SBC.wall}"/><polygon points="6,32 38,6 70,32" fill="${SBC.roof}"/>
         <rect x="34" y="2" width="8" height="12" fill="${SBC.gold}"/><circle cx="38" cy="40" r="9" fill="${SBC.glow}"/>
         <rect x="30" y="58" width="16" height="26" fill="${SBC.wood}"/></svg>`
};
function buildingArtHtml(id) {
    const s = sprites['bldg_' + id];
    if (s) {
        const h = 104, w = Math.round(h * (s.w / s.h));
        return `<div class="bldg-sprite" style="width:${w}px;height:${h}px;background-image:url(${s.url})"></div>`;
    }
    return (BUILDING_ART[id] || BUILDING_ART.cottage)();
}

function renderVista() {
    let html = '';
    for (const id in BUILDING_PLOTS) {
        const b = buildings[id];
        if (!b) continue;
        const p = BUILDING_PLOTS[id];
        const leftPct = (p.x / 100) * TOWN_REGION_FRAC * 100; // % of stage width
        // nearer = larger; the upper band holds four buildings side by side,
        // so the back rows scale down harder than the old prototype curve
        const depth = 0.85 + (p.y / 100) * 1.75;
        const z = Math.round(p.y * 4);
        const pos = `left:${leftPct.toFixed(2)}%;top:${p.y}%;z-index:${z}`;

        if (getBuildingCap(id) <= 0) {
            const lvl = levels.find(l => l.caps[id] > 0);
            html += `<div class="plot locked" style="${pos}">
                <div class="ghost"><span class="nm">${b.name}</span><br>Unlocks at ${lvl ? lvl.name : '???'}</div></div>`;
            continue;
        }
        const art = `<div class="art" style="transform:scale(${depth.toFixed(2)})">${buildingArtHtml(id)}`;
        if (b.count === 0) {
            // Ghost-preview: desaturated, NOT washed out — a fresh save shows
            // several of these at once and stacked transparency read as a bug.
            html += `<div class="plot plot--unbuilt" data-action="openScenePlot:${id}" data-bldg="${id}" style="${pos}">${art}</div>
                <span class="tag">${b.name} · click to build</span></div>`;
            continue;
        }
        html += `<div class="plot" data-action="openScenePlot:${id}" data-bldg="${id}" style="${pos}">
            ${art}<span class="count">×${b.count}</span></div>
            <span class="tag">${b.name} ×${b.count} · click to manage</span></div>`;
    }
    setPanelHtml('scene-vista', html);
}

function renderSceneHud() {
    const current = levels[kingdomLevel];
    const next = levels[kingdomLevel + 1];
    // Structure only — no per-frame values in the memoized string (gold/gps/
    // legacy/HP and every countdown live in fixed spans updated by renderScene
    // each frame), so buttons are never rebuilt mid-click. canAfford flips rarely.
    let levelBtn;
    if (next) {
        const unlockNames = next.unlocks.map(id => buildings[id].name).join(', ');
        levelBtn = `${unlockNames ? `<div style="font-size:10px;color:#8a7f63">Unlocks: ${unlockNames}</div>` : ''}
            <button data-action="levelUpKingdom" ${gold >= next.cost ? '' : 'disabled'}>Become a ${next.name} — ${next.cost.toLocaleString()}g</button>`;
    } else {
        levelBtn = `<div style="color:#8a7f63;font-size:11px;margin-top:5px">Highest tier reached</div>`;
    }
    // Manual run-ender (same confirm flow as the classic left panel)
    if (raidsStarted && !runEnded) {
        levelBtn += confirmingNewAge
            ? `<div style="margin-top:6px;font-size:11px;color:#c06060">End this Age?
                <button data-action="confirmNewAge" style="color:#e08080;border-color:#8a4040">Yes, end it</button>
                <button data-action="cancelNewAge">Cancel</button></div>`
            : `<button data-action="showNewAgeConfirm" style="margin-top:6px;opacity:0.8">Found a New Age</button>`;
    }

    // Town Square chip: arrival countdowns + auto-hire (structure changes only
    // on unlock or auto-hire mode click — the ticking texts are volatile spans).
    const autoOptions = [
        { value: null, label: 'Off' }, { value: 'common', label: 'Common+' },
        { value: 'rare', label: 'Rare+' }, { value: 'epic', label: 'Epic+' },
        { value: 'legendary', label: 'Legendary' }
    ];
    const autoHtml = autoRecruitAvailable()
        ? `<div style="margin-top:3px">${autoOptions.map(o =>
            `<button class="${autoRecruitRarity === o.value ? 'on' : ''}" data-action="setAutoRecruit:${o.value === null ? 'null' : o.value}">${o.label}</button>`).join('')}</div>`
        : '';
    const heroLine = kingdomLevel >= RAID_TRIGGER_LEVEL
        ? `<div class="row"><span class="lbl">Heroes</span> <span id="scene-hero-timer" style="font-size:11px"></span></div>`
        : `<div class="row"><span class="lbl">Heroes</span> <span style="font-size:10px;color:#8a7f63">unlock at ${levels[RAID_TRIGGER_LEVEL].name}</span></div>`;
    const squareChip = `<div class="chip" id="scene-square-chip" style="left:14px;top:212px;min-width:150px;font-size:11px">
        <div class="row"><span class="lbl">Town Square</span> <span id="scene-pool-timer" style="font-size:11px"></span></div>
        ${autoHtml}${heroLine}</div>`;

    // System corner: game speed, motion, reset — classic's admin controls,
    // reusing the same actions and lock rules (Swift Seasons / DEV_MODE).
    const unlockedSpeed = speedSelectorAvailable();
    let speedBtns = PLAYER_SPEEDS.map(s => {
        const locked = s > 1 && !unlockedSpeed;
        return locked
            ? `<button disabled title="Unlocks with Swift Seasons (Economy tree)">${s}×</button>`
            : `<button class="${s === gameSpeed ? 'on' : ''}" data-action="setGameSpeed:${s}">${s}×</button>`;
    }).join('');
    if (DEV_MODE) speedBtns += DEV_SPEEDS.map(s =>
        `<button class="${s === gameSpeed ? 'on' : ''}" data-action="setGameSpeed:${s}" style="color:#7a6428">${s}×</button>`).join('');
    const motionBtns = SYSTEM_REDUCED_MOTION
        ? `<button disabled class="on" title="Your system requests reduced motion">Reduced</button>`
        : `<button class="${meta.reduceMotion ? '' : 'on'}" data-action="setReduceMotion:0">Full</button>
           <button class="${meta.reduceMotion ? 'on' : ''}" data-action="setReduceMotion:1" title="No shake, flashes, or floating numbers">Reduced</button>`;
    const resetBtns = confirmingReset
        ? `<span style="color:#c06060">Reset all progress?</span>
           <button data-action="doResetGame" style="color:#e08080">Yes</button>
           <button data-action="cancelReset">No</button>`
        : `<button data-action="showResetConfirm" title="Dev wipe: run AND meta">Reset</button>`;
    const cornerChip = `<div class="chip" id="scene-corner-chip">
        <span class="lbl">Speed</span> ${speedBtns}
        <span class="lbl" style="margin-left:8px">Motion</span> ${motionBtns}
        <span style="margin-left:8px">${resetBtns}</span></div>`;

    // Raid chip over the battlefield — mirrors renderRaidStatusBar's states.
    let raidChip = '';
    if (currentInvasion) {
        raidChip = `<div class="chip" id="scene-raid-chip">
            <div class="rname">${currentInvasion.name}</div>
            <div style="font-size:11px;color:#8a7f63">${currentInvasion.finalSiege ? `Phase ${currentInvasion.phase} of ${FINAL_SIEGE_PHASES.length}` : 'Battle in progress'}</div>
            ${escalationMult(currentInvasion) > 1 ? `<div class="resc" id="scene-esc-line"></div>` : ''}
            ${!squadAlive(heroSquad) ? `<div class="rsiege">The Kingdom is under siege!</div>` : ''}
            ${lastVictory ? `<div class="rvict">Repelled: ${lastVictory.name} +${lastVictory.loot.toLocaleString()}g${lastVictory.legacy ? ` · +${lastVictory.legacy.toLocaleString()} Legacy` : ''}</div>` : ''}
        </div>`;
    } else if (raidsStarted) {
        const nextName = finalSiegeCountdown === 0 ? 'THE FINAL SIEGE' : getInvasionName(raidTierIndex, tierWave);
        raidChip = `<div class="chip" id="scene-raid-chip">
            <div class="rname">Next: ${nextName}</div>
            <div style="font-size:11px;color:#8a7f63">Arrives in <span id="scene-raid-timer"></span></div>
            ${finalSiegeCountdown > 0 ? `<div class="rsiege">A herald arrives: the Final Siege approaches — ${finalSiegeCountdown} raid${finalSiegeCountdown === 1 ? '' : 's'} remain${finalSiegeCountdown === 1 ? 's' : ''}!</div>` : ''}
            ${lastVictory ? `<div class="rvict">Repelled: ${lastVictory.name} +${lastVictory.loot.toLocaleString()}g${lastVictory.legacy ? ` · +${lastVictory.legacy.toLocaleString()} Legacy` : ''}</div>` : ''}
        </div>`;
    }

    setPanelHtml('scene-hud',
        `<div class="chip" id="hud-econ">
            <div class="row"><span class="lbl">Gold</span> <b id="scene-gold">0</b></div>
            <div class="row"><span class="lbl">Per sec</span> <b id="scene-gps">0</b></div>
            <div class="row"><span class="lbl">Legacy</span> <b id="scene-legacy" style="color:#b48ae8">0</b></div>
        </div>
        <div class="chip" id="hud-level">
            <span class="lbl">Kingdom · Age ${meta.age}</span><br>
            <span class="kname">${current.name}</span>
            ${levelBtn}
        </div>
        ${squareChip}
        ${cornerChip}
        <div class="chip" id="hud-wall">
            <span class="lbl">Kingdom</span> <b id="scene-hp-text">—</b>
            <div class="bar"><div class="fill" id="scene-hp-fill"></div></div>
        </div>
        ${raidChip}`);
}

// ---------- world units: a character standing at a feet point ----------
// Wrapper div anchored at the feet (left/top %); sprite/letter, shadow, and
// rarity ring are px-offset children computed from the sprite's foot anchor.
// No transform on the wrapper, so the shared fx-lunge classes animate safely.
function sceneUnitBits(sKey, h, letter, rarity) {
    const s = sprites[sKey];
    let inner, sw;
    if (s) {
        const scale = h / s.h;
        sw = s.w * scale;
        inner = `<img class="sprite" src="${s.url}" style="height:${h.toFixed(0)}px;left:${(-s.ax * scale).toFixed(1)}px;top:${(-s.ay * scale).toFixed(1)}px">`;
    } else {
        sw = 40;
        inner = `<span class="letter-chip" style="left:-17px;top:-42px">${letter}</span>`;
    }
    const shW = Math.max(26, sw * 0.62);
    let html = `<span class="shadow" style="left:${(-shW / 2).toFixed(1)}px;top:-7px;width:${shW.toFixed(0)}px;height:14px"></span>`;
    if (rarity) {
        const rw = Math.max(34, sw * 0.72);
        html += `<span class="ring ring--${rarity}" style="left:${(-rw / 2).toFixed(1)}px;top:-9px;width:${rw.toFixed(0)}px;height:18px"></span>`;
    }
    return { html: html + inner, sw };
}

// ---------- increment 2: the hiring crowd ----------
// Recruits stand in the town square as world units. Memoized via setPanelHtml:
// the string carries pool identity + sprite readiness (blob URLs appear in it),
// so it rebuilds exactly on pool change / hire / sprite load. Affordability is
// a volatile class toggled per frame — never part of the string.
// Spread wide with alternating depth so five nameplates never stack.
const TOWN_CROWD_SPOTS = [[0.05, 0.86], [0.15, 0.905], [0.25, 0.868], [0.35, 0.915], [0.45, 0.878]];
const HERO_CROWD_SPOTS = [[0.56, 0.87], [0.67, 0.905], [0.78, 0.868], [0.88, 0.92], [0.62, 0.95]];

function renderSceneCrowd() {
    let html = '';
    recruitPool.forEach((recruit, i) => {
        const spot = TOWN_CROWD_SPOTS[i % TOWN_CROWD_SPOTS.length];
        const x = spot[0] * TOWN_REGION_FRAC * 100, y = spot[1] * 100;
        const h = 74 + (spot[1] - 0.84) * 170;
        const type = recruitTypes[recruit.typeId];
        const tier = rarityTiers[recruit.rarity];
        const b = buildings[recruit.buildingId];
        const isHp = b.type === 'hpregen';
        const valueLabel = isHp
            ? `${Math.max(0.1, Math.round(type.incomeMin * tier.incomeMult * 10) / 10)}-${Math.max(0.1, Math.round(type.incomeMax * tier.incomeMult * 10) / 10)} hp/s`
            : `${Math.max(1, Math.floor(type.incomeMin * tier.incomeMult))}-${Math.floor(type.incomeMax * tier.incomeMult)} g/s`;
        let hint = `Hire — ${recruit.cost.toLocaleString()}g`;
        if (getBuildingCap(recruit.buildingId) <= 0) hint = `Needs ${b.name}`;
        else if (b.residents.length >= b.count * b.slotsPerBuilding) hint = 'No open slots';
        const bits = sceneUnitBits('town_' + recruit.typeId, h, recruit.name[0].toUpperCase(), recruit.rarity);
        html += `<div class="sunit sunit--recruit" data-action="hireRecruit:${recruit.id}" data-recruit-id="${recruit.id}"
            style="left:${x.toFixed(2)}%;top:${y.toFixed(2)}%;z-index:${Math.round(y * 4)}">
            ${bits.html}
            <div class="plate" style="left:-75px;top:6px">${recruit.name}
                <div class="sub" style="color:${tier.color}">${tier.name} · ${valueLabel}</div>
                <div class="cost">${recruit.cost.toLocaleString()}g</div></div>
            <div class="hint" style="left:-75px;top:${(-h - 26).toFixed(0)}px"><span>${hint}</span></div>
        </div>`;
    });
    if (kingdomLevel >= RAID_TRIGGER_LEVEL) {
        const hasSlot = heroSquad.some(s => s === null);
        heroRecruitPool.forEach((recruit, i) => {
            const spot = HERO_CROWD_SPOTS[i % HERO_CROWD_SPOTS.length];
            const x = spot[0] * TOWN_REGION_FRAC * 100, y = spot[1] * 100;
            const h = 82 + (spot[1] - 0.84) * 170;
            const tier = rarityTiers[recruit.rarity];
            const hint = hasSlot ? `Hire — ${recruit.cost.toLocaleString()}g` : 'Squad full';
            const bits = sceneUnitBits(heroSpriteKey(recruit.archetypeKey, recruit.rarity), h, recruit.name[0].toUpperCase(), recruit.rarity);
            html += `<div class="sunit sunit--recruit" data-action="hireHero:${recruit.id}" data-hero-id="${recruit.id}"
                style="left:${x.toFixed(2)}%;top:${y.toFixed(2)}%;z-index:${Math.round(y * 4)}">
                ${bits.html}
                <div class="plate" style="left:-75px;top:6px">${recruit.name}
                    <div class="sub" style="color:${tier.color}">${tier.name}</div>
                    <div class="cost">${recruit.cost.toLocaleString()}g</div></div>
                <div class="hint" style="left:-75px;top:${(-h - 26).toFixed(0)}px"><span>${hint}</span></div>
            </div>`;
        });
    }
    setPanelHtml('scene-crowd', html);
}

// ---------- increment 3: the battle diorama ----------
// Game grid → field geometry: a unit's game ROW picks its screen column
// (hero front row nearest the enemies, and vice versa), its game COL picks
// the depth lane (top lane = col 0, farther = higher + smaller). All in
// stage-% so the layout survives resizes.
function sceneHeroRowX(r)  { return 62 - r * 5; }     // r0 front … r3 rear (toward wall)
function sceneEnemyRowX(r) { return 74 + r * 5.5; }   // r0 front … r3 rear (toward treeline)
function sceneLaneY(c, n)  { return (n >= 4 ? [63, 73, 83, 92] : [67, 78, 90])[c]; }
function sceneLaneH(c)     { return 90 + c * 13; }

const sceneUnitElByKey = new Map(); // unit._domKey -> scene wrapper (FX routing)
const sceneBattleLive = [];         // per-unit bindings for the per-frame update

function sceneBattleSig(dims, enemyGrid, enemies) {
    let sig = dims.rows + 'x' + dims.cols + '|' + enemyGrid.rows + 'x' + enemyGrid.cols
        + '|' + (kingdomLevel >= RAID_TRIGGER_LEVEL ? 1 : 0) + '|';
    for (const u of heroSquad) sig += u ? unitDomKey(u) + (sprites[unitSpriteKey(u)] ? 's' : 'l') + ',' : 'e,';
    sig += '/';
    for (const u of enemies) sig += u ? unitDomKey(u) + (sprites[unitSpriteKey(u)] ? 's' : 'l') + ',' : 'e,';
    return sig;
}

function unitStatStr(unit) {
    const parts = [];
    if (unit.attack) parts.push(`ATK ${unit.attack.power}`);
    if (unit.heal) parts.push(`HLR ${unit.heal.power}`);
    parts.push(`DEF ${unit.defense}%`);
    if (unit.guard) parts.push(`GRD ×${unit.guard}`);
    return parts.join(' · ');
}

function sceneBattleUnitHtml(unit, index, xPct, yPct, h, isHero) {
    const key = unitDomKey(unit);
    const boss = !isHero && unit.spriteKey && unit.spriteKey.startsWith('boss_');
    if (boss) h = Math.min(155, h * 1.28);
    const bits = sceneUnitBits(unitSpriteKey(unit), h, unit.name[0].toUpperCase(), isHero ? unit.rarity : null);
    const cls = 'sunit' + (isHero ? ' sunit--hero' : ' sunit--enemy') + (boss ? ' sunit--boss' : '');
    const action = isHero ? ` data-action="sceneHeroClick:${index}" data-hidx="${index}"` : '';
    // Enemies get their stat tooltip at build time; heroes get theirs in the
    // per-frame update (folded into the armed/unarmed dismiss hint).
    const title = isHero ? '' : ` title="${unit.name} — ${unitStatStr(unit)}"`;
    return `<div class="${cls}" data-ukey="${key}"${action}${title}
        style="left:${xPct.toFixed(2)}%;top:${yPct.toFixed(2)}%;z-index:${Math.round(yPct * 4) + 1}">
        ${bits.html}
        <div class="plate" style="left:-75px;top:${(-h - 30).toFixed(0)}px">${unit.name}
            <div class="hp hp--${isHero ? 'hero' : 'enemy'}"><i></i></div></div>
        <span class="chillbadge" style="left:24px;top:${(-h - 8).toFixed(0)}px">❄</span>
    </div>`;
}

// Formation editing on the diorama: the same HTML5 drag pattern (and the same
// swapHeroes state change) as the classic battle slots. Empty positions are
// droppable via their ground tiles.
function attachSceneDragHandlers(el, index) {
    const unit = heroSquad[index];
    if (unit && unit.alive) {
        el.draggable = true;
        el.addEventListener('dragstart', e => {
            isDraggingHero = true;
            if (armedHeroSlot === index) armedHeroSlot = null;
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', String(index));
        });
        el.addEventListener('dragend', () => {
            isDraggingHero = false;
            updateUI();
        });
    }
    el.addEventListener('dragover', e => {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });
    el.addEventListener('dragenter', e => { e.preventDefault(); el.classList.add('drag-over'); });
    el.addEventListener('dragleave', () => el.classList.remove('drag-over'));
    el.addEventListener('drop', e => {
        e.preventDefault();
        el.classList.remove('drag-over');
        swapHeroes(parseInt(e.dataTransfer.getData('text/plain'), 10), index);
    });
}

function buildSceneBattle(el, dims, enemyGrid, enemies) {
    for (const k of sceneUnitElByKey.keys()) sceneUnitElByKey.delete(k);
    sceneBattleLive.length = 0;
    let html = '';
    const showHeroes = kingdomLevel >= RAID_TRIGGER_LEVEL;
    // ground tiles for every grid position (capacity reads even when empty)
    if (showHeroes) for (let r = 0; r < dims.rows; r++) for (let c = 0; c < dims.cols; c++) {
        const w = 66 + c * 8;
        const tidx = r * dims.cols + c;
        html += `<span class="btile btile--hero btile--drop" data-tidx="${tidx}" style="left:${sceneHeroRowX(r)}%;top:${sceneLaneY(c, dims.cols)}%;width:${w}px;height:${Math.round(w * 0.3)}px;margin-left:${-w / 2}px;margin-top:${-Math.round(w * 0.15)}px;z-index:${sceneLaneY(c, dims.cols) * 4 - 2}"></span>`;
    }
    for (let r = 0; r < enemyGrid.rows; r++) for (let c = 0; c < enemyGrid.cols; c++) {
        const w = 66 + c * 8;
        html += `<span class="btile btile--enemy" style="left:${sceneEnemyRowX(r)}%;top:${sceneLaneY(c, enemyGrid.cols)}%;width:${w}px;height:${Math.round(w * 0.3)}px;margin-left:${-w / 2}px;margin-top:${-Math.round(w * 0.15)}px;z-index:${sceneLaneY(c, enemyGrid.cols) * 4 - 2}"></span>`;
    }
    if (showHeroes) heroSquad.forEach((unit, index) => {
        if (!unit) return;
        const r = Math.floor(index / dims.cols), c = index % dims.cols;
        html += sceneBattleUnitHtml(unit, index, sceneHeroRowX(r), sceneLaneY(c, dims.cols), sceneLaneH(c), true);
    });
    enemies.forEach((unit, index) => {
        if (!unit) return;
        const r = Math.floor(index / enemyGrid.cols), c = index % enemyGrid.cols;
        html += sceneBattleUnitHtml(unit, index, sceneEnemyRowX(r), sceneLaneY(c, enemyGrid.cols), sceneLaneH(c), false);
    });
    el.innerHTML = html;
    // wire refs for FX routing + per-frame updates (unit objects mutate in place)
    const byKey = {};
    if (showHeroes) heroSquad.forEach((u, i) => { if (u) byKey[unitDomKey(u)] = { unit: u, hidx: i }; });
    enemies.forEach(u => { if (u) byKey[unitDomKey(u)] = { unit: u, hidx: -1 }; });
    el.querySelectorAll('.sunit[data-ukey]').forEach(uel => {
        const key = Number(uel.dataset.ukey);
        sceneUnitElByKey.set(key, uel);
        const bind = byKey[key];
        if (bind) {
            sceneBattleLive.push({
                el: uel, unit: bind.unit, hidx: bind.hidx,
                hpFill: uel.querySelector('.hp i'),
                statStr: unitStatStr(bind.unit)
            });
            if (bind.hidx >= 0) attachSceneDragHandlers(uel, bind.hidx);
        }
    });
    // Empty hero positions accept drops via their ground tiles
    el.querySelectorAll('.btile--drop').forEach(t => {
        const tidx = Number(t.dataset.tidx);
        if (!heroSquad[tidx]) attachSceneDragHandlers(t, tidx);
    });
}

function renderSceneBattle() {
    if (isDraggingHero) return; // a rebuild would destroy the dragged element
    const el = document.getElementById('scene-battle');
    const dims = heroGridDims();
    const enemyGrid = currentInvasion ? currentInvasion.grid : RAID_TIERS[raidTierIndex].grid;
    const enemies = currentInvasion ? currentInvasion.enemies : [];
    const sig = sceneBattleSig(dims, enemyGrid, enemies);
    if (el._sceneSig !== sig) {
        el._sceneSig = sig;
        buildSceneBattle(el, dims, enemyGrid, enemies);
    }
    // per-frame in-place updates
    for (const b of sceneBattleLive) {
        const u = b.unit;
        if (b.hpFill) b.hpFill.style.width = Math.max(0, (u.hp / u.maxHp) * 100) + '%';
        b.el.classList.toggle('sunit--dead', !u.alive);
        b.el.classList.toggle('sunit--chilled', chilled(u));
        if (b.hidx >= 0) {
            const armed = armedHeroSlot === b.hidx && Date.now() - armedHeroSlotTime < ARM_TIMEOUT_MS;
            b.el.classList.toggle('sunit--armed', armed);
            const title = `${u.name} — ${b.statStr}\n${armed ? 'Click again to dismiss · drag to move' : 'Click to dismiss · drag to move'}`;
            if (b.el.title !== title) b.el.title = title;
        }
    }
}

// ---------- scene FX (drainFx routes here when the scene is open) ----------
function sceneFxLayer() { return document.getElementById('scene-fx'); }

function spawnSceneFloatAt(unitEl, text, cls) {
    if (reducedMotion()) return;
    const layer = sceneFxLayer();
    if (!layer || layer.querySelectorAll('.fx-float').length >= FX_MAX_FLOATS) return;
    const target = unitEl.querySelector('.sprite, .letter-chip') || unitEl;
    const lr = layer.getBoundingClientRect();
    const tr = target.getBoundingClientRect();
    const f = document.createElement('div');
    f.className = 'fx-float ' + cls;
    f.textContent = text;
    f.style.left = (tr.left - lr.left + tr.width / 2) + 'px';
    f.style.top = (tr.top - lr.top - 6) + 'px';
    removeOnAnimationDone(f);
    layer.appendChild(f);
}

function spawnSceneGhost(unitEl) {
    if (reducedMotion()) return;
    const layer = sceneFxLayer();
    if (!layer) return;
    const img = unitEl.querySelector('.sprite');
    if (!img) { spawnSceneFloatAt(unitEl, '☠', 'fx-float--dmg'); return; }
    const lr = layer.getBoundingClientRect();
    const ir = img.getBoundingClientRect();
    const g = document.createElement('img');
    g.className = 'sghost';
    g.src = img.src;
    g.style.left = (ir.left - lr.left) + 'px';
    g.style.top = (ir.top - lr.top) + 'px';
    g.style.width = ir.width + 'px';
    g.style.height = ir.height + 'px';
    removeOnAnimationDone(g);
    layer.appendChild(g);
}

let scenePlotOpen = null;
function openScenePlot(id) { scenePlotOpen = id; renderScenePlotDrawer(); document.getElementById('scene-drawer').classList.remove('hidden'); }
function closeScenePlot() { scenePlotOpen = null; document.getElementById('scene-drawer').classList.add('hidden'); }
function renderScenePlotDrawer() {
    const b = buildings[scenePlotOpen];
    if (!b) return;
    const isHp = b.type === 'hpregen';
    const totalSlots = b.count * b.slotsPerBuilding;
    const sorted = b.residents.map((r, i) => ({ ...r, originalIndex: i })).sort((a, b) => a.income - b.income);
    let slots = '';
    for (const r of sorted) {
        const letter = r.name ? r.name[0].toUpperCase() : '?';
        const injured = isInjured(r);
        const val = isHp ? `${r.income} hp/s` : `${r.income} g/s`;
        const rinfo = rarityTiers[r.rarity] || rarityTiers.common;
        slots += `<div class="portrait portrait--${r.rarity || 'common'}${injured ? ' portrait--injured' : ''}"
            title="${r.name} (${rinfo.name}) — ${val}&#10;Click to dismiss" data-action="fireResident:${scenePlotOpen}:${r.originalIndex}">
            ${injured ? '<span class="portrait-letter">✚</span>' : portraitInner('town_' + (r.typeId || 'villager'), letter)}
            <span class="portrait-stat">${r.income}</span></div>`;
    }
    for (let i = b.residents.length; i < totalSlots; i++)
        slots += `<div class="portrait portrait--empty" title="Empty slot"><span class="portrait-letter">·</span></div>`;
    // Build row: same purchase-info source as the classic buildings panel.
    // canAfford flips at most once between purchases (gold rises monotonically),
    // so baking it into the memo string can't thrash; a mid-click rebuild is
    // survivable anyway (delegated data-action dispatch).
    const info = buildingPurchaseInfo(scenePlotOpen);
    const qtyRow = `<div style="margin:2px 0 4px;font-size:10px;color:#8a7f63">Buy:
        ${[1, 5, 10, 'max'].map(q => `<button class="btn-qty ${buyQuantity === q ? 'btn-qty--active' : ''}" data-action="setBuyQuantity:${q}">×${q}</button>`).join('')}</div>`;
    const buildRow = `${qtyRow}<div style="margin:2px 0 10px;display:flex;gap:10px;align-items:center">
        <button class="btn-upgrade" data-action="buyBuilding:${scenePlotOpen}" ${info.canAfford ? '' : 'disabled'}>Build</button>
        <span style="font-size:11px;color:#8a7f63">${info.costLabel}</span></div>`;
    setPanelHtml('scene-drawer-body',
        `<h3>${b.name} ×${b.count}</h3>
         <div class="meta">${b.residents.length} / ${totalSlots} residents · hire from the Town Square</div>
         ${buildRow}
         <div class="dw-list"><div class="dw-slots">${slots || '<div class="dw-empty">No resident slots.</div>'}</div></div>`);
}

function sceneSetText(id, t) { const el = document.getElementById(id); if (el) el.textContent = t; }
function renderScene() {
    if (!sceneOpen) return;
    renderSceneHud();
    renderVista();
    renderSceneCrowd();
    renderSceneBattle();
    if (scenePlotOpen) renderScenePlotDrawer();

    // Volatile numbers, updated in place each frame (kept out of memoized strings).
    sceneSetText('scene-gold', Math.floor(displayedGold === null ? gold : displayedGold).toLocaleString());
    sceneSetText('scene-gps', Math.round(goldPerSecond * econIncomeMult()).toLocaleString());
    sceneSetText('scene-legacy', meta.legacy.toLocaleString());
    const hpFill = document.getElementById('scene-hp-fill');
    if (hpFill) {
        const max = getKingdomHpMax();
        hpFill.style.width = Math.max(0, Math.min(100, kingdomHP / max * 100)) + '%';
        sceneSetText('scene-hp-text', Math.ceil(kingdomHP).toLocaleString() + ' / ' + max.toLocaleString());
    }

    // Countdowns (fixed spans in the memoized chips)
    sceneSetText('scene-pool-timer', `arrivals in ${Math.max(0, POOL_REFRESH_INTERVAL - poolTimer)}s`);
    sceneSetText('scene-hero-timer', `new in ${Math.max(0, HERO_POOL_REFRESH_INTERVAL - heroPoolTimer)}s`);
    sceneSetText('scene-raid-timer', formatTimer(invasionTimer));
    if (currentInvasion && escalationMult(currentInvasion) > 1) {
        sceneSetText('scene-esc-line', `The siege escalates! Enemy attack +${Math.round((escalationMult(currentInvasion) - 1) * 100)}%`);
    }

    // Crowd affordability — volatile class, never part of the memo string
    document.querySelectorAll('#scene-crowd [data-recruit-id]').forEach(el => {
        const r = recruitPool.find(x => x.id === Number(el.dataset.recruitId));
        if (r) el.classList.toggle('sunit--cant', !canHireRecruit(r));
    });
    const heroHasSlot = heroSquad.some(s => s === null);
    document.querySelectorAll('#scene-crowd [data-hero-id]').forEach(el => {
        const r = heroRecruitPool.find(x => x.id === Number(el.dataset.heroId));
        if (r) el.classList.toggle('sunit--cant', !(gold >= r.cost && heroHasSlot));
    });

    // Escalation wash over the battlefield half
    const wash = document.getElementById('scene-esc-wash');
    if (wash) {
        const esc = currentInvasion ? escalationMult(currentInvasion) : 1;
        const op = esc > 1 ? Math.min(0.5, (esc - 1) * 0.8).toFixed(2) : '0';
        if (wash.style.opacity !== op) wash.style.opacity = op;
    }

    // file:// notice — placeholders should never look like a broken wire
    sceneSetText('scene-note', spriteLoadBlocked
        ? '⚠ Art needs http — double-click start-game-server.bat (file:// blocks sprite processing)'
        : 'Scene view — work in progress');
}

// A requestAnimationFrame loop capped at RENDER_INTERVAL_MS repaints
// everything: memoized panels only touch the DOM when content changed,
// battle slots update in place, and the FX queue drains under its budget.
// Render cost is now independent of dev speed — 100x sim, ~15fps paint.
let displayedGold = null;   // eased display value — the counter rolls, never snaps
let paintedPoolGen = 0, paintedHeroPoolGen = 0;
let lastShuffleWall = 0;

function renderAll() {
    // FX drain FIRST: death-ghosts must capture slot geometry before this
    // frame's squad render rebuilds the structure out from under them.
    drainFx();

    document.body.classList.toggle('reduce-motion', reducedMotion());

    // Gold counter easing: roll 25% of the gap per frame, snap when close.
    // Purely presentational — every purchase check reads the real `gold`.
    const goldTarget = Math.floor(gold);
    if (displayedGold === null || Math.abs(goldTarget - displayedGold) < 2) displayedGold = goldTarget;
    else displayedGold += (goldTarget - displayedGold) * 0.25;
    document.getElementById('gold-display').textContent = Math.floor(displayedGold).toLocaleString();
    document.getElementById('gps-display').textContent = Math.round(goldPerSecond * econIncomeMult()).toLocaleString();
    document.getElementById('legacy-display').textContent = meta.legacy.toLocaleString();
    document.getElementById('siege-indicator').textContent = currentInvasion ? ' (siege)' : '';

    renderKingdomHP();
    renderLeftPanel();
    renderSpeedButtons(); // locks lift the frame after Swift Seasons is bought
    renderMotionToggle();
    renderRaidStatusBar();
    renderBattleSquads();
    renderRecruitPool();
    renderBuildings();
    renderHeroRecruitPool();
    renderScene(); // M15 scene view (no-op unless toggled open)

    refreshVolatileUI();

    // Post-render FX: flashes and entrance animations that target content
    // inside memoized panels — must run AFTER the panels have settled.
    for (const f of postRenderFlashes) flashClass(document.querySelector(f.selector), f.cls);
    postRenderFlashes.length = 0;

    // Pool-refresh shuffle: stagger the fresh cards in. Wall-clock gated so
    // 100x dev speed (a refresh every ~0.1s real time) doesn't strobe.
    const now = performance.now();
    if (paintedPoolGen !== poolGeneration) {
        paintedPoolGen = poolGeneration;
        if (!reducedMotion() && now - lastShuffleWall > 400) {
            lastShuffleWall = now;
            flashClass(document.getElementById('recruit-pool'), 'fx-pool-shuffle');
        }
    }
    if (paintedHeroPoolGen !== heroPoolGeneration) {
        paintedHeroPoolGen = heroPoolGeneration;
        if (!reducedMotion() && now - lastShuffleWall > 400) {
            lastShuffleWall = now;
            flashClass(document.getElementById('hero-recruit-pool'), 'fx-pool-shuffle');
        }
    }
}

// Kept as the universal "something changed, repaint" entry point for event
// handlers — an immediate full pass is cheap now that panels are memoized.
function updateUI() {
    renderAll();
}

// --- Delegated UI actions (click-eating fix, 2026-07-17) ---
// Generated panels use data-action="name:arg:arg" instead of inline onclick.
// Two document-level listeners dispatch by ACTION STRING, not by element:
// if a panel rebuild replaces a button between pointerdown and pointerup, the
// replacement under the cursor carries the same action string and the press
// still lands. Identity is part of the string (recruit/hero ids are unique
// forever), so a pool refresh mid-click yields a MISMATCH and safely drops
// the press instead of buying whatever took that spot.
const UI_ACTIONS = {
    hireRecruit:     id => hireRecruit(Number(id)),
    hireHero:        id => hireHero(Number(id)),
    fireResident:    (id, idx) => fireResident(id, Number(idx)),
    buyBuilding:     id => buyBuilding(id),
    toggleBuilding:  id => toggleBuilding(id),
    setBuyQuantity:  q => setBuyQuantity(q === 'max' ? 'max' : Number(q)),
    setAutoRecruit:  r => setAutoRecruit(r === 'null' ? null : r),
    setGameSpeed:    s => setGameSpeed(Number(s)),
    levelUpKingdom:  () => levelUpKingdom(),
    showNewAgeConfirm: () => showNewAgeConfirm(),
    confirmNewAge:   () => confirmNewAge(),
    cancelNewAge:    () => cancelNewAge(),
    showResetConfirm: () => showResetConfirm(),
    doResetGame:     () => doResetGame(),
    cancelReset:     () => cancelReset(),
    buyUpgrade:      id => buyUpgrade(id),
    foundNewAge:     () => foundNewAge(),
    continueEndless: () => continueEndless(),
    setReduceMotion: v => { meta.reduceMotion = v === '1'; saveMeta(); updateUI(); },
    toggleSceneView: () => toggleSceneView(),
    openScenePlot:   id => openScenePlot(id),
    closeScenePlot:  () => closeScenePlot(),
    // Scene battle hero click: same shared armed-to-dismiss state as the
    // classic battle slots (arming in one view shows in the other).
    sceneHeroClick:  i => {
        const index = Number(i);
        const armed = armedHeroSlot === index && Date.now() - armedHeroSlotTime < ARM_TIMEOUT_MS;
        if (armed) {
            armedHeroSlot = null;
            fireHero(index);
        } else {
            armedHeroSlot = index;
            armedHeroSlotTime = Date.now();
        }
    }
};

function runUiAction(actionStr) {
    const [name, ...args] = actionStr.split(':');
    const fn = UI_ACTIONS[name];
    if (fn) fn(...args);
}

let pressedActionStr = null;
let lastDispatched = { action: null, t: 0 };

function bindActionDispatch() {
    document.addEventListener('pointerdown', e => {
        const el = e.target.closest && e.target.closest('[data-action]');
        pressedActionStr = el && !el.disabled ? el.dataset.action : null;
    }, true);
    document.addEventListener('pointerup', e => {
        const pressed = pressedActionStr;
        pressedActionStr = null;
        if (!pressed) return;
        const el = e.target.closest && e.target.closest('[data-action]');
        if (!el || el.disabled || el.dataset.action !== pressed) return;
        lastDispatched = { action: pressed, t: performance.now() };
        runUiAction(pressed);
    }, true);
    // Keyboard activation (Enter/Space) arrives as a click with no pointer
    // press. Dispatch it — but swallow the synthetic click that trails a
    // pointerup we already handled, or every mouse press would fire twice.
    document.addEventListener('click', e => {
        const el = e.target.closest && e.target.closest('[data-action]');
        if (!el || el.disabled) return;
        if (el.dataset.action === lastDispatched.action && performance.now() - lastDispatched.t < 600) {
            lastDispatched.action = null; // swallow only the one trailing click
            return;
        }
        runUiAction(el.dataset.action);
    });
}

const RENDER_INTERVAL_MS = 66; // ~15fps paint cadence
let lastRenderTs = 0;
function renderFrame(ts) {
    requestAnimationFrame(renderFrame);
    if (ts - lastRenderTs < RENDER_INTERVAL_MS) return;
    lastRenderTs = ts;
    renderAll();
}

loadSprites(); // async — sprites pop into portraits/slots as each file processes
loadChrome();  // async — panel frame chrome pops in once the texture is keyed
loadScene();   // async — M15 scene backdrop; the scene view is opt-in via #scene-toggle
bindActionDispatch(); // delegated data-action dispatch — see UI_ACTIONS
loadMeta();
loadGame();
resizeHeroSquad(); // no-save startups still need the squad sized to War Banners rank
if (recruitPool.length === 0) refreshPool();
if (kingdomLevel >= RAID_TRIGGER_LEVEL && heroRecruitPool.length === 0) refreshHeroPool();
if (meta.sceneView) toggleSceneView(); // restore the persisted scene/classic choice
updateUI();
renderRunSummary(); // reshow the run-summary screen if the game was closed mid-summary
renderVictory();    // likewise the victory screen (closed mid-celebration)
setGameSpeed(gameSpeed); // also starts the tick interval
requestAnimationFrame(renderFrame); // M15 Phase 0: the render loop (sim renders nothing itself)
