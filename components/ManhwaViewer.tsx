'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { 
  ArrowLeft, 
  ChevronLeft, 
  ChevronRight, 
  Maximize, 
  Minimize, 
  Bookmark, 
  List, 
  Layers, 
  ScrollText, 
  BookOpen, 
  Eye, 
  Heart 
} from 'lucide-react';

interface Chapter {
  id: string;
  chapter_number: number;
  title: string;
  season_number?: number;
  images: { id: string; url: string; page_number: number }[];
}

interface ManhwaViewerProps {
  seriesId: string;
  seriesTitle: string;
  chapters: Chapter[];
  currentChapterId: string;
}

export function ManhwaViewer({
  seriesId,
  seriesTitle,
  chapters,
  currentChapterId,
}: ManhwaViewerProps) {
  const [activeChapterId, setActiveChapterId] = useState(currentChapterId);
  const [viewMode, setViewMode] = useState<'vertical' | 'paginated'>('vertical');
  const [pageIndex, setPageIndex] = useState(0);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showChapterDrawer, setShowChapterDrawer] = useState(false);
  const [bookmarked, setBookmarked] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);

  const activeChapter = chapters.find((c) => c.id === activeChapterId) || chapters[0];
  const sortedImages = [...(activeChapter?.images || [])].sort((a, b) => a.page_number - b.page_number);

  const currentChapterIdx = chapters.findIndex((c) => c.id === activeChapterId);
  const prevChapter = currentChapterIdx > 0 ? chapters[currentChapterIdx - 1] : null;
  const nextChapter = currentChapterIdx < chapters.length - 1 ? chapters[currentChapterIdx + 1] : null;

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen();
      setIsFullscreen(true);
    } else {
      document.exitFullscreen();
      setIsFullscreen(false);
    }
  };

  return (
    <div ref={containerRef} className="min-h-screen bg-novelix-950 text-white flex flex-col">
      {/* Top Header Controls */}
      <header className="sticky top-0 z-40 bg-novelix-950/90 backdrop-blur-xl border-b border-novelix-800 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Link
            href={`/book/${seriesId}`}
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-800 transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div className="max-w-xs sm:max-w-md truncate">
            <h1 className="text-sm font-bold text-white truncate">{seriesTitle}</h1>
            <p className="text-[11px] text-novelix-neon font-mono truncate">
              Ch. {activeChapter.chapter_number}: {activeChapter.title}
            </p>
          </div>
        </div>

        {/* Action icons */}
        <div className="flex items-center gap-2">
          {/* Mode Switch: Continuous Vertical Scroll vs Paginated */}
          <button
            onClick={() => setViewMode(viewMode === 'vertical' ? 'paginated' : 'vertical')}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-novelix-900 border border-novelix-800 hover:border-novelix-neon text-zinc-300 hover:text-white transition-colors"
            title="Toggle Continuous Webtoon Scroll / Page Mode"
          >
            {viewMode === 'vertical' ? (
              <>
                <ScrollText className="w-3.5 h-3.5 text-novelix-neon" />
                <span className="hidden sm:inline">Webtoon Scroll</span>
              </>
            ) : (
              <>
                <BookOpen className="w-3.5 h-3.5 text-novelix-electric" />
                <span className="hidden sm:inline">Page Mode</span>
              </>
            )}
          </button>

          {/* Chapters Drawer Trigger */}
          <button
            onClick={() => setShowChapterDrawer(true)}
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-800"
            title="Chapters List"
          >
            <List className="w-4 h-4" />
          </button>

          {/* Fullscreen Toggle */}
          <button
            onClick={toggleFullscreen}
            className="p-2 rounded-xl text-zinc-400 hover:text-white hover:bg-novelix-900 border border-novelix-800"
            title="Fullscreen"
          >
            {isFullscreen ? <Minimize className="w-4 h-4" /> : <Maximize className="w-4 h-4" />}
          </button>
        </div>
      </header>

      {/* Main Reading Canvas */}
      <main className="flex-1 flex flex-col items-center justify-center p-0 select-none">
        {viewMode === 'vertical' ? (
          /* Continuous Vertical Webtoon Strip */
          <div className="w-full max-w-2xl mx-auto flex flex-col items-center bg-black">
            {sortedImages.map((img, idx) => (
              <img
                key={img.id || idx}
                src={img.url}
                alt={`Page ${idx + 1}`}
                className="w-full h-auto block"
                loading={idx < 3 ? 'eager' : 'lazy'}
              />
            ))}

            {/* End of chapter banner */}
            <div className="w-full p-8 text-center bg-novelix-900 border-t border-novelix-800 my-8 rounded-2xl max-w-xl mx-4 space-y-4">
              <h3 className="text-base font-bold text-white">
                You completed Chapter {activeChapter.chapter_number}!
              </h3>
              <p className="text-xs text-zinc-400">
                Support the creators by giving a star rating or following the series.
              </p>

              <div className="flex items-center justify-center gap-3 pt-2">
                {prevChapter && (
                  <button
                    onClick={() => {
                      setActiveChapterId(prevChapter.id);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className="px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-800 hover:bg-novelix-750 text-white transition-colors"
                  >
                    ← Previous Ch. {prevChapter.chapter_number}
                  </button>
                )}

                {nextChapter && (
                  <button
                    onClick={() => {
                      setActiveChapterId(nextChapter.id);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    className="px-5 py-2 rounded-xl text-xs font-bold bg-gradient-to-r from-novelix-purple to-novelix-neon text-white shadow-glow-sm hover:scale-105 transition-all"
                  >
                    Next Ch. {nextChapter.chapter_number} →
                  </button>
                )}
              </div>
            </div>
          </div>
        ) : (
          /* Single Page / Manga View */
          <div className="w-full max-w-3xl flex flex-col items-center p-4">
            {sortedImages[pageIndex] && (
              <img
                src={sortedImages[pageIndex].url}
                alt={`Page ${pageIndex + 1}`}
                className="max-h-[85vh] w-auto rounded-lg shadow-2xl block"
              />
            )}

            {/* Page navigation controls */}
            <div className="flex items-center gap-4 mt-6">
              <button
                onClick={() => setPageIndex((p) => Math.max(0, p - 1))}
                disabled={pageIndex === 0}
                className="p-2.5 rounded-xl bg-novelix-900 border border-novelix-800 disabled:opacity-40"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>

              <span className="text-xs font-mono text-zinc-400">
                Page {pageIndex + 1} of {sortedImages.length}
              </span>

              <button
                onClick={() => setPageIndex((p) => Math.min(sortedImages.length - 1, p + 1))}
                disabled={pageIndex >= sortedImages.length - 1}
                className="p-2.5 rounded-xl bg-novelix-900 border border-novelix-800 disabled:opacity-40"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Chapters Sidebar Drawer */}
      {showChapterDrawer && (
        <div className="fixed inset-0 z-50 flex justify-end bg-black/60 backdrop-blur-sm animate-in fade-in">
          <div className="w-80 h-full bg-novelix-900 border-l border-novelix-800 p-6 flex flex-col shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-novelix-800 mb-4">
              <h3 className="font-bold text-sm text-white">Series Chapters</h3>
              <button
                onClick={() => setShowChapterDrawer(false)}
                className="p-1 rounded-lg text-zinc-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="flex-1 overflow-y-auto space-y-2">
              {chapters.map((ch) => (
                <button
                  key={ch.id}
                  onClick={() => {
                    setActiveChapterId(ch.id);
                    setShowChapterDrawer(false);
                    setPageIndex(0);
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                  }}
                  className={`w-full text-left p-3 rounded-xl transition-all flex items-center justify-between ${
                    ch.id === activeChapterId
                      ? 'bg-novelix-electric/25 border border-novelix-neon text-white font-bold'
                      : 'bg-novelix-950/60 hover:bg-novelix-850 text-zinc-300 border border-transparent'
                  }`}
                >
                  <div>
                    <p className="text-xs">Chapter {ch.chapter_number}</p>
                    <p className="text-[11px] text-zinc-400 truncate max-w-[180px]">{ch.title}</p>
                  </div>
                  <span className="text-[10px] text-zinc-400 font-mono">
                    {ch.images?.length || 0}p
                  </span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
