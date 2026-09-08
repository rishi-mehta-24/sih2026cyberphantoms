"""
BIS Assistant - Database Query Examples for Backend/API Integration

This file provides ready-to-use SQL queries for common API endpoints
"""

# ============================================================================
# 1. SEARCH QUERIES - Used by the AI Assistant for RAG
# ============================================================================

def search_standards_by_text(query_text: str, limit: int = 5):
    """
    Semantic search for standards using embeddings
    Used by: GET /api/standards/search?q=cement
    """
    return """
    SELECT
        is_number,
        title,
        description,
        category,
        (embedding <-> %s::vector) as relevance_score
    FROM indian_standards
    WHERE status = 'ACTIVE'
    ORDER BY relevance_score
    LIMIT %s;
    """
    # Parameters: (embedding_vector, limit)


def search_clauses_for_standard(is_id: str):
    """
    Get all clauses for a specific standard
    Used by: GET /api/standards/{is_number}/clauses
    """
    return """
    SELECT
        clause_number,
        clause_title,
        clause_text,
        importance_level,
        testing_requirement
    FROM standard_clauses
    WHERE is_id = (SELECT id FROM indian_standards WHERE is_number = %s)
    ORDER BY clause_number;
    """


def search_faqs_by_query(query_text: str, limit: int = 5):
    """
    Find FAQs relevant to user query using semantic search
    Used by: GET /api/faqs/search?q=certification
    """
    return """
    SELECT
        question,
        answer,
        category,
        (embedding <-> %s::vector) as relevance_score
    FROM consumer_faqs
    WHERE language = %s
    ORDER BY relevance_score
    LIMIT %s;
    """
    # Parameters: (embedding_vector, language, limit)


# ============================================================================
# 2. PRODUCT QUERIES - Find applicable standards
# ============================================================================

def get_applicable_standards_for_product(product_name: str):
    """
    Get all applicable standards for a product
    Used by: GET /api/products/{product_name}/standards
    """
    return """
    SELECT
        p.product_name,
        s.is_number,
        s.title,
        s.category,
        psm.mandatory,
        s.effective_date,
        s.document_url
    FROM products p
    JOIN product_standard_mapping psm ON p.id = psm.product_id
    JOIN indian_standards s ON psm.is_id = s.id
    WHERE p.product_name ILIKE %s
    ORDER BY psm.mandatory DESC, s.is_number;
    """


def get_mandatory_standards_by_category(category: str):
    """
    Get all mandatory standards in a category
    Used by: GET /api/categories/{category}/mandatory-standards
    """
    return """
    SELECT DISTINCT
        s.is_number,
        s.title,
        s.category,
        COUNT(DISTINCT p.id) as products_count
    FROM indian_standards s
    LEFT JOIN product_standard_mapping psm ON s.id = psm.is_id
    LEFT JOIN products p ON psm.product_id = p.id
    WHERE s.category = %s
        AND s.status = 'ACTIVE'
        AND psm.mandatory = TRUE
    GROUP BY s.is_number, s.title, s.category
    ORDER BY s.is_number;
    """


# ============================================================================
# 3. CERTIFICATION SCHEME QUERIES
# ============================================================================

def get_scheme_details(scheme_code: str):
    """
    Get complete scheme details with process steps
    Used by: GET /api/schemes/{scheme_code}
    """
    return """
    SELECT
        b.id,
        b.scheme_name,
        b.scheme_code,
        b.description,
        b.eligibility_criteria,
        b.application_fee,
        b.processing_time_days,
        b.validity_period_years,
        json_agg(
            json_build_object(
                'step_number', s.step_number,
                'step_title', s.step_title,
                'step_description', s.step_description,
                'duration_days', s.duration_days,
                'required_documents', s.required_documents
            ) ORDER BY s.step_number
        ) as process_steps
    FROM bis_schemes b
    LEFT JOIN scheme_process_steps s ON b.id = s.scheme_id
    WHERE b.scheme_code = %s
    GROUP BY b.id, b.scheme_name, b.scheme_code, b.description,
             b.eligibility_criteria, b.application_fee,
             b.processing_time_days, b.validity_period_years;
    """


def get_certification_timeline(scheme_code: str):
    """
    Get total timeline for certification
    Used by: GET /api/schemes/{scheme_code}/timeline
    """
    return """
    SELECT
        scheme_id,
        COUNT(*) as total_steps,
        SUM(duration_days) as total_duration_days,
        json_agg(
            json_build_object(
                'step', step_number,
                'title', step_title,
                'duration', duration_days,
                'cumulative', SUM(duration_days) OVER (ORDER BY step_number)
            )
        ) as timeline
    FROM scheme_process_steps
    WHERE scheme_id = (SELECT id FROM bis_schemes WHERE scheme_code = %s)
    GROUP BY scheme_id;
    """


