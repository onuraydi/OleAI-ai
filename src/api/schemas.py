from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class InteractionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"
    SAVE = "save"

class RecommendationMode(str, Enum):
    DEFAULT = "default"
    ULTIMATE = "ultimate"
    STRICT = "strict"
    FOR_YOU = "foryou"
    QUICK = "quick"
    EXPLORE = "explore"
    MINIMAL = "minimalshopping"

class PantryItem(BaseModel): 
    id: UUID
    name: str
    quantity: float
    unit: str
    expiration_date: Optional[datetime] = Field(default=None, alias="expirationDate")

    model_config = ConfigDict(populate_by_name=True)

class RecipeInteraction(BaseModel):
    recipe_id: UUID = Field(..., alias="recipeId")
    interaction_type: str = Field(..., alias="type")
    interaction_date: datetime = Field(..., alias="date")

    model_config = ConfigDict(populate_by_name=True)

class RecommendationRequest(BaseModel):
    user_id: UUID = Field(..., alias="id")
    pantry_items: List[PantryItem] = Field(default_factory=list, alias="pantryItems")
    interactions: List[RecipeInteraction] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    excluded_ingredients: List[str] = Field(default_factory=list, alias="excludedIngredients")
    excluded_categories: List[str] = Field(default_factory=list, alias="excludedCategories")
    mode: RecommendationMode = Field(default=RecommendationMode.DEFAULT)
    use_zero_waste: bool = Field(default=False, alias="useZeroWaste")
    staple_ingredient_ids: List[str] = Field(default_factory=list, alias="stapleIngredientIds")

    model_config = ConfigDict(populate_by_name=True)

class RecipeScore(BaseModel):
    recipe_id: UUID = Field(..., alias="recipeId")
    score: float

    model_config = ConfigDict(populate_by_name=True)

class AiRecommendationResponse(BaseModel):
    recipes: List[RecipeScore] = Field(default_factory=list)

class RecipeIngredientSchema(BaseModel):
    id: UUID
    name: str
    amount: float
    unit: str
    aliases: List[str] = Field(default_factory=list)

class RecipeSyncRequest(BaseModel):
    recipe_id: UUID = Field(..., alias="recipeId")
    title: str
    ingredients: List[RecipeIngredientSchema]
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    is_published: bool = Field(default=True, alias="isPublished")
    popularity: int = Field(default=0)

    model_config = ConfigDict(populate_by_name=True)