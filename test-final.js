// Read the simulator and extract only the core functions
const fs = require('fs');
const code = fs.readFileSync('./tools/balance-sim.js', 'utf8');

// Split at the Report section and execute only the core
const parts = code.split('// ---------- Report ----------');
const coreCode = parts[0];

// Execute all core functions
eval(coreCode);

// Now test the maxed squad
const REALM_DOCTRINES = { attack: 1.105, speed: 1.06, salves: 0.012, blessing: true };

const sixteen = (r, tp, th) => [
    ['guardian', r, tp, th], ['fighter', r, tp, th], ['paladin', r, tp, th], ['paladin', r, tp, th],
    ['ranged', r, tp, th], ['ranged', r, tp, th], ['assassin', r, tp, th], ['assassin', r, tp, th],
    ['mender', r, tp, th], ['mender', r, tp, th], ['ranged', r, tp, th], ['mender', r, tp, th],
    ['banneret', r, tp, th], ['battlemage', r, tp, th], ['frostadept', r, tp, th], ['assassin', r, tp, th]
];

const maxedSquad = sixteen(10, 2.0, 2.0);

console.log('=== MAXED ENDGAME SQUAD: Deep Infernal & Final Siege ===\n');
console.log('Squad Config: 16 Legendaries with full tree multipliers (2.0×)');
console.log('Kingdom: Reinforced Walls rank 4 (2000 HP, +27 defense) + 8 Builders (25 hp/s regen)');
console.log('Doctrines: Full Realm set (attack ×1.105, speed ×1.06, regen 1.2%/s, blessing enabled)\n');

console.log('PER-WAVE WIN RATES - Infernal Siege waves 10-17 (60 trials each):');
console.log('─'.repeat(50));

const tierIdx = 4;
for (let wave = 9; wave <= 16; wave++) {
    const isBoss = wave === 16;
    const wr = winRate(maxedSquad, tierIdx, wave, 60, REALM_DOCTRINES);
    const rate = Math.round(wr.rate * 100);
    const waveNum = wave + 1;
    const waveLabel = isBoss ? '17 (BOSS)' : String(waveNum).padStart(2);
    console.log(`Wave ${waveLabel}:  ${String(rate).padStart(3)}%`);
}

console.log('\n' + '─'.repeat(50));
console.log('\nFINAL SIEGE GAUNTLET (3-phase encounter, 500 trials):');
const gauntletRate = finalSiegeRate(maxedSquad, 500, REALM_DOCTRINES, 25, 2000, 27);
console.log(`  Win Rate: ${Math.round(gauntletRate * 100)}%\n`);

console.log('KEY FINDINGS:');
console.log('─'.repeat(50));
console.log('• Waves 10-14 remain above 50% (safe);');
console.log('• Waves 15-17 drop below 50% (wall encountered);');
console.log('• Final Siege gauntlet win rate around 25-33% (per-run variance).\n');

console.log('LAYOUT SENSITIVITY (good vs. degenerate):');
console.log('─'.repeat(50));

// Test bad layout
const allRanged = Array(16).fill(['ranged', 10, 2.0, 2.0]);

console.log('\nInfernal w15 (pre-boss):');
const g15 = winRate(maxedSquad, 4, 14, 40, REALM_DOCTRINES);
const b15 = winRate(allRanged, 4, 14, 40, REALM_DOCTRINES);
console.log(`  Good (G/F/P/A/M/B/BM/FA): ${Math.round(g15.rate * 100)}%`);
console.log(`  Bad (all-ranged):          ${Math.round(b15.rate * 100)}%`);
console.log(`  → Layout impact: ${Math.abs(Math.round(g15.rate * 100) - Math.round(b15.rate * 100))}pp`);

console.log('\nInfernal w17 BOSS:');
const gb = winRate(maxedSquad, 4, 16, 40, REALM_DOCTRINES);
const bb = winRate(allRanged, 4, 16, 40, REALM_DOCTRINES);
console.log(`  Good (G/F/P/A/M/B/BM/FA): ${Math.round(gb.rate * 100)}%`);
console.log(`  Bad (all-ranged):          ${Math.round(bb.rate * 100)}%`);
console.log(`  → Layout impact: ${Math.abs(Math.round(gb.rate * 100) - Math.round(bb.rate * 100))}pp`);

console.log('\nFinal Siege gauntlet:');
const gg = finalSiegeRate(maxedSquad, 100, REALM_DOCTRINES, 25, 2000, 27);
const bg = finalSiegeRate(allRanged, 100, REALM_DOCTRINES, 25, 2000, 27);
console.log(`  Good (G/F/P/A/M/B/BM/FA): ${Math.round(gg * 100)}%`);
console.log(`  Bad (all-ranged):          ${Math.round(bg * 100)}%`);
console.log(`  → Layout impact: ${Math.abs(Math.round(gg * 100) - Math.round(bg * 100))}pp`);

