import httpx
import logging
from src.core.config import settings

logger = logging.getLogger("OleAI-Sync")

class RecipeSyncService:
    """
    Backend (ASP.NET Core) ile AI servisi arasındaki veri senkronizasyonunu yönetir.
    Sistem ilk açıldığında tüm tarifleri çeker.
    """

    async def fetch_initial_recipes(self):
        """Backend'den tüm aktif tarifleri toplu olarak çeker."""
        try:
            # Local development için SSL doğrulamasını devre dışı bırakıyoruz (Self-signed certs)
            async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
                logger.info(f"Tarifler senkronize ediliyor: {settings.BACKEND_SYNC_URL}")
                response = await client.get(settings.BACKEND_SYNC_URL)
                
                if response.status_code == 200:
                    recipes = response.json()
                    logger.info(f"Backend'den {len(recipes)} tarif başarıyla alındı.")
                    return recipes
                else:
                    logger.warning(f"Backend senkronizasyon hatası: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"Backend'e bağlanılamadı, Mock verilerle devam ediliyor: {str(e)}")
            return []
