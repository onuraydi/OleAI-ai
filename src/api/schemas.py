from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

# Etkileşim türleri (Beğendi / Beğenmedi)
class InteractionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"

class RecommendationMode(str, Enum):
    QUICK = "quick"              # Fast recipes
    EXPLORE = "explore"          # New types of recipes
    HEALTHY = "healthy"          # Low cal/healthy ingredients
    MINIMAL_SHOPPING = "minimal" # Maximize pantry use
    FOR_YOU = "for_you"          # Focus on user taste/history
    ULTIMATE = "ultimate"        # Full combination of pantry + interactions
    DEFAULT = "default"          # Balanced

class PantryItem(BaseModel): 
    id: UUID = Field(..., description="Malzemenin sistemdeki benzersiz kimliği")
    name: str = Field(..., min_length=2, description="Malzemenin sistemdeki adı (örn: domates)")

class RecipeInteraction(BaseModel):
    recipe_id: UUID = Field(..., alias="recipeId", description="Etkileşime girilen tarifin ID'si")
    interaction_type: InteractionType = Field(..., alias="type", description="Etkileşim türü (like/dislike)")
    interaction_date: datetime = Field(..., alias="date", description="Etkileşimin gerçekleştiği tarih")

    class Config:
        populate_by_name = True

class RecommendationRequest(BaseModel):
    user_id: UUID = Field(..., alias="id", description="Kullanıcının benzersiz kimliği") 
    preferences: List[str] = Field(default_factory=list, description="Diyet kısıtları (örn: vegan, glutensiz)")
    pantry_items: List[PantryItem] = Field(..., alias="pantryItems", description="Dolaptaki malzemeler")
    
    # YENİ EKLENEN: Kullanıcının geçmiş etkileşimleri (Opsiyonel, yeni kullanıcıda boş gelebilir)
    interactions: List[RecipeInteraction] = Field(default_factory=list, alias="interactions", description="Kullanıcının geçmiş etkileşimleri")

    class Config:
        populate_by_name = True

class RecipeScore(BaseModel):
    recipe_id: UUID = Field(..., alias="recipeId", description="Önerilen tarifin kimliği (GUID)")
    score: float = Field(..., ge=0.0, le=1.0, description="0 ile 1 arasındaki benzerlik/uygunluk skoru")

    class Config:
        populate_by_name = True