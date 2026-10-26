CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

DO $$ BEGIN
  CREATE TYPE ecom_platform AS ENUM ('SHOPIFY','WOOCOMMERCE','MAGENTO','CUSTOM','OTHER');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS companies (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  domain TEXT NOT NULL UNIQUE,
  company_name TEXT,
  country_code TEXT NOT NULL DEFAULT 'HK',
  ecom_platform ecom_platform NOT NULL DEFAULT 'OTHER',
  estimated_monthly_traffic INTEGER,
  tech_stack JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_companies_domain ON companies (domain);
CREATE INDEX IF NOT EXISTS idx_companies_updated_at ON companies (updated_at);

CREATE TABLE IF NOT EXISTS company_contacts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  job_title TEXT,
  email TEXT NOT NULL,
  linkedin_url TEXT,
  is_verified BOOLEAN NOT NULL DEFAULT false,
  UNIQUE (company_id, email)
);
CREATE INDEX IF NOT EXISTS idx_company_contacts_email ON company_contacts (email);

CREATE TABLE IF NOT EXISTS ad_intelligence (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  active_meta_ads BOOLEAN NOT NULL DEFAULT false,
  active_google_ads BOOLEAN NOT NULL DEFAULT false,
  ad_creative_urls TEXT[] NOT NULL DEFAULT '{}',
  detected_ad_copy TEXT,
  last_scraped_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_ad_intelligence_company ON ad_intelligence (company_id);

CREATE TABLE IF NOT EXISTS aeo_audits (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,
  brand_positioning_summary TEXT,
  embeddings vector(1536),
  llm_recommendation_score DOUBLE PRECISION,
  raw_scraped_html_text TEXT
);
CREATE INDEX IF NOT EXISTS idx_aeo_audits_company ON aeo_audits (company_id);
CREATE INDEX IF NOT EXISTS idx_aeo_audits_embeddings
  ON aeo_audits USING hnsw (embeddings vector_cosine_ops);
