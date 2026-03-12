"""
Audio Generator Service - Interface and OpenAI implementation
Generates audio based on creative manifests using AI models
"""
import os
import time
import tempfile
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import openai
from pydub import AudioSegment
import json

logger = logging.getLogger(__name__)

class AudioGenerator(ABC):
    """Abstract base class for audio generators"""
    
    @abstractmethod
    def generate(self, manifest