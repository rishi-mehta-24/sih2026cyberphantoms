# BIS Assistant - Database & Data Architecture
## Hybrid Approach Implementation Guide

### Overview
This is a complete database and data pipeline for the BIS (Bureau of Indian Standards) AI-powered assistant using a hybrid approach:
- **Structured Data**: PostgreSQL for standards, schemes, labs, products
- **Vector Embeddings**: OpenAI embeddings for semantic search (RAG)
- **Sample Data**: Pre-loaded with 6 Indian Standards, 5 products, 3 schemes, 3 labs, hallmarking data, and FAQs

---

## Files Created

### 1. **bis-assistant-schema.sql**
PostgreSQL database schema with 12 tables:
- `indian_standards` - Core standards data with embeddings
- `standard_clauses` - Detailed clause breakdowns
- `products` - Product catalog
- `product_standard_mapping` - Which standards apply to which products
- `bis_schemes` - ISI Mark, Hallmarking, Product Certification schemes
- `scheme_process_steps` - Step-by-step certification workflows
- `testing_laboratories` - Accredited labs with geo-location
- `hallmarking` - Precious metal purity standards
- `consumer_faqs` - Q&A with embeddings
- `documents` - References and guidelines
- `translations` - Multilingual support (ready for Hindi, Marathi, etc.)
- `user_queries` - Analytics & improvement log

**Key Features:**
- pgvector extension for vector similarity search
- IVFFlat indexes for fast embedding lookup
- Views for common queries (mandatory_standards_by_product, labs_by_capability)
- Foreign key constraints for data integrity

### 2. **bis-sample-data.json**
Sample data covering:
- **6 Indian Standards**: Cement (IS 1199), Steel (IS 226), Concrete (IS 383), Electrical (IS 732), LPG Cylinders (IS 15959), Medical (IS 1571)
- **5 Products**: Portland Cement, Structural Steel, LPG Cylinder, Clinical Thermometer, Copper Cable
- **3 BIS Schemes**: ISI Mark, Hallmarking, Product Certification with 4-step workflows
- **3 Accredited Labs**: Delhi, Mumbai, Bengaluru with specific capabilities
- **3 Hallmark Standards**: Gold (916, 999), Silver (925)
- **5 Consumer FAQs**: Covering certification, hallmarking, testing

### 3. **data_ingestion.py**
Python script to:
- Load JSON data
- Generate OpenAI embeddings for standards, clauses, FAQs, labs
- Insert into PostgreSQL with proper foreign key relationships
- Handle conflicts gracefully
- Provide detailed logging

---

## Setup Instructions

### Prerequisites
```bash
# Install Python dependencies
pip install -r requirements.txt

# Ensure PostgreSQL is installed and running
# Install pgvector extension
sudo apt-get install postgresql-contrib
# Connect to PostgreSQL and enable pgvector:
# CREATE EXTENSION IF NOT EXISTS vector;
```

### Step 1: Create Database
```bash
createdb bis_assistant
```

### Step 2: Initialize Schema
```bash
psql bis_assistant < bis-assistant-schema.sql
```

### Step 3: Set Environment Variables
```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=bis_assistant
export DB_USER=postgres
export DB_PASSWORD=your_password
export OPENAI_API_KEY=sk-xxx...
```

### Step 4: Run Data Ingestion
```bash
python data_ingestion.py bis-sample-data.json
```

Expected output:
```
============================================================
BIS Assistant Data Ingestion Pipeline
============================================================
✓ Connected to database
Loading 6 Indian Standards...
✓ Indian Standards inserted
Loading 5 Standard Clauses...
✓ Standard Clauses inserted
...
============================================================
✓ Data ingestion completed successfully!
============================================================
```

---

## Data Structure Examples

### Query 1: Find Standards for a Product
```sql
SELECT p.product_name, s.is_number, s.title, psm.mandatory
FROM products p
JOIN product_standard_mapping psm ON p.id = psm.product_id
JOIN indian_standards s ON psm.is_id = s.id
WHERE p.product_name = 'LPG Cylinder';
```

### Query 2: Semantic Search (Vector Similarity)
```sql
SELECT is_number, title
FROM indian_standards
ORDER BY embedding <-> (SELECT embedding FROM indian_standards WHERE is_number = 'IS 1199:2018')
LIMIT 5;
```

