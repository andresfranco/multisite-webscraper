import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useSearchParams } from 'react-router-dom'
import { Search } from 'lucide-react'
import { resultsApi } from '@/api/results'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent } from '@/components/ui/card'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { PageLoading } from '@/components/shared/LoadingSpinner'
import { EmptyState } from '@/components/shared/EmptyState'
import { ErrorAlert } from '@/components/shared/ErrorAlert'
import { Pagination } from '@/components/shared/Pagination'

export function ResultsBrowser() {
  const [searchParams] = useSearchParams()
  const [page, setPage] = useState(1)
  const [jobIdInput, setJobIdInput] = useState(searchParams.get('job_id') ?? '')
  const [configIdInput, setConfigIdInput] = useState('')
  const [appliedJobId, setAppliedJobId] = useState<number | undefined>(
    searchParams.get('job_id') ? Number(searchParams.get('job_id')) : undefined
  )
  const [appliedConfigId, setAppliedConfigId] = useState<number | undefined>(undefined)

  const { data, isLoading, error } = useQuery({
    queryKey: ['results', page, appliedJobId, appliedConfigId],
    queryFn: () =>
      resultsApi.list({
        page,
        page_size: 10,
        job_id: appliedJobId,
        config_id: appliedConfigId,
      }),
  })

  function applyFilters() {
    setAppliedJobId(jobIdInput ? Number(jobIdInput) : undefined)
    setAppliedConfigId(configIdInput ? Number(configIdInput) : undefined)
    setPage(1)
  }

  return (
    <div className="space-y-6">
      <Header title="Results" />

      {error && <ErrorAlert message={(error as Error).message} />}

      {/* Filters */}
      <div className="flex items-end gap-3">
        <div className="space-y-1">
          <label className="text-xs font-medium text-muted-foreground">Job ID</label>
          <Input
            value={jobIdInput}
            onChange={(e) => setJobIdInput(e.target.value)}
            placeholder="Filter by job ID"
            className="w-40"
          />
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium text-muted-foreground">Config ID</label>
          <Input
            value={configIdInput}
            onChange={(e) => setConfigIdInput(e.target.value)}
            placeholder="Filter by config ID"
            className="w-40"
          />
        </div>
        <Button onClick={applyFilters} size="sm">
          <Search className="mr-1 h-4 w-4" />
          Apply Filters
        </Button>
      </div>

      {isLoading ? (
        <PageLoading />
      ) : (
        <Card>
          <CardContent className="p-0">
            {!data?.items.length ? (
              <EmptyState
                title="No results found"
                description="No scraped results match the current filters."
              />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>ID</TableHead>
                    <TableHead>Job ID</TableHead>
                    <TableHead>Config ID</TableHead>
                    <TableHead>Source URL</TableHead>
                    <TableHead>Scraped At</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.items.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell className="font-mono text-xs">#{item.id}</TableCell>
                      <TableCell>{item.job_id}</TableCell>
                      <TableCell>{item.config_id}</TableCell>
                      <TableCell className="max-w-xs">
                        <span
                          className="block truncate text-sm text-muted-foreground"
                          title={item.source_url}
                        >
                          {item.source_url.length > 50
                            ? `${item.source_url.slice(0, 50)}…`
                            : item.source_url}
                        </span>
                      </TableCell>
                      <TableCell className="text-sm text-muted-foreground">
                        {new Date(item.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/results/${item.id}`}>View</Link>
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

      {data && (
        <Pagination page={data.page} pages={data.pages} onPageChange={setPage} />
      )}
    </div>
  )
}
