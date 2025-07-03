import { ReactNode, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ProgressTracker } from '@/components/shared/ProgressTracker';

interface TabTemplateProps {
  title: string;
  description: string;
  children: ReactNode;
  infoSection?: ReactNode;
  onSubmit: () => Promise<void>;
  onReset: () => void;
  submitButtonText: string;
  processingText: string;
  isSubmitDisabled: boolean;
  shouldShowReset: boolean;
  isProcessing: boolean;
  currentTaskId: string | null;
  error: string | null;
  success?: boolean;
  successMessage?: string;
}

export function TabTemplate({
  title,
  description,
  children,
  infoSection,
  onSubmit,
  onReset,
  submitButtonText,
  processingText,
  isSubmitDisabled,
  shouldShowReset,
  isProcessing,
  currentTaskId,
  error,
  success,
  successMessage
}: TabTemplateProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      await onSubmit();
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleComplete = () => {
    setIsSubmitting(false);
  };

  const handleError = (errorMessage: string) => {
    setIsSubmitting(false);
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        <CardDescription>{description}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {children}

        {success && successMessage && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-md">
            <p className="text-sm text-green-600">
              ✓ {successMessage}
            </p>
          </div>
        )}

        {infoSection}

        <div className="flex gap-2">
          <Button
            onClick={handleSubmit}
            disabled={isSubmitDisabled || isProcessing || isSubmitting}
            className="w-auto"
          >
            {isProcessing || isSubmitting ? processingText : submitButtonText}
          </Button>
          
          {shouldShowReset && (
            <Button variant="outline" onClick={onReset} disabled={isProcessing || isSubmitting}>
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