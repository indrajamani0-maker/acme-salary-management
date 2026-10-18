import { useEffect, useMemo, useState } from 'react';
import { deactivateEmployee, exportUrl, getAnalytics, getEmployees, saveEmployee } from './api';

const emptyForm = {
  employee_code: '', full_name: '', email: '', department: 'Engineering',
  country: 'India', employment_status: 'active', salary_amount: '0.00',
  currency: 'INR', salary_effective_date: new Date().toISOString().slice(0, 10),
};
const departments = ['Engineering', 'Finance', 'Human Resources', 'Marketing', 'Operations', 'Sales', 'Support', 'Data'];
const countries = ['India', 'United States', 'United Kingdom', 'Germany', 'Canada', 'Australia'];
const currencies = ['INR', 'USD', 'GBP', 'EUR', 'CAD', 'AUD'];

function money(amount, currency) {
  return `${currency} ${Number(amount || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export default function App() {
  const [employees, setEmployees] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [search, setSearch] = useState('');
  const [country, setCountry] = useState('');
  const [department, setDepartment] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const filters = useMemo(() => ({ search, country, department, status }), [search, country, department, status]);

  async function refresh() {
    setLoading(true);
    setError('');
    try {
      const [employeeData, analyticsData] = await Promise.all([
        getEmployees({ ...filters, page, page_size: 10 }),
        getAnalytics(),
      ]);
      setEmployees(employeeData.items);
      setTotalPages(Math.max(employeeData.pages, 1));
      setAnalytics(analyticsData);
    } catch (err) {
      setError(`${err.message}. Make sure the FastAPI backend is running on port 8000.`);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { refresh(); }, [filters, page]);

  function openCreate() {
    setEditingId(null);
    setForm({ ...emptyForm, employee_code: `ACME${String(Date.now()).slice(-6)}` });
    setShowForm(true);
    setNotice('');
  }
  function openEdit(employee) {
    setEditingId(employee.id);
    setForm({
      ...employee,
      salary_amount: String(employee.salary_amount),
      salary_effective_date: employee.salary_effective_date,
    });
    setShowForm(true);
    setNotice('');
  }
  function updateField(event) {
    setForm(current => ({ ...current, [event.target.name]: event.target.value }));
  }
  async function submitForm(event) {
    event.preventDefault();
    setError('');
    setNotice('');
    try {
      await saveEmployee({ ...form, salary_amount: Number(form.salary_amount) }, editingId);
      setShowForm(false);
      setNotice(editingId ? 'Employee updated successfully.' : 'Employee created successfully.');
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }
  async function deactivate(employee) {
    if (!window.confirm(`Deactivate ${employee.full_name}?`)) return;
    try {
      await deactivateEmployee(employee.id);
      setNotice(`${employee.full_name} was deactivated.`);
      await refresh();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-mark">A</div>
        <div><div className="brand-name">ACME <span>People</span></div><div className="brand-subtitle">Salary management workspace</div></div>
        <div className="topbar-right"><span className="status-dot" /> HR MANAGER <div className="avatar">HR</div></div>
      </header>

      <main className="content">
        <section className="page-heading">
          <div><div className="eyebrow">PEOPLE OPERATIONS / COMPENSATION</div><h1>Salary overview</h1><p>Manage employee records and review compensation across your organization.</p></div>
          <button className="primary-button" onClick={openCreate}>＋ Add employee</button>
        </section>

        {error && <div className="alert error">{error}</div>}
        {notice && <div className="alert success">{notice}</div>}

        <section className="stat-grid">
          <StatCard label="Total employees" value={analytics?.total_employees ?? '—'} detail="Across all locations" />
          <StatCard label="Active employees" value={analytics?.active_employees ?? '—'} detail="Currently active" />
          <StatCard label="Inactive employees" value={analytics?.inactive_employees ?? '—'} detail="Not currently active" />
          <StatCard label="Countries" value={analytics ? new Set(analytics.by_country.map(row => row.country)).size : '—'} detail="With employee records" />
        </section>

        <section className="panel">
          <div className="panel-heading"><div><h2>Employee directory</h2><p>Search and manage salary records</p></div><a className="secondary-button" href={exportUrl(filters)} target="_blank" rel="noreferrer">↓ Export CSV</a></div>
          <div className="filters">
            <label className="search-box"><span>⌕</span><input value={search} onChange={e => { setPage(1); setSearch(e.target.value); }} placeholder="Search name, email or employee ID" /></label>
            <select value={country} onChange={e => { setPage(1); setCountry(e.target.value); }}><option value="">All countries</option>{countries.map(x => <option key={x}>{x}</option>)}</select>
            <select value={department} onChange={e => { setPage(1); setDepartment(e.target.value); }}><option value="">All departments</option>{departments.map(x => <option key={x}>{x}</option>)}</select>
            <select value={status} onChange={e => { setPage(1); setStatus(e.target.value); }}><option value="">All statuses</option><option value="active">Active</option><option value="inactive">Inactive</option></select>
          </div>

          <div className="table-wrap">
            <table>
              <thead><tr><th>EMPLOYEE</th><th>DEPARTMENT</th><th>COUNTRY</th><th>ANNUAL SALARY</th><th>STATUS</th><th>ACTIONS</th></tr></thead>
              <tbody>
                {loading ? <tr><td colSpan="6" className="empty-state">Loading employee records…</td></tr> :
                employees.length === 0 ? <tr><td colSpan="6" className="empty-state">No employees match these filters.</td></tr> :
                employees.map(employee => <tr key={employee.id}>
                  <td><div className="employee-cell"><div className="employee-avatar">{employee.full_name.split(' ').map(part => part[0]).slice(0, 2).join('').toUpperCase()}</div><div><strong>{employee.full_name}</strong><small>{employee.employee_code} · {employee.email}</small></div></div></td>
                  <td>{employee.department}</td><td>{employee.country}</td>
                  <td><strong>{money(employee.salary_amount, employee.currency)}</strong><small className="subline">Effective {employee.salary_effective_date}</small></td>
                  <td><span className={`pill ${employee.employment_status}`}>{employee.employment_status}</span></td>
                  <td><div className="actions"><button className="text-button" onClick={() => openEdit(employee)}>Edit</button>{employee.employment_status === 'active' && <button className="text-button danger-text" onClick={() => deactivate(employee)}>Deactivate</button>}</div></td>
                </tr>)}
              </tbody>
            </table>
          </div>
          <div className="table-footer"><span>{analytics ? `Showing ${employees.length} on this page · ${' '} ${' '}records may be filtered` : 'Loading totals…'}</span><div className="pagination"><button disabled={page <= 1} onClick={() => setPage(p => p - 1)}>← Previous</button><span>Page {page} of {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage(p => p + 1)}>Next →</button></div></div>
        </section>

        <section className="panel analytics-panel">
          <div className="panel-heading"><div><h2>Compensation breakdown</h2><p>Salary totals are separated by currency—no misleading cross-currency totals.</p></div></div>
          <div className="analytics-grid">
            <div><h3>By country and currency</h3><Breakdown rows={analytics?.by_country || []} labelKey="country" /></div>
            <div><h3>By department and currency</h3><Breakdown rows={analytics?.by_department || []} labelKey="department" /></div>
          </div>
        </section>
        <footer>ACME People · Salary data workspace <span>Demo data only · No real employee information</span></footer>
      </main>

      {showForm && <div className="modal-backdrop" onMouseDown={e => { if (e.target === e.currentTarget) setShowForm(false); }}>
        <form className="employee-form" onSubmit={submitForm}>
          <div className="form-heading"><div><h2>{editingId ? 'Edit employee' : 'Add employee'}</h2><p>Enter employee and salary details.</p></div><button type="button" className="close-button" onClick={() => setShowForm(false)}>×</button></div>
          <div className="form-grid">
            <FormField label="Employee ID"><input required name="employee_code" value={form.employee_code} onChange={updateField} minLength="2" maxLength="20" /></FormField>
            <FormField label="Full name"><input required name="full_name" value={form.full_name} onChange={updateField} minLength="2" /></FormField>
            <FormField label="Email"><input required type="email" name="email" value={form.email} onChange={updateField} /></FormField>
            <FormField label="Department"><select name="department" value={form.department} onChange={updateField}>{departments.map(x => <option key={x}>{x}</option>)}</select></FormField>
            <FormField label="Country"><select name="country" value={form.country} onChange={updateField}>{countries.map(x => <option key={x}>{x}</option>)}</select></FormField>
            <FormField label="Employment status"><select name="employment_status" value={form.employment_status} onChange={updateField}><option value="active">Active</option><option value="inactive">Inactive</option></select></FormField>
            <FormField label="Annual salary"><input required type="number" name="salary_amount" min="0" step="0.01" value={form.salary_amount} onChange={updateField} /></FormField>
            <FormField label="Currency"><select name="currency" value={form.currency} onChange={updateField}>{currencies.map(x => <option key={x}>{x}</option>)}</select></FormField>
            <FormField label="Effective date"><input required type="date" name="salary_effective_date" value={form.salary_effective_date} onChange={updateField} /></FormField>
          </div>
          <div className="form-actions"><button type="button" className="secondary-button" onClick={() => setShowForm(false)}>Cancel</button><button className="primary-button" type="submit">{editingId ? 'Save changes' : 'Create employee'}</button></div>
        </form>
      </div>}
    </div>
  );
}

function StatCard({ label, value, detail }) {
  return <div className="stat-card"><div className="stat-label">{label}</div><div className="stat-value">{value}</div><div className="stat-detail"><span className="tiny-dot" />{detail}</div></div>;
}
function FormField({ label, children }) { return <label className="form-field"><span>{label}</span>{children}</label>; }
function Breakdown({ rows, labelKey }) {
  if (!rows.length) return <p className="muted">No data available yet.</p>;
  return <div className="breakdown-list">{rows.map((row, index) => <div className="breakdown-row" key={`${row[labelKey]}-${row.currency}`}><div className="breakdown-name"><span>{row[labelKey]}</span><small>{row.employee_count} employees · {row.currency}</small></div><strong>{money(row.salary_total, row.currency)}</strong><div className="bar-track"><div className="bar-fill" style={{ width: `${Math.max(3, Math.min(100, row.employee_count / Math.max(...rows.map(x => x.employee_count)) * 100))}%` }} /></div></div>)}</div>;
}
