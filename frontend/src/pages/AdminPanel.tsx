import { useEffect, useState } from 'react'
import { api } from '../api'
import { store } from '../store'
import { Company, Department, Function, Project, Task, User } from '../types'
import { fmtDate, label } from '../constants'
import SearchableSelect from '../components/SearchableSelect'

const ROLES = ['group_executive', 'business_head', 'functional_head', 'sponsor', 'pmo', 'pm', 'team_lead', 'employee', 'reviewer', 'auditor', 'admin']

interface UserForm {
  employee_id: string
  name: string
  email: string
  designation?: string
  role: string
  company_id?: number | null
  function_id?: number | null
  department_id?: number | null
  reports_to?: number | null
}

const EMPTY_USER: UserForm = { employee_id: '', name: '', email: '', designation: '', role: 'employee', company_id: null, function_id: null, department_id: null, reports_to: null }

export default function AdminPanel() {
  const [tab, setTab] = useState<'users' | 'tasks' | 'roles' | 'hierarchy'>('users')
  const [users, setUsers] = useState<User[]>([])
  const [tasks, setTasks] = useState<Task[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [companies, setCompanies] = useState<Company[]>([])
  const [functions, setFunctions] = useState<Function[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<User | null>(null)
  const [form, setForm] = useState<UserForm>(EMPTY_USER)
  const [msg, setMsg] = useState('')
  const [err, setErr] = useState('')
  const [privileged, setPrivileged] = useState<string[]>([])
  const [allRoles, setAllRoles] = useState<string[]>([])
  const [newRole, setNewRole] = useState('')

  const load = () => {
    api.get<User[]>('/organizations/users').then(setUsers)
    api.get<Task[]>('/tasks').then(setTasks)
    api.get<Project[]>('/projects').then(setProjects)
    api.get<Company[]>('/organizations/companies').then(setCompanies)
    api.get<Function[]>('/organizations/functions').then(setFunctions)
    api.get<Department[]>('/organizations/departments').then(setDepartments)
    api.get<string[]>('/privileged-roles').then(setPrivileged)
    api.get<string[]>('/all-roles').then(setAllRoles)
  }

  useEffect(load, [])

  const addRole = async () => {
    if (!newRole.trim()) return
    await api.post('/privileged-roles', { role: newRole.trim().toLowerCase().replace(/\s+/g, '_') })
    setNewRole('')
    load()
  }

  const removeRole = async (role: string) => {
    await api.del(`/privileged-roles?role=${encodeURIComponent(role)}`)
    load()
  }

  const projectName = (id?: number) => projects.find((p) => p.id === id)?.name ?? '—'
  const set = (k: keyof UserForm, v: string | number | null) => setForm((f) => ({ ...f, [k]: v }))

  const openCreate = () => { setEditing(null); setForm(EMPTY_USER); setErr(''); setShowForm(true) }
  const openEdit = (u: User) => {
    setEditing(u)
    setForm({ employee_id: u.employee_id, name: u.name, email: u.email, designation: u.designation ?? '', role: u.role, company_id: u.company_id ?? null, function_id: u.function_id ?? null, department_id: u.department_id ?? null, reports_to: u.reports_to ?? null })
    setErr('')
    setShowForm(true)
  }

  const saveUser = async () => {
    setErr('')
    if (!form.name || !form.email || !form.employee_id) { setErr('Name, email and employee id are required'); return }
    try {
      if (editing) {
        await api.patch(`/organizations/users/${editing.id}`, {
          ...form,
          company_id: form.company_id ?? null,
          function_id: form.function_id ?? null,
          department_id: form.department_id ?? null,
        })
        setMsg(`Updated ${form.name}`)
      } else {
        await api.post('/organizations/users', form)
        setMsg(`Created ${form.name}`)
      }
      setShowForm(false)
      load()
    } catch (e: any) { setErr(e.message) }
  }

  const deactivate = async (u: User) => {
    await api.del(`/organizations/users/${u.id}`)
    setMsg(`Deactivated ${u.name}`)
    load()
  }

  const removeUser = async (u: User) => {
    if (!confirm(`Permanently delete user "${u.name}" (${u.email})? This cannot be undone.`)) return
    await api.del(`/organizations/users/${u.id}/permanent`)
    setMsg(`Permanently deleted ${u.name}`)
    load()
  }

  const removeTask = async (t: Task) => {
    if (!confirm(`Permanently delete ${t.code} — "${t.title}"? This cannot be undone.`)) return
    await api.del(`/tasks/${t.id}/permanent`)
    setMsg(`Permanently deleted ${t.code}`)
    load()
  }

  return (
    <div>
      <div className="topbar">
        <div>
          <h1>Admin Panel</h1>
          <div className="crumb">User management &amp; enterprise task administration</div>
        </div>
      </div>

      {msg && <div className="card mb" style={{ background: '#e3f5ea' }}>{msg}</div>}

      <div className="row mb">
        <button className={`btn ${tab === 'users' ? 'primary' : ''}`} onClick={() => setTab('users')}>Users ({users.length})</button>
        <button className={`btn ${tab === 'tasks' ? 'primary' : ''}`} onClick={() => setTab('tasks')}>All Tasks ({tasks.length})</button>
        <button className={`btn ${tab === 'roles' ? 'primary' : ''}`} onClick={() => setTab('roles')}>Privileged Roles</button>
        <button className={`btn ${tab === 'hierarchy' ? 'primary' : ''}`} onClick={() => setTab('hierarchy')}>Hierarchy Mapping</button>
      </div>

      {tab === 'hierarchy' && (
        <div className="card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr><th>Employee</th><th>Role</th><th>Reports To</th><th>Approval Chain</th></tr>
            </thead>
            <tbody>
              {users.map((u) => {
                const manager = users.find((m) => m.id === u.reports_to)
                const chain = store.reportingChain(u.id)
                return (
                  <tr key={u.id}>
                    <td>{u.name}</td>
                    <td><span className={`badge ${u.role === 'admin' ? 'gold' : 'gray'}`}>{label(u.role)}</span></td>
                    <td className="small">{manager ? manager.name : '—'}</td>
                    <td className="small muted">{chain.map((c) => c.name).join(' → ')}</td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}

      {tab === 'roles' && (
        <div className="card">
          <div className="section-title" style={{ marginTop: 0 }}>Privileged Roles</div>
          <div className="small muted" style={{ marginBottom: 12 }}>
            These roles can view all group-wide tasks and approve date-revision / completion requests.
          </div>
          <div className="row mb" style={{ flexWrap: 'wrap' }}>
            {privileged.map((r) => (
              <span key={r} className="badge gold" style={{ padding: '6px 12px', fontSize: 13, display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                {label(r)}
                {r !== 'admin' && (
                  <span style={{ cursor: 'pointer', fontWeight: 700 }} onClick={() => removeRole(r)} title="Remove">✕</span>
                )}
              </span>
            ))}
          </div>
          <div className="row" style={{ alignItems: 'end' }}>
            <div className="field" style={{ minWidth: 260 }}>
              <label>Add role</label>
              <SearchableSelect
                value={newRole}
                items={allRoles.map((r) => ({ value: r, label: label(r) }))}
                onChange={(v) => setNewRole(v)}
                placeholder="Search or type new role…"
                allowCustom
              />
            </div>
            <button className="btn primary" onClick={addRole}>Add Role</button>
          </div>
          <div className="small muted" style={{ marginTop: 12 }}>
            Available roles: {allRoles.filter((r) => !privileged.includes(r)).map(label).join(', ') || 'all roles are privileged'}
          </div>
        </div>
      )}

      {tab === 'users' && (
        <>
          <div className="mb">
            <button className="btn primary" onClick={openCreate}>+ New User</button>
          </div>
          <div className="card" style={{ padding: 0 }}>
            <table>
              <thead>
                <tr><th>ID</th><th>Name</th><th>Email</th><th>Designation</th><th>Role</th><th>Active</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td className="muted small">{u.employee_id}</td>
                    <td>{u.name}</td>
                    <td className="small">{u.email}</td>
                    <td className="small">{u.designation ?? '—'}</td>
                    <td><span className={`badge ${u.role === 'admin' ? 'gold' : 'gray'}`}>{label(u.role)}</span></td>
                    <td>{u.is_active ? <span className="badge green">Active</span> : <span className="badge red">Inactive</span>}</td>
                    <td>
                      <div className="row">
                        <button className="btn sm" onClick={() => openEdit(u)}>Edit</button>
                        {u.role !== 'admin' && (
                          <>
                            {u.is_active && <button className="btn sm danger" onClick={() => deactivate(u)}>Deactivate</button>}
                            <button className="btn sm danger" onClick={() => removeUser(u)}>Remove</button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}

      {tab === 'tasks' && (
        <div className="card" style={{ padding: 0 }}>
          <table>
            <thead>
              <tr><th>Code</th><th>Task</th><th>Project</th><th>Responsible</th><th>Status</th><th>Due</th><th>Action</th></tr>
            </thead>
            <tbody>
              {tasks.map((t) => (
                <tr key={t.id}>
                  <td className="muted small">{t.code}</td>
                  <td>{t.title}</td>
                  <td className="small">{projectName(t.project_id)}</td>
                  <td className="small">{users.find((u) => u.id === t.responsible_id)?.name ?? '—'}</td>
                  <td><span className="badge gray">{label(t.status)}</span></td>
                  <td className="small">{fmtDate(t.approved_due_date || t.baseline_due_date)}</td>
                  <td><button className="btn sm danger" onClick={() => removeTask(t)}>Remove</button></td>
                </tr>
              ))}
            </tbody>
          </table>
          {tasks.length === 0 && <div className="empty">No tasks.</div>}
        </div>
      )}

      {showForm && (
        <div className="modal-backdrop" onClick={() => setShowForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h2>{editing ? `Edit User — ${editing.name}` : 'New User'}</h2>
            {err && <div className="badge red" style={{ marginBottom: 12 }}>{err}</div>}
            <div className="form-row">
              <div><label>Employee ID *</label><input value={form.employee_id} onChange={(e) => set('employee_id', e.target.value)} /></div>
              <div><label>Name *</label><input value={form.name} onChange={(e) => set('name', e.target.value)} /></div>
            </div>
            <div className="form-row">
              <div><label>Email *</label><input value={form.email} onChange={(e) => set('email', e.target.value)} /></div>
              <div><label>Designation</label><input value={form.designation} onChange={(e) => set('designation', e.target.value)} /></div>
            </div>
            <div className="form-row">
              <div>
                <label>Company (SBU)</label>
                <select value={form.company_id ?? ''} onChange={(e) => set('company_id', e.target.value ? Number(e.target.value) : null)}>
                  <option value="">—</option>
                  {companies.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
              </div>
              <div>
                <label>Function</label>
                <select value={form.function_id ?? ''} onChange={(e) => set('function_id', e.target.value ? Number(e.target.value) : null)}>
                  <option value="">—</option>
                  {functions.map((f) => <option key={f.id} value={f.id}>{f.name}</option>)}
                </select>
              </div>
            </div>
            <div className="form-row">
              <div>
                <label>Department</label>
                <select value={form.department_id ?? ''} onChange={(e) => set('department_id', e.target.value ? Number(e.target.value) : null)}>
                  <option value="">—</option>
                  {departments.map((dp) => <option key={dp.id} value={dp.id}>{dp.name}</option>)}
                </select>
              </div>
              <div>
                <label>Reports To (manager)</label>
                <select value={form.reports_to ?? ''} onChange={(e) => set('reports_to', e.target.value ? Number(e.target.value) : null)}>
                  <option value="">— No manager —</option>
                  {users.filter((u) => u.id !== editing?.id).map((u) => <option key={u.id} value={u.id}>{u.name} — {label(u.role)}</option>)}
                </select>
              </div>
            </div>
            <label>Role</label>
            <select value={form.role} onChange={(e) => set('role', e.target.value)}>
              {allRoles.map((r) => <option key={r} value={r}>{label(r)}</option>)}
            </select>
            <div className="modal-actions">
              <button className="btn" onClick={() => setShowForm(false)}>Cancel</button>
              <button className="btn primary" onClick={saveUser}>{editing ? 'Save Changes' : 'Create User'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
