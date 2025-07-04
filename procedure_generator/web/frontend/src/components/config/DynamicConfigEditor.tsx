import { useEffect, useState } from "react"
import { useForm } from "react-hook-form"
import { Save, RotateCcw, Loader2, ChevronDown, ChevronRight } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ConfigField } from "./ConfigField"
import { FieldMappingEditor } from "./FieldMappingEditor"
import { NopPagesEditor } from "./NopPagesEditor"
import type { Configuration, ConfigValue } from "@/lib/types"
import { getConfig, updateConfig } from "@/lib/api"

interface ConfigSectionProps {
  title: string
  description?: string
  children: React.ReactNode
  defaultCollapsed?: boolean
  useColumnLayout?: boolean
}

function ConfigSectionComponent({ 
  title, 
  description, 
  children, 
  defaultCollapsed = false,
  useColumnLayout = false
}: ConfigSectionProps) {
  const [isCollapsed, setIsCollapsed] = useState(defaultCollapsed)

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="space-y-1">
            <CardTitle className="text-lg">{title}</CardTitle>
            {description && (
              <CardDescription>{description}</CardDescription>
            )}
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="ml-4"
          >
            {isCollapsed ? (
              <ChevronRight className="h-4 w-4" />
            ) : (
              <ChevronDown className="h-4 w-4" />
            )}
          </Button>
        </div>
      </CardHeader>
      {!isCollapsed && (
        <CardContent className="pt-0">
          <div className={useColumnLayout ? "grid gap-4 md:grid-cols-2" : "space-y-6"}>
            {children}
          </div>
        </CardContent>
      )}
    </Card>
  )
}

