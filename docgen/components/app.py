# from fastapi import FastAPI, HTTPException
# from modules.schemas import UserInput, DocumentSection, Document
# from modules.gemini_client import SchemaGenerator, DocumentGenerator
# from modules.db import save_section, get_section
# from modules.utils import parse_schema
# import uuid
# from typing import List, Optional

# app = FastAPI()

# # Step 1: Generate Schema from User Input
# @app.post("/generate-schema")
# async def generate_document_schema(user_input: UserInput):
#     try:
#         schema_raw = generate_schema(user_input.dict())
#         sections = parse_schema(schema_raw)
#         doc_id = str(uuid.uuid4())
#         return {"doc_id": doc_id, "sections": sections}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # Step 2: Generate Content Iteratively
# @app.post("/generate-section")
# async def generate_section(
#     section_title: str,
#     keywords: List[str],
#     previous_section_id: Optional[str] = None
# ):
#     try:
#         previous_summary = ""
#         if previous_section_id:
#             previous_section = get_section(previous_section_id)
#             previous_summary = previous_section.get("summary", "")

#         content = generate_section_content(section_title, keywords, previous_summary)
#         summary = summarize_content(content)

#         section_data = {
#             "section_id": str(uuid.uuid4()),
#             "title": section_title,
#             "content": content,
#             "summary": summary,
#             "keywords": keywords
#         }
#         save_section(section_data)
#         return section_data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# from fastapi import FastAPI, HTTPException
# from docgen.components.modules.schemas import UserInput, DocumentSection
# from docgen.components.modules.gemini_client import SchemaGenerator, DocumentGenerator
# from docgen.components.modules.db import save_section, get_section
# from docgen.components.modules.utils import parse_schema
# import uuid
# from typing import List, Optional
# import json

# app = FastAPI(
#     title="IT Report Generator API",
#     description="Generate full-length IT reports and documents using Gemini AI",
#     version="1.0.0"
# )

# # -------------------------------
# # Step 1: Generate Schema
# # -------------------------------
# @app.post("/generate-schema", summary="Generate document schema from user input")
# async def generate_document_schema(user_input: UserInput):
#     """
#     Generate a detailed schema of the document based on project details.
#     """
#     try:
#         # Create Schema
#         schema_raw = SchemaGenerator.generate_schema(user_input.dict())
#         sections = parse_schema(schema_raw)
#         doc_id = str(uuid.uuid4())
        
#         with open('schema.json', 'w', encoding='utf-8') as f:
#             json.dump(sections, f, indent=4, ensure_ascii=False)

#         return {
#             "doc_id": doc_id,
#             "sections": sections
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# # -------------------------------
# # Step 2: Generate Section Content
# # -------------------------------
# @app.post("/generate-section", summary="Generate content for a single section")
# async def generate_section(
#     doc_id: str,
#     section_id: str,
#     section_title: str,
#     keywords: List[str],
#     depends_on: Optional[List[str]] = None,
# ):
#     """
#     Generate content for a section given the title, keywords, and dependency context.
#     """
#     try:
#         # Create a minimal fake project context to initialize DocumentGenerator
#         # (you can enhance it to real context later)
#         fake_context = {
#             "project_title": section_title,
#             "primary_objective": "Placeholder objective",
#             "abstract": "Placeholder abstract",
#             "technologies": keywords,
#             "functional_requirements": "Placeholder functional requirements",
#         }

#         doc_gen = DocumentGenerator(fake_context)

#         section_data = {
#             "section_id": section_id,
#             "title": section_title,
#             "keywords": keywords,
#             "depends_on": depends_on or [],
#         }

#         # Generate content and summary
#         content, summary = doc_gen.generate_section(section_data)

#         # Save section into database
#         section_record = {
#             "doc_id": doc_id,
#             "section_id": section_id,
#             "title": section_title,
#             "content": content,
#             "summary": summary,
#             "keywords": keywords,
#             "depends_on": depends_on or [],
#         }
#         save_section(section_record)

#         return section_record

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from modules.gemini_client import SchemaGenerator, DocumentGenerator
from modules.db import save_section, get_section, get_document_sections, create_document, get_document
from modules.utils import parse_schema
import uuid
import json
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret_key")
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ------------------------------
# Web UI Routes
# ------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/new-document", methods=["GET", "POST"])
def new_document():
    if request.method == "POST":
        try:
            # Extract form data
            data = {
                "project_title": request.form.get("project_title"),
                "primary_objective": request.form.get("primary_objective"),
                "problem_solves": request.form.get("problem_solves"),
                "abstract": request.form.get("abstract"),
                "problem_audience_facing": request.form.get("problem_audience_facing"),
                "resources_available": request.form.get("resources_available"),
                "risk_or_constraints": request.form.get("risk_or_constraints"),
                "functional_requirements": request.form.get("functional_requirements"),
                "technologies": request.form.get("technologies", "").split(","),
                "er_or_dataflow_diagram": request.form.get("er_or_dataflow_diagram"),
                "components": request.form.get("components", "").split(","),
                "development_methodology": request.form.get("development_methodology"),
                "testing_strategy": request.form.get("testing_strategy"),
                "limitations": request.form.get("limitations"),
                "future_enhancements": request.form.get("future_enhancements")
            }
            
            # Clean up empty lists
            data["technologies"] = [t.strip() for t in data["technologies"] if t.strip()]
            data["components"] = [c.strip() for c in data["components"] if c.strip()]
            
            # Generate schema
            schema_raw = SchemaGenerator.generate_schema(data)
            schema_parsed = parse_schema(schema_raw)

            with open('schema.json', 'w', encoding='utf-8') as f:
                json.dump(schema_parsed, f, indent=4, ensure_ascii=False)
            
            # Create document in database
            doc_id = str(uuid.uuid4())
            create_document(doc_id, data, schema_parsed)
            
            # Save to session for redirect
            session["doc_id"] = doc_id
            flash("Document schema created successfully!", "success")
            return redirect(url_for("document_editor", doc_id=doc_id))
        
        except Exception as e:
            flash(f"Error creating document: {str(e)}", "error")
            return render_template("new_document.html")
    
    return render_template("new_document.html")

