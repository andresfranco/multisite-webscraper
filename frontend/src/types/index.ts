// ── Field & Config ──────────────────────────────────────────────────────────

export interface FieldConfig {
  name: string
  selector: string
  attribute: string | null
  transform: string | null
  required: boolean
  default_value: string | null
}

export type PaginationType = 'none' | 'next_link' | 'scroll' | 'page_param'

export interface ScrapeConfigCreate {
  name: string
  base_url: string
  use_headless_browser?: boolean
  wait_for_selector?: string | null
  custom_headers?: Record<string, string> | null
  pagination_type?: PaginationType
  pagination_selector?: string | null
  max_pages?: number
  item_selector: string
  fields: FieldConfig[]
  request_delay_ms?: number
  concurrent_requests?: number
  schedule_cron?: string | null
  is_active?: boolean
}

export interface ScrapeConfigUpdate extends Partial<ScrapeConfigCreate> {}

export interface ScrapeConfigResponse {
  id: number
  name: string
  base_url: string
  domain: string
  use_headless_browser: boolean
  wait_for_selector: string | null
  custom_headers: Record<string, string> | null
  pagination_type: PaginationType
  pagination_selector: string | null
  max_pages: number
  item_selector: string
  fields: FieldConfig[]
  request_delay_ms: number
  concurrent_requests: number
  schedule_cron: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

// ── Jobs ────────────────────────────────────────────────────────────────────

export type JobStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled'

export interface JobCreate {
  config_id: number
}

export interface JobResponse {
  id: number
  config_id: number
  status: JobStatus
  started_at: string | null
  completed_at: string | null
  pages_scraped: number
  items_found: number
  items_created: number
  items_skipped: number
  errors: number
  error_message: string | null
  celery_task_id: string | null
  created_at: string
}

export interface JobProgress {
  job_id: number
  status: JobStatus
  pages_scraped: number
  items_found: number
  items_created: number
  items_skipped: number
  errors: number
}

// ── Results ─────────────────────────────────────────────────────────────────

export interface ScrapedItemResponse {
  id: number
  job_id: number
  config_id: number
  source_url: string
  item_url: string | null
  data: Record<string, unknown>
  content_hash: string
  created_at: string
}

export interface ResultsListResponse {
  items: ScrapedItemResponse[]
  total: number
  page: number
  page_size: number
  pages: number
}

export interface ResultStats {
  total_items: number
  total_jobs: number
  total_configs: number
  items_by_domain: Record<string, number>
  jobs_by_status: Record<string, number>
}

// ── Auto-detect ─────────────────────────────────────────────────────────────

export interface AutoDetectRequest {
  url: string
  use_playwright?: boolean
}

export interface DetectedField {
  name: string
  selector: string
  attribute: string | null
  sample_values: string[]
}

export interface AutoDetectResponse {
  url: string
  item_selector: string
  fields: DetectedField[]
  confidence: number
  pagination_type: PaginationType
  pagination_selector: string | null
  detected_via: string
  preview_items: Record<string, unknown>[]
}

// ── Test Config ──────────────────────────────────────────────────────────────

export interface TestConfigResponse {
  items: Record<string, unknown>[]
  pages_scraped: number
  items_found: number
  errors: string[]
}

// ── API list params ──────────────────────────────────────────────────────────

export interface ConfigsListParams {
  offset?: number
  limit?: number
}

export interface JobsListParams {
  status?: JobStatus
  config_id?: number
  offset?: number
  limit?: number
}

export interface ResultsListParams {
  config_id?: number
  job_id?: number
  page?: number
  page_size?: number
}

export interface ExportParams {
  format: 'json' | 'csv' | 'xlsx'
  config_id?: number
  job_id?: number
}

// ── Schedules ────────────────────────────────────────────────────────────────

export interface ScheduleResponse {
  id: number
  name: string
  config_id: number
  cron_expression: string
  is_active: boolean
  last_run_at: string | null
  next_run_at: string | null
  created_at: string
  updated_at: string
}
