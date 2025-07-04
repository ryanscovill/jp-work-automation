import { useState } from "react"
import { ChevronDown, ChevronRight } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

interface ConfigSectionProps {
  title: string
  description?: string
  children: React.ReactNode
  defaultCollapsed?: boolean
}

export function ConfigSection({ 
  title, 
  description, 
  children, 
  defaultCollapsed = false 
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
          <div className="grid gap-4 md:grid-cols-2">
            {children}
          </div>
        </CardContent>
      )}
    </Card>
  )
}