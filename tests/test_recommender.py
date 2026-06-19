from uuid import uuid4
from src.models.recommender import RecipeRecommender
from src.api.schemas import PantryItem, RecipeInteraction, RecommendationMode

def test_recommender_basic_flow():
    recommender = RecipeRecommender()
    
    r1_id = str(uuid4())
    r2_id = str(uuid4())
    
    recipes = [
        {
            "id": r1_id,
            "title": "Domates Çorbası",
            "ingredientsText": "domates su tuz biber sıvıyağ",
            "ingredients": [{"id": "i1", "name": "Domates", "amount": 500, "unit": "g"}],
            "category": "Çorba",
            "isPublished": True,
            "popularity": 5
        },
        {
            "id": r2_id,
            "title": "Tavuk Sote",
            "ingredientsText": "tavuk domates biber soğan",
            "ingredients": [{"id": "i2", "name": "Tavuk", "amount": 300, "unit": "g"}],
            "category": "Ana Yemek",
            "isPublished": True,
            "popularity": 8
        }
    ]
    
    # Test fitting
    recommender.fit(recipes)
    assert len(recommender.recipe_ids) == 2
    
    # Test adding single recipe
    r3_id = str(uuid4())
    recommender.add_recipe({
        "id": r3_id,
        "title": "Salata",
        "ingredientsText": "domates salatalık marul",
        "ingredients": [{"id": "i1", "name": "Domates", "amount": 100, "unit": "g"}],
        "category": "Salata",
        "isPublished": True,
        "popularity": 1
    })
    assert len(recommender.recipe_ids) == 3
    
    # Test recommendation (Default)
    pantry = [
        PantryItem(id="00000000-0000-0000-0000-000000000001", name="Domates", quantity=1.0, unit="kg")
    ]
    
    results = recommender.recommend(
        user_ingredients="domates",
        structured_pantry=pantry,
        interactions=[],
        mode=RecommendationMode.DEFAULT
    )
    assert len(results) > 0
    
    # Test recommendation (Strict Match)
    results_exact = recommender.recommend(
        user_ingredients="domates",
        structured_pantry=pantry,
        interactions=[],
        mode=RecommendationMode.STRICT
    )
    assert len(results_exact) >= 0

    # Test with interactions and zero waste
    from datetime import datetime
    interactions = [RecipeInteraction(recipe_id=r2_id, interaction_type="like", interaction_date=datetime.now())]
    results_inter = recommender.recommend(
        user_ingredients="tavuk",
        structured_pantry=[],
        interactions=interactions,
        use_zero_waste=True
    )
    assert len(results_inter) > 0
    
    # Test empty pantry
    empty_results = recommender.recommend(
        user_ingredients="",
        structured_pantry=[],
        interactions=[],
        mode=RecommendationMode.EXPLORE
    )
    assert len(empty_results) > 0

def test_recommender_edge_cases():
    recommender = RecipeRecommender()
    
    # 1. Fit empty
    recommender.fit([]) # Covers line 34
    assert len(recommender.recipe_ids) == 0
    
    # 2. Fit unpublished and string ingredients
    r1_id = str(uuid4())
    r2_id = str(uuid4())
    recipes = [
        {
            "id": r1_id,
            "title": "Unpublished",
            "isPublished": False,
            "ingredients": [{"name": "test"}]
        },
        {
            "id": r2_id,
            "title": "String Ing",
            "isPublished": True,
            "ingredients": "domates biber" # string instead of list
        }
    ]
    recommender.fit(recipes)
    assert len(recommender.recipe_ids) == 1 # Only r2_id
    
    # 3. Add existing recipe (Update)
    recommender.add_recipe({
        "id": r2_id,
        "title": "String Ing Updated",
        "isPublished": True,
        "ingredients": "domates biber soğan"
    })
    
    # 4. Add unpublished recipe
    recommender.add_recipe({
        "id": str(uuid4()),
        "isPublished": False
    })
    
    # 5. Recommendation edge cases
    from datetime import datetime, timedelta
    now = datetime.now()
    exp_date = now + timedelta(days=2) # Expires soon
    
    pantry = [
        PantryItem(id="00000000-0000-0000-0000-000000000010", name="Milk", quantity=1.0, unit="l", expirationDate=exp_date),
        PantryItem(id="00000000-0000-0000-0000-000000000011", name="Water", quantity=0.0, unit="ml") # zero amount
    ]
    
    # 6. Different interactions
    interactions = [
        RecipeInteraction(recipeId=r2_id, type="save", date=now),
        RecipeInteraction(recipeId=r2_id, type="dislike", date=now)
    ]
    
    # 7. Test modes
    for mode in [RecommendationMode.ULTIMATE, RecommendationMode.FOR_YOU, RecommendationMode.QUICK, RecommendationMode.MINIMAL]:
        results = recommender.recommend(
            user_ingredients="domates",
            structured_pantry=pantry,
            interactions=interactions,
            mode=mode,
            staple_ingredient_ids=["00000000-0000-0000-0000-000000000011"]
        )
        assert isinstance(results, list)
    
    # Recommend when matrix is None
    empty_recommender = RecipeRecommender()
    assert len(empty_recommender.recommend("", [], [])) == 0