export function DynamicConfigEditor() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [originalConfig, setOriginalConfig] = useState<Configuration | null>(null)
  const [comments, setComments] = useState<Record<string, string>>({})

  const { control, handleSubmit, reset, setValue, formState: { isDirty } } = useForm<Configuration>()

  useEffect(() => {
    loadConfig()
  }, [])

  const loadConfig = async () => {
    try {
      setLoading(true)
      const response = await getConfig()
      setOriginalConfig(response.config)
      setComments(response.comments)
      reset(response.config)
      toast.success("Configuration loaded successfully")
    } catch (error) {
      console.error("Failed to load configuration:", error)
      toast.error("Failed to load configuration")
    } finally {
      setLoading(false)
    }
  }

  const onSubmit = async (data: Configuration) => {
    try {
      setSaving(true)
      await updateConfig(data)
      setOriginalConfig(data)
      reset(data)
      toast.success("Configuration saved successfully")
    } catch (error) {
      console.error("Failed to save configuration:", error)
      toast.error("Failed to save configuration")
    } finally {
      setSaving(false)
    }
  }

  const handleReset = () => {
    if (originalConfig) {
      reset(originalConfig)
      toast.info("Configuration reset to original values")
    }
  }

  const getCommentForPath = (path: string, fallback: string = "") => {
    return comments[path] || fallback
  }

  const detectFieldType = (value: ConfigValue): "text" | "number" | "textarea" | "select" | "checkbox" | "url" => {
    if (typeof value === "boolean") return "checkbox"
    if (typeof value === "number") return "number"
    if (typeof value === "string") {
      if (value.startsWith("http://") || value.startsWith("https://")) return "url"
      if (value.includes("\\") || value.includes("/")) return "text" // file path
      if (value.length > 100) return "textarea"
      return "text"
    }
    return "text"
  }

  const formatFieldLabel = (key: string): string => {
    // Convert snake_case or camelCase to Title Case
    return key
      .replace(/[_-]/g, " ")
      .replace(/([a-z])([A-Z])/g, "$1 $2")
      .split(" ")
      .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
      .join(" ")
  }

  const formatSectionTitle = (key: string): string => {
    const formatted = formatFieldLabel(key)
    // Special cases for better readability
    const specialCases: Record<string, string> = {
      "Ui Settings": "User Interface Settings",
      "Worksafe Bc": "WorkSafe BC Configuration",
      "Excel To Pdf": "Excel to PDF Configuration",
      "Nop": "Notice of Project (NOP) Configuration",
      "Debug Paths": "Debug/Development Paths"
    }
    return specialCases[formatted] || formatted
  }

  const shouldCollapseSection = (key: string): boolean => {
    // Collapse complex sections by default
    const complexSections = ["debug_paths", "NOP", "EXCEL_TO_PDF", "timeouts"]
    return complexSections.includes(key)
  }

  const hasOnlyPrimitiveValues = (obj: Record<string, ConfigValue>): boolean => {
    return Object.values(obj).every(value => 
      typeof value !== "object" || 
      Array.isArray(value) || 
      value === null || 
      value === undefined
    )
  }

  const renderConfigValue = (value: ConfigValue, path: string, key: string): React.ReactNode => {
    if (value === null || value === undefined) return null
    
    // Hide keys that end with __HIDDEN
    if (key.endsWith('__HIDDEN')) {
      return null
    }

    // Special handling for field_mappings - use FieldMappingEditor
    if (key === "field_mappings" && typeof value === "object" && !Array.isArray(value)) {
      return (
        <FieldMappingEditor
          key={path}
          title="Excel to PDF Field Mappings"
          description={getCommentForPath(path, "Map Excel column names to PDF form field names")}
          initialValue={value as Record<string, any>}
          onChange={(updatedValue: Record<string, any>) => {
            setValue(path as any, updatedValue, { shouldDirty: true })
          }}
        />
      )
    }

    // Special handling for NOP pages - use NopPagesEditor
    if (key === "pages" && Array.isArray(value)) {
      return (
        <NopPagesEditor
          key={path}
          title="NOP Form Pages Configuration"
          description={getCommentForPath(path, "Configure data key mappings for NOP form pages")}
          initialValue={value as Array<Record<string, any>>}
          onChange={(updatedValue: Array<Record<string, any>>) => {
            setValue(path as any, updatedValue, { shouldDirty: true })
          }}
        />
      )
    }

    if (typeof value === "object" && !Array.isArray(value)) {
      // This is a nested object - render as a section
      const sectionTitle = formatSectionTitle(key)
      const sectionComment = getCommentForPath(path)
      const valueObj = value as Record<string, ConfigValue>
      const hasOnlyPrimitives = hasOnlyPrimitiveValues(valueObj)
      
      return (
        <ConfigSectionComponent 
          key={path}
          title={sectionTitle}
          description={sectionComment}
          defaultCollapsed={shouldCollapseSection(key)}
          useColumnLayout={hasOnlyPrimitives}
        >
          {Object.entries(valueObj)
            .filter(([nestedKey]) => !nestedKey.endsWith('__HIDDEN'))
            .map(([nestedKey, nestedValue]) => {
              const nestedPath = `${path}.${nestedKey}`
              return renderConfigValue(nestedValue, nestedPath, nestedKey)
            })}
        </ConfigSectionComponent>
      )
    }

    if (Array.isArray(value)) {
      // Handle arrays - for now, we'll handle simple arrays like [800, 600]
      if (value.length === 2 && typeof value[0] === "number" && typeof value[1] === "number") {
        // Treat as width/height pair
        return (
          <div key={path} className="col-span-2 grid grid-cols-2 gap-4">
            <ConfigField
              name={`${path}.0` as any}
              label={`${formatFieldLabel(key)} Width`}
              description={getCommentForPath(path, `${formatFieldLabel(key)} width value`)}
              type="number"
              control={control}
              min={1}
            />
            <ConfigField
              name={`${path}.1` as any}
              label={`${formatFieldLabel(key)} Height`}
              description={getCommentForPath(path, `${formatFieldLabel(key)} height value`)}
              type="number"
              control={control}
              min={1}
            />
          </div>
        )
      }
      // For other arrays, we'll skip for now or handle as JSON
      return null
    }

    // Primitive value - render as a field
    const fieldType = detectFieldType(value)
    const label = formatFieldLabel(key)
    const description = getCommentForPath(path, `Configure ${label.toLowerCase()}`)

    return (
      <ConfigField
        key={path}
        name={path as any}
        label={label}
        description={description}
        type={fieldType}
        control={control}
        required={path.includes("url") || path.includes("path")}
      />
    )
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-6 w-6 animate-spin" />
          <span>Loading configuration...</span>
        </div>
      </div>
    )
  }

  if (!originalConfig) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <p className="text-muted-foreground">No configuration data available</p>
          <Button onClick={loadConfig} className="mt-4">
            Retry Loading
          </Button>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Configuration Editor</h2>
          <p className="text-muted-foreground">
            Modify application settings and save changes to swp_config.yaml
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            type="button"
            variant="outline"
            onClick={handleReset}
            disabled={!isDirty || saving}
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button
            type="submit"
            disabled={!isDirty || saving}
          >
            {saving ? (
              <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <Save className="h-4 w-4 mr-2" />
            )}
            Save Changes
          </Button>
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(originalConfig)
          .filter(([key]) => !key.endsWith('__HIDDEN'))
          .map(([key, value]) => 
            renderConfigValue(value, key, key)
          )}
      </div>
    </form>
  )
}