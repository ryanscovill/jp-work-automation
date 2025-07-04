from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import tempfile
import uuid
from typing import Optional, Dict, Any
from pathlib import Path
import sys
import asyncio
import concurrent.futures
from ruamel.yaml import YAML
import re
from pydantic import BaseModel

# Add parent directories to path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from procedure_generator.swp.swp import generate_pdf, update_master
from procedure_generator.config_loader import config
from procedure_generator.worksafe_nop.fill import fill_nop_from_pdf
from procedure_generator.excel_pdf.excel_pdf import excel_pdf

app = FastAPI(
    title="Work Procedure PDF Generator API",
    description="Web API for PDF generation and form filling",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage for temporary files and task status
temp_files = {}
task_status = {}

# Configuration file path
CONFIG_PATH = Path(__file__).parent.parent.parent / "swp_config.yaml"

class ConfigUpdate(BaseModel):
    """Model for configuration update requests"""
    config: Dict[str, Any]

# YAML handler with comment preservation
yaml_handler = YAML()
yaml_handler.preserve_quotes = True
yaml_handler.map_indent = 2
yaml_handler.sequence_indent = 2

def parse_yaml_comments(file_path: Path) -> Dict[str, str]:
    """Parse YAML file and extract comments for each field path"""
    comments = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        current_path = []
        pending_comment = None
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Skip empty lines
            if not stripped:
                continue
                
            # Check if this line is a comment only
            if stripped.startswith('#'):
                # Store comment for next non-comment line
                comment_text = stripped[1:].strip()
                # Skip general header comments
                if not any(word in comment_text.lower() for word in ['configuration', 'file contains', 'settings']):
                    pending_comment = comment_text
                continue
                
            # Extract inline comment from line
            inline_comment_match = re.search(r'#\s*(.+)$', line)
            inline_comment = inline_comment_match.group(1).strip() if inline_comment_match else None
            
            # Parse YAML structure to build path
            if ':' in line and not stripped.startswith('-'):
                # Get indentation level
                indent_level = (len(line) - len(line.lstrip())) // 2
                
                # Extract key (remove any inline comments first)
                key_part = line.split('#')[0] if '#' in line else line
                key = key_part.split(':')[0].strip().strip('"\'')
                
                # Adjust current path based on indentation
                current_path = current_path[:indent_level] + [key]
                path_str = '.'.join(current_path)
                
                # Store comment (prefer inline comment, then pending comment)
                comment_to_store = inline_comment or pending_comment
                if comment_to_store:
                    comments[path_str] = comment_to_store
                    pending_comment = None  # Clear pending comment after use
                    
    except Exception as e:
        print(f"Error parsing comments: {e}")
    
    return comments

def update_yaml_preserving_structure(file_path: Path, new_data: Dict[str, Any]) -> None:
    """Update YAML file while preserving comments and structure"""
    # Read the current file with ruamel.yaml
    with open(file_path, 'r', encoding='utf-8') as file:
        yaml_data = yaml_handler.load(file)
    
    # Update the data while preserving the original structure
    def update_recursive(original, new, path=""):
        if isinstance(new, dict) and isinstance(original, dict):
            for key, value in new.items():
                if key in original:
                    if isinstance(value, dict) and isinstance(original[key], dict):
                        # Special handling for field_mappings - complete replacement
                        if key == "field_mappings":
                            original[key] = value
                        else:
                            update_recursive(original[key], value, f"{path}.{key}" if path else key)
                    elif isinstance(value, list) and isinstance(original[key], list):
                        # Special handling for pages array - complete replacement
                        if key == "pages":
                            original[key] = value
                        else:
                            original[key] = value
                    else:
                        original[key] = value
                else:
                    original[key] = value
        else:
            return new
    
    update_recursive(yaml_data, new_data)
    
    # Write back to file preserving comments
    with open(file_path, 'w', encoding='utf-8') as file:
        yaml_handler.dump(yaml_data, file)

# Serve static frontend files in production
if Path("../frontend/dist").exists():
    app.mount("/static", StaticFiles(directory="../frontend/dist"), name="static")

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Work Procedure API is running"}

@app.get("/api/health")
async def health_check():
    """Health check for API"""
    return {"status": "healthy", "api_version": "1.0.0"}

@app.get("/api/config")
async def get_config():
    """Get current configuration from swp_config.yaml with comments"""
    try:
        if not CONFIG_PATH.exists():
            raise HTTPException(status_code=404, detail="Configuration file not found")
        
        # Load configuration data
        with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
            config = yaml_handler.load(file)
        
        # Parse comments
        comments = parse_yaml_comments(CONFIG_PATH)
        
        return {"config": config, "comments": comments}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading configuration: {str(e)}")

@app.post("/api/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration file with new values while preserving comments"""
    try:
        if not CONFIG_PATH.exists():
            raise HTTPException(status_code=404, detail="Configuration file not found")
        
        # Read the current YAML file to create backup
        with open(CONFIG_PATH, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Create a backup of the original file
        backup_path = CONFIG_PATH.with_suffix('.yaml.backup')
        with open(backup_path, 'w', encoding='utf-8') as backup_file:
            backup_file.write(content)
        
        # Update the configuration while preserving comments
        update_yaml_preserving_structure(CONFIG_PATH, config_update.config)
        
        # Reload the global config instance to reflect changes
        try:
            config.reload()
        except Exception as reload_error:
            print(f"Warning: Failed to reload config in memory: {reload_error}")
            # Still return success since the file was updated
        
        return {"message": "Configuration updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating configuration: {str(e)}")

def cleanup_temp_file(file_path: str):
    """Clean up temporary file after use"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        pass

def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file to temporary location"""
    file_id = str(uuid.uuid4())
    file_extension = Path(upload_file.filename).suffix
    temp_path = f"/tmp/{file_id}{file_extension}"
    
    with open(temp_path, "wb") as buffer:
        buffer.write(upload_file.file.read())
    
    temp_files[file_id] = temp_path
    return temp_path

async def run_excel_to_pdf_task(task_id: str, excel_file: str, pdf_template: str, output_path: str):
    """Background task for Excel to PDF conversion"""
    try:
        task_status[task_id] = {"status": "processing", "progress": 0}
        
        # Run the Excel to PDF function
        excel_pdf(excel_file, pdf_template, output_path)
        
        task_status[task_id] = {"status": "completed", "progress": 100, "output_file": output_path}
    except Exception as e:
        task_status[task_id] = {"status": "error", "error": str(e)}
    finally:
        # Cleanup input files
        cleanup_temp_file(excel_file)
        cleanup_temp_file(pdf_template)

@app.post("/api/excel-to-pdf")
async def excel_to_pdf_endpoint(
    background_tasks: BackgroundTasks,
    excel_file: UploadFile = File(...),
    pdf_template: UploadFile = File(...)
):
    """Convert Excel data to filled PDF form"""
    try:
        # Validate file types
        if not excel_file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="Excel file must be .xlsx or .xls")
        if not pdf_template.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Template must be a PDF file")
        
        # Save uploaded files
        excel_path = save_upload_file(excel_file)
        template_path = save_upload_file(pdf_template)
        
        # Create output file path
        task_id = str(uuid.uuid4())
        output_path = f"/tmp/output_{task_id}.pdf"
        
        # Start background task
        background_tasks.add_task(
            run_excel_to_pdf_task, 
            task_id, 
            excel_path, 
            template_path, 
            output_path
        )
        
        return {"task_id": task_id, "message": "Excel to PDF conversion started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_generate_pdf_task(task_id: str, source_pdf: str, template_folder: str, work_procedure_folder: str):
    """Background task for SWP generation"""
    try:
        task_status[task_id] = {"status": "processing", "progress": 0}
        
        # Run the generate PDF function
        output_path = generate_pdf(source_pdf, template_folder, work_procedure_folder)
        
        task_status[task_id] = {"status": "completed", "progress": 100, "output_file": output_path}
    except Exception as e:
        task_status[task_id] = {"status": "error", "error": str(e)}
    finally:
        cleanup_temp_file(source_pdf)

@app.post("/api/generate-swp")
async def generate_swp_endpoint(
    background_tasks: BackgroundTasks,
    source_pdf: UploadFile = File(...),
    template_folder: str = Form(...),
    work_procedure_folder: str = Form(...)
):
    """Generate Safe Work Procedure PDF"""
    try:
        if not source_pdf.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Source file must be a PDF")
        
        source_path = save_upload_file(source_pdf)
        task_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            run_generate_pdf_task,
            task_id,
            source_path,
            template_folder,
            work_procedure_folder
        )
        
        return {"task_id": task_id, "message": "SWP generation started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_fill_nop_task(task_id: str, swp_file: str):
    """Background task for NOP form filling"""
    try:
        task_status[task_id] = {"status": "processing", "progress": 0}
        
        # Run the fill NOP function in a thread pool to avoid asyncio loop conflict
        # since fill_nop_from_pdf uses sync Playwright API
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            await loop.run_in_executor(executor, fill_nop_from_pdf, swp_file)
        
        task_status[task_id] = {"status": "completed", "progress": 100}
    except Exception as e:
        task_status[task_id] = {"status": "error", "error": str(e)}
    finally:
        cleanup_temp_file(swp_file)

@app.post("/api/fill-nop")
async def fill_nop_endpoint(
    background_tasks: BackgroundTasks,
    swp_file: UploadFile = File(...)
):
    """Fill WorkSafe BC NOP form"""
    try:
        if not swp_file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="SWP file must be a PDF")
        
        swp_path = save_upload_file(swp_file)
        task_id = str(uuid.uuid4())
        
        background_tasks.add_task(run_fill_nop_task, task_id, swp_path)
        
        return {"task_id": task_id, "message": "NOP form filling started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_update_master_task(task_id: str, source_pdf: str, template_folder: str, work_procedure_folder: str):
    """Background task for master PDF update"""
    try:
        task_status[task_id] = {"status": "processing", "progress": 0}
        
        # Run the update master function
        output_path = update_master(source_pdf, template_folder, work_procedure_folder)
        
        task_status[task_id] = {"status": "completed", "progress": 100, "output_file": output_path}
    except Exception as e:
        task_status[task_id] = {"status": "error", "error": str(e)}
    finally:
        cleanup_temp_file(source_pdf)

@app.post("/api/update-master")
async def update_master_endpoint(
    background_tasks: BackgroundTasks,
    source_pdf: UploadFile = File(...),
    template_folder: str = Form(...),
    work_procedure_folder: str = Form(...)
):
    """Update master PDF dropdown fields"""
    try:
        if not source_pdf.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Source file must be a PDF")
        
        source_path = save_upload_file(source_pdf)
        task_id = str(uuid.uuid4())
        
        background_tasks.add_task(
            run_update_master_task,
            task_id,
            source_path,
            template_folder,
            work_procedure_folder
        )
        
        return {"task_id": task_id, "message": "Master PDF update started"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/task-status/{task_id}")
async def get_task_status(task_id: str):
    """Get status of background task"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_status[task_id]

@app.get("/api/download/{task_id}")
async def download_file(task_id: str):
    """Download generated file"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_status[task_id]
    if task_info["status"] != "completed" or "output_file" not in task_info:
        raise HTTPException(status_code=404, detail="File not ready or not available")
    
    file_path = task_info["output_file"]
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    filename = Path(file_path).name
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/pdf'
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)