# ============================================================================
# 4. TESTING LABORATORY QUERIES
# ============================================================================

def find_labs_by_city(city: str, capability: str = None):
    """
    Find accredited labs by city and optional capability
    Used by: GET /api/labs?city=Delhi&capability=Cement+Testing
    """
    if capability:
        return """
        SELECT
            lab_name,
            accreditation_number,
            address,
            city,
            state,
            pincode,
            phone,
            email,
            website,
            capabilities,
            accreditation_date,
            latitude,
            longitude
        FROM testing_laboratories
        WHERE city ILIKE %s
            AND is_accredited = TRUE
            AND %s = ANY(capabilities)
        ORDER BY lab_name;
        """
    else:
        return """
        SELECT
            lab_name,
            accreditation_number,
            address,
            city,
            state,
            pincode,
            phone,
            email,
            website,
            capabilities,
            accreditation_date,
            latitude,
            longitude
        FROM testing_laboratories
        WHERE city ILIKE %s
            AND is_accredited = TRUE
        ORDER BY lab_name;
        """


def find_nearest_labs(latitude: float, longitude: float, radius_km: float = 50):
    """
    Find labs near user location (using PostGIS would be better)
    Used by: GET /api/labs/nearest?lat=28.5&lon=77.2&radius=50
    """
    return """
    SELECT
        lab_name,
        address,
        city,
        phone,
        email,
        capabilities,
        (
            111.111 *
            DEGREES(
                ACOS(
                    LEAST(1.0,
                        COS(RADIANS(latitude)) *
                        COS(RADIANS(%s)) *
                        COS(RADIANS(%s - longitude)) +
                        SIN(RADIANS(latitude)) *
                        SIN(RADIANS(%s))
                    )
                )
            )
        ) AS distance_km
    FROM testing_laboratories
    WHERE is_accredited = TRUE
    HAVING distance_km < %s
    ORDER BY distance_km;
    """
    # Parameters: (user_lat, user_lon, user_lat, radius_km)


# ============================================================================
# 5. HALLMARKING QUERIES
# ============================================================================

def get_hallmarking_standards(metal_type: str = None):
    """
    Get hallmarking standards for precious metals
    Used by: GET /api/hallmarking?metal=Gold
    """
    if metal_type:
        return """
        SELECT
            hallmark_code,
            metal_type,
            purity_standard,
            is_number,
            assay_procedure,
            fineness_guaranteed,
            marking_requirements
        FROM hallmarking
        WHERE metal_type = %s
        ORDER BY purity_standard DESC;
        """
    else:
        return """
        SELECT
            hallmark_code,
            metal_type,
            purity_standard,
            is_number,
            assay_procedure,
            fineness_guaranteed,
            marking_requirements
        FROM hallmarking
        ORDER BY metal_type, purity_standard DESC;
        """


# ============================================================================
# 6. CONSUMER FAQ QUERIES
# ============================================================================

def get_faqs_by_category(category: str, language: str = 'en'):
    """
    Get FAQs by category
    Used by: GET /api/faqs?category=Hallmarking&lang=en
    """
    return """
    SELECT
        id,
        question,
        answer,
        category,
        created_at
    FROM consumer_faqs
    WHERE category = %s
        AND language = %s
    ORDER BY created_at DESC;
    """


def get_faq_for_standard(is_number: str, language: str = 'en'):
    """
    Get FAQs related to a specific standard
    Used by: GET /api/standards/{is_number}/faqs
    """
    return """
    SELECT
        cf.question,
        cf.answer,
        cf.category
    FROM consumer_faqs cf
    WHERE cf.related_is_id = (
        SELECT id FROM indian_standards WHERE is_number = %s
    ) AND cf.language = %s;
    """


# ============================================================================
# 7. TRANSLATION QUERIES
# ============================================================================

def get_translated_standard(is_number: str, language: str):
    """
    Get translated content for a standard
    Used by: GET /api/standards/{is_number}?lang=hi
    """
    return """
    SELECT
        s.is_number,
        COALESCE(t_title.translated_text, s.title) as title,
        COALESCE(t_desc.translated_text, s.description) as description,
        s.category,
        s.status,
        s.effective_date
    FROM indian_standards s
    LEFT JOIN translations t_title ON
        t_title.source_table = 'indian_standards'
        AND t_title.source_id = s.id
        AND t_title.language = %s
        AND t_title.field_name = 'title'
    LEFT JOIN translations t_desc ON
        t_desc.source_table = 'indian_standards'
        AND t_desc.source_id = s.id
        AND t_desc.language = %s
        AND t_desc.field_name = 'description'
    WHERE s.is_number = %s;
    """


