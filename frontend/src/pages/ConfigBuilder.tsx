import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { ArrowLeft, Plus, Trash2, Wand2 } from 'lucide-react'
import { configsApi } from '@/api/configs'
import type { FieldConfig, ScrapeConfigCreate } from '@/types'
import { Header } from '@/components/layout/Header'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'

type FieldType = 'text' | 'attribute' | 'html' | 'url'

interface FieldRow {
  name: string
  selector: string
  field_type: FieldType
  attribute_name: string
  multiple: boolean
  required: boolean
}

const emptyField = (): FieldRow => ({
  name: '',
  selector: '',
  field_type: 'text',
  attribute_name: '',
  multiple: false,
  required: false,
})

interface FormErrors {
  name?: string
  base_url?: string
  item_selector?: string
}

export function ConfigBuilder() {
  const navigate = useNavigate()

  const [name, setName] = useState('')
  const [baseUrl, setBaseUrl] = useState('')
  const [itemSelector, setItemSelector] = useState('')
  const [maxPages, setMaxPages] = useState(100)
  const [requestDelayMs, setRequestDelayMs] = useState(1000)
  const [useHeadless, setUseHeadless] = useState(false)
  const [isActive, setIsActive] = useState(true)
  const [fields, setFields] = useState<FieldRow[]>([emptyField()])
  const [errors, setErrors] = useState<FormErrors>({})

  // Auto-detect
  const [detectUrl, setDetectUrl] = useState('')
  const [detectError, setDetectError] = useState('')

  const autoDetectMutation = useMutation({
    mutationFn: () => configsApi.autoDetect({ url: detectUrl }),
    onSuccess: (data) => {
      if (data.item_selector) setItemSelector(data.item_selector)
      const newFields: FieldRow[] = data.fields.map((f) => ({
        name: f.name,
        selector: f.selector,
        field_type: f.attribute ? 'attribute' : 'text',
        attribute_name: f.attribute ?? '',
        multiple: false,
        required: false,
      }))
      setFields((prev) => [...prev.filter((f) => f.name || f.selector), ...newFields])
      setDetectError('')
    },
    onError: (err: Error) => setDetectError(err.message),
  })

  const createMutation = useMutation({
    mutationFn: (payload: ScrapeConfigCreate) => configsApi.create(payload),
    onSuccess: (config) => navigate(`/configs/${config.id}`),
  })

  function validate(): boolean {
    const errs: FormErrors = {}
    if (!name.trim()) errs.name = 'Name is required'
    if (!baseUrl.trim()) errs.base_url = 'Base URL is required'
    else if (!baseUrl.startsWith('http')) errs.base_url = 'URL must start with http'
    if (!itemSelector.trim()) errs.item_selector = 'Item selector is required'
    setErrors(errs)
    return Object.keys(errs).length === 0
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!validate()) return

    const builtFields: FieldConfig[] = fields
      .filter((f) => f.name && f.selector)
      .map((f) => ({
        name: f.name,
        selector: f.selector,
        attribute: f.field_type === 'attribute' ? f.attribute_name || null : null,
        transform: null,
        required: f.required,
        default_value: null,
      }))

    createMutation.mutate({
      name,
      base_url: baseUrl,
      item_selector: itemSelector,
      max_pages: maxPages,
      request_delay_ms: requestDelayMs,
      use_headless_browser: useHeadless,
      is_active: isActive,
      fields: builtFields,
    })
  }

  function updateField(index: number, key: keyof FieldRow, value: string | boolean) {
    setFields((prev) =>
      prev.map((f, i) => (i === index ? { ...f, [key]: value } : f))
    )
  }

  function removeField(index: number) {
    setFields((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-6">
      <Header title="New Configuration">
        <Button variant="outline" size="sm" asChild>
          <Link to="/configs">
            <ArrowLeft className="mr-1 h-4 w-4" />
            Back
          </Link>
        </Button>
      </Header>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic info */}
        <Card>
          <CardHeader>
            <CardTitle>Basic Settings</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <Label htmlFor="name">Name *</Label>
              <Input
                id="name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="My Scraper"
              />
              {errors.name && <p className="text-xs text-red-500">{errors.name}</p>}
            </div>
            <div className="space-y-1">
              <Label htmlFor="base_url">Base URL *</Label>
              <Input
                id="base_url"
                value={baseUrl}
                onChange={(e) => setBaseUrl(e.target.value)}
                placeholder="https://example.com"
              />
              {errors.base_url && <p className="text-xs text-red-500">{errors.base_url}</p>}
            </div>
            <div className="space-y-1">
              <Label htmlFor="item_selector">Item Selector *</Label>
              <Input
                id="item_selector"
                value={itemSelector}
                onChange={(e) => setItemSelector(e.target.value)}
                placeholder=".article, .product-card"
              />
              {errors.item_selector && (
                <p className="text-xs text-red-500">{errors.item_selector}</p>
              )}
            </div>
            <div className="space-y-1">
              <Label htmlFor="max_pages">Max Pages</Label>
              <Input
                id="max_pages"
                type="number"
                min={1}
                value={maxPages}
                onChange={(e) => setMaxPages(Number(e.target.value))}
              />
            </div>
            <div className="space-y-1">
              <Label htmlFor="delay">Request Delay (ms)</Label>
              <Input
                id="delay"
                type="number"
                min={0}
                value={requestDelayMs}
                onChange={(e) => setRequestDelayMs(Number(e.target.value))}
              />
            </div>
            <div className="flex items-center gap-6 pt-6">
              <div className="flex items-center gap-2">
                <Switch
                  id="headless"
                  checked={useHeadless}
                  onCheckedChange={setUseHeadless}
                />
                <Label htmlFor="headless">Headless Browser</Label>
              </div>
              <div className="flex items-center gap-2">
                <Switch
                  id="active"
                  checked={isActive}
                  onCheckedChange={setIsActive}
                />
                <Label htmlFor="active">Active</Label>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Auto-detect */}
        <Card>
          <CardHeader>
            <CardTitle>Auto-detect Fields</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2">
              <Input
                value={detectUrl}
                onChange={(e) => setDetectUrl(e.target.value)}
                placeholder="https://example.com/page-to-analyze"
                className="flex-1"
              />
              <Button
                type="button"
                variant="secondary"
                disabled={!detectUrl || autoDetectMutation.isPending}
                onClick={() => autoDetectMutation.mutate()}
              >
                <Wand2 className="mr-1 h-4 w-4" />
                {autoDetectMutation.isPending ? 'Detecting…' : 'Auto-detect'}
              </Button>
            </div>
            {detectError && <p className="text-xs text-red-500">{detectError}</p>}
            {autoDetectMutation.isSuccess && (
              <p className="text-xs text-green-600">
                Detected {autoDetectMutation.data.fields.length} fields.
              </p>
            )}
          </CardContent>
        </Card>

        {/* Fields table */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Fields</CardTitle>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => setFields((prev) => [...prev, emptyField()])}
            >
              <Plus className="mr-1 h-4 w-4" />
              Add Field
            </Button>
          </CardHeader>
          <CardContent className="p-0">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Selector</TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Attribute</TableHead>
                  <TableHead>Required</TableHead>
                  <TableHead />
                </TableRow>
              </TableHeader>
              <TableBody>
                {fields.map((field, i) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Input
                        value={field.name}
                        onChange={(e) => updateField(i, 'name', e.target.value)}
                        placeholder="field_name"
                        className="h-8"
                      />
                    </TableCell>
                    <TableCell>
                      <Input
                        value={field.selector}
                        onChange={(e) => updateField(i, 'selector', e.target.value)}
                        placeholder=".css-selector"
                        className="h-8"
                      />
                    </TableCell>
                    <TableCell>
                      <Select
                        value={field.field_type}
                        onValueChange={(v) => updateField(i, 'field_type', v)}
                      >
                        <SelectTrigger className="h-8 w-28">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="text">text</SelectItem>
                          <SelectItem value="attribute">attribute</SelectItem>
                          <SelectItem value="html">html</SelectItem>
                          <SelectItem value="url">url</SelectItem>
                        </SelectContent>
                      </Select>
                    </TableCell>
                    <TableCell>
                      {field.field_type === 'attribute' && (
                        <Input
                          value={field.attribute_name}
                          onChange={(e) => updateField(i, 'attribute_name', e.target.value)}
                          placeholder="href"
                          className="h-8 w-24"
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      <Switch
                        checked={field.required}
                        onCheckedChange={(v) => updateField(i, 'required', v)}
                      />
                    </TableCell>
                    <TableCell>
                      <Button
                        type="button"
                        variant="ghost"
                        size="sm"
                        onClick={() => removeField(i)}
                      >
                        <Trash2 className="h-4 w-4 text-red-400" />
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {createMutation.isError && (
          <p className="text-sm text-red-500">{(createMutation.error as Error).message}</p>
        )}

        <div className="flex gap-3">
          <Button type="submit" disabled={createMutation.isPending}>
            {createMutation.isPending ? 'Creating…' : 'Create Configuration'}
          </Button>
          <Button type="button" variant="outline" asChild>
            <Link to="/configs">Cancel</Link>
          </Button>
        </div>
      </form>
    </div>
  )
}
