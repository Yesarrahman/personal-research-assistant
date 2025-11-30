"""
Research Assistant Agent - REST API
Modern FastAPI with PDF/DOCX Support and Coordinator Orchestration

Author: Yesar Rahman
Date: November 2025
"""

from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from contextlib import asynccontextmanager
import os
import logging
import io
from dotenv import load_dotenv

# Import your existing agents
from agents.coordinator import CoordinatorAgent
from agents.researcher import ResearcherAgent
from agents.summarizer import SummarizerAgent
from utils.session_manager import SessionManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Initialize the research system
class ResearchSystem:
    def __init__(self):
        from google import generativeai as genai

        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")

        genai.configure(api_key=api_key)

        # Initialize agents
        self.researcher = ResearcherAgent()
        self.summarizer = SummarizerAgent()
        self.coordinator = CoordinatorAgent()

        # Give coordinator access to sub-agents
        self.coordinator.set_agents(self.researcher, self.summarizer)

        self.session_manager = SessionManager()
        logger.info("Research system initialized with coordinator orchestration")


# Global instance
research_system = None


# Modern lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global research_system
    try:
        research_system = ResearchSystem()
        logger.info("✓ API startup successful")
    except Exception as e:
        logger.error(f"✗ Startup failed: {e}")
        raise

    yield
    logger.info("API shutting down gracefully")


