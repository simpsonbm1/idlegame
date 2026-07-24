// Directly execute the balance-sim code with custom test output
const Module = require('module');

// Read and execute the core simulator code (up to the Report section)
const fs = require('fs');
const simCode = fs.readFileSync('./tools/balance-sim.js', 'utf8');
const coreCode = simCode.split('// ---------- Report ----------')[0];

// Execute the core
eval(coreCode);

// Now run our custom tests
const REALM_DOCTRINES = { attack: 1.105, speed: 1.06, salves: 0.012, blessing: true };

const sixteen = (r, tp, th) => [
    ['guardian', r, tp, th], ['fighter', r, tp, th], ['paladin', r, tp, th], ['paladin', r, tp, th],
    ['ranged', r, tp, th], ['ranged', r, tp, th], ['assassin', r, tp, th], ['assassin', r, tp, th],
    ['mender', r, tp, th], ['mender', r, tp, th], ['ranged', r, tp, th], ['mender', r, tp, th],
    ['banneret', r, tp, th], ['battlemage', r, tp, th], ['frostadept', r, tp, th], ['assassin', r, tp, th]
];

const maxedSquad = sixteen(10, 2.0, 2.0);

console.log('=== MAXED ENDGAME SQUAD PERFORMANCE ===');
console.log('Configuration: 16 Legendaries (10×), Tree Mult 2.0×, ALL Realm Doctrines');
console.log('Kingdom: Reinforced Walls rank 4 (2000 HP, +27 def), 8 Builders (25 hp/s regen)\n');

console.log('Infernal Siege Waves 10-17 Win Rates (60 trials each):');
console.log('Wave  | With Doctrines | Status');
console.log('------|----------------|--------');

const tierIdx = 4; // Infernal
let lastWinAbove50 = null;
let firstWinBelow50 = null;
let firstWinBelow25 = null;

for (let wave = 9; wave <= 16; wave++) {
    const isBoss = wave === 16;
    const wr = winRate(maxedSquad, tierIdx, wave, 60, REALM_DOCTRINES);
    const rate = Math.round(wr.rate * 100);
    const waveLabel = isBoss ? '17 (BOSS)' : String(wave + 1).padStart(2);
    
    if (rate >= 50 && lastWinAbove50 === null) lastWinAbove50 = wave + 1;
    if (rate < 50 && firstWinBelow50 === null) firstWinBelow50 = wave + 1;
    if (rate < 25 && firstWinBelow25 === null) firstWinBelow25 = wave + 1;
    
    let status = '✓ Safe';
    if (rate < 50) status = '⚠ Wall';
    if (rate < 25) status = '✗ Fail';
    
    console.log(`  ${waveLabel}  |      ${String(rate).padStart(3)}%       | ${status}`);
}

console.log('\n');
console.log('Final Siege Gauntlet (3 phases, 500 trials):');
const gauntletRate = finalSiegeRate(maxedSquad, 500, REALM_DOCTRINES, 25, 2000, 27);
console.log(`  Win Rate: ${Math.round(gauntletRate * 100)}%\n`);

console.log('Wall Analysis (maxed endgame kit):');
if (firstWinBelow50) {
    console.log(`  - First wave below 50% win rate: Infernal Siege wave ${firstWinBelow50}`);
}
if (firstWinBelow25) {
    console.log(`  - First wave below 25% win rate: Infernal Siege wave ${firstWinBelow25}`);
} else {
    console.log(`  - All tested waves remain above 25% (no clear wall)`);
}

console.log('\n=== LAYOUT SENSITIVITY TEST ===');
console.log('Comparing balanced layout vs. all-ranged (degenerate) at deep Infernal:\n');

const allRanged = Array(16).fill(['ranged', 10, 2.0, 2.0]);

console.log('Infernal Siege wave 15 (60 trials each):');
const goodRate15 = winRate(maxedSquad, 4, 14, 60, REALM_DOCTRINES);
const badRate15 = winRate(allRanged, 4, 14, 60, REALM_DOCTRINES);
console.log(`  Balanced (G/F/P/A/M/B/BM/FA): ${Math.round(goodRate15.rate * 100)}%`);
console.log(`  All-ranged (16× Archer):       ${Math.round(badRate15.rate * 100)}%`);
console.log(`  Layout matters: ${Math.round(Math.abs(goodRate15.rate - badRate15.rate) * 100)} percentage points\n`);

console.log('Infernal Siege wave 17 BOSS (60 trials each):');
const goodRateBoss = winRate(maxedSquad, 4, 16, 60, REALM_DOCTRINES);
const badRateBoss = winRate(allRanged, 4, 16, 60, REALM_DOCTRINES);
console.log(`  Balanced (G/F/P/A/M/B/BM/FA): ${Math.round(goodRateBoss.rate * 100)}%`);
console.log(`  All-ranged (16× Archer):       ${Math.round(badRateBoss.rate * 100)}%`);
console.log(`  Layout matters: ${Math.round(Math.abs(goodRateBoss.rate - badRateBoss.rate) * 100)} percentage points\n`);

console.log('Final Siege gauntlet (100 trials each):');
const goodGauntlet = finalSiegeRate(maxedSquad, 100, REALM_DOCTRINES, 25, 2000, 27);
const badGauntlet = finalSiegeRate(allRanged, 100, REALM_DOCTRINES, 25, 2000, 27);
console.log(`  Balanced (G/F/P/A/M/B/BM/FA): ${Math.round(goodGauntlet * 100)}%`);
console.log(`  All-ranged (16× Archer):       ${Math.round(badGauntlet * 100)}%`);
console.log(`  Layout matters: ${Math.round(Math.abs(goodGauntlet - badGauntlet) * 100)} percentage points`);
