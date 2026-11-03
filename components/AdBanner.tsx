'use client';

import React, { useEffect, useRef } from 'react';
import { ExternalLink, Sparkles } from 'lucide-react';

interface AdItem {
  id: string;
  title: string;
  description?: string;
  image_url: string;
  target_url: string;
  placement: string;
}

interface AdBannerProps {
  placement: 'homepage_banner' | 'explore_banner' | 'between_cards' | 'book_details' | 'author_dashboard';
  ad?: AdItem;
  className?: string;
}

export function AdBanner({ placement, ad, className = '' }: AdBannerProps) {
  const trackedRef = useRef(false);

  const defaultAd: AdItem = ad || {
    id: 'novelix-official-ad-1',
    title: 'NOVELIX Creator Pass — Unlimited Publishing & Drive Sync',
    description: 'Get verified creator status, connect multiple Google Drives, and monetize multi-language novels.',
    image_url: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&auto=format&fit=crop&q=80',
    target_url: '/publish',
    placement: placement,
  };

  useEffect(() => {
    if (!trackedRef.current) {
      trackedRef.current = true;
      fetch('/api/ads/track', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ adId: defaultAd.id, eventType: 'impression' }),
      }).catch(() => {});
    }
  }, [defaultAd.id]);

  const handleClick = () => {
    fetch('/api/ads/track', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ adId: defaultAd.id, eventType: 'click' }),
    }).catch(() => {});
  };

  if (placement === 'between_cards') {
    return (
      <div className={`col-span-full my-6 p-4 rounded-2xl bg-gradient-to-r from-novelix-950 via-novelix-900 to-novelix-purple/10 border border-novelix-800 flex flex-col md:flex-row items-center gap-6 justify-between overflow-hidden relative ${className}`}>
        <div className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded text-[9px] font-bold tracking-widest uppercase bg-novelix-950/80 border border-novelix-800 text-amber-400 flex items-center gap-1">
          <Sparkles className="w-2.5 h-2.5" />
          Sponsored
        </div>

        <div className="flex-1 space-y-1.5 pt-4 md:pt-0">
          <h4 className="text-sm font-bold text-white">{defaultAd.title}</h4>
          <p className="text-xs text-zinc-400 line-clamp-2">{defaultAd.description}</p>
        </div>

        <a
          href={defaultAd.target_url}
          onClick={handleClick}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-novelix-electric hover:bg-novelix-neon hover:text-novelix-950 text-white transition-all duration-200 shrink-0 shadow-glow-sm"
        >
          <span>Learn More</span>
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      </div>
    );
  }

  return (
    <div className={`relative rounded-2xl overflow-hidden border border-novelix-800 bg-novelix-950 group ${className}`}>
      <div className="absolute top-2 left-2 z-10 px-2 py-0.5 rounded text-[9px] font-bold tracking-widest uppercase bg-black/70 backdrop-blur-md border border-novelix-800 text-amber-400 flex items-center gap-1">
        <Sparkles className="w-2.5 h-2.5" />
        Sponsored
      </div>

      <div className="h-32 sm:h-40 w-full overflow-hidden relative">
        <img
          src={defaultAd.image_url}
          alt={defaultAd.title}
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-60"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-novelix-950 via-novelix-950/60 to-transparent" />
      </div>

      <div className="p-4 relative -mt-8 flex items-end justify-between gap-4">
        <div className="space-y-1">
          <h4 className="text-sm font-bold text-white group-hover:text-novelix-neon transition-colors">
            {defaultAd.title}
          </h4>
          <p className="text-xs text-zinc-400 line-clamp-1">{defaultAd.description}</p>
        </div>

        <a
          href={defaultAd.target_url}
          onClick={handleClick}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-novelix-electric/30 border border-novelix-electric/50 text-novelix-neon hover:bg-novelix-electric hover:text-white transition-colors shrink-0"
        >
          <span>Visit</span>
          <ExternalLink className="w-3 h-3" />
        </a>
      </div>
    </div>
  );
}
