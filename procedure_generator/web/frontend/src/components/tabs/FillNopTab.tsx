import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { FileUpload } from '@/components/shared/FileUpload';
import { ProgressTracker } from '@/components/shared/ProgressTracker';
import { apiClient } from '@/lib/api';

export function FillNopTab() {
  const [swpFile, setSwpFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentTaskId, setCurrentTaskId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSwpFileSelect = (files: File[]) => {
    if (files.length > 0) {
      setSwpFile(files[0]);
      setError(null);
      setSuccess(false);
    }
  };

  const handleSubmit = async () => {
    if (!swpFile) {
      setError('Please select a SWP PDF file');
      return;
    }

    try {
      setIsProcessing(true);
      setError(null);
      setSuccess(false);
      
      const response = await apiClient.fillNop({
        swp_file: swpFile,
      });
      
      setCurrentTaskId(response.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
      setIsProcessing(false);
    }
  };

  const handleComplete = () => {
    setIsProcessing(false);
    setSuccess(true);
  };

  const handleError = (errorMessage: string) => {
    setIsProcessing(false);
    setError(errorMessage);
  };

  const resetForm = () => {
    setSwpFile(null);
    setCurrentTaskId(null);
    setError(null);
    setSuccess(false);
    setIsProcessing(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Fill NOP Form</CardTitle>
        <CardDescription>
          Automate filling of NOP (Notice of Project) forms on the WorkSafeBC website using browser automation
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="space-y-2">
          <label className="text-sm font-medium">SWP PDF File</label>
          <FileUpload
            accept=".pdf"
            onFileSelect={handleSwpFileSelect}
            disabled={isProcessing}
          >
            {swpFile ? (
              <div className="space-y-2">
                <p className="text-sm font-medium text-green-600">
                  ✓ {swpFile.name}
                </p>
                <p className="text-xs text-muted-foreground">
                  Click to change or drag new file
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                <p className="text-sm font-medium">Select SWP PDF</p>
                <p className="text-xs text-muted-foreground">
                  The Safe Work Procedure PDF file
                </p>
              </div>
            )}
          </FileUpload>
        </div>

        {success && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-600">
              ✓ NOP form filling completed successfully!
            </p>
          </div>
        )}

        <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
          <h4 className="text-sm font-medium text-blue-800 mb-2">Important Notes:</h4>
          <ul className="text-sm text-blue-700 space-y-1">
            <li>• This process will open a browser window automatically</li>
            <li>• Make sure you have a stable internet connection</li>
            <li>• The browser will navigate to the WorkSafeBC website</li>
            <li>• Do not close the browser window during processing</li>
          </ul>
        </div>

        <div className="flex gap-2">
          <Button
            onClick={handleSubmit}
            disabled={!swpFile || isProcessing}
            className="w-auto"
          >
            {isProcessing ? 'Filling Form...' : 'Fill NOP Form'}
          </Button>
          
          {(swpFile || error || success) && (
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