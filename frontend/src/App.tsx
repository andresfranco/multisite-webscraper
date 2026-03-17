import { Routes, Route, Navigate } from 'react-router-dom'
import { Layout } from '@/components/layout/Layout'
import { ProtectedRoute } from '@/components/auth/ProtectedRoute'
import { Login } from '@/pages/Login'
import { Register } from '@/pages/Register'
import { Dashboard } from '@/pages/Dashboard'
import { ConfigsList } from '@/pages/ConfigsList'
import { ConfigBuilder } from '@/pages/ConfigBuilder'
import { ConfigDetail } from '@/pages/ConfigDetail'
import { JobsList } from '@/pages/JobsList'
import { JobDetail } from '@/pages/JobDetail'
import { ResultsBrowser } from '@/pages/ResultsBrowser'
import { ResultDetail } from '@/pages/ResultDetail'
import { Export } from '@/pages/Export'
import { SchedulesList } from '@/pages/SchedulesList'
import { ScheduleForm } from '@/pages/ScheduleForm'

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      {/* Protected routes */}
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="configs" element={<ConfigsList />} />
        <Route path="configs/new" element={<ConfigBuilder />} />
        <Route path="configs/:id" element={<ConfigDetail />} />
        <Route path="jobs" element={<JobsList />} />
        <Route path="jobs/:id" element={<JobDetail />} />
        <Route path="results" element={<ResultsBrowser />} />
        <Route path="results/:id" element={<ResultDetail />} />
        <Route path="export" element={<Export />} />
        <Route path="schedules" element={<SchedulesList />} />
        <Route path="schedules/new" element={<ScheduleForm />} />
        <Route path="schedules/:id/edit" element={<ScheduleForm />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  )
}
