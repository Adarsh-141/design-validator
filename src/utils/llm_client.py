"""
Ollama LLM client for local LLM inference.
Handles connection, prompt construction, and response parsing.
"""

import json
import requests
from typing import Optional, Dict, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class OllamaClient:
    """
    Local LLM interface via Ollama.
    
    Configuration:
    - Base URL: http://localhost:11434 (default)
    - Model: mistral:7b or neural-chat:7b (recommended)
    - Temperature: 0.3 (low for structured output)
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "mistral:7b",
        temperature: float = 0.3,
        timeout: int = 300
    ):
        """
        Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL
            model: Model name (must be pulled already)
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds (increased to 300 for slow systems)
        """
        self.base_url = base_url.rstrip('/')
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.tokens_used = 0
        
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify Ollama is running and model is available."""
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )
            response.raise_for_status()
            models = response.json().get('models', [])
            model_names = [m.get('name', '').split(':')[0] for m in models]
            
            if self.model.split(':')[0] not in model_names:
                raise RuntimeError(
                    f"Model {self.model} not found. "
                    f"Available: {model_names}. "
                    f"Run: ollama pull {self.model}"
                )
            logger.info(f"✓ Connected to Ollama at {self.base_url}")
            logger.info(f"✓ Model {self.model} available")
        except requests.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000,
        json_mode: bool = True
    ) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: User prompt/query
            system_prompt: System context for the model
            max_tokens: Maximum tokens to generate
            json_mode: Enforce JSON output format
            
        Returns:
            Generated text response
            
        Raises:
            RuntimeError: If generation fails
        """
        messages = []
        
        if system_prompt:
            messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })

        try:
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": self.temperature,
                        "num_predict": max_tokens,
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            result = response.json()
            
            # Track token usage
            if 'eval_count' in result:
                self.tokens_used += result.get('eval_count', 0)
            
            content = result.get('message', {}).get('content', '')
            
            if not content:
                raise RuntimeError("Empty response from model")
            
            return content.strip()
            
        except requests.Timeout:
            raise RuntimeError(
                f"Request timed out after {self.timeout}s. "
                "Try increasing timeout or reducing max_tokens."
            )
        except requests.RequestException as e:
            raise RuntimeError(f"Ollama request failed: {str(e)}")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2000
    ) -> Dict[str, Any]:
        """
        Generate and parse JSON response.
        
        Args:
            prompt: User prompt
            system_prompt: System context
            max_tokens: Maximum tokens
            
        Returns:
            Parsed JSON dictionary
            
        Raises:
            ValueError: If response is not valid JSON
        """
        response = self.generate(
            prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            json_mode=True
        )
        
        try:
            # Try to parse as-is
            return json.loads(response)
        except json.JSONDecodeError:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}|\[.*\]', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
            
            raise ValueError(
                f"Cannot parse JSON from response: {response[:200]}..."
            )

    def get_token_count(self) -> int:
        """Get total tokens used in this session."""
        return self.tokens_used

    def reset_token_count(self) -> None:
        """Reset token counter."""
        self.tokens_used = 0
