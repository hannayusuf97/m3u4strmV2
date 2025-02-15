import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, Loader2 } from 'lucide-react';
import { useWebSocket } from './WebSocketContext';

const M3UProgress = () => {
  const { processingProgress } = useWebSocket();

  const calculateTotalProgress = () => {
    if (processingProgress.totalM3Us === 0) return 0;
    return (processingProgress.currentM3U / processingProgress.totalM3Us) * 100;
  };

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>M3U Processing Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Overall Progress</span>
            <span>{processingProgress.currentM3U} of {processingProgress.totalM3Us}</span>
          </div>
          <Progress value={calculateTotalProgress()} />
        </div>

        <div className="mt-4">
          <strong>Current File:</strong> {processingProgress.currentFile}
          <p>{processingProgress.message}</p>
        </div>
      </CardContent>
    </Card>
  );
};

export default M3UProgress;
