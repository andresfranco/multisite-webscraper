import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard,
  Settings2,
  Play,
  Database,
  Download,
  Globe,
  CalendarClock,
  LogOut,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useAuth } from '@/context/AuthContext'

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard, end: true },
  { to: '/configs', label: 'Configs', icon: Settings2 },
  { to: '/jobs', label: 'Jobs', icon: Play },
  { to: '/results', label: 'Results', icon: Database },
  { to: '/schedules', label: 'Schedules', icon: CalendarClock },
  { to: '/export', label: 'Export', icon: Download },
]

export function Sidebar() {
  const { user, logout } = useAuth()

  return (
    <aside className="flex h-screen w-56 flex-shrink-0 flex-col bg-slate-900">
      {/* Logo */}
      <div className="flex items-center gap-2 px-4 py-5">
        <Globe className="h-6 w-6 text-blue-400" />
        <span className="text-lg font-bold text-white">WebScraper</span>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-3 py-2">
        {navItems.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                isActive
                  ? 'bg-slate-700 text-white'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-white'
              )
            }
          >
            <Icon className="h-4 w-4" />
            {label}
          </NavLink>
        ))}
      </nav>

      {/* User / Logout */}
      {user && (
        <div className="border-t border-slate-700 px-4 py-3">
          <p className="truncate text-xs font-medium text-slate-300">{user.username}</p>
          <p className="truncate text-xs text-slate-500">{user.email}</p>
          <button
            onClick={logout}
            className="mt-2 flex items-center gap-2 text-xs text-slate-400 hover:text-white"
          >
            <LogOut className="h-3.5 w-3.5" />
            Sign out
          </button>
        </div>
      )}
    </aside>
  )
}
