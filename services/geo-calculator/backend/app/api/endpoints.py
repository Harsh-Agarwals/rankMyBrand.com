from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
import asyncio

from ..core.calculator import GEOCalculator
from ..database.db import get_db, GEOAnalysis
from ..models.schemas import GEORequest, GEOResponse, BatchRequest

router = APIRouter()

# Initialize calculator
calculator = GEOCalculator()

@router.post("/analyze", response_model=GEOResponse)
async def analyze_content(
    request: GEORequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze content for GEO score."""
    try:
        result = await calculator.calculate_geo_score(
            url=str(request.url),
            content=request.content,
            brand_terms=request.brand_terms,
            target_queries=request.target_queries,
            check_ai_visibility=request.check_ai_visibility,
            db=db
        )
        
        return GEOResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze/batch")
async def batch_analyze(
    request: BatchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Analyze multiple URLs in batch."""
    job_id = str(uuid.uuid4())
    
    # Start background processing
    background_tasks.add_task(
        process_batch_analysis,
        job_id,
        request.urls,
        db
    )
    
    return {
        "job_id": job_id,
        "status": "processing",
        "urls_count": len(request.urls)
    }

@router.get("/analysis/{domain}")
async def get_domain_analysis(
    domain: str,
    db: Session = Depends(get_db)
):
    """Get latest analysis for a domain."""
    analysis = db.query(GEOAnalysis).filter_by(
        domain=domain
    ).order_by(GEOAnalysis.created_at.desc()).first()
    
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis found for domain")
    
    return {
        "domain": analysis.domain,
        "geo_score": analysis.geo_score,
        "metrics": analysis.metrics,
        "recommendations": analysis.recommendations,
        "analyzed_at": analysis.created_at
    }

@router.get("/trending")
async def get_trending_metrics(db: Session = Depends(get_db)):
    """Get trending GEO metrics across all analyses."""
    # Get recent analyses
    recent = db.query(GEOAnalysis).order_by(
        GEOAnalysis.created_at.desc()
    ).limit(100).all()
    
    if not recent:
        return {"message": "No data available"}
    
    # Calculate averages
    avg_scores = {
        'geo_score': sum(a.geo_score for a in recent) / len(recent),
        'statistics': sum(a.statistics_score for a in recent) / len(recent),
        'quotation': sum(a.quotation_score for a in recent) / len(recent),
        'fluency': sum(a.fluency_score for a in recent) / len(recent),
    }
    
    return {
        "sample_size": len(recent),
        "average_scores": avg_scores,
        "top_performers": [
            {
                "domain": a.domain,
                "score": a.geo_score
            }
            for a in sorted(recent, key=lambda x: x.geo_score, reverse=True)[:5]
        ]
    }

async def process_batch_analysis(job_id: str, urls: List[str], db: Session):
    """Process batch analysis in background."""
    # Implementation for batch processing
    pass
