import { useParams, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, XCircle } from 'lucide-react'
import { jobsApi } from '@/api/jobs'
import { useJobProgress } from '@/hooks/useJobProgress'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { StatusBadge } from '@/components/shared/StatusBadge'
import { PageLoading } from '@/components/shared/LoadingSpinner'
import { ErrorAlert } from '@/components/shared/ErrorAlert'

export function JobDetail() {
  const { id } = useParams<{ id: string }>()
  const jobId = Number(id)
  const queryClient = useQueryClient()

  const { data: job, isLoading, error } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsApi.get(jobId),
    enabled: !isNaN(jobId),
  })

  // Live polling (reuses jobsApi.get under the hood)
  const { data: liveJob } = useJobProgress(isNaN(jobId) ? undefined : jobId)

  // Prefer live data when available
  const displayJob = liveJob ?? job

  const cancelMutation = useMutation({
    mutationFn: () => jobsApi.cancel(jobId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', jobId] })
      queryClient.invalidateQueries({ queryKey: ['job-progress', jobId] })
    },
  })

  if (isLoading) return <PageLoading />
  if (error) return <ErrorAlert message={(error as Error).message} />
  if (!displayJob) return null

  const canCancel = displayJob.status === 'pending' || displayJob.status === 'running'
  const totalItems = displayJob.items_found > 0 ? displayJob.items_found : 1
  const progressPct = Math.round((displayJob.items_created / totalItems) * 100)

  return (
    <div className="space-y-6">
      <Header title={`Job #${jobId}`}>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/jobs">
              <ArrowLeft className="mr-1 h-4 w-4" />
              Back
            </Link>
          </Button>
          {canCancel && (
            <Button
              variant="destructive"
              size="sm"
              onClick={() => cancelMutation.mutate()}
              disabled={cancelMutation.isPending}
            >
              <XCircle className="mr-1 h-4 w-4" />
              {cancelMutation.isPending ? 'Cancelling…' : 'Cancel Job'}
            </Button>
          )}
          <Button variant="outline" size="sm" asChild>
            <Link to={`/results?job_id=${jobId}`}>View Results</Link>
          </Button>
        </div>
      </Header>

      {cancelMutation.isError && (
        <ErrorAlert message={(cancelMutation.error as Error).message} />
      )}

      {/* Job info */}
      <Card>
        <CardHeader>
          <CardTitle>Job Details</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-xs font-medium text-muted-foreground">Config ID</p>
            <Link
              to={`/configs/${displayJob.config_id}`}
              className="mt-0.5 font-medium text-blue-600 hover:underline"
            >
              {displayJob.config_id}
            </Link>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Status</p>
            <div className="mt-0.5">
              <StatusBadge status={displayJob.status} />
            </div>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Created At</p>
            <p className="mt-0.5 text-sm">{new Date(displayJob.created_at).toLocaleString()}</p>
          </div>
          {displayJob.started_at && (
            <div>
              <p className="text-xs font-medium text-muted-foreground">Started At</p>
              <p className="mt-0.5 text-sm">
                {new Date(displayJob.started_at).toLocaleString()}
              </p>
            </div>
          )}
          {displayJob.completed_at && (
            <div>
              <p className="text-xs font-medium text-muted-foreground">Completed At</p>
              <p className="mt-0.5 text-sm">
                {new Date(displayJob.completed_at).toLocaleString()}
              </p>
            </div>
          )}
          {displayJob.celery_task_id && (
            <div>
              <p className="text-xs font-medium text-muted-foreground">Task ID</p>
              <p className="mt-0.5 font-mono text-xs text-muted-foreground">
                {displayJob.celery_task_id}
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Progress */}
      <Card>
        <CardHeader>
          <CardTitle>Progress</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <Progress value={progressPct} className="h-3" />
          <div className="grid grid-cols-4 gap-4 text-center">
            <div>
              <p className="text-2xl font-bold">{displayJob.pages_scraped}</p>
              <p className="text-xs text-muted-foreground">Pages Scraped</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{displayJob.items_found}</p>
              <p className="text-xs text-muted-foreground">Items Found</p>
            </div>
            <div>
              <p className="text-2xl font-bold">{displayJob.items_created}</p>
              <p className="text-xs text-muted-foreground">Items Created</p>
            </div>
            <div>
              <p className={`text-2xl font-bold ${displayJob.errors > 0 ? 'text-red-500' : ''}`}>
                {displayJob.errors}
              </p>
              <p className="text-xs text-muted-foreground">Errors</p>
            </div>
          </div>
          {displayJob.error_message && (
            <div className="rounded border border-red-200 bg-red-50 p-3">
              <p className="text-xs font-medium text-red-700">Error</p>
              <p className="mt-1 text-sm text-red-600">{displayJob.error_message}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
