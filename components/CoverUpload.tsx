'use client';

import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, Trash2, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';

interface CoverUploadProps {
  value?: string;
  onChange: (url: string) => void;
  className?: string;
}

export function CoverUpload({ value, onChange, className = '' }: CoverUploadProps) {
  const [preview, setPreview] = useState<string | null>(value || null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);

    // Validate type
    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      setError('Please upload a valid image (JPG, PNG, or WebP).');
      return;
    }

    // Validate size (max 16MB)
    if (file.size > 16 * 1024 * 1024) {
      setError('Image file is too large (maximum 16MB).');
      return;
    }

    // Create local preview immediately
    const reader = new FileReader();
    reader.onload = (event) => {
      setPreview(event.target?.result as string);
    };
    reader.readAsDataURL(file);

    // Upload to ImgBB via our secure API route
    setIsUploading(true);
    setUploadProgress(20);

    const formData = new FormData();
    formData.append('image', file);

    try {
      // Simulate progress progression
      const progressTimer = setInterval(() => {
        setUploadProgress((prev) => (prev < 90 ? prev + 15 : prev));
      }, 250);

      const res = await fetch('/api/upload/cover', {
        method: 'POST',
        body: formData,
      });

      clearInterval(progressTimer);
      setUploadProgress(100);

      const data = await res.json();

      if (!res.ok || !data.success) {
        throw new Error(data.error || 'ImgBB upload failed');
      }

      setPreview(data.url);
      onChange(data.url);
    } catch (err: any) {
      setError(err.message || 'Failed to upload cover image');
      // If failed and no previous value, reset preview
      if (!value) setPreview(null);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const handleRemove = (e: React.MouseEvent) => {
    e.stopPropagation();
    setPreview(null);
    onChange('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const triggerUpload = () => {
    if (!isUploading) {
      fileInputRef.current?.click();
    }
  };

  return (
    <div className={`space-y-2 ${className}`}>
      <input
        ref={fileInputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,image/jpg"
        onChange={handleFileSelect}
        className="hidden"
      />

      {preview ? (
        <div className="relative group rounded-2xl overflow-hidden aspect-[2/3] w-full max-w-[240px] border border-novelix-800 bg-novelix-950 shadow-lg">
          <img
            src={preview}
            alt="Cover Preview"
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
          />

          {/* Action overlay */}
          <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex flex-col items-center justify-center gap-2 p-3">
            <button
              type="button"
              onClick={triggerUpload}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-novelix-electric text-white hover:bg-novelix-violet transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Replace</span>
            </button>

            <button
              type="button"
              onClick={handleRemove}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-red-600/80 text-white hover:bg-red-600 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Remove</span>
            </button>
          </div>

          <div className="absolute bottom-2 left-2 right-2 bg-black/70 backdrop-blur-md px-2 py-1 rounded text-[10px] text-novelix-neon flex items-center justify-center gap-1">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            <span>ImgBB Hosted Cover</span>
          </div>
        </div>
      ) : (
        <div
          onClick={triggerUpload}
          className={`border-2 border-dashed rounded-2xl aspect-[2/3] w-full max-w-[240px] flex flex-col items-center justify-center p-6 text-center cursor-pointer transition-all duration-200 ${
            isUploading
              ? 'border-novelix-electric bg-novelix-900/40'
              : 'border-novelix-800 hover:border-novelix-neon bg-novelix-950/60 hover:bg-novelix-900/60'
          }`}
        >
          {isUploading ? (
            <div className="space-y-3 w-full px-4">
              <RefreshCw className="w-8 h-8 text-novelix-neon animate-spin mx-auto" />
              <p className="text-xs text-white font-medium">Uploading to ImgBB...</p>
              <div className="w-full h-1.5 bg-novelix-800 rounded-full overflow-hidden">
                <div
                  className="h-full bg-novelix-neon transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="w-12 h-12 rounded-full bg-novelix-900 border border-novelix-800 flex items-center justify-center mx-auto text-novelix-neon group-hover:scale-110 transition-transform">
                <UploadCloud className="w-6 h-6" />
              </div>
              <div>
                <p className="text-xs font-bold text-white">Click or drag book cover</p>
                <p className="text-[11px] text-zinc-400 mt-0.5">JPG, PNG, WebP up to 16MB</p>
              </div>
              <span className="inline-block text-[10px] px-2.5 py-1 rounded-md bg-novelix-850 text-novelix-neon border border-novelix-800">
                ImgBB Powered
              </span>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="flex items-center gap-1.5 text-xs text-red-400 bg-red-500/10 border border-red-500/20 px-3 py-1.5 rounded-xl">
          <AlertCircle className="w-3.5 h-3.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}
    </div>
  );
}
