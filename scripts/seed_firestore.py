import os
from google.cloud import firestore

# Hardcoded Project ID string as required
PROJECT_ID = "qwiklabs-gcp-02-57822a4ad31b"

SAMPLE_RECIPES = [
    {
        "id": "mediterranean-chickpea-salad",
        "title": "Mediterranean Chickpea Salad",
        "cuisine": "Mediterranean",
        "prep_time": "15 mins",
        "cook_time": "0 mins",
        "servings": 4,
        "dietary_tags": ["vegetarian", "vegan", "gluten-free", "quick"],
        "ingredients": [
            "2 cans chickpeas, drained and rinsed",
            "1 cucumber, diced",
            "1 cup cherry tomatoes, halved",
            "1/2 red onion, finely chopped",
            "1/2 cup crumbled feta cheese (optional)",
            "1/4 cup extra virgin olive oil",
            "2 tbsp fresh lemon juice",
            "1 tsp dried oregano",
            "Salt and black pepper to taste"
        ],
        "instructions": [
            "In a large salad bowl, combine chickpeas, cucumber, tomatoes, and red onion.",
            "In a small jar, whisk together olive oil, lemon juice, oregano, salt, and pepper.",
            "Pour dressing over salad and toss gently to combine.",
            "Top with crumbled feta cheese before serving."
        ],
        "is_favorite": True,
        "image_url": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "creamy-tuscan-garlic-chicken",
        "title": "Creamy Tuscan Garlic Chicken",
        "cuisine": "Italian",
        "prep_time": "10 mins",
        "cook_time": "20 mins",
        "servings": 4,
        "dietary_tags": ["keto", "gluten-free", "high-protein"],
        "ingredients": [
            "1.5 lbs chicken breasts",
            "1 tbsp olive oil",
            "1 cup heavy cream",
            "1/2 cup chicken broth",
            "1 tsp garlic powder & 4 cloves minced garlic",
            "1 cup sun-dried tomatoes",
            "2 cups fresh spinach",
            "1/2 cup grated Parmesan cheese"
        ],
        "instructions": [
            "Season chicken breasts with salt, pepper, and garlic powder.",
            "Heat olive oil in a skillet over medium-high heat and sear chicken for 5 mins per side until golden.",
            "Remove chicken, add garlic and sun-dried tomatoes to the skillet.",
            "Pour in heavy cream and chicken broth, bring to a gentle simmer.",
            "Stir in Parmesan cheese and fresh spinach until wilted.",
            "Return chicken to skillet and simmer for 5 minutes until sauce thickens."
        ],
        "is_favorite": True,
        "image_url": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "spicy-thai-basil-tofu",
        "title": "Spicy Thai Basil Tofu (Pad Krapow)",
        "cuisine": "Thai",
        "prep_time": "10 mins",
        "cook_time": "10 mins",
        "servings": 2,
        "dietary_tags": ["vegan", "vegetarian", "spicy"],
        "ingredients": [
            "14 oz extra firm tofu, pressed and crumbled",
            "1 tbsp vegetable oil",
            "3 cloves garlic, minced",
            "2 Thai red chilies, chopped",
            "1 tbsp soy sauce & 1 tbsp dark soy sauce",
            "1 tbsp vegetarian mushroom sauce",
            "1 tsp sugar",
            "1 cup fresh Thai basil leaves"
        ],
        "instructions": [
            "Heat oil in a wok or large skillet over high heat.",
            "Add garlic and chilies, stir-fry for 30 seconds until fragrant.",
            "Add crumbled tofu and stir-fry for 3-4 minutes until lightly browned.",
            "Mix soy sauces, mushroom sauce, and sugar, then pour into the wok.",
            "Remove from heat and fold in fresh Thai basil until wilted.",
            "Serve hot over jasmine rice."
        ],
        "is_favorite": False,
        "image_url": "https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=800&q=80"
    },
    {
        "id": "avocado-black-bean-tacos",
        "title": "Avocado & Black Bean Tacos",
        "cuisine": "Mexican",
        "prep_time": "10 mins",
        "cook_time": "10 mins",
        "servings": 3,
        "dietary_tags": ["vegetarian", "vegan", "quick"],
        "ingredients": [
            "1 can black beans, rinsed and warmed with ground cumin",
            "6 small corn tortillas",
            "2 ripe avocados, sliced",
            "1/2 cup fresh corn kernels",
            "1/4 cup cilantro, chopped",
            "Lime wedges & salsa for serving"
        ],
        "instructions": [
            "Warm corn tortillas on a dry skillet or open flame.",
            "Layer warmed black beans and corn inside each tortilla.",
            "Top with avocado slices and fresh cilantro.",
            "Squeeze fresh lime juice on top and serve with salsa."
        ],
        "is_favorite": False,
        "image_url": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?auto=format&fit=crop&w=800&q=80"
    }
]

def seed_database():
    print(f"Connecting to Firestore for project: {PROJECT_ID}")
    db = firestore.Client(project=PROJECT_ID)
    
    recipes_ref = db.collection("recipes")
    favorites_ref = db.collection("favorites")
    
    for recipe in SAMPLE_RECIPES:
        doc_id = recipe["id"]
        recipes_ref.document(doc_id).set(recipe)
        print(f"Seeded recipe: {recipe['title']} (ID: {doc_id})")
        
        if recipe["is_favorite"]:
            favorites_ref.document(doc_id).set(recipe)
            print(f"  -> Added to favorites collection: {recipe['title']}")

    print("Successfully seeded Firestore database!")

if __name__ == "__main__":
    seed_database()
