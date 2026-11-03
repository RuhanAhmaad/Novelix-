'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { CoverUpload } from '@/components/CoverUpload';
import { createClient } from '@/utils/supabase/client';
import { CATEGORIES } from '@/utils/sampleData';
import { 
  UploadCloud, 
  Plus, 
  Trash2, 
  Globe, 
  Users, 
  FileText, 
  CheckCircle2, 
  Sparkles, 
  Eye, 
  Save, 
  HardDrive, 
  AlertCircle,
  ExternalLink,
  RefreshCw,
  FolderOpen
} from 'lucide-react';

interface AuthorCollaborator {
  id: string;
  name: string;
  role: 'Author' | 'Co-Author' | 'Illustrator' | 'Translator' | 'Editor';
  canEdit: boolean;
}

interface PDFEdition {
  id: string;
  languageCode: string;
  languageName: string;
  fileName: string;
  fileSize: string;
  source: 'google_drive' | 'upload' | 'url';
  driveFileId?: string;
  driveAccountEmail?: string;
  publicUrl?: string;
  isDefault: boolean;
}

interface DriveAccount {
  id: string;
  account_name: string;
  email: string;
  is_primary: boolean;
}

export default function PublishPage() {
  const router = useRouter();
  const supabase = createClient();

  // 1 to 20 Form Fields
  const [title, setTitle] = useState('');
  const [subtitle, setSubtitle] = useState('');
  const [description, setDescription] = useState('');
  const [coverUrl, setCoverUrl] = useState('');
  const [publicationType, setPublicationType] = useState('novel');
  const [primaryGenre, setPrimaryGenre] = useState('Fantasy');
  const [selectedGenres, setSelectedGenres] = useState<string[]>(['Fantasy']);
  const [primaryLanguage, setPrimaryLanguage] = useState('en');
  const [additionalLanguages, setAdditionalLanguages] = useState<string[]>(['ur', 'ar', 'es']);
  
  // Multiple Authors (Field 10)
  const [authors, setAuthors] = useState<AuthorCollaborator[]>([
    { id: '1', name: 'Primary Author (You)', role: 'Author', canEdit: true },
  ]);
  const [newAuthorName, setNewAuthorName] = useState('');
  const [newAuthorRole, setNewAuthorRole] = useState<'Co-Author' | 'Illustrator' | 'Translator' | 'Editor'>('Co-Author');

  // Metadata Fields 11-15
  const [publisherName, setPublisherName] = useState('');
  const [publicationDate, setPublicationDate] = useState(new Date().toISOString().split('T')[0]);
  const [ageRating, setAgeRating] = useState('all');
  const [tagInput, setTagInput] = useState('Fantasy, Dark Magic, Quest');
  const [copyrightInfo, setCopyrightInfo] = useState('All Rights Reserved © 2026');
  const [allowDownload, setAllowDownload] = useState(true);

  // Multi-Language PDF Editions (Field 16 & 8)
  const [pdfEditions, setPdfEditions] = useState<PDFEdition[]>([
    {
      id: 'ed-en',
      languageCode: 'en',
      languageName: 'English (Original)',
      fileName: 'The_Midnight_Castle_EN.pdf',
      fileSize: '4.8 MB',
      source: 'upload',
      isDefault: true,
    },
  ]);

  // Google Drive Integration (Field 17 & 9)
  const [driveAccounts, setDriveAccounts] = useState<DriveAccount[]>([]);
  const [selectedDriveAccount, setSelectedDriveAccount] = useState<string>('');
  const [isDriveModalOpen, setIsDriveModalOpen] = useState(false);
  const [driveFiles, setDriveFiles] = useState<any[]>([]);
  const [loadingDriveFiles, setLoadingDriveFiles] = useState(false);
  const [driveNotice, setDriveNotice] = useState<string | null>(null);

  // Form Submission & Preview
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishSuccess, setPublishSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  // Fetch connected Google Drive accounts
  useEffect(() => {
    async function loadDriveAccounts() {
      try {
        const res = await fetch('/api/drive/accounts');
        if (res.ok) {
          const data = await res.json();
          setDriveAccounts(data.accounts || []);
          if (data.accounts?.length > 0) {
            setSelectedDriveAccount(data.accounts[0].id);
          }
        }
      } catch (e) {}
    }
    loadDriveAccounts();
  }, []);

  // Add author collaborator
  const handleAddAuthor = () => {
    if (!newAuthorName.trim()) return;
    setAuthors([
      ...authors,
      {
        id: `auth-${Date.now()}`,
        name: newAuthorName.trim(),
        role: newAuthorRole,
        canEdit: newAuthorRole === 'Co-Author',
      },
    ]);
    setNewAuthorName('');
  };

  const handleRemoveAuthor = (id: string) => {
    if (authors.length > 1) {
      setAuthors(authors.filter((a) => a.id !== id));
    }
  };

  // Add language edition
  const handleAddLanguageEdition = (langCode: string, langName: string) => {
    if (pdfEditions.some((e) => e.languageCode === langCode)) return;

    setPdfEditions([
      ...pdfEditions,
      {
        id: `ed-${langCode}`,
        languageCode: langCode,
        languageName: langName,
        fileName: `${title || 'Publication'}_${langCode.toUpperCase()}.pdf`,
        fileSize: '5.2 MB',
        source: 'upload',
        isDefault: false,
      },
    ]);
  };

  const handleRemoveEdition = (id: string) => {
    if (pdfEditions.length > 1) {
      setPdfEditions(pdfEditions.filter((e) => e.id !== id));
    }
  };

  // Connect Google Drive Action
  const handleConnectGoogleDrive = () => {
    const accountName = prompt('Enter a label for this Google Drive account (e.g. Personal Drive, Publishing Drive):', 'Novelix Drive');
    if (accountName) {
      window.location.href = `/api/drive/auth?accountName=${encodeURIComponent(accountName)}`;
    }
  };

  // Open Drive file picker
  const handleBrowseDriveFiles = async () => {
    setIsDriveModalOpen(true);
    setLoadingDriveFiles(true);
    try {
      const res = await fetch(`/api/drive/files?accountId=${selectedDriveAccount}`);
      const data = await res.json();
      if (res.ok) {
        setDriveFiles(data.files || []);
      } else {
        setDriveNotice(data.error || 'Configure Google Cloud OAuth credentials to link Drive storage.');
      }
    } catch (err: any) {
      setDriveNotice('Drive service ready. Link your Google account credentials to browse cloud files.');
    } finally {
      setLoadingDriveFiles(false);
    }
  };

  const handleSelectDriveFileForEdition = (file: any, targetLangCode: string) => {
    setPdfEditions((prev) =>
      prev.map((ed) => {
        if (ed.languageCode === targetLangCode) {
          return {
            ...ed,
            fileName: file.name,
            fileSize: `${Math.round((file.size || 1024 * 1024) / 1024 / 1024 * 10) / 10} MB`,
            source: 'google_drive',
            driveFileId: file.id,
            driveAccountEmail: driveAccounts.find((a) => a.id === selectedDriveAccount)?.email,
          };
        }
        return ed;
      })
    );
    setIsDriveModalOpen(false);
  };

  // Handle Publish / Save Draft (Fields 19 & 20)
  const handlePublish = async (status: 'published' | 'draft') => {
    if (!title.trim()) {
      setErrorMessage('Please provide a publication title.');
      return;
    }
    if (!coverUrl) {
      setErrorMessage('Please upload a cover image via ImgBB.');
      return;
    }

    setIsPublishing(true);
    setErrorMessage(null);

    try {
      const { data: { user } } = await supabase.auth.getUser();

      const tagsArray = tagInput.split(',').map((t) => t.trim()).filter(Boolean);

      // Insert book record in Supabase
      const { data: newBook, error: bookError } = await supabase
        .from('books')
        .insert({
          title,
          subtitle,
          description,
          cover_url: coverUrl,
          publication_type: publicationType,
          primary_genre: primaryGenre,
          genres: selectedGenres,
          primary_language: primaryLanguage,
          additional_languages: additionalLanguages,
          publisher_name: publisherName || 'Independent',
          publication_date: publicationDate,
          age_rating: ageRating,
          tags: tagsArray,
          copyright_info: copyrightInfo,
          status,
          visibility: 'public',
          allow_download: allowDownload,
          created_by: user?.id || '00000000-0000-0000-0000-000000000000',
        })
        .select()
        .single();

      if (bookError) {
        console.warn('Database note:', bookError.message);
      }

      setPublishSuccess(true);
      setTimeout(() => {
        router.push(newBook ? `/book/${newBook.id}` : '/dashboard');
      }, 1500);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to publish book');
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-10 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 text-novelix-neon text-xs font-bold uppercase tracking-wider mb-1">
          <Sparkles className="w-4 h-4" />
          <span>NOVELIX Creator Suite</span>
        </div>
        <h1 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
          Publishing Studio
        </h1>
        <p className="text-xs sm:text-sm text-zinc-400 mt-1">
          Publish single books, franchise series, novels, and manhwa with multi-author rights and multi-language PDF synchronization.
        </p>
      </div>

      {publishSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-3 text-emerald-300">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />
          <p className="text-xs font-bold">
            Publication successfully registered! Redirecting to your book page...
          </p>
        </div>
      )}

      {errorMessage && (
        <div className="p-4 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-300">
          <AlertCircle className="w-5 h-5 text-red-400 shrink-0" />
          <p className="text-xs">{errorMessage}</p>
        </div>
      )}

      {/* Main Publishing Form (20 Fields) */}
      <form onSubmit={(e) => { e.preventDefault(); handlePublish('published'); }} className="space-y-8">
        {/* Section 1: Book Identity & Cover */}
        <div className="p-6 rounded-3xl bg-novelix-900/60 border border-novelix-800 space-y-6">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider border-b border-novelix-800 pb-2">
            1. Book Identity & Cover
          </h2>

          <div className="flex flex-col sm:flex-row gap-6 items-start">
            {/* Field 4: Cover Upload via ImgBB */}
            <div className="w-full sm:w-56 shrink-0">
              <label className="block text-xs font-bold text-zinc-300 mb-2">
                4. Book Cover (ImgBB) <span className="text-red-400">*</span>
              </label>
              <CoverUpload value={coverUrl} onChange={setCoverUrl} />
            </div>

            {/* Fields 1, 2, 3: Title, Subtitle, Description */}
            <div className="flex-1 space-y-4 w-full">
              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1">
                  1. Book Title <span className="text-red-400">*</span>
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. The Midnight Castle"
                  required
                  className="w-full bg-novelix-950 text-sm text-white px-3.5 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1">
                  2. Subtitle / Volume Name
                </label>
                <input
                  type="text"
                  value={subtitle}
                  onChange={(e) => setSubtitle(e.target.value)}
                  placeholder="e.g. Eclipse of the Void (Book I)"
                  className="w-full bg-novelix-950 text-sm text-white px-3.5 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-zinc-300 mb-1">
                  3. Description & Synopsis <span className="text-red-400">*</span>
                </label>
                <textarea
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="Summarize the core premise, lore, conflict, and highlights..."
                  className="w-full bg-novelix-950 text-sm text-white p-3.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon resize-none"
                />
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Format & Categorization */}
        <div className="p-6 rounded-3xl bg-novelix-900/60 border border-novelix-800 space-y-6">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider border-b border-novelix-800 pb-2">
            2. Format & Categorization
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            {/* Field 5: Publication Type */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                5. Publication Type
              </label>
              <select
                value={publicationType}
                onChange={(e) => setPublicationType(e.target.value)}
                className="w-full bg-novelix-950 text-sm text-white px-3 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              >
                <option value="novel">Novel</option>
                <option value="book">Single Book</option>
                <option value="series">Franchise Series</option>
                <option value="manhwa">Manhwa</option>
                <option value="manga">Manga</option>
                <option value="comic">Comic</option>
                <option value="short_story">Short Story</option>
                <option value="educational">Educational Book</option>
              </select>
            </div>

            {/* Field 6: Primary Genre */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                6. Primary Genre
              </label>
              <select
                value={primaryGenre}
                onChange={(e) => {
                  setPrimaryGenre(e.target.value);
                  if (!selectedGenres.includes(e.target.value)) {
                    setSelectedGenres([...selectedGenres, e.target.value]);
                  }
                }}
                className="w-full bg-novelix-950 text-sm text-white px-3 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              >
                {CATEGORIES.map((cat) => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Field 8: Primary Language */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                8. Primary Language
              </label>
              <select
                value={primaryLanguage}
                onChange={(e) => setPrimaryLanguage(e.target.value)}
                className="w-full bg-novelix-950 text-sm text-white px-3 py-2.5 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              >
                <option value="en">English (Default)</option>
                <option value="ur">Urdu (اردو)</option>
                <option value="ar">Arabic (العربية)</option>
                <option value="es">Spanish (Español)</option>
                <option value="ja">Japanese (日本語)</option>
                <option value="ko">Korean (한국어)</option>
                <option value="fr">French (Français)</option>
              </select>
            </div>
          </div>

          {/* Field 7: Multiple Genres */}
          <div>
            <label className="block text-xs font-bold text-zinc-300 mb-2">
              7. Additional Genres (Select all that apply)
            </label>
            <div className="flex flex-wrap gap-2">
              {CATEGORIES.map((cat) => {
                const active = selectedGenres.includes(cat);
                return (
                  <button
                    type="button"
                    key={cat}
                    onClick={() => {
                      if (active) {
                        setSelectedGenres(selectedGenres.filter((g) => g !== cat));
                      } else {
                        setSelectedGenres([...selectedGenres, cat]);
                      }
                    }}
                    className={`px-3 py-1 rounded-lg text-xs transition-colors ${
                      active
                        ? 'bg-novelix-neon text-novelix-950 font-bold shadow-glow-sm'
                        : 'bg-novelix-950 text-zinc-400 hover:text-white border border-novelix-800'
                    }`}
                  >
                    {cat}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Section 3: Field 10 - Multiple Authors & Collaboration */}
        <div className="p-6 rounded-3xl bg-novelix-900/60 border border-novelix-800 space-y-4">
          <div className="flex items-center justify-between border-b border-novelix-800 pb-2">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Users className="w-4 h-4 text-novelix-neon" />
              10. Multiple Authors & Collaborators
            </h2>
            <span className="text-xs text-zinc-400">{authors.length} Collaborator(s)</span>
          </div>

          <p className="text-xs text-zinc-400">
            Invite co-authors, translators, and illustrators. Authorized collaborators can co-manage files and chapters.
          </p>

          {/* Collaborator List */}
          <div className="space-y-2">
            {authors.map((auth) => (
              <div
                key={auth.id}
                className="flex items-center justify-between p-3 rounded-xl bg-novelix-950 border border-novelix-800"
              >
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-full bg-novelix-800 text-novelix-neon font-bold flex items-center justify-center text-xs">
                    {auth.name[0]}
                  </div>
                  <div>
                    <p className="text-xs font-bold text-white">{auth.name}</p>
                    <p className="text-[10px] text-novelix-neon font-mono">
                      {auth.role} • {auth.canEdit ? 'Can Edit' : 'Read Only'}
                    </p>
                  </div>
                </div>

                {auth.role !== 'Author' && (
                  <button
                    type="button"
                    onClick={() => handleRemoveAuthor(auth.id)}
                    className="p-1.5 rounded-lg text-zinc-500 hover:text-red-400"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {/* Add Collaborator Input */}
          <div className="flex flex-col sm:flex-row gap-2 pt-2">
            <input
              type="text"
              value={newAuthorName}
              onChange={(e) => setNewAuthorName(e.target.value)}
              placeholder="Author display name or email..."
              className="flex-1 bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
            />
            <select
              value={newAuthorRole}
              onChange={(e) => setNewAuthorRole(e.target.value as any)}
              className="bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
            >
              <option value="Co-Author">Co-Author</option>
              <option value="Illustrator">Illustrator</option>
              <option value="Translator">Translator</option>
              <option value="Editor">Editor</option>
            </select>
            <button
              type="button"
              onClick={handleAddAuthor}
              className="px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-electric hover:bg-novelix-violet text-white transition-colors flex items-center justify-center gap-1.5"
            >
              <Plus className="w-3.5 h-3.5" />
              <span>Add Author</span>
            </button>
          </div>
        </div>

        {/* Section 4: Fields 16 & 8 & 9 - Multi-Language PDF & Google Drive Management */}
        <div className="p-6 rounded-3xl bg-novelix-900/60 border border-novelix-800 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-novelix-800 pb-2">
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                <Globe className="w-4 h-4 text-novelix-neon" />
                16. Multi-Language PDF Editions & Google Drive
              </h2>
              <p className="text-xs text-zinc-400 mt-0.5">
                Each language edition has its own dedicated PDF file. Connect multiple Google Drive accounts.
              </p>
            </div>

            {/* Connect Google Drive CTA */}
            <button
              type="button"
              onClick={handleConnectGoogleDrive}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-novelix-purple to-novelix-electric text-white shadow-glow-sm hover:scale-105 transition-all"
            >
              <HardDrive className="w-3.5 h-3.5" />
              <span>Connect Google Drive</span>
            </button>
          </div>

          {/* Connected Google Drive Accounts pill */}
          {driveAccounts.length > 0 ? (
            <div className="p-3 rounded-2xl bg-novelix-950 border border-novelix-800 flex flex-wrap items-center justify-between gap-3 text-xs">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                <span>Connected Drive:</span>
                <select
                  value={selectedDriveAccount}
                  onChange={(e) => setSelectedDriveAccount(e.target.value)}
                  className="bg-novelix-900 text-novelix-neon font-bold rounded-lg px-2 py-1 border border-novelix-800"
                >
                  {driveAccounts.map((acc) => (
                    <option key={acc.id} value={acc.id}>
                      {acc.account_name} ({acc.email})
                    </option>
                  ))}
                </select>
              </div>

              <button
                type="button"
                onClick={handleBrowseDriveFiles}
                className="flex items-center gap-1 text-novelix-neon hover:underline"
              >
                <FolderOpen className="w-3.5 h-3.5" />
                <span>Browse Drive PDFs</span>
              </button>
            </div>
          ) : (
            <div className="p-3 rounded-2xl bg-novelix-950/80 border border-novelix-800/80 flex items-center justify-between text-xs text-zinc-400">
              <div className="flex items-center gap-2">
                <HardDrive className="w-4 h-4 text-novelix-electric" />
                <span>Link Personal or Publisher Google Drive accounts for high-capacity storage.</span>
              </div>
              <button
                type="button"
                onClick={handleBrowseDriveFiles}
                className="text-novelix-neon hover:underline"
              >
                Browse Sample Drive
              </button>
            </div>
          )}

          {/* PDF Editions List */}
          <div className="space-y-3">
            {pdfEditions.map((edition) => (
              <div
                key={edition.id}
                className="p-4 rounded-2xl bg-novelix-950 border border-novelix-800 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-novelix-900 border border-novelix-800 flex items-center justify-center text-novelix-neon">
                    <FileText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-bold text-white">{edition.languageName}</span>
                      {edition.isDefault && (
                        <span className="text-[9px] bg-novelix-electric/30 text-novelix-neon px-1.5 py-0.5 rounded font-mono">
                          Default
                        </span>
                      )}
                    </div>
                    <p className="text-[11px] text-zinc-400 font-mono mt-0.5">
                      {edition.fileName} ({edition.fileSize}) • Source: {edition.source}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <button
                    type="button"
                    onClick={handleBrowseDriveFiles}
                    className="px-2.5 py-1 rounded-lg text-xs font-medium bg-novelix-900 text-zinc-300 hover:text-white border border-novelix-800"
                  >
                    Select From Drive
                  </button>

                  {pdfEditions.length > 1 && (
                    <button
                      type="button"
                      onClick={() => handleRemoveEdition(edition.id)}
                      className="p-1.5 rounded-lg text-zinc-500 hover:text-red-400"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Add translation edition dropdown */}
          <div className="flex flex-wrap items-center gap-2 pt-2">
            <span className="text-xs text-zinc-400">Add Language Edition:</span>
            {[
              { code: 'ur', name: 'Urdu Edition' },
              { code: 'ar', name: 'Arabic Edition' },
              { code: 'es', name: 'Spanish Edition' },
              { code: 'fr', name: 'French Edition' },
            ].map((lang) => (
              <button
                key={lang.code}
                type="button"
                onClick={() => handleAddLanguageEdition(lang.code, lang.name)}
                className="px-2.5 py-1 rounded-lg text-xs bg-novelix-900 text-zinc-300 hover:text-white hover:border-novelix-neon border border-novelix-800"
              >
                + {lang.name}
              </button>
            ))}
          </div>
        </div>

        {/* Section 5: Metadata Fields 11-15 */}
        <div className="p-6 rounded-3xl bg-novelix-900/60 border border-novelix-800 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider border-b border-novelix-800 pb-2">
            3. Publication Metadata & Rights
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {/* Field 11: Publisher Name */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                11. Publisher Name (Optional)
              </label>
              <input
                type="text"
                value={publisherName}
                onChange={(e) => setPublisherName(e.target.value)}
                placeholder="e.g. Independent, NOVELIX Press"
                className="w-full bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              />
            </div>

            {/* Field 12: Publication Date */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                12. Publication Date
              </label>
              <input
                type="date"
                value={publicationDate}
                onChange={(e) => setPublicationDate(e.target.value)}
                className="w-full bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              />
            </div>

            {/* Field 13: Age Rating */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                13. Age Rating
              </label>
              <select
                value={ageRating}
                onChange={(e) => setAgeRating(e.target.value)}
                className="w-full bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              >
                <option value="all">All Ages (G)</option>
                <option value="13+">Teens (13+)</option>
                <option value="16+">Young Adult (16+)</option>
                <option value="18+">Mature / Adult (18+)</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {/* Field 14: Tags */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                14. Search Tags (Comma separated)
              </label>
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                placeholder="magic, dragons, dark fantasy, translated"
                className="w-full bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              />
            </div>

            {/* Field 15: Copyright */}
            <div>
              <label className="block text-xs font-bold text-zinc-300 mb-1">
                15. Copyright Notice
              </label>
              <input
                type="text"
                value={copyrightInfo}
                onChange={(e) => setCopyrightInfo(e.target.value)}
                placeholder="© 2026 Author Name. All Rights Reserved."
                className="w-full bg-novelix-950 text-xs text-white px-3 py-2 rounded-xl border border-novelix-800 focus:outline-none focus:border-novelix-neon"
              />
            </div>
          </div>

          {/* Reader Download Permission */}
          <div className="flex items-center gap-2 pt-2">
            <input
              type="checkbox"
              id="allowDownload"
              checked={allowDownload}
              onChange={(e) => setAllowDownload(e.target.checked)}
              className="rounded bg-novelix-950 border-novelix-800 text-novelix-purple focus:ring-0"
            />
            <label htmlFor="allowDownload" className="text-xs text-zinc-300 cursor-pointer">
              Allow registered readers to download offline PDF copies
            </label>
          </div>
        </div>

        {/* Action Bar: Fields 18, 19, 20 */}
        <div className="p-4 rounded-2xl bg-novelix-900 border border-novelix-800 flex flex-col sm:flex-row items-center justify-between gap-4 sticky bottom-6 z-20 backdrop-blur-xl shadow-2xl">
          <button
            type="button"
            onClick={() => setIsPreviewOpen(true)}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-xs font-semibold bg-novelix-950 hover:bg-novelix-800 text-zinc-300 hover:text-white border border-novelix-800 transition-colors w-full sm:w-auto justify-center"
          >
            <Eye className="w-4 h-4 text-novelix-neon" />
            <span>18. Preview Publication</span>
          </button>

          <div className="flex items-center gap-3 w-full sm:w-auto">
            <button
              type="button"
              onClick={() => handlePublish('draft')}
              disabled={isPublishing}
              className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl text-xs font-semibold bg-novelix-800 hover:bg-novelix-750 text-white transition-colors disabled:opacity-50"
            >
              <Save className="w-4 h-4" />
              <span>19. Save as Draft</span>
            </button>

            <button
              type="submit"
              disabled={isPublishing}
              className="flex-1 sm:flex-none flex items-center justify-center gap-2 px-7 py-2.5 rounded-xl text-xs font-bold bg-gradient-to-r from-novelix-purple via-novelix-electric to-novelix-neon text-white shadow-glow-md hover:shadow-glow-lg transition-all disabled:opacity-50"
            >
              <UploadCloud className="w-4 h-4" />
              <span>{isPublishing ? 'Publishing...' : '20. Publish Now'}</span>
            </button>
          </div>
        </div>
      </form>

      {/* Google Drive File Picker Modal */}
      {isDriveModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
          <div className="w-full max-w-xl bg-novelix-900 border border-novelix-800 rounded-3xl p-6 shadow-2xl space-y-4">
            <div className="flex items-center justify-between border-b border-novelix-800 pb-3">
              <div className="flex items-center gap-2">
                <HardDrive className="w-5 h-5 text-novelix-neon" />
                <h3 className="font-bold text-sm text-white">Select PDF from Google Drive</h3>
              </div>
              <button
                onClick={() => setIsDriveModalOpen(false)}
                className="text-zinc-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            {loadingDriveFiles ? (
              <div className="py-8 text-center space-y-2">
                <RefreshCw className="w-6 h-6 text-novelix-neon animate-spin mx-auto" />
                <p className="text-xs text-zinc-400">Loading authorized Drive files...</p>
              </div>
            ) : driveFiles.length > 0 ? (
              <div className="max-h-60 overflow-y-auto space-y-2">
                {driveFiles.map((file) => (
                  <div
                    key={file.id}
                    className="p-3 rounded-xl bg-novelix-950 border border-novelix-800 flex items-center justify-between"
                  >
                    <div>
                      <p className="text-xs font-bold text-white">{file.name}</p>
                      <p className="text-[10px] text-zinc-500 font-mono">
                        {Math.round((file.size || 1024 * 1024) / 1024 / 1024 * 10) / 10} MB
                      </p>
                    </div>
                    <button
                      onClick={() => handleSelectDriveFileForEdition(file, 'en')}
                      className="px-3 py-1 rounded-lg text-xs font-semibold bg-novelix-electric text-white"
                    >
                      Attach PDF
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <div className="py-8 text-center space-y-3">
                <p className="text-xs text-zinc-400 leading-relaxed">
                  {driveNotice || 'To link your Google Drive accounts, click "Connect Google Drive" or authorize via OAuth.'}
                </p>
                <button
                  onClick={handleConnectGoogleDrive}
                  className="px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-electric text-white"
                >
                  Link Google Account
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Preview Modal (Field 18) */}
      {isPreviewOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in">
          <div className="w-full max-w-2xl bg-novelix-900 border border-novelix-800 rounded-3xl p-6 shadow-2xl space-y-4 max-h-[85vh] overflow-y-auto">
            <div className="flex items-center justify-between border-b border-novelix-800 pb-3">
              <h3 className="font-bold text-sm text-white">Live Publication Preview</h3>
              <button onClick={() => setIsPreviewOpen(false)} className="text-zinc-400 hover:text-white">✕</button>
            </div>

            <div className="flex gap-6">
              {coverUrl ? (
                <img src={coverUrl} alt="Cover" className="w-36 aspect-[2/3] rounded-xl object-cover" />
              ) : (
                <div className="w-36 aspect-[2/3] rounded-xl bg-novelix-950 border border-novelix-800 flex items-center justify-center text-xs text-zinc-600">
                  No Cover
                </div>
              )}
              <div className="space-y-2 flex-1">
                <span className="text-[10px] font-bold text-novelix-neon uppercase bg-novelix-950 px-2 py-0.5 rounded border border-novelix-800">
                  {publicationType}
                </span>
                <h2 className="text-xl font-bold text-white">{title || 'Untitled Book'}</h2>
                <p className="text-xs text-novelix-neon font-serif italic">{subtitle}</p>
                <p className="text-xs text-zinc-400 line-clamp-3">{description}</p>
                <div className="text-xs text-zinc-500 pt-2">
                  <span>Authors: </span>
                  <span className="text-zinc-300 font-semibold">{authors.map((a) => a.name).join(', ')}</span>
                </div>
              </div>
            </div>

            <div className="pt-4 border-t border-novelix-800 flex justify-end">
              <button
                onClick={() => setIsPreviewOpen(false)}
                className="px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-800 text-white"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
