import { useState, useEffect } from "react"
import { Plus, Trash2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select } from "@/components/ui/select"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

interface FieldMapping {
  excelField: string
  pdfField: string
  type?: string
}

interface FieldMappingEditorProps {
  title: string
  description?: string
  initialValue?: Record<string, any>
  onChange?: (value: Record<string, any>) => void
}

export function FieldMappingEditor({ 
  title, 
  description,
  initialValue = {},
  onChange
}: FieldMappingEditorProps) {
  const [mappings, setMappings] = useState<FieldMapping[]>([])
  const [newExcelField, setNewExcelField] = useState("")
  const [newPdfField, setNewPdfField] = useState("")
  const [newType, setNewType] = useState("")

  useEffect(() => {
    setMappings(convertToArray(initialValue))
  }, [initialValue])

  // Convert object structure to array for easier manipulation
  const convertToArray = (mappings: Record<string, any>): FieldMapping[] => {
    return Object.entries(mappings || {}).map(([excelField, config]) => ({
      excelField,
      pdfField: typeof config === "object" ? config.pdf_field : config,
      type: typeof config === "object" ? config.type : undefined
    }))
  }

  const convertToObject = (mappings: FieldMapping[]): Record<string, any> => {
    const result: Record<string, any> = {}
    mappings.forEach(({ excelField, pdfField, type }) => {
      if (excelField && pdfField) {
        result[excelField] = type ? { pdf_field: pdfField, type } : { pdf_field: pdfField }
      }
    })
    return result
  }

  const updateForm = (newMappings: FieldMapping[]) => {
    const objectForm = convertToObject(newMappings)
    setMappings(newMappings)
    onChange?.(objectForm)
  }

  const addMapping = () => {
    if (!newExcelField.trim() || !newPdfField.trim()) return

    const newMapping: FieldMapping = {
      excelField: newExcelField.trim(),
      pdfField: newPdfField.trim(),
      type: newType.trim() || undefined
    }

    const updatedMappings = [...mappings, newMapping]
    updateForm(updatedMappings)
    
    // Clear the input fields
    setNewExcelField("")
    setNewPdfField("")
    setNewType("")
  }

  const removeMapping = (index: number) => {
    const updatedMappings = mappings.filter((_, i) => i !== index)
    updateForm(updatedMappings)
  }

  const updateMapping = (index: number, field: keyof FieldMapping, value: string) => {
    const updatedMappings = [...mappings]
    updatedMappings[index] = { ...updatedMappings[index], [field]: value }
    updateForm(updatedMappings)
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Existing Mappings */}
        <div className="space-y-3">
          {mappings.map((mapping, index) => (
            <div key={index} className="grid grid-cols-12 gap-2 items-end p-3 border rounded-lg">
              <div className="col-span-4">
                <Label htmlFor={`excel-${index}`} className="text-xs">Excel Field</Label>
                <Input
                  id={`excel-${index}`}
                  value={mapping.excelField}
                  onChange={(e) => updateMapping(index, 'excelField', e.target.value)}
                  placeholder="Excel column name"
                />
              </div>
              <div className="col-span-4">
                <Label htmlFor={`pdf-${index}`} className="text-xs">PDF Field</Label>
                <Input
                  id={`pdf-${index}`}
                  value={mapping.pdfField}
                  onChange={(e) => updateMapping(index, 'pdfField', e.target.value)}
                  placeholder="PDF field name"
                />
              </div>
              <div className="col-span-3">
                <Label htmlFor={`type-${index}`} className="text-xs">Type (Optional)</Label>
                <Select
                  value={mapping.type || ""}
                  onChange={(e) => updateMapping(index, 'type', e.target.value)}
                >
                  <option value="">Default</option>
                  <option value="checkbox">Checkbox</option>
                  <option value="radio">Radio</option>
                  <option value="select">Select</option>
                  <option value="textarea">Textarea</option>
                </Select>
              </div>
              <div className="col-span-1">
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={() => removeMapping(index)}
                  className="text-red-500 hover:text-red-700"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        {/* Add New Mapping */}
        <div className="border-t pt-4">
          <div className="grid grid-cols-12 gap-2 items-end">
            <div className="col-span-4">
              <Label htmlFor="new-excel" className="text-xs">Excel Field</Label>
              <Input
                id="new-excel"
                value={newExcelField}
                onChange={(e) => setNewExcelField(e.target.value)}
                placeholder="Excel column name"
              />
            </div>
            <div className="col-span-4">
              <Label htmlFor="new-pdf" className="text-xs">PDF Field</Label>
              <Input
                id="new-pdf"
                value={newPdfField}
                onChange={(e) => setNewPdfField(e.target.value)}
                placeholder="PDF field name"
              />
            </div>
            <div className="col-span-3">
              <Label htmlFor="new-type" className="text-xs">Type (Optional)</Label>
              <Select
                value={newType}
                onChange={(e) => setNewType(e.target.value)}
              >
                <option value="">Default</option>
                <option value="checkbox">Checkbox</option>
                <option value="radio">Radio</option>
                <option value="select">Select</option>
                <option value="textarea">Textarea</option>
              </Select>
            </div>
            <div className="col-span-1">
              <Button
                type="button"
                onClick={addMapping}
                disabled={!newExcelField.trim() || !newPdfField.trim()}
                size="sm"
              >
                <Plus className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>

        {mappings.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>No field mappings configured.</p>
            <p className="text-sm">Add your first mapping above.</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}