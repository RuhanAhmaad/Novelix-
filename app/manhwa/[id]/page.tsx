'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { ManhwaViewer } from '@/components/ManhwaViewer';
import { SAMPLE_BOOKS } from '@/utils/sampleData';

export default function ManhwaPage() {
  const params = useParams();
  const bookId = params.id as string;

  const book = SAMPLE_BOOKS.find((b) => b.id === bookId) || SAMPLE_BOOKS[1];

  // Sample chapters with vertical manhwa strips
  const sampleChapters = [
    {
      id: 'ch-1',
      chapter_number: 1,
      title: 'The Reawakening of the Shadow Monarch',
      season_number: 1,
      images: [
        {
          id: 'img-1-1',
          url: 'https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=1000&q=80',
          page_number: 1,
        },
        {
          id: 'img-1-2',
          url: 'https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=1000&q=80',
          page_number: 2,
        },
        {
          id: 'img-1-3',
          url: 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=1000&q=80',
          page_number: 3,
        },
      ],
    },
    {
      id: 'ch-2',
      chapter_number: 2,
      title: 'Dungeon of the Forgotten Kings',
      season_number: 1,
      images: [
        {
          id: 'img-2-1',
          url: 'https://images.unsplash.com/photo-1534447677768-be436bb09401?w=1000&q=80',
          page_number: 1,
        },
        {
          id: 'img-2-2',
          url: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?w=1000&q=80',
          page_number: 2,
        },
      ],
    },
    {
      id: 'ch-3',
      chapter_number: 3,
      title: 'Sigil of the Void Lord',
      season_number: 1,
      images: [
        {
          id: 'img-3-1',
          url: 'https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=1000&q=80',
          page_number: 1,
        },
      ],
    },
  ];

  return (
    <ManhwaViewer
      seriesId={book.id}
      seriesTitle={book.title}
      chapters={sampleChapters}
      currentChapterId="ch-1"
    />
  );
}
