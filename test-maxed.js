// Load the full balance simulator module
const fs = require('fs');
const Module = require('module');
const path = require('path');

// Capture console.log calls
const originalLog = console.log;
const output = [];
console.log = (...args) => {
    output.push(args.join(' '));
};

// Run the full sim
require('./tools/balance-sim.js');

// Restore console
console.log = originalLog;

// Find and extract the relevant sections
const text = output.join('\n');

// Extract the doctrine check section
const doctrineStart = text.indexOf('=== M12 doctrine check');
const doctrineEnd = text.indexOf('=== M14 campaign-arc check');
const doctrineSection = text.substring(doctrineStart, doctrineEnd);

// Extract the gauntlet section
const gauntletStart = text.indexOf('=== M13 Final Siege gauntlet');
const gauntletEnd = text.indexOf('=== Fair-fight win durations');
const gauntletSection = text.substring(gauntletStart, gauntletEnd);

console.log('\n========== ENDGAME SQUAD TEST RESULTS ==========\n');
console.log(doctrineSection);
console.log('\n');
console.log(gauntletSection);
