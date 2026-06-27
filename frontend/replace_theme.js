const fs = require('fs');
const path = require('path');

const replacements = {
  'bg-zinc-900': 'glass-panel',
  'bg-zinc-800': 'bg-green-900/20 border-green-500/20',
  'bg-zinc-950': 'bg-black/60',
  'border-zinc-800': 'border-green-500/20',
  'border-zinc-700': 'border-green-500/30',
  'border-zinc-600': 'border-green-500/40',
  'text-zinc-400': 'text-green-100/60',
  'text-zinc-500': 'text-green-100/40',
  'text-zinc-300': 'text-green-100/80',
  'text-white': 'text-green-50',
  'hover:border-zinc-600': 'hover:border-green-400/40',
  'hover:border-zinc-700': 'hover:border-green-500/50',
  'hover:bg-zinc-800': 'hover:bg-green-900/40 hover:shadow-[0_0_15px_rgba(34,197,94,0.1)] transition-all duration-300',
  'hover:bg-zinc-700': 'hover:bg-green-800/40',
  'bg-blue-600': 'bg-green-600',
  'hover:bg-blue-500': 'hover:bg-green-500',
  'text-blue-400': 'text-emerald-400',
  'bg-blue-500/20': 'bg-emerald-500/20',
  'shadow-blue-500/20': 'shadow-green-500/20',
  'focus:border-blue-500': 'focus:border-green-500',
  'bg-zinc-700': 'bg-green-800/40',
  'bg-black': 'bg-transparent',
  'bg-zinc-900/50': 'bg-green-950/30',
  'bg-zinc-800/50': 'bg-green-900/30'
};

function walkDir(dir) {
  let results = [];
  const list = fs.readdirSync(dir);
  list.forEach(file => {
    const filePath = path.join(dir, file);
    const stat = fs.statSync(filePath);
    if (stat && stat.isDirectory()) {
      results = results.concat(walkDir(filePath));
    } else {
      if (filePath.endsWith('.tsx') || filePath.endsWith('.ts')) {
        results.push(filePath);
      }
    }
  });
  return results;
}

const files = walkDir('./src');
files.forEach(file => {
  let content = fs.readFileSync(file, 'utf8');
  let changed = false;
  
  // Apply all replacements
  for (const [search, replace] of Object.entries(replacements)) {
    // Basic string replace all using regex
    const regex = new RegExp(search.replace(/[-\/\\^$*+?.()|[\]{}]/g, '\\$&'), 'g');
    if (regex.test(content)) {
      content = content.replace(regex, replace);
      changed = true;
    }
  }
  
  if (changed) {
    fs.writeFileSync(file, content, 'utf8');
    console.log(`Updated ${file}`);
  }
});