# ============================================================================
# 8. ANALYTICS QUERIES
# ============================================================================

def log_user_query(user_query: str, matched_standard_id: str = None,
                   matched_scheme_id: str = None, ai_response: str = None,
                   language: str = 'en'):
    """
    Log user query for analytics and model improvement
    Used by: POST /api/queries/log
    """
    return """
    INSERT INTO user_queries
    (user_query, matched_standard_id, matched_scheme_id, ai_response, language, created_at)
    VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
    RETURNING id;
    """


def get_popular_queries(limit: int = 10):
    """
    Get most frequently asked queries
    Used by: GET /api/analytics/popular-queries
    """
    return """
    SELECT
        user_query,
        COUNT(*) as frequency,
        COUNT(CASE WHEN user_satisfied = TRUE THEN 1 END) as satisfied_count
    FROM user_queries
    GROUP BY user_query
    ORDER BY frequency DESC
    LIMIT %s;
    """


def get_query_satisfaction_rate():
    """
    Get satisfaction rate of responses
    Used by: GET /api/analytics/satisfaction
    """
    return """
    SELECT
        COUNT(*) as total_queries,
        COUNT(CASE WHEN user_satisfied = TRUE THEN 1 END) as satisfied,
        COUNT(CASE WHEN user_satisfied = FALSE THEN 1 END) as unsatisfied,
        ROUND(
            100.0 * COUNT(CASE WHEN user_satisfied = TRUE THEN 1 END) /
            COUNT(*), 2
        ) as satisfaction_percentage
    FROM user_queries
    WHERE feedback IS NOT NULL;
    """


# ============================================================================
# 9. AGGREGATION QUERIES - For Dashboard/Admin
# ============================================================================

def get_database_statistics():
    """
    Get overall database statistics
    Used by: GET /api/admin/stats
    """
    return """
    SELECT
        (SELECT COUNT(*) FROM indian_standards) as total_standards,
        (SELECT COUNT(*) FROM products) as total_products,
        (SELECT COUNT(*) FROM bis_schemes) as total_schemes,
        (SELECT COUNT(*) FROM testing_laboratories WHERE is_accredited = TRUE) as accredited_labs,
        (SELECT COUNT(*) FROM consumer_faqs) as faq_count,
        (SELECT COUNT(*) FROM user_queries) as total_queries,
        (SELECT COUNT(DISTINCT category) FROM products) as product_categories,
        (SELECT COUNT(DISTINCT language) FROM translations) as languages_supported;
    """


def get_standards_by_category_stats():
    """
    Get statistics of standards by category
    Used by: GET /api/admin/stats/by-category
    """
    return """
    SELECT
        category,
        COUNT(*) as standard_count,
        COUNT(DISTINCT products.id) as product_count,
        MAX(effective_date) as latest_standard_date
    FROM indian_standards
    LEFT JOIN product_standard_mapping ON indian_standards.id = product_standard_mapping.is_id
    LEFT JOIN products ON product_standard_mapping.product_id = products.id
    GROUP BY category
    ORDER BY standard_count DESC;
    """


# ============================================================================
# 10. MAINTENANCE QUERIES
# ============================================================================

def refresh_embeddings_for_standards():
    """
    Refresh embeddings for all standards (call after bulk updates)
    """
    return """
    UPDATE indian_standards
    SET embedding = %s
    WHERE is_number = %s;
    """


def find_missing_embeddings():
    """
    Find records missing embeddings
    """
    return """
    SELECT table_name, count
    FROM (
        SELECT 'indian_standards' as table_name, COUNT(*) as count
        FROM indian_standards WHERE embedding IS NULL
        UNION ALL
        SELECT 'standard_clauses', COUNT(*)
        FROM standard_clauses WHERE embedding IS NULL
        UNION ALL
        SELECT 'consumer_faqs', COUNT(*)
        FROM consumer_faqs WHERE embedding IS NULL
    ) as missing_data
    WHERE count > 0;
    """


def analyze_database_performance():
    """
    Analyze database performance metrics
    """
    return """
    SELECT
        schemaname,
        tablename,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes
    ORDER BY idx_scan DESC;
    """