@app.route("/document/<doc_id>")
def document_editor(doc_id):
    # Get document and its sections
    document = get_document(doc_id)
    sections = get_document_sections(doc_id)
    
    if not document:
        flash("Document not found", "error")
        return redirect(url_for("index"))
    
    return render_template(
        "document_editor.html", 
        doc_id=doc_id, 
        document=document,
        sections=sections
    )

from datetime import datetime

# Add the now() function to Jinja templates
@app.context_processor
def utility_processor():
    return {
        'now': datetime.now,
    }

# Add custom filter for date formatting
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a date time to a readable string."""
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
        except ValueError:
            return value
    return value.strftime(format)

@app.route("/generate-section/<doc_id>/<section_id>", methods=["POST"])
def generate_section_ui(doc_id, section_id):
    document = get_document(doc_id)
    
    if not document:
        flash("Document not found", "error")
        return redirect(url_for("index"))
    
    # Access the nested sections structure correctly
    sections_list = document.get("schema", {}).get("sections", {}).get("sections", [])
    
    # Find the section in the schema
    section_info = None
    for section in sections_list:
        if section.get("section_id") == section_id:
            section_info = section
            break
    
    if not section_info:
        flash("Section not found in schema", "error")
        return redirect(url_for("document_editor", doc_id=doc_id))
    
    try:
        # Create context from document data
        context = {
            "project_title": document.get("data", {}).get("project_title", ""),
            "primary_objective": document.get("data", {}).get("primary_objective", ""),
            "abstract": document.get("data", {}).get("abstract", ""),
            "technologies": document.get("data", {}).get("technologies", []),
            "functional_requirements": document.get("data", {}).get("functional_requirements", []),
        }
        
        doc_gen = DocumentGenerator(context)
        
        # Generate content
        content, summary = doc_gen.generate_section(section_info)
        
        # Save to database
        section_record = {
            "doc_id": doc_id,
            "section_id": section_id,
            "title": section_info.get("title", ""),
            "content": content,
            "summary": summary,
            "keywords": section_info.get("keywords", []),
            "depends_on": section_info.get("depends_on", []),
        }
        save_section(section_record)
        
        flash("Section generated successfully!", "success")
        return redirect(url_for("document_editor", doc_id=doc_id))
    
    except Exception as e:
        flash(f"Error generating section: {str(e)}", "error")
        return redirect(url_for("document_editor", doc_id=doc_id))

@app.route("/view/<doc_id>")
def view_document(doc_id):
    document = get_document(doc_id)
    sections = get_document_sections(doc_id)
    
    if not document:
        flash("Document not found", "error")
        return redirect(url_for("index"))
    
    return render_template(
        "view_document.html",
        doc_id=doc_id,
        document=document,
        sections=sections
    )

@app.route("/download/<doc_id>")
def download_document(doc_id):
    document = get_document(doc_id)
    sections = get_document_sections(doc_id)
    
    if not document:
        flash("Document not found", "error")
        return redirect(url_for("index"))
    
    # Generate HTML document
    html_content = render_template(
        "document_export.html",
        document=document,
        sections=sections
    )
    
    response = app.response_class(
        response=html_content,
        status=200,
        mimetype='text/html'
    )
    response.headers["Content-Disposition"] = f"attachment; filename={document.get('data', {}).get('project_title', 'document').replace(' ', '_')}.html"
    
    return response

# ------------------------------
# API Routes
# ------------------------------
@app.route("/api/generate-schema", methods=["POST"])
def generate_document_schema():
    """
    Generate a detailed schema of the document based on project details.
    """
    try:
        # Parse the request data
        data = request.get_json()
        
        # Create Schema
        schema_raw = SchemaGenerator.generate_schema(data)
        sections = parse_schema(schema_raw)
        doc_id = str(uuid.uuid4())
        
        # Save to database
        create_document(doc_id, data, sections)
        
        return jsonify({
            "doc_id": doc_id,
            "sections": sections
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/generate-section", methods=["POST"])
def generate_section():
    """
    Generate content for a section given the title, keywords, and dependency context.
    """
    try:
        # Parse the request data
        data = request.get_json()
        doc_id = data.get("doc_id")
        section_id = data.get("section_id")
        section_title = data.get("section_title")
        keywords = data.get("keywords", [])
        depends_on = data.get("depends_on", [])
        
        # Get document context
        document = get_document(doc_id)
        if not document:
            return jsonify({"error": "Document not found"}), 404
        
        # Create project context
        context = {
            "project_title": document.get("data", {}).get("project_title", ""),
            "primary_objective": document.get("data", {}).get("primary_objective", ""),
            "abstract": document.get("data", {}).get("abstract", ""),
            "technologies": document.get("data", {}).get("technologies", []),
            "functional_requirements": document.get("data", {}).get("functional_requirements", ""),
        }

        doc_gen = DocumentGenerator(context)

        section_data = {
            "section_id": section_id,
            "title": section_title,
            "keywords": keywords,
            "depends_on": depends_on,
        }

        # Generate content and summary
        content, summary = doc_gen.generate_section(section_data)

        # Save section into database
        section_record = {
            "doc_id": doc_id,
            "section_id": section_id,
            "title": section_title,
            "content": content,
            "summary": summary,
            "keywords": keywords,
            "depends_on": depends_on,
        }
        save_section(section_record)

        return jsonify(section_record)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)