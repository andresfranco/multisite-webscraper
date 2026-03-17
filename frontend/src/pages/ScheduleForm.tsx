import { useState, type FormEvent, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { schedulesApi, type ScheduleCreateRequest, type ScheduleUpdateRequest } from '@/api/schedules'
import { configsApi } from '@/api/configs'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent } from '@/components/ui/card'
import { ErrorAlert } from '@/components/shared/ErrorAlert'
import { LoadingSpinner } from '@/components/shared/LoadingSpinner'

// ── Helpers ────────────────────────────────────────────────────────────────

const CRON_EXAMPLES = [
  { label: 'Every hour', value: '0 * * * *' },
  { label: 'Every day at 6 am', value: '0 6 * * *' },
  { label: 'Every Monday at 9 am', value: '0 9 * * 1' },
  { label: 'Every 15 minutes', value: '*/15 * * * *' },
]

// ── Component ─────────────────────────────────────────────────────────────

export function ScheduleForm() {
  const { id } = useParams<{ id?: string }>()
  const isEdit = Boolean(id)
  const scheduleId = id ? Number(id) : undefined
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const [name, setName] = useState('')
  const [configId, setConfigId] = useState<number | ''>('')
  const [cron, setCron] = useState('0 6 * * *')
  const [isActive, setIsActive] = useState(true)
  const [submitError, setSubmitError] = useState<string | null>(null)

  // Load existing schedule when editing
  const { data: existing, isLoading: loadingSchedule } = useQuery({
    queryKey: ['schedule', scheduleId],
    queryFn: () => schedulesApi.get(scheduleId!),
    enabled: isEdit && !!scheduleId,
  })

  useEffect(() => {
    if (existing) {
      setName(existing.name)
      setConfigId(existing.config_id)
      setCron(existing.cron_expression)
      setIsActive(existing.is_active)
    }
  }, [existing])

  // Load configs for the dropdown
  const { data: configs, isLoading: loadingConfigs } = useQuery({
    queryKey: ['configs'],
    queryFn: () => configsApi.list(),
  })

  const createMutation = useMutation({
    mutationFn: (data: ScheduleCreateRequest) => schedulesApi.create(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      navigate('/schedules')
    },
    onError: (err: Error) => setSubmitError(err.message),
  })

  const updateMutation = useMutation({
    mutationFn: (data: ScheduleUpdateRequest) => schedulesApi.update(scheduleId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['schedules'] })
      navigate('/schedules')
    },
    onError: (err: Error) => setSubmitError(err.message),
  })

  const isPending = createMutation.isPending || updateMutation.isPending

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitError(null)
    if (!configId) {
      setSubmitError('Please select a config.')
      return
    }
    if (isEdit) {
      updateMutation.mutate({ name, cron_expression: cron, is_active: isActive })
    } else {
      createMutation.mutate({
        name,
        config_id: Number(configId),
        cron_expression: cron,
        is_active: isActive,
      })
    }
  }

  if (isEdit && loadingSchedule) {
    return (
      <div className="flex justify-center py-16">
        <LoadingSpinner />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <Header title={isEdit ? 'Edit Schedule' : 'New Schedule'} />

      <Card className="mx-auto max-w-xl">
        <CardContent className="pt-6">
          {submitError && <ErrorAlert message={submitError} className="mb-4" />}

          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Name */}
            <div className="space-y-1">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                required
                minLength={1}
                maxLength={255}
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isPending}
                placeholder="Daily product scrape"
              />
            </div>

            {/* Config */}
            {!isEdit && (
              <div className="space-y-1">
                <Label htmlFor="config">Config</Label>
                {loadingConfigs ? (
                  <p className="text-sm text-muted-foreground">Loading configs…</p>
                ) : (
                  <select
                    id="config"
                    required
                    className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                    value={configId}
                    onChange={(e) => setConfigId(Number(e.target.value))}
                    disabled={isPending}
                  >
                    <option value="">Select a config…</option>
                    {configs?.map((c) => (
                      <option key={c.id} value={c.id}>
                        {c.name} — {c.base_url}
                      </option>
                    ))}
                  </select>
                )}
              </div>
            )}

            {/* Cron expression */}
            <div className="space-y-1">
              <Label htmlFor="cron">Cron expression</Label>
              <Input
                id="cron"
                required
                value={cron}
                onChange={(e) => setCron(e.target.value)}
                disabled={isPending}
                placeholder="0 6 * * *"
                className="font-mono"
              />
              <div className="flex flex-wrap gap-1 pt-1">
                {CRON_EXAMPLES.map((ex) => (
                  <button
                    key={ex.value}
                    type="button"
                    onClick={() => setCron(ex.value)}
                    className="rounded border border-slate-200 bg-slate-50 px-2 py-0.5 text-xs text-slate-600 hover:bg-slate-100"
                  >
                    {ex.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Active toggle */}
            <div className="flex items-center gap-3">
              <Switch
                id="active"
                checked={isActive}
                onCheckedChange={setIsActive}
                disabled={isPending}
              />
              <Label htmlFor="active">Active</Label>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-2">
              <Button type="submit" disabled={isPending}>
                {isPending ? 'Saving…' : isEdit ? 'Save changes' : 'Create schedule'}
              </Button>
              <Button
                type="button"
                variant="outline"
                onClick={() => navigate('/schedules')}
                disabled={isPending}
              >
                Cancel
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
