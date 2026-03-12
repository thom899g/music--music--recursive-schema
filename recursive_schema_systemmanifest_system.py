"""
Manifest System - Creative DNA definition and management
Defines the creative intent, technical specifications, and distribution strategy
"""
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QualityGateStatus(Enum):
    """Status of quality gate checks"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"

@dataclass
class CreativeIntent:
    """Creative direction for music generation"""
    emotional_adjectives: List[str]
    reference_tracks: List[str]
    target_genres: List[str]
    visual_keywords: List[str]
    brand_identity: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

@dataclass
class TechnicalSpec:
    """Technical specifications for audio"""
    tempo_range: List[int]
    duration_range: List[int]
    quality_gates: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

@dataclass
class DistributionSchedule:
    """Distribution strategy and scheduling"""
    primary_platform: str
    secondary_formats: List[str]
    release_time: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

class GenerationManifest:
    """Main manifest class for tracking generation lifecycle"""
    
    def __init__(
        self,
        campaign_id: Optional[str] = None,
        creative_intent: Optional[CreativeIntent] = None,
        technical_spec: Optional[TechnicalSpec] = None,
        distribution_schedule: Optional[DistributionSchedule] = None
    ):
        """Initialize manifest with default values or provided values"""
        self.campaign_id = campaign_id or f"rs_{datetime.now().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
        self.creation_time = datetime.utcnow().isoformat()
        
        # Default creative intent for minimal techno
        self.creative_intent = creative_intent or CreativeIntent(
            emotional_adjectives=["hypnotic", "driving", "evolving", "atmospheric", "mechanical"],
            reference_tracks=["Basic Channel - Phylyps", "Robert Hood - Minus", "Jeff Mills - The Bells"],
            target_genres=["Minimal Techno", "AI-Generated Music", "Electronic"],
            visual_keywords=["generative", "cybernetic", "recursive", "modular"],
            brand_identity="Recursive Schema - Autonomous Music System"
        )
        
        # Default technical spec
        self.technical_spec = technical_spec or TechnicalSpec(
            tempo_range=[124, 132],
            duration_range=[240, 420],  # 4-7 minutes
            quality_gates={
                "min_loudness": -23.0,
                "max_true_peak": -1.0,
                "spectral_threshold": 60.0,
                "min_dynamic_range": 8.0
            }
        )
        
        # Default distribution
        self.distribution_schedule = distribution_schedule or DistributionSchedule(
            primary_platform="claw.fm",
            secondary_formats=["tiktok_60s", "youtube_ambient", "stems", "instagram_30s"],
            release_time="auto"
        )
        
        # Generation tracking
        self.generation_id: Optional[str] = None
        self.status: str = "initialized"
        self.quality_gate_status: QualityGateStatus = QualityGateStatus.PENDING
        self.quality_metrics: Dict[str, Any] = {}
        self.error_log: List[str] = []
        self.generation_count: int = 0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary for serialization"""
        return {
            "campaign_id": self.campaign_id,
            "creation_time": self.creation_time,
            "creative_intent": self.creative_intent.to_dict(),
            "technical_spec": self.technical_spec.to_dict(),
            "distribution_schedule": self.distribution_schedule.to_dict(),
            "generation_id": self.generation_id,
            "status": self.status,
            "quality_gate_status": self.quality_gate_status.value,
            "quality_metrics": self.quality_metrics,
            "error_log": self.error_log,
            "generation_count": self.generation_count
        }
    
    def save(self, filepath: str = "generation_manifest.json") -> None:
        """Save manifest to JSON file"""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.to_dict(), f, indent=2)
            logger.info(f"Manifest saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save manifest: {e}")
            raise
    
    @classmethod
    def load(cls, filepath: str) -> "GenerationManifest":
        """Load manifest from JSON file"""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            # Reconstruct objects
            creative_intent = CreativeIntent(**data["creative_intent"])
            technical_spec = TechnicalSpec(**data["technical_spec"])
            distribution_schedule = DistributionSchedule(**data["distribution_schedule"])
            
            manifest = cls(
                campaign_id=data["campaign_id"],
                creative_intent=creative_intent,
                technical_spec=technical_spec,
                distribution_schedule=distribution_schedule
            )
            
            # Restore state
            manifest.generation_id = data.get("generation_id")
            manifest.status = data.get("status", "initialized")
            manifest.quality_gate_status = QualityGateStatus(data.get("quality_gate_status", "pending"))
            manifest.quality_metrics = data.get("quality_metrics", {})
            manifest.error_log = data.get("error_log", [])
            manifest.generation_count = data.get("generation_count", 0)
            
            logger.info(f"Manifest loaded from {filepath}")
            return manifest
            
        except FileNotFoundError:
            logger.warning(f"Manifest file not found, creating new: {filepath}")
            return cls()
        except Exception as e:
            logger.error(f"Failed to load manifest: {e}")
            raise
    
    def log_error(self, error: str) -> None:
        """Log error to manifest"""
        timestamp = datetime.utcnow().isoformat()
        self.error_log.append(f"{timestamp}: {error}")
        logger.error(f"Manifest error logged: {error}")
    
    def update_status(self, status: str) -> None:
        """Update generation status"""
        self.status = status
        logger.info(f"Manifest status updated: {status}")
    
    def increment_generation(self) -> None:
        """Increment generation counter"""
        self.generation_count += 1
        logger.info(f"Generation count: {self.generation_count}")