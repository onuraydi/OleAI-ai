from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class InteractionType(str, Enum):
    LIKE = "like"
    DISLIKE = "dislike"

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

    model_config = ConfigDict(populate_by_name=True)

class RecipeScore(BaseModel):
    recipe_id: UUID = Field(..., alias="recipeId")
    score: float

    model_config = ConfigDict(populate_by_name=True)

class AiRecommendationResponse(BaseModel):
    recipes: List[RecipeScore] = Field(default_factory=list)

class RecipeSyncRequest(BaseModel):
    recipe_id: UUID = Field(..., alias="recipeId")
    title: str
    ingredients: str
    category: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)