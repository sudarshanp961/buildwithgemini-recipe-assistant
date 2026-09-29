# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.adk.memory import VertexAiMemoryBankService
from google.genai import types

from a2ui.schema.manager import A2uiSchemaManager
from a2ui.basic_catalog.provider import BasicCatalog

from app.firestore_tools import (
    search_recipes,
    get_favorite_recipes,
    add_recipe,
    save_favorite_recipe,
    remove_favorite_recipe,
)
from app.image_tools import generate_dish_image
from app.a2ui_utils import a2ui_callback

MEMORY_BANK_ID = "3040430576021536768"
PROJECT_ID = "qwiklabs-gcp-02-57822a4ad31b"
LOCATION = "us-central1"


async def generate_memories_callback(callback_context: CallbackContext):
    """Callback triggered after each turn to extract and store durable user memories, allergies, and dietary preferences into Memory Bank."""
    try:
        await callback_context.add_session_to_memory()
    except Exception as e:
        print(f"Memory bank add_session_to_memory skipped or failed: {e}")
    return None


def memory_service_builder():
    """Returns a VertexAiMemoryBankService instance targeting the Memory Bank."""
    return VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=MEMORY_BANK_ID,
    )


# Instantiate memory service for local / deployed application use
memory_service = memory_service_builder()

# Build A2UI System Prompt using A2uiSchemaManager version 0.8
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are a friendly and knowledgeable Recipe Assistant. "
        "Your goal is to help home cooks discover recipes, search the recipe catalog stored in Firestore, "
        "retrieve and manage their favorite recipes, suggest meal ideas tailored to dietary preferences, "
        "remember user preferences across conversations using long-term memory, "
        "and generate appetizing food imagery using generate_dish_image."
    ),
    workflow_description=(
        "Analyze the user's culinary request, search recipes or retrieve memory/favorites as needed, "
        "and return structured A2UI UI when appropriate."
    ),
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        "{\"Image\": {\"url\": {\"literalString\": \"https://...\"}}}. Never point an "
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)

root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-flash-latest",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        search_recipes,
        get_favorite_recipes,
        add_recipe,
        save_favorite_recipe,
        remove_favorite_recipe,
        generate_dish_image,
    ],
    after_model_callback=a2ui_callback,
    after_agent_callback=generate_memories_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
