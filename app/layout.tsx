import type { Metadata } from 'next';
import './globals.css';
import { ThemeProvider } from '@/components/ThemeProvider';
import { AppShell } from '@/components/AppShell';

export const metadata: Metadata = {
  title: 'NOVELIX — Read Beyond Limits. Create Without Boundaries.',
  description:
    'Advanced digital publishing platform for books, novels, comics, and manhwa with multi-language editions and Google Drive synchronization.',
  keywords: [
    'novels',
    'books',
    'publishing',
    'manhwa',
    'manga',
    'comics',
    'pdf reader',
    'authors',
    'google drive storage',
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-novelix-950 text-zinc-100 antialiased">
        <ThemeProvider>
          <AppShell>{children}</AppShell>
        </ThemeProvider>
      </body>
    </html>
  );
}
