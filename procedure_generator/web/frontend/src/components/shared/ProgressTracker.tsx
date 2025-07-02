import { useEffect, useState } from 'react';
import type { TaskStatus } from '@/lib/types';
import { apiClient } from '@/lib/api';

interface ProgressTrackerProps {
  taskId: string | null;
  onComplete?: (outputFile?: string) => void;
  onError?: (error: string) => void;
}

export function ProgressTracker({ taskId, onComplete, onError }: ProgressTrackerProps) {
  const [status, setStatus] = useState<TaskStatus | null>(null);

  useEffect(() => {
    if (!taskId) {
      setStatus(null);
      return;
    }
    const pollInterval = setInterval(async () => {
      try {
        const taskStatus = await apiClient.getTaskStatus(taskId);
        setStatus(taskStatus);

        if (taskStatus.status === 'completed') {
          clearInterval(pollInterval);
          onComplete?.(taskStatus.output_file);
        } else if (taskStatus.status === 'error') {
          clearInterval(pollInterval);
          onError?.(taskStatus.error || 'Unknown error occurred');
        }
      } catch (error) {
        clearInterval(pollInterval);
        onError?.(error instanceof Error ? error.message : 'Failed to get task status');
      }
    }, 1000);

    return () => {
      clearInterval(pollInterval);
    };
  }, [taskId, onComplete, onError]);

  if (!taskId || !status) {
    return null;
  }

  return (
    <div className="space-y-2">
      <div className="flex justify-between text-sm">
        <span>
          {status.status === 'processing' ? 'Processing...' : 
           status.status === 'completed' ? 'Completed' : 
           status.status === 'error' ? 'Error' : 'Unknown'}
        </span>
        <span>{status.progress}%</span>
      </div>
      <div className="w-full bg-muted rounded-full h-2">
        <div 
          className={`h-2 rounded-full transition-all ${
            status.status === 'error' ? 'bg-destructive' : 
            status.status === 'completed' ? 'bg-green-500' : 'bg-primary'
          }`}
          style={{ width: `${status.progress}%` }}
        />
      </div>
      {status.status === 'error' && status.error && (
        <p className="text-sm text-destructive">{status.error}</p>
      )}
    </div>
  );
}