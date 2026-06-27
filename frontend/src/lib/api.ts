import { getToken } from './auth';
import { Repository, Job } from '../types/repository';
import { Query } from '../types/query';

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
