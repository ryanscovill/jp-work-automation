import { useState, useEffect } from "react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ChevronDown, ChevronRight } from "lucide-react"
import { Button } from "@/components/ui/button"

interface NopField {
  type: string
  data_key: string
}

interface NopPage {
  [fieldName: string]: NopField
}

interface NopPagesEditorProps {
  title: string
  description?: string
  initialValue?: Array<Record<string, NopPage>>
  onChange?: (value: Array<Record<string, NopPage>>) => void
}

export function NopPagesEditor({ 
  title, 
  description,
  initialValue = [],
  onChange
}: NopPagesEditorProps) {
  const [pages, setPages] = useState<Array<Record<string, NopPage>>>(initialValue)
  const [collapsedPages, setCollapsedPages] = useState<Set<string>>(new Set())

  useEffect(() => {
    setPages(initialValue)
  }, [initialValue])

  const updateDataKey = (pageIndex: number, pageName: string, fieldName: string, newDataKey: string) => {
    const updatedPages = [...pages]
    if (updatedPages[pageIndex] && updatedPages[pageIndex][pageName] && updatedPages[pageIndex][pageName][fieldName]) {
      updatedPages[pageIndex][pageName][fieldName] = {
        ...updatedPages[pageIndex][pageName][fieldName],
        data_key: newDataKey
      }
      setPages(updatedPages)
      onChange?.(updatedPages)
    }
  }

  const togglePageCollapse = (pageKey: string) => {
    const newCollapsed = new Set(collapsedPages)
    if (newCollapsed.has(pageKey)) {
      newCollapsed.delete(pageKey)
    } else {
      newCollapsed.add(pageKey)
    }
    setCollapsedPages(newCollapsed)
  }

  const formatFieldLabel = (fieldName: string): string => {
    // Convert camelCase to Title Case
    return fieldName
      .replace(/([a-z])([A-Z])/g, '$1 $2')
      .replace(/^./, str => str.toUpperCase())
  }

  const formatPageTitle = (pageName: string): string => {
    return pageName
      .split(' ')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-lg">{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent className="space-y-4">
        {pages.map((pageObj, pageIndex) => {
          return Object.entries(pageObj).map(([pageName, fields]) => {
            const pageKey = `${pageIndex}-${pageName}`
            const isCollapsed = collapsedPages.has(pageKey)
            
            return (
              <Card key={pageKey} className="border-l-4 border-l-blue-500">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="text-base">{formatPageTitle(pageName)}</CardTitle>
                      <CardDescription className="text-sm">
                        {Object.keys(fields).length} form fields
                      </CardDescription>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => togglePageCollapse(pageKey)}
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
                    <div className="grid gap-4 md:grid-cols-2">
                      {Object.entries(fields).map(([fieldName, fieldData]) => (
                        <div key={fieldName} className="space-y-2">
                          <div className="flex items-center justify-between">
                            <Label htmlFor={`${pageKey}-${fieldName}`} className="text-sm font-medium">
                              {formatFieldLabel(fieldName)}
                            </Label>
                            <span className="text-xs text-muted-foreground px-2 py-1 bg-muted rounded">
                              {fieldData.type}
                            </span>
                          </div>
                          <Input
                            id={`${pageKey}-${fieldName}`}
                            value={fieldData.data_key}
                            onChange={(e) => updateDataKey(pageIndex, pageName, fieldName, e.target.value)}
                            placeholder="Enter data key"
                            className="font-mono text-sm"
                          />
                        </div>
                      ))}
                    </div>
                  </CardContent>
                )}
              </Card>
            )
          })
        })}
        
        {pages.length === 0 && (
          <div className="text-center py-8 text-muted-foreground">
            <p>No NOP pages configured.</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}