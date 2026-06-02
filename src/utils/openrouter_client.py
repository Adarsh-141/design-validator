"""
OpenRouter LLM client for fast, model-agnostic LLM inference.
Supports dozens of models: Claude, GPT-4, Mistral, Llama, etc.
"""

import json
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class OpenRouterClient:
    """
    OpenRouter LLM client for accessing multiple models via single API.
    
    Configuration:
    - Base URL: https://openrouter.ai/api/v1
    - Models: claude-3-haiku (fast), gpt-4-turbo, mistral-large, etc.
    - API Key: Required (from openrouter.ai)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.3,
        timeout: int = 60
    ):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key (get from https://openrouter.ai)
            model: Model to use (see MODELS dict for options)
            temperature: Sampling temperature (0.0-1.0)
            timeout: Request timeout in seconds
            
        Raises:
            ValueError: If API key is empty
        """
        if not api_key or not api_key.strip():
            raise ValueError(
                "OpenRouter API key required. Get it from https://openrouter.ai\n"
                "Set: $env:OPENROUTER_API_KEY='sk-or-...'"
            )
        
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.timeout = timeout
        self.tokens_used = 0
        self.base_url = "https://openrouter.ai/api/v1"
        
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify API key is valid."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            
            if response.status_code == 401:
                raise RuntimeError(
                    "Invalid OpenRouter API key. "
                    "Get it from https://openrouter.ai/keys"
                )
            
            response.raise_for_status()
            logger.info(f"✓ Connected to OpenRouter")
            logger.info(f"✓ Model: {self.model}")
            
        except requests.ConnectionError:
            raise ConnectionError(
                "Cannot connect to OpenRouter. Check your internet connection."
            )

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000,
        json_mode: bool = True
    ) -> str:
        """
        Generate text using OpenRouter.
        
        Args:
            prompt: User prompt/query
            system_prompt: System context for the model
            max_tokens: Maximum tokens to generate
            json_mode: Request JSON output format
            
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
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/design-validator",
                "X-Title": "Design Validator"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature,
                "max_tokens": max_tokens,
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 429:
                raise RuntimeError(
                    "Rate limited. Try again in a moment or use a different model."
                )
            
            response.raise_for_status()
            result = response.json()
            
            # Track token usage
            if 'usage' in result:
                self.tokens_used += result['usage'].get('total_tokens', 0)
                logger.debug(
                    f"Tokens: {result['usage'].get('prompt_tokens', 0)} input + "
                    f"{result['usage'].get('completion_tokens', 0)} output"
                )
            
            content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            if not content:
                raise RuntimeError("Empty response from model")
            
            return content.strip()
            
        except requests.Timeout:
            raise RuntimeError(
                f"Request timed out after {self.timeout}s. "
                "Try a faster model or increase timeout."
            )
        except requests.RequestException as e:
            raise RuntimeError(f"OpenRouter request failed: {str(e)}")

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1000
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


# Recommended models for different use cases
OPENROUTER_MODELS = {
    # Fast & Free (good for testing)
    "mistral-7b-free": "mistralai/mistral-7b-instruct:free",
    
    # Fast & Cheap (good balance)
    "mistral-7b": "mistralai/mistral-7b-instruct",
    "llama-8b": "meta-llama/llama-2-8b-chat:free",
    
    # Good reasoning (recommended for conflicts)
    "mistral-large": "mistralai/mistral-large",
    "claude-haiku": "anthropic/claude-3-haiku",
    
    # Best reasoning (but slower/more expensive)
    "claude-opus": "anthropic/claude-3-opus",
    "gpt-4-turbo": "openai/gpt-4-turbo",
    
    # Quick reference
    "list-models": None  # Shows all available models
}
