import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Play, Pencil, Trash2, Clock } from 'lucide-react'
import { schedulesApi } from '@/api/schedules'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorAlert } from '@/components/shared/ErrorAlert'

export function SchedulesList() {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [triggerError, setTriggerError] = useState<string | null>(null)

  const { data: schedules, isLoading, error } = useQuery({
    queryKey: ['schedules'],
    queryFn: () => schedulesApi.list(),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => schedulesApi.delete(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['schedules'] }),
  })

  const triggerMutation = useMutation({
    mutationFn: (id: number) => schedulesApi.trigger(id),
    onSuccess: (data) => {
      setTriggerError(null)
      navigate(`/jobs/${data.job_id}`)
    },
    onError: (err: Error) => setTriggerError(err.message),
  })

  return (
    <div className="space-y-6">
      <Header title="Schedules">
        <Button onClick={() => navigate('/schedules/new')} size="sm">
          <Plus className="mr-1 h-4 w-4" />
          New Schedule
        </Button>
      </Header>

      {(error || triggerError) && (
        <ErrorAlert message={((error as Error) ?? new Error(triggerError!)).message} />
      )}

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-2 p-4">
              {Array.from({ length: 3 }).map((_, i) => (
                <Skeleton key={i} className="h-10 w-full" />
              ))}
            </div>
          ) : !schedules?.length ? (
            <EmptyState
              title="No schedules yet"
              description="Create a schedule to run configs automatically on a cron expression."
            />
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Config ID</TableHead>
                  <TableHead>Cron</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Next Run</TableHead>
                  <TableHead>Last Run</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {schedules.map((s) => (
                  <TableRow key={s.id}>
                    <TableCell className="font-medium">{s.name}</TableCell>
                    <TableCell>{s.config_id}</TableCell>
                    <TableCell>
                      <code className="rounded bg-slate-100 px-1.5 py-0.5 text-xs">
                        {s.cron_expression}
                      </code>
                    </TableCell>
                    <TableCell>
                      <Badge variant={s.is_active ? 'default' : 'secondary'}>
                        {s.is_active ? 'Active' : 'Paused'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {s.next_run_at ? new Date(s.next_run_at).toLocaleString() : '—'}
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {s.last_run_at ? new Date(s.last_run_at).toLocaleString() : '—'}
                    </TableCell>
                    <TableCell className="text-right">
                      <div className="flex items-center justify-end gap-1">
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Run now"
                          onClick={() => triggerMutation.mutate(s.id)}
                          disabled={triggerMutation.isPending}
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Edit"
                          asChild
                        >
                          <Link to={`/schedules/${s.id}/edit`}>
                            <Pencil className="h-4 w-4" />
                          </Link>
                        </Button>
                        <Button
                          variant="ghost"
                          size="icon"
                          title="Delete"
                          onClick={() => {
                            if (confirm(`Delete schedule "${s.name}"?`)) {
                              deleteMutation.mutate(s.id)
                            }
                          }}
                          disabled={deleteMutation.isPending}
                        >
                          <Trash2 className="h-4 w-4 text-red-500" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
