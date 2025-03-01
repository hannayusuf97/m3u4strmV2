import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Progress } from '../components/ui/progress';

const M3UProgress = ({ processingProgress }) => {
  if (!processingProgress || processingProgress.total_progress === 0) {
    return null;
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Upload Progress</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between">
            <span>Overall Progress</span>
            <span>{processingProgress.currentM3U} of {processingProgress.totalM3Us}</span>
          </div>
          <Progress value={processingProgress.total_progress} />
        </div>

        {processingProgress.currentFile && (
          <div className="mt-4">
            <strong>Current File:</strong> {processingProgress.currentFile}
          </div>
        )}

        {processingProgress.message && (
          <div className="text-sm text-muted-foreground">
            {processingProgress.message}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default M3UProgress;
