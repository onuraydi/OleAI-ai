import logging
import uuid
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, status

from src.api.schemas import RecommendationRequest, RecipeScore
from src.models.recommender import RecipeRecommender
from src.services.data_preprocessor import DataPreprocessor

# Senior Standartlarında Loglama Yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("OleAI-AI-Service")

# Global Servis Örnekleri (Singleton benzeri kullanım için uygulama ömrü boyunca yaşarlar)
ai_recommender = RecipeRecommender()
data_preprocessor = DataPreprocessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama Yaşam Döngüsü Yönetimi (Lifespan): 
    Sistem ayağa kalkarken ağır matematiksel modelleri (TF-IDF matrisi vb.) 
    belleğe yükler ve kapanırken güvenli bir şekilde boşaltır.
    """
    logger.info("Yapay Zeka Servisi (OleAI) başlatılıyor...")
    
    try:
        # TODO: Entegrasyon aşamasında .NET Core API'den gerçek tarif listesi çekilecek.
        # Şimdilik modelin boş kalmaması için Mock verilerle sistemi ayağa kaldırıyoruz.
        initial_recipes = [
            {"id": uuid.uuid4(), "ingredients": "domates biber yumurta zeytinyağı"},
            {"id": uuid.uuid4(), "ingredients": "kinoa avokado limon nane"},
            {"id": uuid.uuid4(), "ingredients": "tavuk krema mantar sarımsak"},
            {"id": uuid.uuid4(), "ingredients": "makarna domates fesleğen sarımsak"}
        ]
        
        # Modeli bir kez eğitip RAM'de kilitliyoruz.
        ai_recommender.fit(initial_recipes)
        logger.info(f"Model {len(initial_recipes)} tarif ile başarıyla belleğe yüklendi.")
        
    except Exception as e:
        logger.critical(f"Sistem başlatılırken kritik hata oluştu: {str(e)}")
        # Başlangıçta hata oluşursa servisi hatalı çalıştırmamak için istisna fırlatıyoruz
        raise e

    yield  # API bu noktadan sonra istek kabul etmeye başlar.
    
    logger.info("Yapay Zeka Servisi kapatılıyor. Kaynaklar serbest bırakıldı.")

# FastAPI Uygulama Tanımı
app = FastAPI(
    title="OleAI Recommendation Engine",
    description="Yapay Zekâ Destekli, Zaman Sönümlemeli Dinamik Öneri API",
    version="1.0.0",
    lifespan=lifespan
)

@app.post(
    "/api/v1/recommendations",
    response_model=List[RecipeScore],
    status_code=status.HTTP_200_OK,
    summary="Kişiselleştirilmiş Tarif Önerileri Üret",
    response_description="Kullanıcı profili ve dolap verisine göre puanlanmış tarif ID listesi."
)
async def get_recommendations(request: RecommendationRequest):
    """
    .NET Core Backend'den gelen verileri alır:
    1. Malzemeleri NLP (DataPreprocessor) ile temizler.
    2. Zaman Sönümlemeli (Time Decay) algoritmayı kullanarak dinamik profil oluşturur.
    3. Bellekteki (In-Memory) vektör uzayında Kosinüs Benzerliği ile en yakın tarifleri bulur.
    """
    logger.info(f"Öneri Talebi: Kullanıcı={request.user_id}, Malzeme_Sayısı={len(request.pantry_items)}")
    
    try:
        # Sınır Durum Kontrolü: Malzeme yoksa işlem yapmaya gerek yok (Performance Optimization)
        if not request.pantry_items:
            logger.warning(f"Kullanıcı {request.user_id} için boş dolap verisi gönderildi.")
            return []

        # 1. Aşama: Malzeme İsimlerini Çıkar ve NLP Temizliği Uygula
        raw_pantry_list = [item.name for item in request.pantry_items]
        cleaned_pantry_text = data_preprocessor.process_pantry_items(raw_pantry_list)
        
        if not cleaned_pantry_text:
            return []

        # 2. Aşama: Öneri Motorunu Çalıştır (Dinamik Profilleme ve Vektör Hesabı)
        # top_k parametresi jüri sunumunda veya testlerde ihtiyaca göre artırılabilir
        recommended_results = ai_recommender.recommend(
            user_ingredients=cleaned_pantry_text,
            interactions=request.interactions,
            top_k=10
        )

        # 3. Aşama: Ham sonuçları (UUID, Score) Pydantic modeline dönüştür
        response_payload = [
            RecipeScore(recipeId=recipe_id, score=round(score, 4))
            for recipe_id, score in recommended_results
        ]

        logger.info(f"Kullanıcı {request.user_id} için {len(response_payload)} adet başarılı öneri döndürüldü.")
        return response_payload

    except ValueError as ve:
        logger.error(f"Veri doğrulama hatası: {str(ve)}")
        raise HTTPException(status_code=400, detail="Gönderilen verilerde tutarsızlık tespit edildi.")
        
    except Exception as e:
        logger.error(f"Öneri üretilirken beklenmeyen hata: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Öneri motoru şu an talebinize yanıt veremiyor."
        )

# Health Check Uç Noktası (Deployment ve Docker Monitoring için şarttır)
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Monitoring"])
async def health_check():
    return {"status": "healthy", "model_loaded": ai_recommender.recipe_matrix is not None}