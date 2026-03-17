import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { configsApi } from '@/api/configs'
import { Header } from '@/components/layout/Header'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
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

const PAGE_SIZE = 10

export function ConfigsList() {
  const navigate = useNavigate()
  const [page, setPage] = useState(1)

  const offset = (page - 1) * PAGE_SIZE

  const { data: configs, isLoading, error } = useQuery({
    queryKey: ['configs', page],
    queryFn: () => configsApi.list({ offset, limit: PAGE_SIZE }),
  })

  const totalPages = configs ? Math.ceil(configs.length / PAGE_SIZE) : 1

  return (
    <div className="space-y-6">
      <Header title="Configurations">
        <Button size="sm" onClick={() => navigate('/configs/new')}>
          <Plus className="mr-1 h-4 w-4" />
          New Config
        </Button>
      </Header>

      {error && <ErrorAlert message={(error as Error).message} />}

      {isLoading ? (
        <PageLoading />
      ) : (
        <Card>
          <CardContent className="p-0">
            {!configs?.length ? (
              <EmptyState
                title="No configurations yet"
                description="Create your first scrape configuration to get started."
                action={
                  <Button asChild>
                    <Link to="/configs/new">
                      <Plus className="mr-1 h-4 w-4" />
                      New Config
                    </Link>
                  </Button>
                }
              />
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Name</TableHead>
                    <TableHead>Base URL</TableHead>
                    <TableHead>Fields</TableHead>
                    <TableHead>Active</TableHead>
                    <TableHead>Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {configs.map((config) => (
                    <TableRow key={config.id}>
                      <TableCell className="font-medium">{config.name}</TableCell>
                      <TableCell className="max-w-xs truncate text-sm text-muted-foreground">
                        {config.base_url}
                      </TableCell>
                      <TableCell>{config.fields.length}</TableCell>
                      <TableCell>
                        <Badge variant={config.is_active ? 'default' : 'secondary'}>
                          {config.is_active ? 'Active' : 'Inactive'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Button variant="ghost" size="sm" asChild>
                          <Link to={`/configs/${config.id}`}>View</Link>
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

      {/* Simple pagination */}
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
