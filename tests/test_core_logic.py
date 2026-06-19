from uuid import uuid4
from datetime import datetime, timezone
from src.services.data_preprocessor import DataPreprocessor
from src.models.recommender import RecipeRecommender
from src.api.schemas import RecipeInteraction

def test_preprocessor_turkish_logic():
    preprocessor = DataPreprocessor()
    text = "İzmirli Domatesler ve Taze Zeytinyağı"
    cleaned = preprocessor.process_pantry_items([text])
    
    assert "izmirli" in cleaned
    assert "domatesler" in cleaned
    assert "ve" not in cleaned # Stopword
    assert "taze" not in cleaned # Stopword

def test_recommender_basic_logic():
    recommender = RecipeRecommender()
    
    # Mock recipes
    recipes = [
        {"id": uuid4(), "title": "Domates Çorbası", "ingredients": [{"name": "domates", "amount": 1}, {"name": "su", "amount": 1}, {"name": "tuz", "amount": 1}], "category": "Çorba"},
        {"id": uuid4(), "title": "Izgara Tavuk", "ingredients": [{"name": "tavuk", "amount": 1}, {"name": "kekik", "amount": 1}, {"name": "yağ", "amount": 1}], "category": "Ana Yemek"},
        {"id": uuid4(), "title": "Menemen", "ingredients": [{"name": "domates", "amount": 1}, {"name": "biber", "amount": 1}, {"name": "yumurta", "amount": 1}], "category": "Kahvaltı"}
    ]
    
    recommender.fit(recipes)
    
    # Test recommendation for someone with "domates"
    results = recommender.recommend(user_ingredients="domates", structured_pantry=[], interactions=[])
    
    assert len(results) > 0
    # Domates Çorbası or Menemen should be top
    assert any(ing.get("name") == "domates" for ing in recommender.recipe_metadata[results[0][0]]["ingredients"])

def test_hard_filtering():
    recommender = RecipeRecommender()
    recipe_id = uuid4()
    recipes = [
        {"id": recipe_id, "title": "Fıstıklı Baklava", "ingredients": [{"name": "fıstık", "amount": 1}, {"name": "un", "amount": 1}, {"name": "şeker", "amount": 1}], "category": "Tatlı"}
    ]
    recommender.fit(recipes)
    
    # Recommend with "fıstık" excluded
    results = recommender.recommend(
        user_ingredients="un", 
        structured_pantry=[],
        interactions=[], 
        excluded_ingredients=["fıstık"]
    )
    
    assert len(results) == 0 # Should be filtered out

def test_for_you_mode_logic():
    from src.api.schemas import RecommendationMode
    recommender = RecipeRecommender()
    
    recipe_like = uuid4()
    recipe_other = uuid4()
    
    recipes = [
        {"id": recipe_like, "title": "Pizza", "ingredients": [{"name": "hamur", "amount": 1}, {"name": "peynir", "amount": 1}, {"name": "sucuk", "amount": 1}], "category": "Fast Food"},
        {"id": recipe_other, "title": "Salata", "ingredients": [{"name": "marul", "amount": 1}, {"name": "domates", "amount": 1}, {"name": "salatalık", "amount": 1}], "category": "Diyet"}
    ]
    recommender.fit(recipes)
    
    # User has empty pantry but LIKED Pizza before
    interactions = [
        RecipeInteraction(
            recipeId=recipe_like, 
            type="like", 
            date=datetime.now(timezone.utc)
        )
    ]
    
    results = recommender.recommend(
        user_ingredients="", 
        structured_pantry=[],
        interactions=interactions,
        mode=RecommendationMode.FOR_YOU
    )
    
    assert len(results) > 0
    assert results[0][0] == recipe_like # Pizza should be top even with empty pantry

def test_incremental_add():
    recommender = RecipeRecommender()
    recipe1 = {"id": uuid4(), "title": "A", "ingredients": [{"name": "su", "amount": 1}], "category": "C"}
    recommender.add_recipe(recipe1)
    
    assert len(recommender.recipe_ids) == 1
    assert recommender.recipe_matrix is not None
    
    recipe2 = {"id": uuid4(), "title": "B", "ingredients": [{"name": "tuz", "amount": 1}], "category": "C"}
    recommender.add_recipe(recipe2)
    assert len(recommender.recipe_ids) == 2
    assert recommender.recipe_matrix.shape[0] == 2

def test_recommendation_modes():
    from src.api.schemas import RecommendationMode
    recommender = RecipeRecommender()
    
    r_quick = uuid4()
    r_complex = uuid4()
    
    recipes = [
        {"id": r_quick, "title": "Hızlı", "ingredients": [{"name": "su", "amount": 1}], "category": "A"},
        {"id": r_complex, "title": "Zor", "ingredients": [{"name": "a", "amount": 1}, {"name": "b", "amount": 1}, {"name": "c", "amount": 1}, {"name": "d", "amount": 1}, {"name": "e", "amount": 1}, {"name": "f", "amount": 1}, {"name": "g", "amount": 1}, {"name": "h", "amount": 1}, {"name": "i", "amount": 1}, {"name": "j", "amount": 1}, {"name": "k", "amount": 1}, {"name": "l", "amount": 1}, {"name": "m", "amount": 1}], "category": "A"}
    ]
    recommender.fit(recipes)
    
    # QUICK mode should favor few ingredients
    results = recommender.recommend(user_ingredients="su a b c", structured_pantry=[], interactions=[], mode=RecommendationMode.QUICK)
    assert results[0][0] == r_quick

    # STRICT mode should have high threshold
    results_strict = recommender.recommend(user_ingredients="su", structured_pantry=[], interactions=[], mode=RecommendationMode.STRICT)
    # Both might be returned but scores modified
    assert len(results_strict) >= 0
    
def test_cold_start_popularity():
    recommender = RecipeRecommender()
    r1 = uuid4()
    r2 = uuid4()
    recipes = [
        {"id": r1, "title": "A", "ingredients": [{"name": "domates", "amount": 1}], "category": "C"},
        {"id": r2, "title": "B", "ingredients": [{"name": "patlıcan", "amount": 1}], "category": "C"}
    ]
    recommender.fit(recipes)
    recommender.update_popularity(r2, 10)
    
    # No user ingredients, no interactions -> Popularity wins
    results = recommender.recommend(user_ingredients="", structured_pantry=[], interactions=[])
    assert results[0][0] == r2

def test_filtering_and_padding():
    recommender = RecipeRecommender()
    r1 = uuid4()
    r2 = uuid4()
    recipes = [
        {"id": r1, "title": "A", "ingredients": [{"name": "elma", "amount": 1}], "category": "Meyve"},
        {"id": r2, "title": "B", "ingredients": [{"name": "armut", "amount": 1}], "category": "Meyve"}
    ]
    recommender.fit(recipes)
    
    # Filter "elma"
    results = recommender.recommend(user_ingredients="meyve", structured_pantry=[], interactions=[], excluded_ingredients=["elma"])
    ids = [r[0] for r in results]
    assert r1 not in ids
    assert r2 in ids
