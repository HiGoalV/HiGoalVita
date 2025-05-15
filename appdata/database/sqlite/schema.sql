-- Table: kg_documents
CREATE TABLE kg_documents (
    id TEXT PRIMARY KEY, -- Unique ID of the document
    filename TEXT UNIQUE, -- Filename of the document
    title TEXT DEFAULT '', -- Title of the document
    author TEXT DEFAULT '', -- Author of the document
    source TEXT DEFAULT '', -- Source of the document
    creation_date DATETIME, -- Original creation date of the document
    extracted_date DATETIME DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the document was extracted into the database
    raw_data TEXT -- Raw metadata associated with the document (JSON as TEXT in SQLite)
);

-- Table: kg_chunks
CREATE TABLE kg_chunks (
    id TEXT PRIMARY KEY, -- Unique ID of the text chunk
    text TEXT, -- Text content of the chunk
    source_doc_id TEXT, -- ID of the source document this chunk belongs to
    title TEXT DEFAULT '', -- Title of the source document
    raw_data TEXT, -- Raw metadata associated with the chunk
    FOREIGN KEY (source_doc_id) REFERENCES kg_documents(id) ON DELETE CASCADE
);

CREATE INDEX idx_source_doc_id ON kg_chunks(source_doc_id);

-- Table: user_qa_tasks
CREATE TABLE user_qa_tasks (
    task_id TEXT PRIMARY KEY, -- Unique task ID
    user_id TEXT NOT NULL, -- ID of the user who submitted the task
    user_role TEXT, -- Role of the user (e.g. guest, admin)
    company TEXT, -- Company associated with the user
    category TEXT, -- Primary category of the task
    subcategory TEXT, -- Subcategory of the task
    permissions TEXT, -- Access permissions assigned to the user
    priority INTEGER DEFAULT 0, -- Priority level of the task (0 is lowest)
    status TEXT DEFAULT 'PENDING', -- Current status of the task
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP, -- Timestamp when the task was created
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP -- Timestamp when the task was last updated
);

-- Table: user_queries
CREATE TABLE user_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-incremented ID of the query
    task_id TEXT NOT NULL, -- Associated task ID
    query_text TEXT NOT NULL, -- Text of the user query
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- Timestamp when the query was created
);

-- Table: user_answers
CREATE TABLE user_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT, -- Auto-incremented ID of the answer
    task_id TEXT NOT NULL, -- Associated task ID
    answer_text TEXT, -- Text content of the answer
    answer_image TEXT, -- Path or URL to the answer image (if any)
    score REAL, -- Score or confidence of the answer
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP -- Timestamp when the answer was created
);