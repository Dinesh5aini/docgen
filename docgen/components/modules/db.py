import sqlite3
import os
import json
from datetime import datetime

# Database setup
DB_PATH = 'document_generator.db'

def get_db_connection():
    """Create a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # This enables dictionary-like access to rows
    return conn

def init_db():
    """Initialize the database with required tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create documents table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS documents (
        doc_id TEXT PRIMARY KEY,
        data JSON NOT NULL,
        schema JSON NOT NULL,
        formatting JSON NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    # Create sections table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sections (
        section_id TEXT,
        doc_id TEXT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        summary TEXT NOT NULL,
        keywords JSON NOT NULL,
        depends_on JSON NOT NULL,
        PRIMARY KEY (section_id, doc_id),
        FOREIGN KEY (doc_id) REFERENCES documents (doc_id)
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

def save_section(section: dict):
    """Save a generated section to the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Convert lists to JSON strings
    keywords_json = json.dumps(section.get("keywords", []))
    depends_on_json = json.dumps(section.get("depends_on", []))
    
    cursor.execute('''
    INSERT OR REPLACE INTO sections 
    (section_id, doc_id, title, content, summary, keywords, depends_on)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        section["section_id"],
        section["doc_id"],
        section["title"],
        section["content"],
        section["summary"],
        keywords_json,
        depends_on_json
    ))
    
    conn.commit()
    conn.close()

def get_section(section_id: str) -> dict:
    """Get a specific section by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sections WHERE section_id = ?", (section_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        # Convert row to dict and parse JSON strings back to lists
        section = dict(row)
        section["keywords"] = json.loads(section["keywords"])
        section["depends_on"] = json.loads(section["depends_on"])
        return section
    
    return None

def get_document_sections(doc_id: str) -> list:
    """Get all sections for a document"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sections WHERE doc_id = ? ORDER BY section_id", (doc_id,))
    rows = cursor.fetchall()
    conn.close()
    
    sections = []
    for row in rows:
        section = dict(row)
        section["keywords"] = json.loads(section["keywords"])
        section["depends_on"] = json.loads(section["depends_on"])
        sections.append(section)
    
    return sections

def create_document(doc_id: str, data: dict, schema: dict):
    """Create a new document with user input data and schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO documents (doc_id, data, schema, formatting, created_at)
    VALUES (?, ?, ?, ?, ?)
    ''', (
        doc_id,
        json.dumps(data),
        json.dumps({"sections": schema}),
        json.dumps({}),
        datetime.now().isoformat()
    ))
    
    conn.commit()
    conn.close()
    return doc_id

def get_document(doc_id: str) -> dict:
    """Get document by ID"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM documents WHERE doc_id = ?", (doc_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        document = dict(row)
        # Parse JSON strings back to dictionaries/lists
        document["data"] = json.loads(document["data"])
        document["schema"] = json.loads(document["schema"])
        document["formatting"] = json.loads(document["formatting"])
        return document
    
    return None

def update_document_formatting(doc_id: str, formatting: dict):
    """Update document formatting settings"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE documents 
    SET formatting = ?
    WHERE doc_id = ?
    ''', (json.dumps(formatting), doc_id))
    
    conn.commit()
    conn.close()
    