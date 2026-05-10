from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple, Optional
from uuid import UUID
from datetime import datetime, timezone
import math
import numpy as np
import logging
import threading

from src.api.schemas import RecipeInteraction, RecommendationMode
from src.core.config import settings

logger = logging.getLogger(__name__)

class RecipeRecommender:
    """
    Hybrid Recommender Engine: Content-based filtering with Dynamic Profiling (Rocchio).
    Includes hard-filtering, thread-safety, and specialized recommendation modes.
    """

    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=settings.MODEL_MAX_FEATURES)
        self.recipe_matrix = None
        self.recipe_ids: List[UUID] = []
        self.recipe_metadata: Dict[UUID, Dict] = {} 
        self.popularity_scores: Dict[UUID, int] = {} # Track interactions per recipe
        
        self.decay_constant = settings.DECAY_CONSTANT
        self._lock = threading.RLock() 
        self.last_trained_at: Optional[datetime] = None

    def fit(self, recipes: List[Dict]):
        """
        Full training of the model. 
        recipes: list of dicts with {"id", "ingredients", "title", "category", "created_at"}
        """
        with self._lock:
            if not recipes:
                return
            
            self.recipe_ids = [r["id"] for r in recipes]
            corpus = [r["ingredients"] for r in recipes]
            
            self.recipe_matrix = self.vectorizer.fit_transform(corpus)
            self.recipe_metadata = {r["id"]: r for r in recipes}
            
            # Initialize popularity if not exists
            for rid in self.recipe_ids:
                if rid not in self.popularity_scores:
                    self.popularity_scores[rid] = 0

            self.last_trained_at = datetime.now(timezone.utc)
            logger.info(f"Model trained with {len(corpus)} recipes.")

    def update_popularity(self, recipe_id: UUID, increment: int = 1):
        """Called when a recipe is liked/saved to track popularity for cold-start."""
        with self._lock:
            self.popularity_scores[recipe_id] = self.popularity_scores.get(recipe_id, 0) + increment

    def add_recipe(self, recipe: Dict):
        """Incremental update: Adds a new recipe without full retraining."""
        with self._lock:
            try:
                if self.recipe_matrix is None:
                    logger.info(f"Model not initialized. Training with first recipe: {recipe['id']}")
                    self.fit([recipe])
                    return

                new_vec = self.vectorizer.transform([recipe["ingredients"]])
                self.recipe_ids.append(recipe["id"])
                self.recipe_metadata[recipe["id"]] = recipe
                if recipe["id"] not in self.popularity_scores:
                    self.popularity_scores[recipe["id"]] = 0
                
                from scipy.sparse import vstack
                self.recipe_matrix = vstack([self.recipe_matrix, new_vec])
                logger.debug(f"Recipe {recipe['id']} added incrementally.")
            except Exception as e:
                logger.error(f"Error adding recipe {recipe.get('id')}: {str(e)}")
                # If it's a vocabulary error, we might need a full fit
                if "vocabulary" in str(e).lower():
                    self.fit([recipe])

    def _get_recipe_vector(self, recipe_id: UUID):
        try:
            idx = self.recipe_ids.index(recipe_id)
            return self.recipe_matrix[idx]
        except ValueError:
            return None

    def recommend(
        self, 
        user_ingredients: str, 
        interactions: List[RecipeInteraction], 
        excluded_ingredients: List[str] = [],
        excluded_categories: List[str] = [],
        mode: RecommendationMode = RecommendationMode.DEFAULT,
        top_k: int = 50
    ) -> List[Tuple[UUID, float]]:
        
        with self._lock:
            if self.recipe_matrix is None:
                return []
            
            # 1. Base User Vector
            user_vector = self.vectorizer.transform([user_ingredients]) if user_ingredients else None
            
            pantry_weight = 1.0
            if mode == RecommendationMode.FOR_YOU and interactions:
                pantry_weight = 0.3
            elif mode == RecommendationMode.ULTIMATE:
                pantry_weight = 1.5 # Boost pantry importance in Ultimate mode

            if user_vector is not None:
                user_vector = user_vector * pantry_weight

            # 2. Dynamic Profiling (Rocchio)
            if interactions:
                if user_vector is None:
                    user_vector = np.zeros((1, self.recipe_matrix.shape[1]))
                
                current_time = datetime.now(timezone.utc)
                # Ultimate mode doubles interaction impact along with pantry boost
                interaction_impact = 2.0 if mode in [RecommendationMode.FOR_YOU, RecommendationMode.ULTIMATE] else 1.0

                for interaction in interactions:
                    recipe_vec = self._get_recipe_vector(interaction.recipe_id)
                    if recipe_vec is not None:
                        inter_date = interaction.interaction_date.replace(tzinfo=timezone.utc) if interaction.interaction_date.tzinfo is None else interaction.interaction_date
                        days_passed = max(0.0, (current_time - inter_date).total_seconds() / 86400.0)
                        weight = math.exp(-self.decay_constant * days_passed)

                        sign = 0.7 if interaction.interaction_type == "like" else -1.0
                        user_vector += (recipe_vec * weight * sign * interaction_impact)
                        self.update_popularity(interaction.recipe_id, 1)

            # 3. Similarity Scores
            if user_vector is not None and not np.all(user_vector == 0 if isinstance(user_vector, np.ndarray) else user_vector.toarray() == 0):
                
                # Sckit-learn için np.matrix'i standart array'e çeviriyoruz
                if isinstance(user_vector, np.matrix):
                    user_vector = np.asarray(user_vector)
                    
                similarity_scores = cosine_similarity(user_vector, self.recipe_matrix).flatten()
            else:
                # COLD START: Use popularity as base score, but still apply modes!
                logger.info("Cold start or empty user vector. Using popularity as baseline.")
                max_pop = max(self.popularity_scores.values()) if self.popularity_scores else 1
                similarity_scores = np.array([
                    (self.popularity_scores.get(rid, 0) / (max_pop + 1)) * 0.1 
                    for rid in self.recipe_ids
                ])

            # 4. Filter and Boost
            results = []
            now = datetime.now(timezone.utc)

            for idx, score in enumerate(similarity_scores):
                recipe_id = self.recipe_ids[idx]
                meta = self.recipe_metadata[recipe_id]
                
                # --- HARD FILTERS ---
                if meta.get("category") in excluded_categories: 
                    continue
                if any(exc.lower() in meta["ingredients"].lower() for exc in excluded_ingredients): 
                    continue

                final_score = float(score)
                
                # --- MODE SPECIFIC LOGIC ---
                
                # 1. QUICK: Malzeme sayısı az olanları öne çıkar
                if mode == RecommendationMode.QUICK:
                    ingredient_count = len(meta["ingredients"].split(","))
                    if ingredient_count <= 5: 
                        final_score *= 1.3
                    elif ingredient_count > 10: 
                        final_score *= 0.7

                # 2. EXPLORE: Popülerliği az olan veya yeni kategorileri öne çıkar
                elif mode == RecommendationMode.EXPLORE:
                    popularity = self.popularity_scores.get(recipe_id, 0)
                    final_score *= (1.0 / (1.0 + math.log1p(popularity))) # Az bilinenleri öne çıkar

                # 3. STRICT / MINIMAL: Malzeme uyumuna (Cosine Similarity) aşırı yüksek ağırlık ver
                elif mode in [RecommendationMode.STRICT, RecommendationMode.MINIMAL]:
                    if final_score < 0.75: 
                        final_score *= 0.1 # Malzeme uymuyorsa puanı yerle bir et
                    else: 
                        final_score *= 2.0 # Çok uyuyorsa devasa ödüllendir

                # --- GENERIC BOOSTS ---
                
                # New Recipe Boost (Last 7 days)
                created_at = meta.get("created_at")
                if created_at:
                    if isinstance(created_at, str): 
                        created_at = datetime.fromisoformat(created_at)
                    if created_at.tzinfo is None: 
                        created_at = created_at.replace(tzinfo=timezone.utc)
                    days_old = (now - created_at).days
                    if days_old <= 7:
                        final_score *= 1.15 # 15% boost for fresh content

                if final_score > 0.01:
                    results.append((recipe_id, final_score))

            results.sort(key=lambda x: x[1], reverse=True)
            
            # If results are too few, pad with popular items
            if len(results) < top_k:
                popular_ones = sorted(self.popularity_scores.items(), key=lambda x: x[1], reverse=True)
                for rid, _ in popular_ones:
                    if len(results) >= top_k: 
                        break
                    if rid not in [r[0] for r in results]:
                        meta = self.recipe_metadata[rid]
                        
                        # --- Pad ederken de filtreleri kontrol et ---
                        if meta.get("category") in excluded_categories: 
                            continue
                        if any(exc.lower() in meta["ingredients"].lower() for exc in excluded_ingredients): 
                            continue
                            
                        results.append((rid, 0.1)) # Low score but fills the gap
            
            return results[:top_k]