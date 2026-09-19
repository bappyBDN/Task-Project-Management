import { createContext, useContext, useEffect, useState, ReactNode } from 'react'
import { api, setCurrentUserId } from './api'
import { User } from './types'

interface AuthState {
  user: User | null
  loading: boolean
  login: (userId: number) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthState>({
  user: null,
  loading: true,
  login: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const stored = localStorage.getItem('anwar_user_id')
    if (stored) {
      const id = Number(stored)
      setCurrentUserId(id)
      api.get<User>('/organizations/users/me')
        .then(setUser)
        .catch(() => { setCurrentUserId(null); localStorage.removeItem('anwar_user_id') })
        .finally(() => setLoading(false))
    } else {
      setLoading(false)
    }
  }, [])

  const login = async (userId: number) => {
    setCurrentUserId(userId)
    const u = await api.get<User>('/organizations/users/me')
    localStorage.setItem('anwar_user_id', String(userId))
    setUser(u)
  }

  const logout = () => {
    setCurrentUserId(null)
    localStorage.removeItem('anwar_user_id')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
