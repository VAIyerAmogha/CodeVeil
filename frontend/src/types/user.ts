export interface UsageStats {
  repos_indexed: number;
  queries_made: number;
  last_active: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  password_hash?: string;
  oauth_provider?: string;
  oauth_id?: string;
  created_at: string;
  usage: UsageStats;
}
