import { useEffect, useState } from 'react'
import { useAuth } from '../auth'
import { api } from '../api'
import { User } from '../types'
import { label } from '../constants'

export default function Login() {
  const { login } = useAuth()
  const [users, setUsers] = useState<User[]>([])
  const [selected, setSelected] = useState<number | ''>('')
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    api.get<User[]>('/organizations/users').then(setUsers)
  }, [])

  const submit = async () => {
    if (!selected) { setError('Select a user to continue'); return }
    setBusy(true)
    setError('')
    try {
      await login(Number(selected))
    } catch (e: any) {
      setError(e.message)
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #0b1f3a, #12294d)' }}>
      <div className="card" style={{ width: 420, padding: 32 }}>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
          <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--navy)' }}>Anwar Group</div>
          <div style={{ fontSize: 12, color: 'var(--gold)', letterSpacing: 0.5 }}>Task &amp; Project Management</div>
        </div>
        <label>Continue as</label>
        <select value={selected} onChange={(e) => setSelected(e.target.value ? Number(e.target.value) : '')}>
          <option value="">— Select your account —</option>
          {users.map((u) => (
            <option key={u.id} value={u.id}>{u.name} — {label(u.role)}</option>
          ))}
        </select>
        <div className="small muted mt" style={{ marginTop: 8 }}>
          Demo login: no password. Admin is "System Administrator".
        </div>
        {error && <div className="badge red mt">{error}</div>}
        <button className="btn primary" style={{ width: '100%', marginTop: 20 }} onClick={submit} disabled={busy}>
          {busy ? 'Signing in…' : 'Sign In'}
        </button>
      </div>
    </div>
  )
}
