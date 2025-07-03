import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileUpload } from '@/components/shared/FileUpload';
import { ProgressTracker } from '@/components/shared/ProgressTracker';
import { apiClient } from '@/lib/api';

export function ExcelToPdfTab() {
  const [excelFile, setExcelFile] = useState<File | null>(null);
  const [pdfTemplate, setPdfTemplate] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleExcelFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setExcelFile(files[0]);
      setError(null);
    }
  };

  const handlePdfTemplateSelect = (files: File[]) => {
    if (files.length > 0) {
      setPdfTemplate(files[0]);
      setError(null);
    }
  };

  const handleSubmit = async () => {
    if (!excelFile || !pdfTemplate) {
      setError('Please select both Excel file and PDF template');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      
      const response = await apiClient.excelToPdf({
        excel_file: excelFile,
        pdf_template: pdfTemplate,
      });
      
      setCurrentTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsProcessing(false);
    }
  };

  const handleComplete = () => {
    setIsProcessing(false);
  };

  const handleError = (errorMessage: string) => {
    setIsProcessing(false);
    setError(errorMessage);
  };

  const resetForm = () => {
    setExcelFile(null);
    setPdfTemplate(null);
    setCurrentTaskId(null);
    setError(null);
    setIsProcessing(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Excel to PDF</CardTitle>
        <CardDescription>
          Fill PDF form templates using data from Excel files with field mapping
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="text-sm font-medium">Excel File</label>
            <FileUpload
              accept=".xlsx,.xls"
              onFileSelect={handleExcelFileSelect}
              disabled={isProcessing}
            >
              {excelFile ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-green-600">
                    ✓ {excelFile.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Click to change or drag new file
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Select Excel File</p>
                  <p className="text-xs text-muted-foreground">
                    .xlsx or .xls files only
                  </p>
                </div>
              )}
            </FileUpload>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">PDF Template</label>
            <FileUpload
              accept=".pdf"
              onFileSelect={handlePdfTemplateSelect}
              disabled={isProcessing}
            >
              {pdfTemplate ? (
                <div className="space-y-2">
                  <p className="text-sm font-medium text-green-600">
                    ✓ {pdfTemplate.name}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    Click to change or drag new file
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Select PDF Template</p>
                  <p className="text-xs text-muted-foreground">
                    PDF form to fill
                  </p>
                </div>
              )}
            </FileUpload>
          </div>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleSubmit}
            disabled={!excelFile || !pdfTemplate || isProcessing}
            className="w-auto"
          >
            {isProcessing ? 'Processing...' : 'Generate PDF'}
          </Button>
          
          {(excelFile || pdfTemplate || error) && (
            <Button variant="outline" onClick={resetForm} disabled={isProcessing}>
              Reset
            </Button>
          )}
        </div>

        {currentTaskId && (
          <ProgressTracker
            taskId={currentTaskId}
            onComplete={handleComplete}
            onError={handleError}
          />
        )}

        {error && !currentTaskId && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-md">
            <p className="text-sm text-red-600">{error}</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}