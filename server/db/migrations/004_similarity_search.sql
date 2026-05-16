-- 004_similarity_search: pgvector RAG benzerlik arama fonksiyonu
-- NovaVision anomali tespiti → embedding → benzer görüntü araması
-- Kullanım: SELECT * FROM search_similar_images(query_embedding, exclude_image_name, top_k, min_similarity);

-- ============================================================
-- Yardımcı: vector ile float[] arası dönüşüm için cast
-- ============================================================

-- Float array'den vector oluştur (Supabase REST API float[] gönderdiğinde)
CREATE OR REPLACE FUNCTION array_to_vector(arr float[]) RETURNS vector
LANGUAGE plpgsql IMMUTABLE PARALLEL SAFE
AS $$
BEGIN
    RETURN arr::vector;
END;
$$;

-- ============================================================
-- Ana fonksiyon: Benzer görüntü araması
-- ============================================================

CREATE OR REPLACE FUNCTION search_similar_images(
    query_embedding vector(1024),
    exclude_image_name text DEFAULT NULL,
    top_k integer DEFAULT 5,
    min_similarity float DEFAULT 0.0
)
RETURNS TABLE (
    image_name text,
    set_name text,
    file_path text,
    wear_type text,
    wear float,
    flank_wear float,
    adhesive_wear float,
    combination_wear float,
    similarity float,
    rank int
)
LANGUAGE plpgsql STABLE PARALLEL SAFE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        img.image_name,
        s.name AS set_name,
        img.file_path,
        img.wear_type,
        img.wear,
        img.flank_wear,
        img.adhesive_wear,
        img.combination_wear,
        (1.0 - (img.image_embedding <=> query_embedding))::float AS similarity,
        row_number() OVER (ORDER BY img.image_embedding <=> query_embedding)::int AS rank
    FROM images img
    LEFT JOIN sets s ON s.id = img.set_id
    WHERE img.image_embedding IS NOT NULL
      AND (exclude_image_name IS NULL OR img.image_name != exclude_image_name)
      AND (1.0 - (img.image_embedding <=> query_embedding)) >= min_similarity
    ORDER BY img.image_embedding <=> query_embedding
    LIMIT top_k;
END;
$$;

-- ============================================================
-- Kısa versiyon: Sadece embedding + jsonb metadata dönen
-- (LangChain/LLM context assembly için)
-- ============================================================

CREATE OR REPLACE FUNCTION search_similar_images_rich(
    query_embedding vector(1024),
    exclude_image_name text DEFAULT NULL,
    top_k integer DEFAULT 5,
    min_similarity float DEFAULT 0.0
)
RETURNS TABLE (
    image_name text,
    similarity float,
    metadata jsonb,
    rank int
)
LANGUAGE plpgsql STABLE PARALLEL SAFE
AS $$
BEGIN
    RETURN QUERY
    SELECT
        img.image_name,
        (1.0 - (img.image_embedding <=> query_embedding))::float AS similarity,
        jsonb_build_object(
            'file_path', img.file_path,
            'set_name', s.name,
            'wear_type', img.wear_type,
            'wear', img.wear,
            'flank_wear', img.flank_wear,
            'adhesive_wear', img.adhesive_wear,
            'combination_wear', img.combination_wear,
            'set_id', img.set_id
        ) AS metadata,
        row_number() OVER (ORDER BY img.image_embedding <=> query_embedding)::int AS rank
    FROM images img
    LEFT JOIN sets s ON s.id = img.set_id
    WHERE img.image_embedding IS NOT NULL
      AND (exclude_image_name IS NULL OR img.image_name != exclude_image_name)
      AND (1.0 - (img.image_embedding <=> query_embedding)) >= min_similarity
    ORDER BY img.image_embedding <=> query_embedding
    LIMIT top_k;
END;
$$;
