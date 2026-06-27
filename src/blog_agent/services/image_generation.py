"""Image generation service.

Generates the images based on the given Provider option
"""

from __future__ import annotations
from typing import Protocol
from blog_agent.core import get_settings, get_logger

logger = get_logger(__name__)

class ImageGenerationError(Exception):
    pass

class ImageService(Protocol):
    enabled: bool
    def generate(self, prompt: str) -> bytes: ...

class NullImageService:
    """Used when images are disabled or no key is present."""
    enabled = False
    def generate(self, prompt: str) -> bytes:
        return ImageGenerationError("Image generation is disabled")
    
class GeminiImageService:
    enabled = True

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, prompt: str) -> bytes:
        from google import genai
        from google.genai import types

        client = genai.client(api_key = self._api_key)
        resp = client.models.generate_content(
            model = self._model,
            contents = prompt,
            config = types.GenerateContentConfig(response_modalities=["IMAGE"]),
        )
        parts = getattr(resp, "parts", None)
        if not parts and getattr(resp, "candidates", None):
            parts = resp.candidates[0].content.parts
        for part in parts or []:
            inline = getattr(part, "inline_data", None)
            if inline and getattr(inline, "data", None):
                return inline.data
        raise ImageGenerationError("No image bytes returned.")
    

class OpenAIImageService:
    enabled = True

    def __init__(self, api_key: str, model: str) -> None:
        self._api_key = api_key
        self._model = model

    def generate(self, prompt: str) -> bytes:
        import base64
        import urllib.request
        from openai import OpenAI

        client = OpenAI(api_key=self._api_key)
        resp = client.images.generate(
            model=self._model,
            prompt=prompt,
            size="1024x1024",
            n=1,
        )
        item = resp.data[0]
        if item.b64_json:
            return base64.b64decode(item.b64_json)
        if item.url:
            with urllib.request.urlopen(item.url) as r:
                return r.read()
        raise ImageGenerationError("No image data returned.")


def get_image_service() -> ImageService:
    settings = get_settings()
    if not settings.images_enabled:
        return NullImageService()

    if settings.image_provider == "openai" and settings.openai_api_key:
        return OpenAIImageService(api_key=settings.openai_api_key, model=settings.image_model)
    if settings.image_provider == "gemini" and settings.google_api_key:
        return GeminiImageService(api_key=settings.google_api_key, model=settings.image_model)
    
    logger.info("image_service.disabled", images_enabled=settings.images_enabled)
    return NullImageService()   # no key for chosen provider → graceful degradation