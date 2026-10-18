const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    throw new Error(data.detail || `Request failed (${response.status})`);
  }
  return response;
}

export async function getEmployees(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== '' && value !== undefined && value !== null) query.set(key, value);
  });
  return (await request(`/api/employees?${query.toString()}`)).json();
}
export async function getAnalytics() {
  return (await request('/api/analytics')).json();
}
export async function saveEmployee(employee, id = null) {
  const path = id ? `/api/employees/${id}` : '/api/employees';
  return (await request(path, {
    method: id ? 'PUT' : 'POST',
    body: JSON.stringify(employee),
  })).json();
}
export async function deactivateEmployee(id) {
  return (await request(`/api/employees/${id}`, { method: 'DELETE' })).json();
}
export function exportUrl(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== '' && value !== undefined && value !== null) query.set(key, value);
  });
  return `${API_BASE}/api/employees/export.csv?${query.toString()}`;
}
