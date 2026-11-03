-- ====================================================================
-- NOVELIX PLATFORM SEED DATA
-- Sample data for immediate testing and production preview
-- ====================================================================

-- 1. Sample Advertisements
INSERT INTO public.advertisements (id, title, description, image_url, target_url, placement, is_active, impressions_count, clicks_count)
VALUES 
  ('a1000000-0000-0000-0000-000000000001', 'Novelix Premium Pass', 'Unlock unlimited audiobooks, PDF downloads, and offline manhwa reading.', 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=1200&q=80', '/settings', true, 1420, 89),
  ('a1000000-0000-0000-0000-000000000002', 'Creator Publishing Contest 2026', 'Submit your original fantasy novel or webtoon. $10,000 grand prize.', 'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1200&q=80', '/publish', true, 890, 47),
  ('a1000000-0000-0000-0000-000000000003', 'Mechanical Keyboard for Writers', 'Crafted for authors who write 10,000 words a day. 20% off with code NOVELIX.', 'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80', 'https://example.com', true, 630, 24)
ON CONFLICT (id) DO NOTHING;
