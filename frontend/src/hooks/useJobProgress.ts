import { useQuery } from '@tanstack/react-query'
import { jobsApi } from '@/api/jobs'
import type { JobStatus } from '@/types'

const DONE_STATUSES: JobStatus[] = ['completed', 'failed', 'cancelled']

export function useJobProgress(jobId: number | undefined) {
  return useQuery({
    queryKey: ['job-progress', jobId],
    queryFn: () => jobsApi.get(jobId!),
    enabled: jobId !== undefined,
    staleTime: 0,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      if (!status || DONE_STATUSES.includes(status)) return false
      return 2000
    },
  })
}
