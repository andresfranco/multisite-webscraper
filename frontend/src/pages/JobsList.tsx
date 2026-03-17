import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { jobsApi } from '@/api/jobs'
import type { JobStatus } from '@/types'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { PageLoading } from '@/components/shared/LoadingSpinner'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorAlert } from '@/components/shared/ErrorAlert'
import { cn } from '@/lib/utils'

const STATUS_FILTERS: Array<{ label: string; value: JobStatus | undefined }> = [
  { label: 'All', value: undefined },
  { label: 'Pending', value: 'pending' },
  { label: 'Running', value: 'running' },
  { label: 'Completed', value: 'completed' },
  { label: 'Failed', value: 'failed' },
  { label: 'Cancelled', value: 'cancelled' },
]

const PAGE_SIZE = 10

export function JobsList() {
  const [page, setPage] = useState(1)
  const [statusFilter, setStatusFilter] = useState<JobStatus | undefined>(undefined)

  const offset = (page - 1) * PAGE_SIZE

  const { data: jobs, isLoading, error } = useQuery({
    queryKey: ['jobs', page, statusFilter],
    queryFn: () => jobsApi.list({ offset, limit: PAGE_SIZE, status: statusFilter }),
    refetchInterval: (query) => {
      const data = query.state.data
      if (data?.some((j) => j.status === 'running' || j.status === 'pending')) return 3000
      return false
    },
  })

  const totalPages = jobs ? Math.ceil(jobs.length / PAGE_SIZE) : 1

  return (
    <div className="space-y-6">
      <Header title="Jobs" />

      {error && <ErrorAlert message={(error as Error).message} />}

      {/* Status filter */}
      <div className="flex flex-wrap gap-2">
        {STATUS_FILTERS.map((f) => (
          <Button
            key={f.label}
            variant={statusFilter === f.value ? 'default' : 'outline'}
            size="sm"
            onClick={() => {
              setStatusFilter(f.value)
              setPage(1)
            }}
            className={cn(
              statusFilter === f.value ? '' : 'text-muted-foreground'
            )}
          >
            {f.label}
          </Button>
        ))}
      </div>

      {isLoading ? (
        <PageLoading />
      ) : (
        <Card>
          <CardContent className="p-0">
            {!jobs?.length ? (
              <EmptyState
                title="No jobs found"
                description={
                  statusFilter
                    ? `No jobs with status "${statusFilter}".`
                    : 'No jobs have been created yet.'
                }
              />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Job ID</TableHead>
                    <TableHead>Config ID</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Pages</TableHead>
                    <TableHead>Items Found</TableHead>
                    <TableHead>Errors</TableHead>
                    <TableHead>Created At</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell className="font-mono text-xs">#{job.id}</TableCell>
                      <TableCell>{job.config_id}</TableCell>
                      <TableCell>
                        <StatusBadge status={job.status} />
                      </TableCell>
                      <TableCell>{job.pages_scraped}</TableCell>
                      <TableCell>{job.items_found}</TableCell>
                      <TableCell className={job.errors > 0 ? 'text-red-500' : ''}>
                        {job.errors}
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
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-end gap-2">
          <Button
            variant="outline"
            size="sm"
            disabled={page <= 1}
            onClick={() => setPage((p) => p - 1)}
          >
            Previous
          </Button>
          <span className="text-sm text-muted-foreground">
            Page {page} of {totalPages}
          </span>
          <Button
            variant="outline"
            size="sm"
            disabled={page >= totalPages}
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </Button>
        </div>
      )}
    </div>
  )
}
