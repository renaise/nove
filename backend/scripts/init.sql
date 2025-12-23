-- Novia Database Initialization Script
-- Creates tables and seeds initial dress data

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Tables
-- ============================================================================

CREATE TABLE IF NOT EXISTS dresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    silhouette VARCHAR(50) NOT NULL,
    price_cents INTEGER NOT NULL,
    brand VARCHAR(255),
    description TEXT,
    image_url VARCHAR(512) NOT NULL,
    thumbnail_url VARCHAR(512),
    size_min INTEGER NOT NULL,
    size_max INTEGER NOT NULL,
    tags JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS body_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    bust FLOAT NOT NULL,
    waist FLOAT NOT NULL,
    hips FLOAT NOT NULL,
    body_type VARCHAR(50) NOT NULL,
    estimated_size INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    mesh_url VARCHAR(512),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_dresses_silhouette ON dresses(silhouette);
CREATE INDEX IF NOT EXISTS idx_dresses_price ON dresses(price_cents);
CREATE INDEX IF NOT EXISTS idx_dresses_sizes ON dresses(size_min, size_max);
CREATE INDEX IF NOT EXISTS idx_body_analyses_user ON body_analyses(user_id);

-- ============================================================================
-- Seed Data: Wedding Dresses
-- ============================================================================

INSERT INTO dresses (name, silhouette, price_cents, brand, size_min, size_max, description, image_url, tags) VALUES
-- Ballgowns
('Enchanted Garden', 'ballgown', 280000, 'Vera Wang', 0, 16,
 'A romantic ballgown featuring delicate floral appliqués and a dramatic train.',
 'https://images.unsplash.com/photo-1594552072238-b8a33785b261?w=600&q=80',
 '["floral", "romantic", "train"]'::jsonb),

('Royal Elegance', 'ballgown', 420000, 'Monique Lhuillier', 0, 20,
 'Classic princess silhouette with cathedral-length veil and beaded bodice.',
 'https://images.unsplash.com/photo-1591604466107-ec97de577aff?w=600&q=80',
 '["classic", "beaded", "veil"]'::jsonb),

('Fairy Tale Dream', 'ballgown', 350000, 'Oscar de la Renta', 2, 18,
 'Ethereal tulle layers with sparkling crystal embellishments.',
 'https://images.unsplash.com/photo-1511285560929-80b456fea0bc?w=600&q=80',
 '["tulle", "crystals", "ethereal"]'::jsonb),

-- A-Line
('Modern Romance', 'a-line', 195000, 'Pronovias', 2, 12,
 'Contemporary A-line with clean lines and subtle lace detailing.',
 'https://images.unsplash.com/photo-1519741497674-611481863552?w=600&q=80',
 '["modern", "lace", "minimalist"]'::jsonb),

('Graceful Flow', 'a-line', 180000, 'Jenny Packham', 0, 22,
 'Flowing A-line silhouette perfect for outdoor ceremonies.',
 'https://images.unsplash.com/photo-1518889735218-3e3c81fc4906?w=600&q=80',
 '["flowing", "outdoor", "garden"]'::jsonb),

('Romantic Lace', 'a-line', 220000, 'Claire Pettibone', 4, 16,
 'Vintage-inspired lace with sweetheart neckline and chapel train.',
 'https://images.unsplash.com/photo-1549416853-67360aed1e10?w=600&q=80',
 '["vintage", "lace", "sweetheart"]'::jsonb),

-- Mermaid
('Sleek Silhouette', 'mermaid', 210000, 'Maggie Sottero', 2, 6,
 'Form-fitting mermaid that hugs every curve with dramatic flare.',
 'https://images.unsplash.com/photo-1550005809-91ad75fb315f?w=600&q=80',
 '["fitted", "dramatic", "glamorous"]'::jsonb),

('Sculpted Beauty', 'mermaid', 240000, 'Galia Lahav', 0, 10,
 'Sculptural mermaid with intricate beading and illusion back.',
 'https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=600&q=80',
 '["beaded", "illusion", "sexy"]'::jsonb),

