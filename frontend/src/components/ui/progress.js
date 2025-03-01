import React from 'react';

export const Progress = ({ value, className }) => (
  <div className={`h-2 w-full overflow-hidden rounded-full bg-gray-200 ${className}`}>
    <div
      className="h-full bg-primary transition-all duration-300"
      style={{ width: `${value}%` }}
    />
  </div>
); 