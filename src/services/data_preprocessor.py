import re
import unicodedata
from typing import List

class DataPreprocessor:
    """
    Tarif içeriklerini ve kullanıcı girdilerini makine öğrenimi modeline 
    uygun hale getirmek için temizleme ve normalizasyon yapan servis.
    Türkçe karakter ve stopword (etkisiz kelime) desteğine sahiptir.
    """

    def __init__(self):
        # Öneri kalitesini artırmak için anlam taşımayan bağlaç ve kelimeler
        self.stopwords = {
            "ve", "veya", "ile", "bir", "birkaç", "taze", "kuru", "yemek", 
            "kaşığı", "tatlı", "bardak", "su", "tuz", "için", "gibi", "kadar"
        }

    def _normalize_turkish(self, text: str) -> str:
        """Türkçe karakterleri (ı/i, ş/s vb.) normalize eder ve küçük harfe çevirir."""
        text = text.replace('İ', 'i').replace('I', 'ı')
        text = text.lower()
        return text

    def clean_text(self, text: str) -> str:
        """Metni temizler, noktalama işaretlerini atar ve normalleştirir."""
        if not text:
            return ""
        
        # 1. Normalizasyon
        text = self._normalize_turkish(text)
        
        # 2. Özel karakterleri ve sayıları temizle
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', ' ', text)
        
        # 3. Kelimelere ayır ve stopword'leri temizle
        words = text.split()
        cleaned_words = [w for w in words if w not in self.stopwords and len(w) > 1]
        
        return " ".join(cleaned_words)

    def process_pantry_items(self, items: List[str]) -> str:
        """Kullanıcının dolap malzemelerini temizleyip tek bir metin haline getirir."""
        cleaned_items = [self.clean_text(item) for item in items]
        return " ".join(filter(None, cleaned_items))