# Initialize FastAPI app
app = FastAPI(
    title="Research Assistant API",
    description="AI-powered multi-agent research system with document analysis",
    version="2.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ResearchRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    num_sources: Optional[int] = 5


class FollowUpRequest(BaseModel):
    query: str
    session_id: str


class DocumentAnalysisRequest(BaseModel):
    task: str
    session_id: str


class SourceInfo(BaseModel):
    title: str
    url: str
    snippet: str
    source: str


class ResearchResponse(BaseModel):
    success: bool
    session_id: str
    query: str
    summary: str
    key_findings: List[str]
    sources: List[SourceInfo]
    num_sources: int
    is_follow_up: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str
    agents_initialized: bool


# Document Processing Functions
def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from PDF file using PyPDF2."""
    try:
        import PyPDF2

        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)

        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"

        return text.strip()
    except Exception as e:
        logger.error(f"PDF extraction error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to extract PDF text: {str(e)}"
        )


def extract_text_from_docx(file_content: bytes) -> str:
    """Extract text from DOCX file using python-docx."""
    try:
        import docx

        doc_file = io.BytesIO(file_content)
        doc = docx.Document(doc_file)

        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

        return text.strip()
    except Exception as e:
        logger.error(f"DOCX extraction error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to extract DOCX text: {str(e)}"
        )


# API Endpoints


@app.get("/", response_model=dict)
async def root():
    """Root endpoint - API information."""
    return {
        "name": "Research Assistant API",
        "version": "2.0.0",
        "description": "Multi-agent AI research system with document analysis",
        "endpoints": {
            "health": "/health",
            "research": "/api/v1/research (POST)",
            "follow_up": "/api/v1/follow-up (POST)",
            "upload_document": "/api/v1/upload-document (POST)",
            "analyze_document": "/api/v1/analyze-document (POST)",
            "sessions": "/api/v1/sessions (GET)",
            "docs": "/docs",
        },
        "status": "operational",
        "features": [
            "Web Research",
            "PDF Analysis",
            "DOCX Analysis",
            "Document Summarization",
            "Coordinator-based Orchestration",
        ],
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy" if research_system else "unhealthy",
        "version": "2.0.0",
        "agents_initialized": research_system is not None,
    }


@app.post("/api/v1/research", response_model=ResearchResponse)
async def perform_research(request: ResearchRequest):
    """
    Perform a new research query.
    Now uses coordinator orchestration!
    """
    if not research_system:
        raise HTTPException(status_code=503, detail="Research system not initialized")

    try:
        session_id = (
            request.session_id or research_system.session_manager.create_session()
        )
        logger.info(f"Research request: {request.query}")

        # LET COORDINATOR DO ALL THE ORCHESTRATION!
        results = research_system.coordinator.orchestrate_research(request.query)

        if not results["success"]:
            raise HTTPException(
                status_code=500, detail=results.get("error", "Unknown error")
            )

        # Store in session
        research_system.session_manager.store(
            session_id,
            {
                "query": request.query,
                "plan": results["plan"],
                "sources": results["sources"],
                "report": results["report"],
            },
        )

        return ResearchResponse(
            success=True,
            session_id=session_id,
            query=request.query,
            summary=results["report"].get("summary", ""),
            key_findings=results["report"].get("key_findings", []),
            sources=[SourceInfo(**source) for source in results["sources"]],
            num_sources=len(results["sources"]),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Research error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/follow-up", response_model=ResearchResponse)
async def follow_up_question(request: FollowUpRequest):
    """
    Ask a follow-up question using previous research context.
    Now uses coordinator orchestration!
    """
    if not research_system:
        raise HTTPException(status_code=503, detail="Research system not initialized")

    try:
        context = research_system.session_manager.retrieve(request.session_id)

        if not context:
            raise HTTPException(status_code=404, detail="Session not found")

        logger.info(f"Follow-up request: {request.query}")

        # LET COORDINATOR HANDLE FOLLOW-UPS!
        results = research_system.coordinator.orchestrate_follow_up(
            request.query, context
        )

        if not results["success"]:
            raise HTTPException(
                status_code=500, detail=results.get("error", "Unknown error")
            )

        return ResearchResponse(
            success=True,
            session_id=request.session_id,
            query=request.query,
            summary=results["report"].get("summary", ""),
            key_findings=results["report"].get("key_findings", []),
            sources=[SourceInfo(**source) for source in results["sources"]],
            num_sources=len(results["sources"]),
            is_follow_up=True,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Follow-up error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/upload-document")
async def upload_document(
    file: UploadFile = File(...),
    task: str = Form(default="Summarize this document and extract key insights"),
):
    """
    Upload and analyze a PDF or DOCX document.

    Parameters:
    - file: The PDF or DOCX file to analyze
    - task: What you want to do with the document (summarize, extract key points, etc.)
    """
    if not research_system:
        raise HTTPException(status_code=503, detail="Research system not initialized")

    try:
        # Read file content
        file_content = await file.read()
        logger.info(f"Received file: {file.filename} ({len(file_content)} bytes)")

        # Extract text based on file type
        extracted_text = None
        if file.filename.lower().endswith(".pdf"):
            extracted_text = extract_text_from_pdf(file_content)
        elif file.filename.lower().endswith((".docx", ".doc")):
            extracted_text = extract_text_from_docx(file_content)
        else:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type. Please upload PDF or DOCX files.",
            )

        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(
                status_code=500,
                detail="Failed to extract meaningful text from document. The file may be empty or corrupted.",
            )

        logger.info(f"Extracted {len(extracted_text)} characters from document")

        # Create session
        session_id = research_system.session_manager.create_session()

        # Store document in session
        research_system.session_manager.store(
            session_id,
            {
                "document_text": extracted_text,
                "document_name": file.filename,
                "document_type": file.content_type,
                "task": task,
            },
        )

        # Analyze the document
        analysis_query = (
            f"{task}\n\nDocument: {file.filename}\n\nContent:\n{extracted_text[:5000]}"
        )

        # Use AI to analyze
        from google import generativeai as genai

        model = genai.GenerativeModel("gemini-2.5-flash")

        analysis_prompt = f"""
        Analyze this document and provide a comprehensive response.
        
        Document Name: {file.filename}
        Task: {task}
        
        Document Content:
        {extracted_text[:4000]}
        
        Please provide:
        1. A comprehensive summary
        2. 3-5 key findings or insights
        3. Main themes and conclusions
        
        Format your response clearly and professionally.
        """

        response = model.generate_content(analysis_prompt)
        analysis = response.text

        # Create mock source for the document
        document_source = {
            "title": file.filename,
            "url": f"uploaded://{file.filename}",
            "snippet": (
                extracted_text[:500] + "..."
                if len(extracted_text) > 500
                else extracted_text
            ),
            "source": "Uploaded Document",
        }

        # Extract key findings from analysis (simple extraction)
        key_findings = [
            f"Document analyzed: {file.filename}",
            f"Characters extracted: {len(extracted_text):,}",
            "Analysis completed successfully",
        ]

        return {
            "success": True,
            "session_id": session_id,
            "query": task,
            "summary": analysis,
            "key_findings": key_findings,
            "sources": [document_source],
            "num_sources": 1,
            "is_follow_up": False,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document processing error: {e}")
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )


@app.post("/api/v1/analyze-document")
async def analyze_document(request: DocumentAnalysisRequest):
    """
    Analyze a previously uploaded document with a new task.

    Use the session_id from the upload endpoint.
    """
    if not research_system:
        raise HTTPException(status_code=503, detail="Research system not initialized")

    try:
        # Get session data
        session_data = research_system.session_manager.retrieve(request.session_id)
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get document text
        document_text = session_data.get("document_text")
        if not document_text:
            raise HTTPException(status_code=404, detail="No document found in session")

        logger.info(f"Analyzing document: {request.task}")

        # Use coordinator to do research on the task
        plan = research_system.coordinator.create_plan(request.task)

        # Search for supplementary info
        sources = research_system.researcher.search_web(
            query=request.task, num_results=3
        )

        # Synthesize analysis
        report = research_system.summarizer.synthesize(
            query=request.task,
            sources=sources,
            context=[f"Document: {session_data.get('document_name', 'Unknown')}"],
        )

        return {
            "success": True,
            "analysis": report.get("summary", ""),
            "key_findings": report.get("key_findings", []),
            "sources": [SourceInfo(**source) for source in sources],
            "session_id": request.session_id,
            "document_name": session_data.get("document_name", "Unknown"),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/sessions")
async def list_sessions():
    """List all active sessions."""
    if not research_system:
        raise HTTPException(status_code=503, detail="Research system not initialized")

    try:
        sessions = research_system.session_manager.list_sessions()
        return {"sessions": sessions, "count": len(sessions)}
    except Exception as e:
        return {"sessions": [], "count": 0}


@app.delete("/api/v1/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific session."""
    if not research_system:
        raise HTTPException(status_code=503, detail="Research system not initialized")

    try:
        success = research_system.session_manager.delete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"success": True, "message": f"Session {session_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions gracefully."""
    return {"success": False, "error": exc.detail, "status_code": exc.status_code}


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions gracefully."""
    logger.error(f"Unhandled exception: {exc}")
    return {"success": False, "error": "Internal server error", "detail": str(exc)}


# Run the API
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
