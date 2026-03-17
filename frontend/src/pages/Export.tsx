import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Download } from 'lucide-react'
import { resultsApi } from '@/api/results'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorAlert } from '@/components/shared/ErrorAlert'

export function Export() {
  const [jobId, setJobId] = useState('')
  const [configId, setConfigId] = useState('')
  const [format, setFormat] = useState<'json' | 'csv'>('json')

  const { data: stats, isLoading: statsLoading, error: statsError } = useQuery({
    queryKey: ['result-stats'],
    queryFn: () => resultsApi.stats(),
  })

  function handleDownload() {
    const url = resultsApi.exportUrl({
      format,
      job_id: jobId ? Number(jobId) : undefined,
      config_id: configId ? Number(configId) : undefined,
    })
    window.open(url, '_blank')
  }

  return (
    <div className="space-y-6">
      <Header title="Export" />

      <div className="grid grid-cols-2 gap-6">
        {/* Export form */}
        <Card>
          <CardHeader>
            <CardTitle>Export Results</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-1">
              <Label htmlFor="export-job-id">Job ID (optional)</Label>
              <Input
                id="export-job-id"
                value={jobId}
                onChange={(e) => setJobId(e.target.value)}
                placeholder="Leave empty for all jobs"
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="export-config-id">Config ID (optional)</Label>
              <Input
                id="export-config-id"
                value={configId}
                onChange={(e) => setConfigId(e.target.value)}
                placeholder="Leave empty for all configs"
              />
            </div>
            <div className="space-y-1">
              <Label>Format</Label>
              <Select value={format} onValueChange={(v) => setFormat(v as 'json' | 'csv')}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="json">JSON</SelectItem>
                  <SelectItem value="csv">CSV</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <p className="text-xs text-muted-foreground">
              Leave filters empty to export all results.
            </p>
            <Button onClick={handleDownload} className="w-full">
              <Download className="mr-2 h-4 w-4" />
              Download {format.toUpperCase()}
            </Button>
          </CardContent>
        </Card>

        {/* Stats */}
        <Card>
          <CardHeader>
            <CardTitle>Result Statistics</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {statsError && <ErrorAlert message={(statsError as Error).message} />}

            {statsLoading ? (
              <div className="space-y-3">
                <Skeleton className="h-6 w-32" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
              </div>
            ) : stats ? (
              <>
                <div className="grid grid-cols-3 gap-3 text-center">
                  <div className="rounded border bg-muted/30 p-3">
                    <p className="text-2xl font-bold">{stats.total_items}</p>
                    <p className="text-xs text-muted-foreground">Total Items</p>
                  </div>
                  <div className="rounded border bg-muted/30 p-3">
                    <p className="text-2xl font-bold">{stats.total_jobs}</p>
                    <p className="text-xs text-muted-foreground">Total Jobs</p>
                  </div>
                  <div className="rounded border bg-muted/30 p-3">
                    <p className="text-2xl font-bold">{stats.total_configs}</p>
                    <p className="text-xs text-muted-foreground">Total Configs</p>
                  </div>
                </div>

                {Object.keys(stats.items_by_domain).length > 0 && (
                  <div>
                    <p className="mb-2 text-sm font-medium">Items by Domain</p>
                    <div className="divide-y rounded border">
                      {Object.entries(stats.items_by_domain).map(([domain, count]) => (
                        <div key={domain} className="flex items-center justify-between px-3 py-1.5">
                          <span className="text-sm">{domain}</span>
                          <span className="text-sm font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {Object.keys(stats.jobs_by_status).length > 0 && (
                  <div>
                    <p className="mb-2 text-sm font-medium">Jobs by Status</p>
                    <div className="divide-y rounded border">
                      {Object.entries(stats.jobs_by_status).map(([status, count]) => (
                        <div key={status} className="flex items-center justify-between px-3 py-1.5">
                          <span className="text-sm capitalize">{status}</span>
                          <span className="text-sm font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
