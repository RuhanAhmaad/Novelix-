'use client';

import React, { Suspense } from 'react';
import { useParams, useSearchParams } from 'next/navigation';
import { PDFReader } from '@/components/PDFReader';
import { SAMPLE_BOOKS, SAMPLE_SAMPLE_PDF } from '@/utils/sampleData';

function ReaderContent() {
  const params = useParams();
  const searchParams = useSearchParams();
  const bookId = params.id as string;
  const initialLang = searchParams.get('lang') || 'en';

  const book = SAMPLE_BOOKS.find((b) => b.id === bookId) || SAMPLE_BOOKS[0];

  const languageEditions = [
    {
      code: 'en',
      name: 'English Edition',
      fileUrl: SAMPLE_SAMPLE_PDF,
      fileName: `${book.title}_EN.pdf`,
    },
    {
      code: 'ur',
      name: 'Urdu (اردو)',
      fileUrl: SAMPLE_SAMPLE_PDF,
      fileName: `${book.title}_UR.pdf`,
    },
    {
      code: 'ar',
      name: 'Arabic (العربية)',
      fileUrl: SAMPLE_SAMPLE_PDF,
      fileName: `${book.title}_AR.pdf`,
    },
    {
      code: 'es',
      name: 'Spanish (Español)',
      fileUrl: SAMPLE_SAMPLE_PDF,
      fileName: `${book.title}_ES.pdf`,
    },
  ];

  return (
    <PDFReader
      bookId={book.id}
      bookTitle={book.title}
      languages={languageEditions}
      initialLanguage={initialLang}
      allowDownload={true}
    />
  );
}

export default function ReaderPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-novelix-950 flex items-center justify-center">
        <div className="w-8 h-8 border-4 border-novelix-electric border-t-transparent rounded-full animate-spin" />
      </div>
    }>
      <ReaderContent />
    </Suspense>
  );
}
