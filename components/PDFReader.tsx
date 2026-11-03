'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  ChevronLeft, 
  ChevronRight, 
  ZoomIn, 
  ZoomOut, 
  Maximize, 
  Minimize, 
  Bookmark, 
  Globe, 
  Download, 
  Palette, 
  List, 
  Sliders,
  Check,
  RotateCcw
} from 'lucide-react';

interface LanguageEdition {
  code: string;
  name: string;
  fileUrl: string;
  fileName: string;
}

interface PDFReaderProps {
  bookId: string;
  bookTitle: string;
  languages: LanguageEdition[];
  initialLanguage?: string;
  allowDownload?: boolean;
  initialPage?: number;
}

export function PDFReader({
  bookId,
  bookTitle,
  languages,
  initialLanguage = 'en',
  allowDownload = false,
  initialPage = 1,
}: PDFReaderProps) {
  const [currentLang, setCurrentLang] = useState(initialLanguage);
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [numPages, setNumPages] = useState(1);
  const [scale, setScale] = useState(1.2);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [readerTheme, setReaderTheme] = useState<'dark' | 'sepia' | 'light'>('dark');
  const [bookmarks, setBookmarks] = useState<number[]>([]);
  const [showLangMenu, setShowLangMenu] = useState(false);
  const [showThemeMenu, setShowThemeMenu] = useState(false);
  const [showTOC, setShowTOC] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [renderError, setRenderError] = useState<string | null>(null);

  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const pdfDocRef = useRef<any>(null);

  const activeEdition = languages.find((l) => l.code === currentLang) || languages[0];

  // Load saved progress from API
  useEffect(() => {
    async function fetchProgress() {
      try {
        const res = await fetch(`/api/reading/progress?bookId=${bookId}&language=${currentLang}`);
        if (res.ok) {
          const data = await res.json();
          if (data.progress?.current_page) {
            setCurrentPage(data.progress.current_page);
          }
        }
      } catch (e) {
        console.error('Failed to load saved reading progress', e);
      }
    }
    fetchProgress();
  }, [bookId, currentLang]);

  // Load PDF document using PDF.js
  useEffect(() => {
    let isCancelled = false;
    setIsLoading(true);
    setRenderError(null);

    async function loadPdf() {
      try {
        const pdfjsLib = await import('pdfjs-dist');
        // Point worker to cdnjs or unpkg
        pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`;

        const loadingTask = pdfjsLib.getDocument(activeEdition.fileUrl);
        const pdf = await loadingTask.promise;

        if (isCancelled) return;

        pdfDocRef.current = pdf;
        setNumPages(pdf.numPages);
        setIsLoading(false);
        renderPage(currentPage, pdf);
      } catch (err: any) {
        console.error('Error loading PDF document:', err);
        if (!isCancelled) {
          setRenderError(err.message || 'Unable to render PDF file');
          setIsLoading(false);
        }
      }
    }

    loadPdf();

    return () => {
      isCancelled = true;
    };
  }, [activeEdition.fileUrl]);

  // Render specific page onto canvas
  const renderPage = async (pageNumber: number, pdfInstance?: any) => {
    const pdf = pdfInstance || pdfDocRef.current;
    if (!pdf || !canvasRef.current) return;

    try {
      const page = await pdf.getPage(pageNumber);
      const viewport = page.getViewport({ scale });

      const canvas = canvasRef.current;
      const context = canvas.getContext('2d');
      if (!context) return;

      canvas.height = viewport.height;
      canvas.width = viewport.width;

      const renderContext = {
        canvasContext: context,
        viewport: viewport,
      };

      await page.render(renderContext).promise;

      // Persist progress to server
      saveProgress(pageNumber, pdf.numPages);
    } catch (err) {
      console.error('Page render error:', err);
    }
  };

  // Re-render when page or scale changes
  useEffect(() => {
    if (pdfDocRef.current) {
      renderPage(currentPage);
    }
  }, [currentPage, scale]);

  const saveProgress = async (page: number, total: number) => {
    try {
      await fetch('/api/reading/progress', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          bookId,
          languageCode: currentLang,
          currentPage: page,
          totalPages: total,
        }),
      });
    } catch (e) {
      // offline silent
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) setCurrentPage((p) => p - 1);
  };

  const handleNextPage = () => {
    if (currentPage < numPages) setCurrentPage((p) => p + 1);
  };

  const toggleBookmark = () => {
    if (bookmarks.includes(currentPage)) {
      setBookmarks(bookmarks.filter((b) => b !== currentPage));
    } else {
      setBookmarks([...bookmarks, currentPage]);
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  const themeClasses = {
    dark: 'bg-[#0b0b10] text-zinc-100',
    sepia: 'bg-[#f4ecd8] text-[#5c4b37]',
    light: 'bg-[#fafafa] text-zinc-900',
  };

  const progressPercent = numPages > 0 ? Math.round((currentPage / numPages) * 100) : 0;

  return (
    <div
      ref={containerRef}
      className={`min-h-screen flex flex-col transition-colors duration-300 ${themeClasses[readerTheme]}`}
    >
      {/* Top Reading Toolbar */}
      <header className="sticky top-0 z-30 flex items-center justify-between px-4 py-3 bg-novelix-950/90 backdrop-blur-xl border-b border-novelix-800 text-white select-none">
        <div className="flex items-center gap-3">
          <Link
            href={`/book/${bookId}`}
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-850 transition-colors"
            title="Back to Book Details"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="max-w-xs sm:max-w-md truncate">
            <h1 className="text-sm font-bold truncate">{bookTitle}</h1>
            <p className="text-[11px] text-zinc-400 font-mono">
              Page {currentPage} of {numPages} ({progressPercent}%)
            </p>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center gap-2">
          {/* Language Switcher */}
          <div className="relative">
            <button
              onClick={() => setShowLangMenu(!showLangMenu)}
              className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-medium bg-novelix-900 border border-novelix-800 hover:border-novelix-neon transition-colors"
              title="Select Language Edition"
            >
              <Globe className="w-3.5 h-3.5 text-novelix-neon" />
              <span className="hidden sm:inline">{activeEdition.name}</span>
            </button>

            {showLangMenu && (
              <div className="absolute right-0 mt-2 w-48 rounded-xl bg-novelix-900 border border-novelix-800 shadow-2xl py-1 z-50">
                <div className="px-3 py-1.5 text-[10px] uppercase font-bold text-zinc-400 border-b border-novelix-800">
                  Available Editions
                </div>
                {languages.map((lang) => (
                  <button
                    key={lang.code}
                    onClick={() => {
                      setCurrentLang(lang.code);
                      setShowLangMenu(false);
                      setCurrentPage(1);
                    }}
                    className="w-full flex items-center justify-between px-3 py-2 text-xs text-left text-zinc-300 hover:text-white hover:bg-novelix-800 transition-colors"
                  >
                    <span>{lang.name}</span>
                    {lang.code === currentLang && <Check className="w-3.5 h-3.5 text-novelix-neon" />}
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Theme Palette */}
          <div className="relative">
            <button
              onClick={() => setShowThemeMenu(!showThemeMenu)}
              className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-850"
              title="Reader Colors"
            >
              <Palette className="w-4 h-4" />
            </button>

            {showThemeMenu && (
              <div className="absolute right-0 mt-2 p-2 rounded-xl bg-novelix-900 border border-novelix-800 shadow-2xl flex gap-2 z-50">
                <button
                  onClick={() => { setReaderTheme('dark'); setShowThemeMenu(false); }}
                  className="w-7 h-7 rounded-full bg-[#0b0b10] border border-novelix-700 hover:scale-110 transition-transform"
                  title="Dark Onyx"
                />
                <button
                  onClick={() => { setReaderTheme('sepia'); setShowThemeMenu(false); }}
                  className="w-7 h-7 rounded-full bg-[#f4ecd8] border border-amber-300 hover:scale-110 transition-transform"
                  title="Warm Sepia"
                />
                <button
                  onClick={() => { setReaderTheme('light'); setShowThemeMenu(false); }}
                  className="w-7 h-7 rounded-full bg-[#ffffff] border border-zinc-300 hover:scale-110 transition-transform"
                  title="Paper White"
                />
              </div>
            )}
          </div>

          {/* Bookmark Button */}
          <button
            onClick={toggleBookmark}
            className={`p-2 rounded-xl border transition-colors ${
              bookmarks.includes(currentPage)
                ? 'bg-novelix-electric/30 border-novelix-neon text-novelix-neon'
                : 'text-zinc-400 hover:text-white hover:bg-novelix-900 border-novelix-850'
            }`}
            title="Bookmark this page"
          >
            <Bookmark className={`w-4 h-4 ${bookmarks.includes(currentPage) ? 'fill-novelix-neon' : ''}`} />
          </button>

          {/* Zoom In / Out */}
          <div className="hidden md:flex items-center gap-1 bg-novelix-900 rounded-xl p-0.5 border border-novelix-850">
            <button
              onClick={() => setScale((s) => Math.max(0.6, s - 0.2))}
              className="p-1.5 text-zinc-400 hover:text-white rounded-lg"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <span className="text-[10px] font-mono px-1 text-zinc-300">{Math.round(scale * 100)}%</span>
            <button
              onClick={() => setScale((s) => Math.min(2.5, s + 0.2))}
              className="p-1.5 text-zinc-400 hover:text-white rounded-lg"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Fullscreen */}
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-850"
            title="Fullscreen"
          >
            {isFullscreen ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
          </button>

          {/* Download if permitted */}
          {allowDownload && (
            <a
              href={activeEdition.fileUrl}
              download={activeEdition.fileName}
              className="p-2 rounded-xl text-novelix-neon hover:text-white bg-novelix-electric/20 border border-novelix-electric/40"
              title="Download PDF"
            >
              <Download className="w-4 h-4" />
            </a>
          )}
        </div>
      </header>

      {/* Reading Progress Line */}
      <div className="w-full bg-novelix-950 h-1">
        <div
          className="bg-gradient-to-r from-novelix-purple to-novelix-neon h-full transition-all duration-300"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      {/* Main Canvas Viewport */}
      <main className="flex-1 flex items-center justify-center p-4 sm:p-8 overflow-auto relative">
        {isLoading && (
          <div className="text-center space-y-3 py-16">
            <div className="w-10 h-10 border-4 border-novelix-electric border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs font-semibold text-zinc-400 tracking-wide">
              Loading {activeEdition.name} Edition...
            </p>
          </div>
        )}

        {renderError && (
          <div className="max-w-md p-6 rounded-2xl bg-novelix-900 border border-novelix-800 text-center space-y-3">
            <p className="text-sm font-bold text-red-400">PDF Reader Notice</p>
            <p className="text-xs text-zinc-400 leading-relaxed">
              {renderError}. Verify document permissions or Google Drive authentication status.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-electric text-white"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span>Retry</span>
            </button>
          </div>
        )}

        <div className={`shadow-2xl rounded-xl overflow-hidden transition-opacity duration-300 ${isLoading ? 'opacity-0' : 'opacity-100'}`}>
          <canvas ref={canvasRef} className="max-w-full h-auto block" />
        </div>
      </main>

      {/* Bottom Floating Navigation Bar */}
      <footer className="sticky bottom-4 mx-auto z-30 flex items-center gap-4 px-4 py-2 rounded-2xl bg-novelix-950/90 backdrop-blur-xl border border-novelix-800 shadow-2xl text-white">
        <button
          onClick={handlePrevPage}
          disabled={currentPage <= 1}
          className="p-2 rounded-xl text-zinc-300 hover:text-white disabled:opacity-40 disabled:hover:text-zinc-300 transition-colors"
          title="Previous Page"
        >
          <ChevronLeft className="w-5 h-5" />
        </button>

        <div className="flex items-center gap-2 text-xs font-mono">
          <input
            type="number"
            min={1}
            max={numPages}
            value={currentPage}
            onChange={(e) => {
              const val = parseInt(e.target.value);
              if (val >= 1 && val <= numPages) setCurrentPage(val);
            }}
            className="w-12 bg-novelix-900 text-center py-1 rounded-lg border border-novelix-800 font-bold focus:outline-none focus:border-novelix-neon"
          />
          <span className="text-zinc-500">/</span>
          <span className="text-zinc-400">{numPages}</span>
        </div>

        <button
          onClick={handleNextPage}
          disabled={currentPage >= numPages}
          className="p-2 rounded-xl text-zinc-300 hover:text-white disabled:opacity-40 disabled:hover:text-zinc-300 transition-colors"
          title="Next Page"
        >
          <ChevronRight className="w-5 h-5" />
        </button>
      </footer>
    </div>
  );
}
