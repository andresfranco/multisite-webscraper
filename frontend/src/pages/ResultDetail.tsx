import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery, useMutation } from '@tanstack/react-query'
import { ArrowLeft, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { resultsApi } from '@/api/results'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
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

function renderValue(value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (Array.isArray(value)) return value.join(', ')
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

export function ResultDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const resultId = Number(id)
  const [deleteOpen, setDeleteOpen] = useState(false)

  const { data: result, isLoading, error } = useQuery({
    queryKey: ['result', resultId],
    queryFn: () => resultsApi.get(resultId),
    enabled: !isNaN(resultId),
  })

  const deleteMutation = useMutation({
    mutationFn: () => resultsApi.delete(resultId),
    onSuccess: () => navigate('/results'),
  })

  if (isLoading) return <PageLoading />
  if (error) return <ErrorAlert message={(error as Error).message} />
  if (!result) return null

  return (
    <div className="space-y-6">
      <Header title="Result Detail">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link to="/results">
              <ArrowLeft className="mr-1 h-4 w-4" />
              Back
            </Link>
          </Button>
          <Button variant="destructive" size="sm" onClick={() => setDeleteOpen(true)}>
            <Trash2 className="mr-1 h-4 w-4" />
            Delete
          </Button>
        </div>
      </Header>

      {deleteMutation.isError && (
        <ErrorAlert message={(deleteMutation.error as Error).message} />
      )}

      {/* Metadata */}
      <Card>
        <CardHeader>
          <CardTitle>Metadata</CardTitle>
        </CardHeader>
        <CardContent className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-medium text-muted-foreground">ID</p>
            <p className="mt-0.5 font-mono text-sm">#{result.id}</p>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Job ID</p>
            <Link
              to={`/jobs/${result.job_id}`}
              className="mt-0.5 block font-medium text-blue-600 hover:underline"
            >
              #{result.job_id}
            </Link>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Config ID</p>
            <Link
              to={`/configs/${result.config_id}`}
              className="mt-0.5 block font-medium text-blue-600 hover:underline"
            >
              #{result.config_id}
            </Link>
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground">Scraped At</p>
            <p className="mt-0.5 text-sm">{new Date(result.created_at).toLocaleString()}</p>
          </div>
          <div className="col-span-2">
            <p className="text-xs font-medium text-muted-foreground">Source URL</p>
            <a
              href={result.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-0.5 block break-all text-sm text-blue-600 hover:underline"
            >
              {result.source_url}
            </a>
          </div>
          {result.item_url && (
            <div className="col-span-2">
              <p className="text-xs font-medium text-muted-foreground">Item URL</p>
              <a
                href={result.item_url}
                target="_blank"
                rel="noopener noreferrer"
                className="mt-0.5 block break-all text-sm text-blue-600 hover:underline"
              >
                {result.item_url}
              </a>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Scraped Data */}
      <Card>
        <CardHeader>
          <CardTitle>Scraped Data</CardTitle>
        </CardHeader>
        <CardContent>
          {Object.keys(result.data).length === 0 ? (
            <p className="text-sm text-muted-foreground">No data fields.</p>
          ) : (
            <div className="divide-y rounded border">
              {Object.entries(result.data).map(([key, value]) => (
                <div key={key} className="flex gap-4 px-3 py-2">
                  <span className="w-40 flex-shrink-0 font-mono text-xs font-medium text-muted-foreground">
                    {key}
                  </span>
                  <span className="flex-1 break-all text-sm">{renderValue(value)}</span>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Delete dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Result</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            Are you sure you want to delete result <strong>#{result.id}</strong>? This cannot be
            undone.
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
