from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
import tempfile
import uuid
from typing import Optional
from pathlib import Path
import sys

# Add parent directories to path to import existing modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from swp.swp import generate_pdf, update_master
from worksafe_nop.fill import fill_nop_from_pdf
from excel_pdf.excel_pdf import excel_pdf

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
        
        # Run the fill NOP function
        fill_nop_from_pdf(swp_file)
        
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