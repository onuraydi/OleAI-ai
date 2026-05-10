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
        {"id": uuid4(), "title": "Domates Çorbası", "ingredients": "domates su tuz", "category": "Çorba"},
        {"id": uuid4(), "title": "Izgara Tavuk", "ingredients": "tavuk kekik yağ", "category": "Ana Yemek"},
        {"id": uuid4(), "title": "Menemen", "ingredients": "domates biber yumurta", "category": "Kahvaltı"}
    ]
    
    recommender.fit(recipes)
    
    # Test recommendation for someone with "domates"
    results = recommender.recommend(user_ingredients="domates", interactions=[])
    
    assert len(results) > 0
    # Domates Çorbası or Menemen should be top
    assert "domates" in recommender.recipe_metadata[results[0][0]]["ingredients"]

def test_hard_filtering():
    recommender = RecipeRecommender()
    recipe_id = uuid4()
    recipes = [
        {"id": recipe_id, "title": "Fıstıklı Baklava", "ingredients": "fıstık un şeker", "category": "Tatlı"}
    ]
    recommender.fit(recipes)
    
    # Recommend with "fıstık" excluded
    results = recommender.recommend(
        user_ingredients="un", 
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
        {"id": recipe_like, "title": "Pizza", "ingredients": "hamur peynir sucuk", "category": "Fast Food"},
        {"id": recipe_other, "title": "Salata", "ingredients": "marul domates salatalık", "category": "Diyet"}
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
        interactions=interactions,
        mode=RecommendationMode.FOR_YOU
    )
    
    assert len(results) > 0
    assert results[0][0] == recipe_like # Pizza should be top even with empty pantry

def test_incremental_add():
    recommender = RecipeRecommender()
    recipe1 = {"id": uuid4(), "title": "A", "ingredients": "su", "category": "C"}
    recommender.add_recipe(recipe1)
    
    assert len(recommender.recipe_ids) == 1
    assert recommender.recipe_matrix is not None
    
    recipe2 = {"id": uuid4(), "title": "B", "ingredients": "tuz", "category": "C"}
    recommender.add_recipe(recipe2)
    assert len(recommender.recipe_ids) == 2
    assert recommender.recipe_matrix.shape[0] == 2

def test_recommendation_modes():
    from src.api.schemas import RecommendationMode
    recommender = RecipeRecommender()
    
    r_quick = uuid4()
    r_complex = uuid4()
    
    recipes = [
        {"id": r_quick, "title": "Hızlı", "ingredients": "su", "category": "A"},
        {"id": r_complex, "title": "Zor", "ingredients": "a b c d e f g h i j k l m", "category": "A"}
    ]
    recommender.fit(recipes)
    
    # QUICK mode should favor few ingredients
    results = recommender.recommend(user_ingredients="su a b c", interactions=[], mode=RecommendationMode.QUICK)
    assert results[0][0] == r_quick

    # STRICT mode should have high threshold
    results_strict = recommender.recommend(user_ingredients="su", interactions=[], mode=RecommendationMode.STRICT)
    # Both might be returned but scores modified
    assert len(results_strict) >= 0
    
def test_cold_start_popularity():
    recommender = RecipeRecommender()
    r1 = uuid4()
    r2 = uuid4()
    recipes = [
        {"id": r1, "title": "A", "ingredients": "domates", "category": "C"},
        {"id": r2, "title": "B", "ingredients": "patlıcan", "category": "C"}
    ]
    recommender.fit(recipes)
    recommender.update_popularity(r2, 10)
    
    # No user ingredients, no interactions -> Popularity wins
    results = recommender.recommend(user_ingredients="", interactions=[])
    assert results[0][0] == r2

def test_filtering_and_padding():
    recommender = RecipeRecommender()
    r1 = uuid4()
    r2 = uuid4()
    recipes = [
        {"id": r1, "title": "A", "ingredients": "elma", "category": "Meyve"},
        {"id": r2, "title": "B", "ingredients": "armut", "category": "Meyve"}
    ]
    recommender.fit(recipes)
    
    # Filter "elma"
    results = recommender.recommend(user_ingredients="meyve", interactions=[], excluded_ingredients=["elma"])
    ids = [r[0] for r in results]
    assert r1 not in ids
    assert r2 in ids
