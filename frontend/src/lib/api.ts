import { getToken } from './auth';
import { Repository, Job, RiskReport } from '../types/repository';
import { Query } from '../types/query';
import { User } from '../types/user';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function fetchWithAuth<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };
  
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      const { clearToken } = await import('./auth');
      clearToken();
      if (typeof window !== 'undefined') {
        window.location.href = '/auth/login';
      }
    }
    let errorMsg = 'An error occurred';
    try {
      const errorData = await response.json();
      errorMsg = errorData.detail || errorMsg;
    } catch {
      // ignore JSON parse error
    }
    throw new Error(errorMsg);
  }

  return response.json();
}

export async function indexRepo(github_url: string): Promise<{ job_id: string; repo_id: string }> {
  return fetchWithAuth<{ job_id: string; repo_id: string }>('/repositories/index', {
    method: 'POST',
    body: JSON.stringify({ github_url }),
  });
}

export async function getRepoStatus(repo_id: string): Promise<Job> {
  return fetchWithAuth<Job>(`/repositories/${repo_id}/status`);
}

export async function getRepo(repo_id: string): Promise<Repository> {
  return fetchWithAuth<Repository>(`/repositories/${repo_id}`);
}

export async function getRepos(): Promise<Repository[]> {
  return fetchWithAuth<Repository[]>('/repositories');
}

export async function postQuery(repo_id: string, question: string): Promise<Query> {
  return fetchWithAuth<Query>('/query', {
    method: 'POST',
    body: JSON.stringify({ repo_id, question }),
  });
}

export async function getQueries(repo_id: string): Promise<Query[]> {
  return fetchWithAuth<Query[]>(`/repositories/${repo_id}/queries`);
}

export async function getFileContent(repo_id: string, file_path: string): Promise<{ content: string; language: string }> {
  return fetchWithAuth<{ content: string; language: string }>(`/repositories/${repo_id}/file?path=${encodeURIComponent(file_path)}`);
}

export async function deleteRepo(repo_id: string): Promise<void> {
  return fetchWithAuth<void>(`/repositories/${repo_id}`, {
    method: 'DELETE',
  });
}

export async function getRisks(repo_id: string): Promise<RiskReport> {
  return fetchWithAuth<RiskReport>(`/repositories/${repo_id}/risks`);
}

export async function runRisks(repo_id: string): Promise<{status: string}> {
  return fetchWithAuth<{status: string}>(`/repositories/${repo_id}/risks`, { method: 'POST' });
}

export async function getCurrentUser(): Promise<User> {
  return fetchWithAuth<User>('/users/me');
}

export async function login(email: string, password: string): Promise<{ access_token: string, user: User }> {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to login');
  }
  return response.json();
}

export async function signup(email: string, name: string, password: string): Promise<{ access_token: string, user: User }> {
  const response = await fetch(`${API_URL}/auth/signup`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, name, password }),
  });
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || 'Failed to signup');
  }
  return response.json();
}
