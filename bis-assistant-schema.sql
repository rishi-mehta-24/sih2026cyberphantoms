-- BIS Assistant Database Schema
-- Hybrid approach: Structured data + Vector embeddings for RAG

-- 1. INDIAN STANDARDS
CREATE TABLE indian_standards (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  is_number VARCHAR(50) UNIQUE NOT NULL,  -- e.g., "IS 1199:2018"
  title VARCHAR(500) NOT NULL,
  description TEXT,
  scope TEXT,
  effective_date DATE,
  supersedes_is_number VARCHAR(50),
  is_superseded_by VARCHAR(50),
  status VARCHAR(20),  -- ACTIVE, WITHDRAWN, SUPERSEDED
  category VARCHAR(100),  -- Cement, Steel, Electrical, etc.
  document_url VARCHAR(500),
  pdf_path VARCHAR(500),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  embedding vector(1536)  -- OpenAI embeddings (pgvector extension)
);

-- 2. STANDARD CLAUSES (detailed breakdown)
CREATE TABLE standard_clauses (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  is_id UUID NOT NULL REFERENCES indian_standards(id) ON DELETE CASCADE,
  clause_number VARCHAR(50),  -- e.g., "4.2.1"
  clause_title VARCHAR(300),
  clause_text TEXT NOT NULL,
  importance_level VARCHAR(20),  -- CRITICAL, HIGH, MEDIUM, LOW
  testing_requirement BOOLEAN DEFAULT FALSE,
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. PRODUCTS
CREATE TABLE products (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_name VARCHAR(300) NOT NULL,
  product_code VARCHAR(100),
  category VARCHAR(100),
  description TEXT,
  use_case TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. PRODUCTS TO STANDARDS MAPPING
CREATE TABLE product_standard_mapping (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  is_id UUID NOT NULL REFERENCES indian_standards(id) ON DELETE CASCADE,
  mandatory BOOLEAN DEFAULT FALSE,  -- Is this standard compulsory?
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(product_id, is_id)
);

-- 5. BIS CERTIFICATION SCHEMES
CREATE TABLE bis_schemes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scheme_name VARCHAR(200) NOT NULL,  -- ISI Mark, Hallmark, etc.
  scheme_code VARCHAR(50),
  description TEXT,
  eligibility_criteria TEXT,
  application_fee DECIMAL(10,2),
  processing_time_days INT,
  validity_period_years INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. SCHEME PROCESS STEPS
CREATE TABLE scheme_process_steps (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  scheme_id UUID NOT NULL REFERENCES bis_schemes(id) ON DELETE CASCADE,
  step_number INT,
  step_title VARCHAR(200),
  step_description TEXT,
  duration_days INT,
  required_documents TEXT[],  -- Array of document names
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. TESTING LABORATORIES
CREATE TABLE testing_laboratories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  lab_name VARCHAR(300) NOT NULL,
  accreditation_number VARCHAR(100),
  address TEXT,
  city VARCHAR(100),
  state VARCHAR(100),
  pincode VARCHAR(20),
  phone VARCHAR(20),
  email VARCHAR(100),
  website VARCHAR(200),
  capabilities TEXT[],  -- Array: ["Cement Testing", "Steel Testing", ...]
  is_accredited BOOLEAN DEFAULT TRUE,
  accreditation_date DATE,
  latitude DECIMAL(10, 8),
  longitude DECIMAL(11, 8),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  embedding vector(1536)
);

-- 8. HALLMARKING DATA
CREATE TABLE hallmarking (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  hallmark_code VARCHAR(50) UNIQUE NOT NULL,
  metal_type VARCHAR(100),  -- Gold, Silver, Platinum
  purity_standard VARCHAR(100),  -- e.g., "999", "916", "720"
  is_number VARCHAR(50),
  assay_procedure TEXT,
  fineness_guaranteed VARCHAR(100),
  marking_requirements TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 9. CONSUMER FAQs
CREATE TABLE consumer_faqs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  question TEXT NOT NULL,
  answer TEXT NOT NULL,
  category VARCHAR(100),  -- Certification, Hallmarking, Testing, etc.
  related_is_id UUID REFERENCES indian_standards(id),
  related_scheme_id UUID REFERENCES bis_schemes(id),
  language VARCHAR(20) DEFAULT 'en',  -- en, hi, mr, etc.
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 10. DOCUMENTS & REFERENCES
CREATE TABLE documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_title VARCHAR(300) NOT NULL,
  document_type VARCHAR(50),  -- PDF, LINK, GUIDELINE, etc.
  content TEXT,
  related_is_id UUID REFERENCES indian_standards(id),
  related_scheme_id UUID REFERENCES bis_schemes(id),
  url VARCHAR(500),
  file_path VARCHAR(500),
  language VARCHAR(20) DEFAULT 'en',
  embedding vector(1536),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 11. MULTILINGUAL TRANSLATIONS
CREATE TABLE translations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_table VARCHAR(100),  -- indian_standards, products, faqs, etc.
  source_id UUID,
  language VARCHAR(20),  -- hi, mr, gu, ta, etc.
  field_name VARCHAR(100),  -- title, description, etc.
  translated_text TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(source_table, source_id, language, field_name)
);

-- 12. USER QUERIES LOG (for analytics & improvement)
CREATE TABLE user_queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_query TEXT NOT NULL,
  matched_standard_id UUID REFERENCES indian_standards(id),
  matched_scheme_id UUID REFERENCES bis_schemes(id),
  ai_response TEXT,
  user_satisfied BOOLEAN,
  feedback TEXT,
  language VARCHAR(20) DEFAULT 'en',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- INDEXES for performance
CREATE INDEX idx_is_category ON indian_standards(category);
CREATE INDEX idx_is_status ON indian_standards(status);
CREATE INDEX idx_product_category ON products(category);
CREATE INDEX idx_lab_city ON testing_laboratories(city);
CREATE INDEX idx_lab_state ON testing_laboratories(state);
CREATE INDEX idx_faq_category ON consumer_faqs(category);
CREATE INDEX idx_hallmark_metal ON hallmarking(metal_type);
CREATE INDEX idx_is_embedding ON indian_standards USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_clause_embedding ON standard_clauses USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX idx_faq_embedding ON consumer_faqs USING ivfflat (embedding vector_cosine_ops);

-- VIEWS for common queries
CREATE VIEW mandatory_standards_by_product AS
SELECT
  p.product_name,
  s.is_number,
  s.title,
  s.category
FROM products p
JOIN product_standard_mapping psm ON p.id = psm.product_id
JOIN indian_standards s ON psm.is_id = s.id
WHERE psm.mandatory = TRUE;

CREATE VIEW labs_by_capability AS
SELECT
  capability,
  tl.lab_name,
  tl.city,
  tl.phone,
  tl.email
FROM testing_laboratories tl,
UNNEST(tl.capabilities) AS capability;
