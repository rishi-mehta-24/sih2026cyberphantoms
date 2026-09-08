import json
import os
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import Json, execute_values
from openai import OpenAI
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bis_assistant")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

class BISDataIngestion:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.connect_db()

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            self.conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            self.cursor = self.conn.cursor()
            logger.info("✓ Connected to database")
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            raise

    def get_embedding(self, text: str) -> List[float]:
        """Generate embedding using OpenAI API"""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.warning(f"Embedding generation failed for text: {text[:50]}... Error: {e}")
            return [0.0] * 1536  # Return zero vector as fallback

    def load_json_data(self, filepath: str) -> Dict:
        """Load sample data from JSON file"""
        with open(filepath, 'r') as f:
            return json.load(f)

    def insert_indian_standards(self, data: List[Dict]):
        """Insert Indian Standards with embeddings"""
        logger.info(f"Loading {len(data)} Indian Standards...")

        for standard in data:
            embedding = self.get_embedding(
                f"{standard['is_number']} {standard['title']} {standard['description']}"
            )

            self.cursor.execute("""
                INSERT INTO indian_standards
                (is_number, title, description, scope, effective_date, status, category, document_url, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (is_number) DO NOTHING
            """, (
                standard['is_number'],
                standard['title'],
                standard.get('description', ''),
                standard.get('scope', ''),
                standard.get('effective_date'),
                standard.get('status', 'ACTIVE'),
                standard.get('category', ''),
                standard.get('document_url', ''),
                embedding
            ))

        self.conn.commit()
        logger.info("✓ Indian Standards inserted")

    def insert_standard_clauses(self, data: List[Dict]):
        """Insert Standard Clauses with embeddings"""
        logger.info(f"Loading {len(data)} Standard Clauses...")

        for clause in data:
            # Get the IS ID from is_number
            self.cursor.execute("SELECT id FROM indian_standards WHERE is_number = %s",
                              (clause['is_number'],))
            result = self.cursor.fetchone()
            if not result:
                logger.warning(f"Standard {clause['is_number']} not found")
                continue

            is_id = result[0]
            embedding = self.get_embedding(
                f"{clause['clause_title']} {clause['clause_text']}"
            )

            self.cursor.execute("""
                INSERT INTO standard_clauses
                (is_id, clause_number, clause_title, clause_text, importance_level, testing_requirement, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                is_id,
                clause['clause_number'],
                clause['clause_title'],
                clause['clause_text'],
                clause.get('importance_level', 'MEDIUM'),
                clause.get('testing_requirement', False),
                embedding
            ))

        self.conn.commit()
        logger.info("✓ Standard Clauses inserted")

    def insert_products(self, data: List[Dict]):
        """Insert Products"""
        logger.info(f"Loading {len(data)} Products...")

        for product in data:
            self.cursor.execute("""
                INSERT INTO products
                (product_name, product_code, category, description, use_case)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                product['product_name'],
                product.get('product_code', ''),
                product.get('category', ''),
                product.get('description', ''),
                product.get('use_case', '')
            ))

        self.conn.commit()
        logger.info("✓ Products inserted")

    def insert_product_standard_mapping(self, data: List[Dict]):
        """Insert Product-Standard mappings"""
        logger.info(f"Loading {len(data)} Product-Standard mappings...")

        for mapping in data:
            # Get product and standard IDs
            self.cursor.execute("SELECT id FROM products WHERE product_code = %s",
                              (mapping['product_code'],))
            product_result = self.cursor.fetchone()

            self.cursor.execute("SELECT id FROM indian_standards WHERE is_number = %s",
                              (mapping['is_number'],))
            standard_result = self.cursor.fetchone()

            if not product_result or not standard_result:
                logger.warning(f"Product or Standard not found for mapping")
                continue

            self.cursor.execute("""
                INSERT INTO product_standard_mapping
                (product_id, is_id, mandatory)
                VALUES (%s, %s, %s)
                ON CONFLICT (product_id, is_id) DO NOTHING
            """, (
                product_result[0],
                standard_result[0],
                mapping.get('mandatory', False)
            ))

        self.conn.commit()
        logger.info("✓ Product-Standard mappings inserted")

    def insert_bis_schemes(self, data: List[Dict]):
        """Insert BIS Schemes"""
        logger.info(f"Loading {len(data)} BIS Schemes...")

        for scheme in data:
            self.cursor.execute("""
                INSERT INTO bis_schemes
                (scheme_name, scheme_code, description, eligibility_criteria,
                 application_fee, processing_time_days, validity_period_years)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (scheme_code) DO NOTHING
            """, (
                scheme['scheme_name'],
                scheme.get('scheme_code', ''),
                scheme.get('description', ''),
                scheme.get('eligibility_criteria', ''),
                scheme.get('application_fee', 0),
                scheme.get('processing_time_days', 0),
                scheme.get('validity_period_years', 0)
            ))

        self.conn.commit()
        logger.info("✓ BIS Schemes inserted")

    def insert_scheme_process_steps(self, data: List[Dict]):
        """Insert Scheme Process Steps"""
        logger.info(f"Loading {len(data)} Scheme Process Steps...")

        for step in data:
            # Get scheme ID
            self.cursor.execute("SELECT id FROM bis_schemes WHERE scheme_code = %s",
                              (step['scheme_code'],))
            result = self.cursor.fetchone()
            if not result:
                logger.warning(f"Scheme {step['scheme_code']} not found")
                continue

            scheme_id = result[0]

            self.cursor.execute("""
                INSERT INTO scheme_process_steps
                (scheme_id, step_number, step_title, step_description, duration_days, required_documents)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                scheme_id,
                step['step_number'],
                step['step_title'],
                step['step_description'],
                step.get('duration_days', 0),
                step.get('required_documents', [])
            ))

        self.conn.commit()
        logger.info("✓ Scheme Process Steps inserted")

    def insert_testing_laboratories(self, data: List[Dict]):
        """Insert Testing Laboratories with embeddings"""
        logger.info(f"Loading {len(data)} Testing Laboratories...")

        for lab in data:
            embedding = self.get_embedding(
                f"{lab['lab_name']} {lab['city']} {' '.join(lab.get('capabilities', []))}"
            )

            self.cursor.execute("""
                INSERT INTO testing_laboratories
                (lab_name, accreditation_number, address, city, state, pincode,
                 phone, email, website, capabilities, is_accredited, accreditation_date,
                 latitude, longitude, embedding)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (
                lab['lab_name'],
                lab.get('accreditation_number', ''),
                lab.get('address', ''),
                lab.get('city', ''),
                lab.get('state', ''),
                lab.get('pincode', ''),
                lab.get('phone', ''),
                lab.get('email', ''),
                lab.get('website', ''),
                lab.get('capabilities', []),
                lab.get('is_accredited', True),
                lab.get('accreditation_date'),
                lab.get('latitude'),
                lab.get('longitude'),
                embedding
            ))

        self.conn.commit()
        logger.info("✓ Testing Laboratories inserted")

    def insert_hallmarking(self, data: List[Dict]):
        """Insert Hallmarking data"""
        logger.info(f"Loading {len(data)} Hallmarking records...")

        for hallmark in data:
            self.cursor.execute("""
                INSERT INTO hallmarking
                (hallmark_code, metal_type, purity_standard, is_number,
                 assay_procedure, fineness_guaranteed, marking_requirements)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (hallmark_code) DO NOTHING
            """, (
                hallmark['hallmark_code'],
                hallmark.get('metal_type', ''),
                hallmark.get('purity_standard', ''),
                hallmark.get('is_number', ''),
                hallmark.get('assay_procedure', ''),
                hallmark.get('fineness_guaranteed', ''),
                hallmark.get('marking_requirements', '')
            ))

        self.conn.commit()
        logger.info("✓ Hallmarking data inserted")

    def insert_consumer_faqs(self, data: List[Dict]):
        """Insert Consumer FAQs with embeddings"""
        logger.info(f"Loading {len(data)} Consumer FAQs...")

        for faq in data:
            embedding = self.get_embedding(f"{faq['question']} {faq['answer']}")

            is_id = None
            if 'is_number' in faq:
                self.cursor.execute("SELECT id FROM indian_standards WHERE is_number = %s",
                                  (faq['is_number'],))
                result = self.cursor.fetchone()
                is_id = result[0] if result else None

            self.cursor.execute("""
                INSERT INTO consumer_faqs
                (question, answer, category, related_is_id, language, embedding)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                faq['question'],
                faq['answer'],
                faq.get('category', ''),
                is_id,
                faq.get('language', 'en'),
                embedding
            ))

        self.conn.commit()
        logger.info("✓ Consumer FAQs inserted")

    def insert_documents(self, data: List[Dict]):
        """Insert Documents with embeddings"""
        logger.info(f"Loading {len(data)} Documents...")

        for doc in data:
            embedding = self.get_embedding(f"{doc['document_title']}")

            self.cursor.execute("""
                INSERT INTO documents
                (document_title, document_type, url, language, embedding)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                doc['document_title'],
                doc.get('document_type', 'LINK'),
                doc.get('url', ''),
                doc.get('language', 'en'),
                embedding
            ))

        self.conn.commit()
        logger.info("✓ Documents inserted")

    def run_ingestion(self, json_filepath: str):
        """Run complete data ingestion pipeline"""
        try:
            logger.info("=" * 60)
            logger.info("BIS Assistant Data Ingestion Pipeline")
            logger.info("=" * 60)

            data = self.load_json_data(json_filepath)

            # Insert in dependency order
            if 'indian_standards' in data:
                self.insert_indian_standards(data['indian_standards'])

            if 'standard_clauses' in data:
                self.insert_standard_clauses(data['standard_clauses'])

            if 'products' in data:
                self.insert_products(data['products'])

            if 'product_standard_mapping' in data:
                self.insert_product_standard_mapping(data['product_standard_mapping'])

            if 'bis_schemes' in data:
                self.insert_bis_schemes(data['bis_schemes'])

            if 'scheme_process_steps' in data:
                self.insert_scheme_process_steps(data['scheme_process_steps'])

            if 'testing_laboratories' in data:
                self.insert_testing_laboratories(data['testing_laboratories'])

            if 'hallmarking' in data:
                self.insert_hallmarking(data['hallmarking'])

            if 'consumer_faqs' in data:
                self.insert_consumer_faqs(data['consumer_faqs'])

            if 'documents' in data:
                self.insert_documents(data['documents'])

            logger.info("=" * 60)
            logger.info("✓ Data ingestion completed successfully!")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"✗ Ingestion failed: {e}")
            self.conn.rollback()
            raise
        finally:
            self.close_db()

    def close_db(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    import sys

    json_file = sys.argv[1] if len(sys.argv) > 1 else "bis-sample-data.json"

    ingestion = BISDataIngestion()
    ingestion.run_ingestion(json_file)
