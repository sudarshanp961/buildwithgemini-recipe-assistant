"""
Firestore tools for Recipe Assistant.
Hardcoded Project ID string as required for Agent Platform compatibility.
"""
from typing import Optional, List, Dict, Any
from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-02-57822a4ad31b"

def _get_db_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded Project ID."""
    return firestore.Client(project=PROJECT_ID)


def search_recipes(cuisine: Optional[str] = None, dietary_tag: Optional[str] = None, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Search the recipe catalog in Firestore by cuisine, dietary tag, or keyword.

    Args:
        cuisine: Optional cuisine filter (e.g., 'Mediterranean', 'Italian', 'Thai', 'Mexican').
        dietary_tag: Optional dietary tag filter (e.g., 'vegetarian', 'vegan', 'gluten-free', 'keto', 'quick').
        keyword: Optional search keyword to match in title or ingredients.

    Returns:
        List of matching recipe dictionaries.
    """
    db = _get_db_client()
    recipes_ref = db.collection("recipes")
    docs = recipes_ref.stream()
    
    results = []
    for doc in docs:
        recipe = doc.to_dict()
        recipe["id"] = doc.id
        
        # Filter by cuisine
        if cuisine and recipe.get("cuisine", "").lower() != cuisine.lower():
            continue
            
        # Filter by dietary tag
        if dietary_tag:
            tags = [t.lower() for t in recipe.get("dietary_tags", [])]
            if dietary_tag.lower() not in tags:
                continue
                
        # Filter by keyword in title or ingredients
        if keyword:
            kw = keyword.lower()
            title = recipe.get("title", "").lower()
            ingredients = " ".join(recipe.get("ingredients", [])).lower()
            if kw not in title and kw not in ingredients:
                continue
                
        results.append(recipe)
        
    return results


def get_favorite_recipes() -> List[Dict[str, Any]]:
    """
    Retrieve all favorite recipes stored in Firestore.

    Returns:
        List of favorite recipe dictionaries.
    """
    db = _get_db_client()
    favorites_ref = db.collection("favorites")
    docs = favorites_ref.stream()
    
    favorites = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        favorites.append(data)
        
    return favorites


def add_recipe(
    title: str,
    cuisine: str,
    prep_time: str,
    cook_time: str,
    servings: int,
    dietary_tags: List[str],
    ingredients: List[str],
    instructions: List[str],
    is_favorite: bool = False
) -> Dict[str, Any]:
    """
    Add a new recipe to the Firestore database.

    Args:
        title: Recipe title (e.g., 'Spaghetti Carbonara').
        cuisine: Cuisine type (e.g., 'Italian').
        prep_time: Preparation time (e.g., '15 mins').
        cook_time: Cooking time (e.g., '20 mins').
        servings: Number of servings.
        dietary_tags: List of dietary tags (e.g., ['quick', 'high-protein']).
        ingredients: List of ingredient strings.
        instructions: List of preparation steps.
        is_favorite: Whether to mark as a favorite immediately.

    Returns:
        Dictionary containing the created recipe and its Firestore document ID.
    """
    db = _get_db_client()
    doc_id = title.lower().replace(" ", "-").replace("'", "").replace("&", "and")
    
    recipe_data = {
        "id": doc_id,
        "title": title,
        "cuisine": cuisine,
        "prep_time": prep_time,
        "cook_time": cook_time,
        "servings": servings,
        "dietary_tags": dietary_tags,
        "ingredients": ingredients,
        "instructions": instructions,
        "is_favorite": is_favorite,
        "image_url": "https://images.unsplash.com/photo-1495521821757-a1efb6729352?auto=format&fit=crop&w=800&q=80"
    }
    
    db.collection("recipes").document(doc_id).set(recipe_data)
    if is_favorite:
        db.collection("favorites").document(doc_id).set(recipe_data)
        
    return recipe_data


def save_favorite_recipe(recipe_id: str) -> str:
    """
    Save a recipe from the catalog to favorites in Firestore.

    Args:
        recipe_id: Document ID or slug of the recipe to favorite.

    Returns:
        Confirmation message string.
    """
    db = _get_db_client()
    recipe_doc = db.collection("recipes").document(recipe_id).get()
    
    if not recipe_doc.exists:
        # Try searching by title match
        recipes = search_recipes(keyword=recipe_id)
        if recipes:
            recipe_data = recipes[0]
            recipe_id = recipe_data["id"]
        else:
            return f"Recipe with ID or title '{recipe_id}' was not found in the catalog."
    else:
        recipe_data = recipe_doc.to_dict()
        
    recipe_data["is_favorite"] = True
    db.collection("recipes").document(recipe_id).update({"is_favorite": True})
    db.collection("favorites").document(recipe_id).set(recipe_data)
    
    return f"Successfully saved '{recipe_data.get('title', recipe_id)}' to favorites!"


def remove_favorite_recipe(recipe_id: str) -> str:
    """
    Remove a recipe from favorites in Firestore.

    Args:
        recipe_id: Document ID or slug of the recipe to remove from favorites.

    Returns:
        Confirmation message string.
    """
    db = _get_db_client()
    db.collection("favorites").document(recipe_id).delete()
    
    recipe_doc = db.collection("recipes").document(recipe_id).get()
    if recipe_doc.exists:
        db.collection("recipes").document(recipe_id).update({"is_favorite": False})
        
    return f"Removed recipe '{recipe_id}' from favorites."
