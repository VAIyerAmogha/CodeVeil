import React from 'react';

interface FilePathBreadcrumbProps {
  filePath: string;
  repoName: string;
}

export default function FilePathBreadcrumb({ filePath, repoName }: FilePathBreadcrumbProps) {
  const parts = filePath.split('/').filter(Boolean);
  
  return (
    <div className="font-mono text-sm text-zinc-400 flex items-center flex-wrap">
      <span>{repoName}</span>
      {parts.map((part, index) => (
        <React.Fragment key={index}>
          <span className="text-zinc-600 mx-2">/</span>
          <span>{part}</span>
        </React.Fragment>
      ))}
    </div>
  );
}