### Query 3: Labs by City
```sql
SELECT lab_name, capabilities, phone
FROM testing_laboratories
WHERE city = 'Mumbai'
AND is_accredited = TRUE;
```

### Query 4: Hallmark Details
```sql
SELECT hallmark_code, metal_type, purity_standard, marking_requirements
FROM hallmarking
WHERE metal_type = 'Gold';
```

---

## Next Steps for Production

### Phase 1: Data Expansion
- Scrape additional standards from BIS website
- Add more products (100+ variants)
- Include complete testing procedures
- Add more labs (200+)

### Phase 2: RAG Pipeline
- Use embeddings for semantic search
- Implement retrieval with LLM context injection
- Build chain-of-thought reasoning for complex queries

### Phase 3: Multilingual Support
- Generate translations using Claude/GPT
- Store in `translations` table
- Support Hindi, Marathi, Tamil, Telugu, etc.

### Phase 4: Advanced Features
- Web scraper for automated BIS updates
- Real-time lab availability booking
- Application status tracking
- Document upload & analysis

---

## Architecture Diagram

```
┌─────────────────────────┐
│  User Query (NL)        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  AI Agent (Claude)      │
│  - Understands intent   │
│  - Generates embedding  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  PostgreSQL + pgvector                  │
│  ┌─────────────────────────────────┐   │
│  │ Vector Search (Cosine Similarity)   │
│  │ - Find relevant standards           │
│  │ - Find matching clauses             │
│  │ - Find applicable labs              │
│  └─────────────────────────────────┘   │
└───────────┬─────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────┐
│  Response Generation                    │
│  - Combine retrieved context            │
│  - Add source citations                 │
│  - Format for user's language           │
└─────────────────────────────────────────┘
```

---

## Troubleshooting

### Issue: OpenAI API fails
- Check OPENAI_API_KEY is set correctly
- Verify you have API credits
- Falls back to zero vectors if embedding fails

### Issue: pgvector extension not found
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Issue: Foreign key constraint violation
- Ensure standards are inserted before clauses
- Run ingestion in order: standards → clauses → products → schemes

### Issue: Embedding dimensions mismatch
- Ensure using `text-embedding-3-small` (1536 dims)
- Update if using different model

---

## Configuration for Different Scales

### MVP (Current - Small)
- 6 standards, 5 products, 3 schemes
- 1,000 vector operations
- Suitable for demo & SIH

### Beta (Medium)
- 50 standards, 50 products, 10 schemes
- Partial scraping of BIS website
- 10,000 vector operations

### Production (Large)
- 1,000+ standards
- Automated daily scraping
- 1M+ vector operations
- Caching layer (Redis)
- Async jobs for batch embedding

---

## Cost Estimation (OpenAI Embeddings)

- Text-embedding-3-small: $0.02 per 1M tokens
- Current sample data: ~100K tokens → $0.002
- Scaling to 50 standards: ~1M tokens → $0.02
- Scaling to 1,000 standards: ~20M tokens → $0.40

---

## Files Dependency Graph

```
bis-sample-data.json
         ↓
  data_ingestion.py
         ↓
   PostgreSQL
         ↓
bis-assistant-schema.sql (must be loaded first)
```

**Loading Order:**
1. Create database: `createdb bis_assistant`
2. Load schema: `psql bis_assistant < bis-assistant-schema.sql`
3. Run ingestion: `python data_ingestion.py bis-sample-data.json`

---

## Future Integration Points

### For Backend Team (API/Frontend)
- Query endpoint: `/api/standards/search?query=<text>`
- Lab locator: `/api/labs?city=<city>&capability=<capability>`
- Scheme guide: `/api/schemes/<scheme_code>/steps`
- FAQ endpoint: `/api/faqs?category=<category>`

### For AI/LLM Team
- Embeddings table for RAG context injection
- User query logging for model improvement
- Feedback loop for hallucination detection

### For DevOps/Cloud
- Docker setup for PostgreSQL + pgvector
- Database backups & versioning
- CI/CD for schema migrations
- Monitoring vector search performance

---

## Success Metrics

✓ Schema created with all 12 tables
✓ Sample data loaded successfully
✓ Embeddings generated (1,536 dimensions each)
✓ Vector indexes created for fast search
✓ Foreign key relationships enforced
✓ Ready for AI assistant integration

---

**Last Updated**: 2026-09-08
**Approach**: Hybrid (Structured Data + Vector Embeddings)
**Status**: MVP Ready for Integration
