import { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ArrowLeft, Play, Trash2, Edit, X, Check } from 'lucide-react'
import { configsApi } from '@/api/configs'
import { jobsApi } from '@/api/jobs'
import type { ScrapeConfigUpdate } from '@/types'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { PageLoading } from '@/components/shared/LoadingSpinner'
import { ErrorAlert } from '@/components/shared/ErrorAlert'

export function ConfigDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const configId = Number(id)

  const [editing, setEditing] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)

  // Edit form state
  const [editName, setEditName] = useState('')
  const [editBaseUrl, setEditBaseUrl] = useState('')
  const [editItemSelector, setEditItemSelector] = useState('')
  const [editMaxPages, setEditMaxPages] = useState(100)
  const [editIsActive, setEditIsActive] = useState(true)

  const { data: config, isLoading, error } = useQuery({
    queryKey: ['config', configId],
    queryFn: () => configsApi.get(configId),
    enabled: !isNaN(configId),
  })

  useEffect(() => {
    if (config) {
      setEditName(config.name)
      setEditBaseUrl(config.base_url)
      setEditItemSelector(config.item_selector)
      setEditMaxPages(config.max_pages)
      setEditIsActive(config.is_active)
    }
  }, [config])

  const updateMutation = useMutation({
    mutationFn: (payload: ScrapeConfigUpdate) => configsApi.update(configId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['config', configId] })
      setEditing(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: () => configsApi.delete(configId),
    onSuccess: () => navigate('/configs'),
  })

  const runJobMutation = useMutation({
    mutationFn: () => jobsApi.create({ config_id: configId }),
    onSuccess: (job) => navigate(`/jobs/${job.id}`),
  })

  function handleSave() {
    updateMutation.mutate({
      name: editName,
      base_url: editBaseUrl,
      item_selector: editItemSelector,
      max_pages: editMaxPages,
      is_active: editIsActive,
    })
  }

  if (isLoading) return <PageLoading />
  if (error) return <ErrorAlert message={(error as Error).message} />
  if (!config) return null

  return (
    <div className="space-y-6">
      <Header title={editing ? 'Edit Configuration' : config.name}>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/configs">
              <ArrowLeft className="mr-1 h-4 w-4" />
              Back
            </Link>
          </Button>
          {!editing && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setEditing(true)}
              >
                <Edit className="mr-1 h-4 w-4" />
                Edit
              </Button>
              <Button
                size="sm"
                onClick={() => runJobMutation.mutate()}
                disabled={runJobMutation.isPending}
              >
                <Play className="mr-1 h-4 w-4" />
                {runJobMutation.isPending ? 'Starting…' : 'Run Job'}
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => setDeleteOpen(true)}
              >
                <Trash2 className="mr-1 h-4 w-4" />
                Delete
              </Button>
            </>
          )}
          {editing && (
            <>
              <Button size="sm" onClick={handleSave} disabled={updateMutation.isPending}>
                <Check className="mr-1 h-4 w-4" />
                {updateMutation.isPending ? 'Saving…' : 'Save'}
              </Button>
              <Button variant="outline" size="sm" onClick={() => setEditing(false)}>
                <X className="mr-1 h-4 w-4" />
                Cancel
              </Button>
            </>
          )}
        </div>
      </Header>

      {(updateMutation.isError || runJobMutation.isError) && (
        <ErrorAlert
          message={
            ((updateMutation.error || runJobMutation.error) as Error).message
          }
        />
      )}

      <Card>
        <CardHeader>
          <CardTitle>Configuration Details</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          {editing ? (
            <>
              <div className="space-y-1">
                <Label>Name</Label>
                <Input value={editName} onChange={(e) => setEditName(e.target.value)} />
              </div>
              <div className="space-y-1">
                <Label>Base URL</Label>
                <Input value={editBaseUrl} onChange={(e) => setEditBaseUrl(e.target.value)} />
              </div>
              <div className="space-y-1">
                <Label>Item Selector</Label>
                <Input
                  value={editItemSelector}
                  onChange={(e) => setEditItemSelector(e.target.value)}
                />
              </div>
              <div className="space-y-1">
                <Label>Max Pages</Label>
                <Input
                  type="number"
                  value={editMaxPages}
                  onChange={(e) => setEditMaxPages(Number(e.target.value))}
                />
              </div>
              <div className="flex items-center gap-2 pt-4">
                <Switch
                  id="edit-active"
                  checked={editIsActive}
                  onCheckedChange={setEditIsActive}
                />
                <Label htmlFor="edit-active">Active</Label>
              </div>
            </>
          ) : (
            <>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Name</p>
                <p className="mt-0.5">{config.name}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Base URL</p>
                <p className="mt-0.5 break-all text-sm">{config.base_url}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Domain</p>
                <p className="mt-0.5">{config.domain}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Item Selector</p>
                <p className="mt-0.5 font-mono text-sm">{config.item_selector}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Max Pages</p>
                <p className="mt-0.5">{config.max_pages}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Request Delay</p>
                <p className="mt-0.5">{config.request_delay_ms} ms</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Status</p>
                <Badge
                  variant={config.is_active ? 'default' : 'secondary'}
                  className="mt-0.5"
                >
                  {config.is_active ? 'Active' : 'Inactive'}
                </Badge>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Headless Browser</p>
                <p className="mt-0.5">{config.use_headless_browser ? 'Yes' : 'No'}</p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Created At</p>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {new Date(config.created_at).toLocaleString()}
                </p>
              </div>
              <div>
                <p className="text-xs font-medium text-muted-foreground">Updated At</p>
                <p className="mt-0.5 text-sm text-muted-foreground">
                  {new Date(config.updated_at).toLocaleString()}
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      {/* Fields */}
      {!editing && (
        <Card>
          <CardHeader>
            <CardTitle>Fields ({config.fields.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {config.fields.length === 0 ? (
              <p className="text-sm text-muted-foreground">No fields defined.</p>
            ) : (
              <div className="space-y-2">
                {config.fields.map((field, i) => (
                  <div
                    key={i}
                    className="flex items-center gap-4 rounded border bg-muted/30 px-3 py-2 text-sm"
                  >
                    <span className="font-medium">{field.name}</span>
                    <span className="font-mono text-muted-foreground">{field.selector}</span>
                    {field.attribute && (
                      <span className="text-xs text-blue-600">attr: {field.attribute}</span>
                    )}
                    {field.required && (
                      <Badge variant="outline" className="text-xs">
                        required
                      </Badge>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Delete dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Configuration</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Are you sure you want to delete <strong>{config.name}</strong>? This action cannot
            be undone.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={() => deleteMutation.mutate()}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Deleting…' : 'Delete'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
