import hashlib
from typing import Dict, List, Optional
from urllib.parse import urlparse
from .metrics import MetricsCalculator
from .ai_scrapers import AIVisibilityChecker
from ..database.db import get_db, GEOAnalysis, AIVisibilityCheck
from sqlalchemy.orm import Session
import asyncio

class GEOCalculator:
    """Main GEO calculation engine."""
    
    def __init__(self):
        self.metrics = MetricsCalculator()
        
    async def calculate_geo_score(
        self,
        url: str,
        content: str,
        brand_terms: Optional[List[str]] = None,
        target_queries: Optional[List[str]] = None,
        check_ai_visibility: bool = True,
        db: Optional[Session] = None
    ) -> Dict:
        """Calculate complete GEO score for content."""
        
        # Extract domain
        domain = urlparse(url).netloc.replace('www.', '')
        
        # Default brand terms from domain
        if not brand_terms:
            brand_terms = [domain.split('.')[0]]
        
        # Default queries
        if not target_queries:
            target_queries = self._generate_queries(content, brand_terms)
        
        # Calculate content hash for caching
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        # Check cache if database provided
        if db:
            cached = db.query(GEOAnalysis).filter_by(
                url=url,
                content_hash=content_hash
            ).first()
            
            if cached:
                return self._format_cached_result(cached)
        
        # Calculate individual metrics
        stats_result = self.metrics.calculate_statistics_density(content)
        quote_result = self.metrics.calculate_quotation_authority(content)
        fluency_result = self.metrics.calculate_fluency_score(content)
        
        # Calculate relevance for primary query
        relevance_result = self.metrics.calculate_relevance_score(
            ' '.join(target_queries[:3]),  # Use top 3 queries
            content
        )
        
        # Simple authority score (without expensive APIs)
        authority_score = self._calculate_basic_authority(domain)
        
        # AI Visibility (if requested)
        ai_visibility = {'score': 50}  # Default
        if check_ai_visibility and target_queries:
            async with AIVisibilityChecker() as checker:
                visibility_data = await checker.check_all_platforms(
                    target_queries[:3],
                    brand_terms
                )
                ai_visibility = {
                    'score': visibility_data['summary']['visibility_score'],
                    'data': visibility_data
                }
        
        # Calculate composite score
        metrics = {
            'statistics': stats_result['score'],
            'quotation': quote_result['score'],
            'fluency': fluency_result['score'],
            'relevance': relevance_result['score'],
            'authority': authority_score,
            'ai_visibility': ai_visibility['score']
        }
        
        # Weights based on Princeton research + practical considerations
        weights = {
            'statistics': 0.20,   # 40% improvement in Princeton
            'quotation': 0.20,    # 41% improvement in Princeton
            'fluency': 0.15,      # 15-30% improvement
            'relevance': 0.15,
            'authority': 0.10,
            'ai_visibility': 0.20  # Critical for GEO
        }
        
        geo_score = sum(metrics[key] * weights[key] for key in metrics)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            stats_result, quote_result, fluency_result, 
            relevance_result, authority_score, ai_visibility
        )
        
        result = {
            'url': url,
            'domain': domain,
            'geo_score': round(geo_score, 1),
            'metrics': metrics,
            'detailed_metrics': {
                'statistics': stats_result,
                'quotation': quote_result,
                'fluency': fluency_result,
                'relevance': relevance_result,
                'ai_visibility': ai_visibility
            },
            'recommendations': recommendations,
            'confidence': self._calculate_confidence(metrics),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Save to database if provided
        if db:
            self._save_to_database(db, url, domain, content_hash, result)
        
        return result
    
    def _generate_queries(self, content: str, brand_terms: List[str]) -> List[str]:
        """Generate target queries from content."""
        # Simple implementation - extract key phrases
        words = content.split()
        
        # Find capitalized phrases (likely important)
        queries = []
        for i in range(len(words) - 2):
            if words[i][0].isupper() and words[i+1][0].islower():
                queries.append(f"{words[i]} {words[i+1]}")
        
        # Add brand-based queries
        for brand in brand_terms:
            queries.extend([
                f"{brand} reviews",
                f"best {brand} products",
                f"{brand} vs competitors"
            ])
        
        return queries[:10]  # Limit to 10
    
    def _calculate_basic_authority(self, domain: str) -> float:
        """Calculate basic authority score without expensive APIs."""
        score = 50  # Base score
        
        # Check domain characteristics
        if domain.endswith(('.edu', '.gov')):
            score += 30
        elif domain.endswith('.org'):
            score += 15
        
        # Check for SSL (simplified check)
        # In production, actually verify SSL
        if True:  # Assume HTTPS
            score += 10
        
        # Domain length (shorter = better usually)
        if len(domain) < 15:
            score += 10
        
        return min(score, 100)
    
    def _generate_recommendations(self, stats, quotes, fluency, relevance, authority, ai_visibility) -> List[Dict]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Sort metrics by score
        metric_scores = [
            ('statistics', stats['score'], stats['recommendation']),
            ('quotations', quotes['score'], quotes['recommendation']),
            ('fluency', fluency['score'], fluency['recommendation']),
            ('relevance', relevance['score'], relevance['recommendation']),
        ]
        
        # Focus on lowest 2 scores
        metric_scores.sort(key=lambda x: x[1])
        
        for metric_name, score, recommendation in metric_scores[:2]:
            if score < 70:
                recommendations.append({
                    'priority': 'high' if score < 50 else 'medium',
                    'metric': metric_name,
                    'action': recommendation,
                    'impact': f"Could improve GEO score by {int((70-score)*0.3)}%"
                })
        
        # AI visibility recommendation
        if ai_visibility['score'] < 50:
            recommendations.append({
                'priority': 'high',
                'metric': 'ai_visibility',
                'action': 'Your brand has low visibility in AI search results. Focus on creating authoritative content that directly answers common queries.',
                'impact': 'Critical for GEO success'
            })
        
        return recommendations
    
    def _calculate_confidence(self, metrics: Dict) -> str:
        """Calculate confidence level."""
        valid_metrics = sum(1 for v in metrics.values() if v > 0)
        
        if valid_metrics >= 5:
            return "high"
        elif valid_metrics >= 3:
            return "medium"
        else:
            return "low"
    
    def _save_to_database(self, db: Session, url: str, domain: str, 
                         content_hash: str, result: Dict):
        """Save analysis to database."""
        analysis = GEOAnalysis(
            url=url,
            domain=domain,
            content_hash=content_hash,
            geo_score=result['geo_score'],
            citation_score=result['metrics'].get('ai_visibility', 0),
            statistics_score=result['metrics']['statistics'],
            quotation_score=result['metrics']['quotation'],
            fluency_score=result['metrics']['fluency'],
            authority_score=result['metrics']['authority'],
            relevance_score=result['metrics']['relevance'],
            metrics=result['metrics'],
            recommendations=result['recommendations'],
            ai_visibility_data=result['detailed_metrics'].get('ai_visibility', {})
        )
        
        db.add(analysis)
        db.commit()
    
    def _format_cached_result(self, cached: GEOAnalysis) -> Dict:
        """Format cached database result."""
        return {
            'url': cached.url,
            'domain': cached.domain,
            'geo_score': cached.geo_score,
            'metrics': cached.metrics,
            'recommendations': cached.recommendations,
            'cached': True,
            'cached_at': cached.created_at.isoformat()
        }