('Hollywood Glamour', 'mermaid', 380000, 'Berta', 0, 8,
 'Red carpet-worthy mermaid with plunging neckline and long sleeves.',
 'https://images.unsplash.com/photo-1546026423-cc4642628d2b?w=600&q=80',
 '["glamorous", "sleeves", "plunging"]'::jsonb),

-- Sheath
('Timeless Classic', 'sheath', 165000, 'BHLDN', 0, 20,
 'Elegant sheath with clean lines, perfect for the minimalist bride.',
 'https://images.unsplash.com/photo-1595777457583-95e059d581b8?w=600&q=80',
 '["minimalist", "elegant", "simple"]'::jsonb),

('Minimalist Bride', 'sheath', 135000, 'Sarah Seven', 2, 14,
 'Understated silk sheath with subtle cowl back.',
 'https://images.unsplash.com/photo-1546026423-cc4642628d2b?w=600&q=80',
 '["silk", "minimalist", "cowl"]'::jsonb),

('City Chic', 'sheath', 175000, 'Carolina Herrera', 0, 12,
 'Sophisticated column silhouette for the modern urban bride.',
 'https://images.unsplash.com/photo-1519741497674-611481863552?w=600&q=80',
 '["urban", "sophisticated", "modern"]'::jsonb),

-- Bohemian
('Ocean Breeze', 'bohemian', 140000, 'Grace Loves Lace', 4, 14,
 'Free-spirited bohemian with delicate lace and flowing silhouette.',
 'https://images.unsplash.com/photo-1522653216850-4f1415a174fb?w=600&q=80',
 '["bohemian", "lace", "flowy"]'::jsonb),

('Boho Chic', 'bohemian', 125000, 'Rue de Seine', 2, 16,
 'Romantic boho style with flutter sleeves and open back.',
 'https://images.unsplash.com/photo-1525257944581-1bcb36a54be3?w=600&q=80',
 '["boho", "sleeves", "romantic"]'::jsonb),

('Meadow Dreams', 'bohemian', 155000, 'Daughters of Simone', 0, 18,
 'Whimsical bohemian with wildflower embroidery.',
 'https://images.unsplash.com/photo-1518889735218-3e3c81fc4906?w=600&q=80',
 '["whimsical", "embroidery", "nature"]'::jsonb),

-- Empire
('Grecian Goddess', 'empire', 185000, 'Temperley London', 0, 20,
 'Empire waist gown with flowing chiffon and grecian draping.',
 'https://images.unsplash.com/photo-1519741497674-611481863552?w=600&q=80',
 '["grecian", "chiffon", "flowing"]'::jsonb),

('Ethereal Empire', 'empire', 165000, 'Marchesa', 2, 18,
 'Romantic empire silhouette with delicate floral appliqués.',
 'https://images.unsplash.com/photo-1594552072238-b8a33785b261?w=600&q=80',
 '["romantic", "floral", "ethereal"]'::jsonb),

-- Fit and Flare
('Dancing Queen', 'fit-and-flare', 195000, 'Hayley Paige', 0, 16,
 'Playful fit-and-flare perfect for dancing the night away.',
 'https://images.unsplash.com/photo-1550005809-91ad75fb315f?w=600&q=80',
 '["playful", "dancing", "fun"]'::jsonb),

('Vintage Charm', 'fit-and-flare', 225000, 'Watters', 2, 14,
 '1950s-inspired fit-and-flare with tea-length option available.',
 'https://images.unsplash.com/photo-1549416853-67360aed1e10?w=600&q=80',
 '["vintage", "1950s", "tea-length"]'::jsonb),

('Modern Flare', 'fit-and-flare', 175000, 'Lela Rose', 0, 18,
 'Contemporary take on the classic fit-and-flare silhouette.',
 'https://images.unsplash.com/photo-1519699047748-de8e457a634e?w=600&q=80',
 '["modern", "contemporary", "classic"]'::jsonb);

-- ============================================================================
-- Trigger for updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_dresses_updated_at
    BEFORE UPDATE ON dresses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
