export interface DocumentMetadata {
    department: string;
    access_tier: string;
    date: string;
    source?: string;
    original_filename?: string;
    section?: string;
    page?: number;
    row?: number;
    chunk_index?: number;
    file_type?: string;
    chunking_method?: string;
    [key: string]: string | number | boolean | undefined;
}

export interface SearchResult {
    text: string;
    metadata: DocumentMetadata;
    cosine_distance: number;
}

export interface SearchRequest {
    query: string;
    department: string;
    access_tier: string;
    n_results: number;
}

export interface SearchResponse {
    query: string;
    department: string;
    access_tier: string;
    total_results: number;
    results: SearchResult[];
}

export interface IngestionResponse {
    status: string;
    filename: string;
    source: string;
    documents_loaded: number;
    chunks_created: number;
    elapsed_seconds: number;
}

export interface SystemStats {
    indexed_chunks: number;
    embedding_model: string;
    vector_database: string;
    distance_metric: string;
    supported_formats: string[];
    max_upload_size_mb: number;
}

export interface HealthResponse {
    status: string;
    service: string;
    database: string;
}
