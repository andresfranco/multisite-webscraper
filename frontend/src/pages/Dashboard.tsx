import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Settings2, Play, Database, Plus, ArrowRight } from 'lucide-react'
import { configsApi } from '@/api/configs'
import { jobsApi } from '@/api/jobs'
import { resultsApi } from '@/api/results'
import { Header } from '@/components/layout/Header'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorAlert } from '@/components/shared/ErrorAlert'

function StatCard({
  title,
  icon: Icon,
  value,
  loading,
}: {
  title: string
  icon: React.ElementType
  value: number | undefined
  loading: boolean
}) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        {loading ? (
          <Skeleton className="h-8 w-16" />
        ) : (
          <p className="text-3xl font-bold">{value ?? 0}</p>
        )}
      </CardContent>
    </Card>
  )
}

export function Dashboard() {
  const navigate = useNavigate()

  const { data: configs, isLoading: configsLoading, error: configsError } = useQuery({
    queryKey: ['configs-count'],
    queryFn: () => configsApi.list(),
  })

  const { data: allJobs, isLoading: jobsLoading, error: jobsError } = useQuery({
    queryKey: ['jobs-recent'],
    queryFn: () => jobsApi.list({ limit: 5 }),
  })

  const { data: activeJobs, isLoading: activeLoading } = useQuery({
    queryKey: ['jobs-active'],
    queryFn: () => jobsApi.list({ status: 'running' }),
  })

  const { data: results, isLoading: resultsLoading, error: resultsError } = useQuery({
    queryKey: ['results-count'],
    queryFn: () => resultsApi.list({ page: 1, page_size: 1 }),
  })

  const anyError = configsError || jobsError || resultsError

  return (
    <div className="space-y-6">
      <Header title="Dashboard">
        <Button onClick={() => navigate('/configs/new')} size="sm">
          <Plus className="mr-1 h-4 w-4" />
          New Config
        </Button>
      </Header>

      {anyError && (
        <ErrorAlert message={(anyError as Error).message} />
      )}

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <StatCard
          title="Total Configs"
          icon={Settings2}
          value={configs?.length}
          loading={configsLoading}
        />
        <StatCard
          title="Total Jobs"
          icon={Play}
          value={allJobs?.length}
          loading={jobsLoading}
        />
        <StatCard
          title="Total Results"
          icon={Database}
          value={results?.total}
          loading={resultsLoading}
        />
        <StatCard
          title="Active Jobs"
          icon={LayoutDashboard}
          value={activeJobs?.length}
          loading={activeLoading}
        />
      </div>

      {/* Recent Jobs */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Recent Jobs</CardTitle>
          <Button variant="ghost" size="sm" asChild>
            <Link to="/jobs">
              View All <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
          </Button>
        </CardHeader>
        <CardContent>
          {jobsLoading ? (
            <div className="space-y-2">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !allJobs?.length ? (
            <EmptyState title="No jobs yet" description="Run a config to create your first job." />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Job ID</TableHead>
                  <TableHead>Config ID</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Created At</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {allJobs.map((job) => (
                  <TableRow key={job.id}>
                    <TableCell className="font-mono text-xs">#{job.id}</TableCell>
                    <TableCell>{job.config_id}</TableCell>
                    <TableCell>
                      <StatusBadge status={job.status} />
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {new Date(job.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm" asChild>
                        <Link to={`/jobs/${job.id}`}>View</Link>
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <div className="flex gap-3">
        <Button asChild>
          <Link to="/configs/new">
            <Plus className="mr-1 h-4 w-4" />
            New Config
          </Link>
        </Button>
        <Button variant="outline" asChild>
          <Link to="/jobs">View All Jobs</Link>
        </Button>
      </div>
    </div>
  )
}
