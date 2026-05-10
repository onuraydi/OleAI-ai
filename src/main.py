import sys
from pathlib import Path
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends

# Proje kök dizinini otomatik olarak Python yoluna ekle
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

# sys.path değişikliğinden sonra projedeki lokallerin yüklenmesi için # noqa: E402 ekliyoruz.
from src.api.schemas import RecommendationRequest, AiRecommendationResponse, RecipeScore, RecipeSyncRequest  # noqa: E402
from src.models.recommender import RecipeRecommender  # noqa: E402
from src.services.data_preprocessor import DataPreprocessor  # noqa: E402
from src.services.recipe_sync_service import RecipeSyncService  # noqa: E402
from src.core.security.api_key import get_api_key  # noqa: E402

# Loglama Yapılandırması
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("OleAI-Main")

# Global Servisler
ai_recommender = RecipeRecommender()
data_preprocessor = DataPreprocessor()
sync_service = RecipeSyncService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Sistem açılışında Backend'den tarifleri çeker ve modeli eğitir."""
    logger.info("OleAI Öneri Motoru başlatılıyor...")
    
    # 1. Backend'den tarifleri çek
    initial_recipes = await sync_service.fetch_initial_recipes()
    
    if not initial_recipes:
        logger.warning("Backend'den tarif alınamadı, boş modelle başlatılıyor.")
        initial_recipes = [] # Boş liste ile başlat, sync endpoint'i ile eklenebilir.

    # 2. Modeli eğit
    ai_recommender.fit(initial_recipes)
    logger.info(f"Sistem {len(initial_recipes)} tarif ile hazır.")
    
    yield
    logger.info("Sistem kapatılıyor.")

app = FastAPI(title="OleAI Engine", lifespan=lifespan)

@app.post("/api/v1/recommendations", response_model=AiRecommendationResponse, dependencies=[Depends(get_api_key)])
async def get_recommendations(request: RecommendationRequest):
    """Kullanıcıya özel hibrit öneriler döner."""
    try:
        # Malzemeleri temizle
        pantry_names = [p.name for p in request.pantry_items] if request.pantry_items else []
        pantry_text = data_preprocessor.process_pantry_items(pantry_names)
        
        # Önerileri hesapla
        raw_results = ai_recommender.recommend(
            user_ingredients=pantry_text,
            interactions=request.interactions,
            excluded_ingredients=request.excluded_ingredients,
            excluded_categories=request.excluded_categories,
            mode=request.mode
        )
        
        scores = [RecipeScore(recipeId=res[0], score=res[1]) for res in raw_results]
        return AiRecommendationResponse(recipes=scores)
    except Exception as e:
        logger.error(f"Öneri hatası: {str(e)}")
        raise HTTPException(status_code=500, detail="Öneri oluşturulamadı.")

@app.post("/api/v1/recipes/sync", dependencies=[Depends(get_api_key)])
async def sync_recipe(request: RecipeSyncRequest):
    """Yeni bir tarif eklendiğinde modeli anlık günceller."""
    try:
        clean_ingredients = data_preprocessor.clean_text(request.ingredients)
        recipe_data = {
            "id": request.recipe_id,
            "title": request.title,
            "ingredients": clean_ingredients,
            "category": request.category
        }
        ai_recommender.add_recipe(recipe_data)
        return {"status": "success", "message": f"Recipe {request.recipe_id} synced."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": ai_recommender.recipe_matrix is not None}