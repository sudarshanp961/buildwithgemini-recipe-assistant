"""
Image generation function tools for Recipe Assistant.
"""
import os
import re
import uuid
from typing import Dict, Any
from google import genai
from google.genai import types
from google.cloud import storage

PROJECT_ID = "qwiklabs-gcp-02-57822a4ad31b"
BUCKET_NAME = "recipe-assistant-images-qwiklabs-gcp-02-57822a4ad31b"
ARTIFACTS_DIR = "/config/.gemini/antigravity/brain/9bb2bb85-128f-41b4-ae8a-d34a13a23e9d"


def generate_dish_image(prompt: str) -> str:
    """
    Generate an appetizing food image for a given dish or recipe description using Gemini.
    Saves the image locally as an artifact, uploads it to Cloud Storage, and returns the public URL.

    Args:
        prompt: Detailed description or name of the dish/recipe to generate an image for (e.g., 'A gourmet plate of Creamy Tuscan Garlic Chicken').

    Returns:
        String containing confirmation, saved artifact path, and public Cloud Storage URL.
    """
    clean_prompt = re.sub(r'[^a-zA-Z0-9]', '_', prompt[:20]).strip('_').lower()
    filename = f"dish_{clean_prompt}_{uuid.uuid4().hex[:6]}.jpg"

    # Use Vertex AI Gemini client in global region as requested
    client = genai.Client(vertexai=True, project=PROJECT_ID, location="global")
    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=f"A realistic, professional food photography shot of: {prompt}",
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"]
        )
    )

    img_bytes = None
    if response.candidates:
        for cand in response.candidates:
            if cand.content and cand.content.parts:
                for part in cand.content.parts:
                    if part.inline_data and part.inline_data.data:
                        img_bytes = part.inline_data.data
                        break

    if not img_bytes:
        return f"Failed to generate image for prompt: '{prompt}'."

    # Save to artifacts directory
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    artifact_path = os.path.join(ARTIFACTS_DIR, filename)
    with open(artifact_path, "wb") as f:
        f.write(img_bytes)

    # Save local backup in project directory
    local_dir = os.path.join(os.path.dirname(__file__), "..", "generated_images")
    os.makedirs(local_dir, exist_ok=True)
    local_path = os.path.join(local_dir, filename)
    with open(local_path, "wb") as f:
        f.write(img_bytes)

    # Upload to Cloud Storage
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(filename)
    blob.upload_from_filename(artifact_path, content_type="image/jpeg")

    public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{filename}"
    return f"Successfully generated image for '{prompt}'. Saved artifact: {artifact_path}\nPublic URL: {public_url}"
