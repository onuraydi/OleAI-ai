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
from src.core.exceptions import global_exception_handler, OleAIException  # noqa: E402

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

app.add_exception_handler(OleAIException, global_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

@app.post("/api/v1/recommendations", response_model=AiRecommendationResponse, dependencies=[Depends(get_api_key)])
async def get_recommendations(request: RecommendationRequest):
    """Kullanıcıya özel hibrit öneriler döner."""
    try:
        # Malzemeleri temizle (NLP motoru için metne çeviriyoruz, ayrıca yapısal olanları da iletiyoruz)
        pantry_names = [p.name for p in request.pantry_items] if request.pantry_items else []
        pantry_text = data_preprocessor.process_pantry_items(pantry_names)
        
        # Önerileri hesapla
        raw_results = ai_recommender.recommend(
            user_ingredients=pantry_text,
            structured_pantry=request.pantry_items,
            interactions=request.interactions,
            excluded_ingredients=request.excluded_ingredients,
            excluded_categories=request.excluded_categories,
            staple_ingredient_ids=[str(s) for s in request.staple_ingredient_ids] if getattr(request, "staple_ingredient_ids", None) else [],
            mode=request.mode,
            use_zero_waste=request.use_zero_waste
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
        # NLP motoru için isimleri birleştirip temizle
        ingredient_names = " ".join([i.name for i in request.ingredients])
        clean_ingredients = data_preprocessor.clean_text(ingredient_names)
        
        recipe_data = {
            "id": request.recipe_id,
            "title": request.title,
            "ingredientsText": clean_ingredients,
            "ingredients": [i.model_dump() for i in request.ingredients],
            "category": request.category,
            "isPublished": request.is_published,
            "popularity": request.popularity
        }
        ai_recommender.add_recipe(recipe_data)
        return {"status": "success", "message": f"Recipe {request.recipe_id} synced."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "model_loaded": ai_recommender.recipe_matrix is not None}