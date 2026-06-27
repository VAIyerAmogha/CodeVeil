export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatDate(dateString: string): string {
  if (!dateString) return '';
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function truncate(str: string, n: number): string {
  if (!str) return '';
  return str.length > n ? str.substring(0, n - 1) + '...' : str;
}

export function getLanguageColor(lang: string): string {
  const colors: Record<string, string> = {
    Python: '#3572A5',
    TypeScript: '#2b7489',
    JavaScript: '#f1e05a',
    Java: '#b07219',
    Go: '#00ADD8',
    Rust: '#dea584',
    default: '#6e7681',
  };
  return colors[lang] || colors.default;
}
