import { Controller } from "react-hook-form"
import type { Control, FieldPath, FieldValues } from "react-hook-form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Select } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"

export interface ConfigFieldProps<T extends FieldValues> {
  name: FieldPath<T>
  label: string
  description?: string
  type: "text" | "number" | "textarea" | "select" | "checkbox" | "url"
  control: Control<T>
  options?: Array<{ value: string; label: string }>
  placeholder?: string
  required?: boolean
  min?: number
  max?: number
}

export function ConfigField<T extends FieldValues>({
  name,
  label,
  description,
  type,
  control,
  options,
  placeholder,
  required = false,
  min,
  max,
}: ConfigFieldProps<T>) {
  const renderField = (field: { value: any; onChange: (value: any) => void; onBlur?: () => void }) => {
    const baseProps = {
      ...field,
      placeholder: placeholder || `Enter ${label.toLowerCase()}`,
    }

    switch (type) {
      case "text":
      case "url":
        return (
          <Input
            {...baseProps}
            type={type === "url" ? "url" : "text"}
            required={required}
          />
        )
      
      case "number":
        return (
          <Input
            {...baseProps}
            type="number"
            min={min}
            max={max}
            required={required}
            onChange={(e) => field.onChange(e.target.value ? Number(e.target.value) : '')}
          />
        )
      
      case "textarea":
        return (
          <Textarea
            {...baseProps}
            required={required}
            rows={3}
          />
        )
      
      case "select":
        return (
          <Select
            {...baseProps}
            required={required}
          >
            {options?.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </Select>
        )
      
      case "checkbox":
        return (
          <div className="flex items-center space-x-2">
            <Checkbox
              id={name}
              checked={field.value || false}
              onCheckedChange={(checked) => field.onChange(checked)}
            />
            <Label htmlFor={name} className="text-sm font-normal">
              {label}
            </Label>
          </div>
        )
      
      default:
        return <Input {...baseProps} required={required} />
    }
  }

  if (type === "checkbox") {
    return (
      <div className="space-y-2">
        <Controller
          name={name}
          control={control}
          render={({ field }) => renderField(field)}
        />
        {description && (
          <p className="text-xs text-muted-foreground">{description}</p>
        )}
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <Label htmlFor={name} className="text-sm font-medium">
        {label}
        {required && <span className="text-red-500 ml-1">*</span>}
      </Label>
      <Controller
        name={name}
        control={control}
        render={({ field, fieldState }) => (
          <div>
            {renderField(field)}
            {fieldState.error && (
              <p className="text-xs text-red-500 mt-1">{fieldState.error.message}</p>
            )}
          </div>
        )}
      />
      {description && (
        <p className="text-xs text-muted-foreground">{description}</p>
      )}
    </div>
  )
}