"use client";

import React, { useState } from 'react';

// ── Types ────────────────────────────────────────────────────────────────────

interface TreeNode {
  name: string;
  path: string;          // full path from repo root
  isDir: boolean;
  children: TreeNode[];
}

interface FileTreeProps {
  files: string[];
  selectedFile: string | null;
  onFileSelect: (path: string) => void;
}

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Build a nested TreeNode structure from a flat list of file paths. */
function buildTree(paths: string[]): TreeNode[] {
  const root: TreeNode = { name: '', path: '', isDir: true, children: [] };

  for (const filePath of paths) {
    const parts = filePath.split('/').filter(Boolean);
    let node = root;
    for (let i = 0; i < parts.length; i++) {
      const part = parts[i];
      const fullPath = parts.slice(0, i + 1).join('/');
      const isLast = i === parts.length - 1;
      let child = node.children.find(c => c.name === part);
      if (!child) {
        child = { name: part, path: fullPath, isDir: !isLast, children: [] };
        node.children.push(child);
      }
      if (!isLast) node = child;
    }
  }

  // Sort: directories first, then files, alphabetically within each group
  function sort(nodes: TreeNode[]) {
    nodes.sort((a, b) => {
      if (a.isDir !== b.isDir) return a.isDir ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
    nodes.forEach(n => sort(n.children));
  }
  sort(root.children);
  return root.children;
}

/** Return a simple icon string based on file extension. */
function fileIcon(name: string): string {
  const ext = name.split('.').pop()?.toLowerCase() ?? '';
  const map: Record<string, string> = {
    py: '🐍', js: '📜', jsx: '⚛️', ts: '📘', tsx: '⚛️',
    json: '📋', md: '📝', txt: '📄', html: '🌐', css: '🎨',
    yaml: '⚙️', yml: '⚙️', toml: '⚙️', sh: '🖥️', java: '☕',
    go: '🐹', rs: '🦀', cpp: '🔧', c: '🔧', h: '🔧',
    dockerfile: '🐳', gitignore: '🚫', env: '🔐',
  };
  return map[ext] ?? '📄';
}

// ── TreeRow component ─────────────────────────────────────────────────────────

function TreeRow({
  node,
  depth,
  selectedFile,
  onFileSelect,
}: {
  node: TreeNode;
  depth: number;
  selectedFile: string | null;
  onFileSelect: (path: string) => void;
}) {
  const [open, setOpen] = useState(depth < 2); // auto-expand first two levels
  const isSelected = !node.isDir && selectedFile === node.path;

  return (
    <li>
      <button
        onClick={() => node.isDir ? setOpen(o => !o) : onFileSelect(node.path)}
        style={{ paddingLeft: `${depth * 14 + 8}px` }}
        className={[
          'w-full flex items-center gap-1.5 py-1 pr-3 text-left text-xs rounded-md transition-colors group',
          isSelected
            ? 'bg-green-500/20 text-green-300'
            : node.isDir
              ? 'text-green-100/70 hover:bg-green-500/10 hover:text-green-100'
              : 'text-green-100/60 hover:bg-green-500/10 hover:text-green-100',
        ].join(' ')}
      >
        {/* Chevron for directories */}
        {node.isDir && (
          <svg
            className={`w-3 h-3 flex-shrink-0 transition-transform ${open ? 'rotate-90' : ''}`}
            fill="none" stroke="currentColor" viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        )}
        {/* Icon */}
        <span className="flex-shrink-0 text-[11px]">
          {node.isDir ? (open ? '📂' : '📁') : fileIcon(node.name)}
        </span>
        {/* Name */}
        <span className="truncate font-mono">{node.name}</span>
      </button>

      {node.isDir && open && node.children.length > 0 && (
        <ul>
          {node.children.map(child => (
            <TreeRow
              key={child.path}
              node={child}
              depth={depth + 1}
              selectedFile={selectedFile}
              onFileSelect={onFileSelect}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

// ── Main FileTree component ───────────────────────────────────────────────────

export default function FileTree({ files, selectedFile, onFileSelect }: FileTreeProps) {
  const tree = buildTree(files);

  if (files.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-green-100/40 text-xs gap-2 p-4">
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
            d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
        </svg>
        <span>No files indexed</span>
      </div>
    );
  }

  return (
    <ul className="select-none">
      {tree.map(node => (
        <TreeRow
          key={node.path}
          node={node}
          depth={0}
          selectedFile={selectedFile}
          onFileSelect={onFileSelect}
        />
      ))}
    </ul>
  );
}
