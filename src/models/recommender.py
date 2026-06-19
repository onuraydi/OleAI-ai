from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
from uuid import UUID
from datetime import datetime, timezone
import math
import numpy as np
import logging
import threading

from src.api.schemas import RecipeInteraction, RecommendationMode, PantryItem
from src.core.config import settings

logger = logging.getLogger(__name__)

class RecipeRecommender:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=settings.MODEL_MAX_FEATURES)
        self.recipe_matrix = None
        self.recipe_ids: List[UUID] = []
        self.recipe_metadata: Dict[UUID, Dict] = {} 
        self.popularity_scores: Dict[UUID, int] = {}
        
        # STRUCTURED MEMORY
        self.structured_recipes: Dict[UUID, List[Dict]] = {}
        
        self.decay_constant = settings.DECAY_CONSTANT
        self._lock = threading.RLock() 
        self.last_trained_at: Optional[datetime] = None

    def fit(self, recipes: List[Dict]):
        with self._lock:
            if not recipes:
                return
            
            self.recipe_ids = []
            corpus = []
            
            for r in recipes:
                if not r.get("isPublished", True):
                    continue
                
                rid = r["id"]
                self.recipe_ids.append(rid)
                
                # Extract text for NLP (names + title + category)
                ing_list = r.get("ingredients", [])
                if isinstance(ing_list, str):
                    text = ing_list # fallback
                else:
                    text = " ".join([i.get("name", "") for i in ing_list])
                    
                corpus.append(text + " " + r.get("title", "") + " " + (r.get("category") or ""))
                self.recipe_metadata[rid] = r
                
                if isinstance(ing_list, list):
                    self.structured_recipes[rid] = ing_list
                else:
                    self.structured_recipes[rid] = []
                    
                if rid not in self.popularity_scores:
                    self.popularity_scores[rid] = r.get("popularity", 0)

            if corpus:
                self.recipe_matrix = self.vectorizer.fit_transform(corpus)
            self.last_trained_at = datetime.now(timezone.utc)
            logger.info(f"Model trained with {len(corpus)} recipes.")

    def update_popularity(self, recipe_id: UUID, increment: int = 1):
        with self._lock:
            self.popularity_scores[recipe_id] = self.popularity_scores.get(recipe_id, 0) + increment

    def add_recipe(self, recipe: Dict):
        with self._lock:
            try:
                # Remove if exists (update)
                rid = recipe["id"]
                if rid in self.recipe_ids:
                    # Clean up ALL old references before re-fitting
                    self.recipe_ids = [r for r in self.recipe_ids if r != rid]
                    self.recipe_metadata.pop(rid, None)
                    self.structured_recipes.pop(rid, None)
                    self.popularity_scores.pop(rid, None)
                    all_recipes = list(self.recipe_metadata.values()) + [recipe]
                    self.fit(all_recipes)
                    return

                if not recipe.get("isPublished", True):
                    return
                
                if self.recipe_matrix is None:
                    self.fit([recipe])
                    return

                # NLP Data
                text = recipe.get("ingredientsText", "") + " " + recipe.get("title", "") + " " + (recipe.get("category") or "")
                new_vec = self.vectorizer.transform([text])
                self.recipe_ids.append(rid)
                self.recipe_metadata[rid] = recipe
                self.structured_recipes[rid] = recipe.get("ingredients", [])
                
                if rid not in self.popularity_scores:
                    self.popularity_scores[rid] = recipe.get("popularity", 0)
                
                from scipy.sparse import vstack
                self.recipe_matrix = vstack([self.recipe_matrix, new_vec])
            except Exception as e:
                logger.error(f"Error adding recipe {recipe.get('id')}: {str(e)}")
                if "vocabulary" in str(e).lower():
                    all_recipes = list(self.recipe_metadata.values()) + [recipe]
                    self.fit(all_recipes)

    def _get_recipe_vector(self, recipe_id: UUID):
        try:
            idx = self.recipe_ids.index(recipe_id)
            return self.recipe_matrix[idx]
        except ValueError:
            return None
            
    def _calculate_fulfillment(self, recipe_id: UUID, pantry_dict: Dict[str, Dict], staple_ids: Optional[set] = None) -> float:
        '''
        Calculates the structured fulfillment ratio.
        pantry_dict: { ingredient_name_lower: { 'amount': float, 'id': str } }
        Returns: 0.0 to 1.0
        '''
        required = self.structured_recipes.get(recipe_id, [])
        if not required:
            return 0.0  # No structured ingredient data — cannot verify fulfillment
            
        total_ratio = 0.0
        for req in required:
            req_id = str(req.get("id")).lower()
            
            # Skip staple ingredients (salt, water, pepper) — assumed always available
            if staple_ids and req_id in staple_ids:
                total_ratio += 1.0
                continue
                
            req_name = req.get("name", "").lower()
            req_amount = float(req.get("amount", 0.0))
            aliases = [a.lower() for a in req.get("aliases", [])]
            
            # Find match in pantry
            match = None
            
            # 1. By exact ID
            for p_name, p_data in pantry_dict.items():
                if str(p_data["id"]).lower() == req_id:
                    match = p_data
                    break
            
            # 2. By Name or Alias
            if not match:
                for p_name, p_data in pantry_dict.items():
                    if p_name == req_name or p_name in aliases:
                        match = p_data
                        break
                        
            if match:
                if req_amount > 0:
                    req_unit = str(req.get("unit") or "").lower().strip()
                    p_unit = str(match.get("unit") or "").lower().strip()
                    
                    # Convert to base units for comparison
                    def get_base(amt, u):
                        if u in ["kg", "kilogram", "kilograms"]:
                            return amt * 1000.0, "g"
                        if u in ["g", "gram", "grams"]:
                            return amt, "g"
                        if u in ["l", "liter", "litre", "liters"]:
                            return amt * 1000.0, "ml"
                        if u in ["ml", "milliliter", "milliliters"]:
                            return amt, "ml"
                        return amt, u
                        
                    req_base_amt, req_base_u = get_base(req_amount, req_unit)
                    p_base_amt, p_base_u = get_base(float(match['amount']), p_unit)
                    
                    if req_base_u == p_base_u and req_base_amt > 0:
                        ratio = min(1.0, p_base_amt / req_base_amt)
                    else:
                        ratio = min(1.0, float(match['amount']) / req_amount)
                        
                    total_ratio += ratio
                else:
                    total_ratio += 1.0 # Just needs a pinch
                
        return total_ratio / len(required)

    def recommend(
        self, 
        user_ingredients: str,
        structured_pantry: List[PantryItem],
        interactions: List[RecipeInteraction], 
        excluded_ingredients: Optional[List[str]] = None,
        excluded_categories: Optional[List[str]] = None,
        staple_ingredient_ids: Optional[List[str]] = None,
        mode: RecommendationMode = RecommendationMode.DEFAULT,
        use_zero_waste: bool = False,
        top_k: int = 50
    ) -> List[Tuple[UUID, float]]:
        
        with self._lock:
            excluded_ingredients = excluded_ingredients or []
            excluded_categories = excluded_categories or []
            
            if self.recipe_matrix is None:
                return []
            
            # Prepare fast lookup dictionary for pantry
            pantry_dict = {}
            expiring_ingredients_ids = set()
            now = datetime.now(timezone.utc)
            
            if structured_pantry:
                for p in structured_pantry:
                    pantry_dict[p.name.lower()] = {
                        "id": p.id,
                        "amount": p.quantity,
                        "unit": getattr(p, "unit", "")
                    }
                    if p.expiration_date:
                        # Check if expiring in <= 3 days
                        exp_date = p.expiration_date.replace(tzinfo=timezone.utc) if p.expiration_date.tzinfo is None else p.expiration_date
                        days_left = (exp_date - now).total_seconds() / 86400.0
                        if days_left <= 3.0:
                            expiring_ingredients_ids.add(str(p.id).lower())
            
            # 1. Base User Vector
            user_vector = self.vectorizer.transform([user_ingredients]) if user_ingredients else None
            
            # 2. Dynamic Profiling (Interactions)
            if interactions:
                if user_vector is None:
                    user_vector = np.zeros((1, self.recipe_matrix.shape[1]))
                
                current_time = datetime.now(timezone.utc)
                for interaction in interactions:
                    recipe_vec = self._get_recipe_vector(interaction.recipe_id)
                    if recipe_vec is not None:
                        inter_date = interaction.interaction_date.replace(tzinfo=timezone.utc) if interaction.interaction_date.tzinfo is None else interaction.interaction_date
                        days_passed = max(0.0, (current_time - inter_date).total_seconds() / 86400.0)
                        weight = math.exp(-self.decay_constant * days_passed)

                        if interaction.interaction_type == "save":
                            sign = 1.5
                        elif interaction.interaction_type == "like":
                            sign = 1.2
                        else:
                            sign = -1.0 # Dislike
                            
                        user_vector += (recipe_vec * weight * sign)

            # 3. Taste Similarity Scores (NLP)
            if user_vector is not None and not np.all(user_vector == 0 if isinstance(user_vector, np.ndarray) else user_vector.toarray() == 0):
                if isinstance(user_vector, np.matrix):
                    user_vector = np.asarray(user_vector)
                taste_scores = cosine_similarity(user_vector, self.recipe_matrix).flatten()
            else:
                max_pop = max(self.popularity_scores.values()) if self.popularity_scores else 1
                taste_scores = np.array([
                    (self.popularity_scores.get(rid, 0) / (max_pop + 1)) * 0.1 
                    for rid in self.recipe_ids
                ])

            # 4. Evaluate Structured Fulfillment & Combine
            results = []
            now = datetime.now(timezone.utc)
            staple_set = set(str(s).lower() for s in (staple_ingredient_ids or []))

            for idx, taste_score in enumerate(taste_scores):
                recipe_id = self.recipe_ids[idx]
                meta = self.recipe_metadata[recipe_id]
                
                if not meta.get("isPublished", True):
                    continue
                
                # --- HARD FILTERS ---
                if meta.get("category") in excluded_categories: 
                    continue
                # For ingredients, we use structured list
                recipe_ingredients = self.structured_recipes.get(recipe_id, [])
                excluded_lower = set(exc.lower() for exc in excluded_ingredients)
                should_exclude = False
                for r_ing in recipe_ingredients:
                    if r_ing.get("name", "").lower() in excluded_lower:
                        should_exclude = True
                        break
                if should_exclude:
                    continue

                # --- HYBRID EVALUATION ---
                fulfillment = self._calculate_fulfillment(recipe_id, pantry_dict, staple_set)
                taste_score = float(taste_score)
                
                # Default Weights
                stock_weight = 0.5
                taste_weight = 0.5
                
                if mode == RecommendationMode.STRICT:
                    if fulfillment < 0.90:
                        continue # Hard eliminate
                    stock_weight = 0.8
                    taste_weight = 0.2
                elif mode == RecommendationMode.FOR_YOU:
                    stock_weight = 0.2
                    taste_weight = 0.8
                elif mode == RecommendationMode.MINIMAL:
                    if fulfillment < 0.60:
                        continue # Hard eliminate recipes missing too many ingredients
                    stock_weight = 0.8
                    taste_weight = 0.2
                elif mode == RecommendationMode.QUICK:
                    # Quick mode: prioritize fast recipes with available ingredients
                    cook_time = meta.get("cookTime", 0) or 0
                    prep_time = meta.get("prepTime", 0) or 0
                    total_time = cook_time + prep_time
                    if total_time > 45:  # Eliminate recipes taking > 45 min
                        continue
                    stock_weight = 0.7
                    taste_weight = 0.3
                elif mode == RecommendationMode.EXPLORE:
                    popularity = self.popularity_scores.get(recipe_id, 0)
                    taste_score *= (1.0 / (1.0 + math.log1p(popularity)))
                elif mode == RecommendationMode.ULTIMATE:
                    if fulfillment < 0.70:
                        continue  # Gurme mode requires high ingredient match
                    stock_weight = 0.55
                    taste_weight = 0.45
                    
                final_score = (fulfillment * stock_weight) + (taste_score * taste_weight)
                
                # PERFECT MATCH BONUS
                if fulfillment >= 0.999:
                    final_score *= 1.2
                    
                # Zero Waste Boost
                if use_zero_waste and expiring_ingredients_ids:
                    required_ingredients = self.structured_recipes.get(recipe_id, [])
                    recipe_uses_expiring = False
                    for req in required_ingredients:
                        if str(req.get("id")).lower() in expiring_ingredients_ids:
                            recipe_uses_expiring = True
                            break
                    if recipe_uses_expiring:
                        final_score *= 1.20
                    
                # New Recipe Boost
                created_at = meta.get("createdAt")
                if created_at:
                    if isinstance(created_at, str): 
                        # Handle C# datetime format
                        try:
                            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        except (ValueError, TypeError, AttributeError):
                            created_at = now
                    if created_at.tzinfo is None: 
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    days_old = (now - created_at).days
                    if days_old <= 7:
                        final_score *= 1.15

                if final_score > 0.01:
                    results.append((recipe_id, final_score))

            results.sort(key=lambda x: x[1], reverse=True)
            return results[:top_k]
