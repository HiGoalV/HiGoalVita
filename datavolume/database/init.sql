CREATE TABLE kg_documents (
    id VARCHAR(256) PRIMARY KEY COMMENT 'Unique ID of the document',
    filename VARCHAR(512) UNIQUE COMMENT 'Filename of the document',
    title VARCHAR(512) DEFAULT '' COMMENT 'Title of the document',
    author VARCHAR(128) DEFAULT '' COMMENT 'Author of the document',
    source VARCHAR(512) DEFAULT '' COMMENT 'Source of the document',
    creation_date DATETIME COMMENT 'Original creation date of the document',
    extracted_date DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the document was extracted into the database',
    raw_data JSON COMMENT 'Raw metadata associated with the document'
);

CREATE TABLE kg_chunks (
    id VARCHAR(64) PRIMARY KEY COMMENT 'Unique ID of the text chunk',
    text TEXT COMMENT 'Text content of the chunk',
    source_doc_id VARCHAR(256) COMMENT 'ID of the source document this chunk belongs to',
    title VARCHAR(512) DEFAULT '' COMMENT 'Title of the source document',
    raw_data JSON COMMENT 'Raw metadata associated with the chunk',
    CONSTRAINT fk_chunk_doc FOREIGN KEY (source_doc_id) REFERENCES kg_documents(id) ON DELETE CASCADE,
    INDEX idx_source_doc_id (source_doc_id)
);

CREATE TABLE user_qa_tasks (
    task_id VARCHAR(64) PRIMARY KEY COMMENT 'Unique task ID',
    user_id VARCHAR(64) NOT NULL COMMENT 'ID of the user who submitted the task',
    user_role VARCHAR(50) COMMENT 'Role of the user (e.g. guest, admin)',
    company VARCHAR(50) COMMENT 'Company associated with the user',
    category VARCHAR(50) COMMENT 'Primary category of the task',
    subcategory VARCHAR(50) COMMENT 'Subcategory of the task',
    permissions VARCHAR(500) COMMENT 'Access permissions assigned to the user',
    priority INT DEFAULT 0 COMMENT 'Priority level of the task (0 is lowest)',
    status VARCHAR(50) DEFAULT 'PENDING' COMMENT 'Current status of the task',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the task was created',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Timestamp when the task was last updated'
);

CREATE TABLE user_queries (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Auto-incremented ID of the query',
    task_id VARCHAR(64) NOT NULL COMMENT 'Associated task ID',
    query_text TEXT NOT NULL COMMENT 'Text of the user query',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the query was created'
);

CREATE TABLE user_answers (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Auto-incremented ID of the answer',
    task_id VARCHAR(64) NOT NULL COMMENT 'Associated task ID',
    answer_text TEXT COMMENT 'Text content of the answer',
    answer_image TEXT COMMENT 'Path or URL to the answer image (if any)',
    score FLOAT COMMENT 'Score or confidence of the answer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the answer was created'
);