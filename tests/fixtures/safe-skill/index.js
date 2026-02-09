// Safe skill that just reads data
const fs = require('fs');
const data = fs.readFileSync('./data/input.txt', 'utf8');
fs.writeFileSync('./output/result.txt', data.toUpperCase());
