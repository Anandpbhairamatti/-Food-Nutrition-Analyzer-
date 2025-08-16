import os
import requests
from typing import Optional

LOCAL_NUTRITION_DB = {
    'burger': {
        'name': 'Hamburger (one medium)', 'calories': 354.0, 'protein_g': 17.0, 'fat_g': 20.0, 'carbs_g': 29.0, 'serving_size': '1 burger'
    },
    'pasta': {
        'name': 'Pasta (cooked, 1 plate)', 'calories': 375.0, 'protein_g': 12.5, 'fat_g': 1.79, 'carbs_g': 78.6, 'serving_size': '1 plate (approx 300 g)'
    },
    'rice': {
        'name': 'White rice (cooked, 1 cup)', 'calories': 206.0, 'protein_g': 4.25, 'fat_g': 0.44, 'carbs_g': 45.0, 'serving_size': '1 cup (158 g)'
    },
    'fries': {
        'name': 'French fries (medium serving)', 'calories': 365.0, 'protein_g': 3.4, 'fat_g': 17.0, 'carbs_g': 48.0, 'serving_size': '1 medium serving'
    },
    'salad': {
        'name': 'Mixed salad (no dressing)', 'calories': 33.0, 'protein_g': 2.0, 'fat_g': 0.2, 'carbs_g': 6.0, 'serving_size': '1 cup'
    },
    'apple': {
        'name': 'Apple (medium)', 'calories': 95.0, 'protein_g': 0.5, 'fat_g': 0.3, 'carbs_g': 25.0, 'serving_size': '1 medium (182 g)'
    },
    'egg': {
        'name': 'Egg (large)', 'calories': 78.0, 'protein_g': 6.3, 'fat_g': 5.3, 'carbs_g': 0.6, 'serving_size': '1 large (50 g)'
    },
    'pizza': {
        'name': 'Pizza (1 slice, cheese)', 'calories': 285.0, 'protein_g': 12.0, 'fat_g': 10.0, 'carbs_g': 33.0, 'serving_size': '1 slice'
    }
}

LABEL_TO_CANONICAL = {
    'hamburger': 'burger',
    'burger': 'burger',
    'cheeseburger': 'burger',
    'pasta': 'pasta',
    'spaghetti': 'pasta',
    'rice': 'rice',
    'fried_rice': 'rice',
    'french_fries': 'fries',
    'fries': 'fries',
    'salad': 'salad',
    'apple': 'apple',
    'banana': 'banana',
    'egg': 'egg',
    'pizza': 'pizza'
}

class NutritionClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('USDA_API_KEY', None)
        self.search_url = 'https://api.nal.usda.gov/fdc/v1/foods/search'
        self.details_url = 'https://api.nal.usda.gov/fdc/v1/food/{}'
        self._cache = {}

    def _from_local(self, key: str):
        data = LOCAL_NUTRITION_DB.get(key)
        if not data:
            return None
        out = data.copy()
        out['match'] = key
        out['source'] = 'local'
        return out

    def _parse_usda_food(self, f):
        nutrients = {n.get('nutrientName','').lower(): n for n in f.get('foodNutrients', [])}
        def by_name(possible_names):
            for name in possible_names:
                n = nutrients.get(name.lower())
                if n:
                    return n.get('value')
            return None
        calories = by_name(['Energy', 'Calories'])
        protein = by_name(['Protein'])
        fat = by_name(['Total lipid (fat)','Lipid, total'])
        carbs = by_name(['Carbohydrate, by difference','Carbohydrate'])
        return {
            'name': f.get('description'),
            'calories': float(calories) if calories is not None else None,
            'protein_g': float(protein) if protein is not None else None,
            'fat_g': float(fat) if fat is not None else None,
            'carbs_g': float(carbs) if carbs is not None else None,
            'serving_size': f.get('servingSize') or '100 g',
            'match': f.get('description'),
            'source': 'usda'
        }

    def lookup_food(self, query: str):
        if not query:
            return {'name': None}
        q = query.lower().strip()
        canonical = LABEL_TO_CANONICAL.get(q, q)

        local = self._from_local(canonical)
        if local:
            return local

        if q in self._cache:
            return self._cache[q]

        if self.api_key:
            params = {'api_key': self.api_key, 'query': query, 'pageSize': 3}
            try:
                r = requests.get(self.search_url, params=params, timeout=8)
                r.raise_for_status()
                data = r.json()
                foods = data.get('foods') or []
                if foods:
                    parsed = self._parse_usda_food(foods[0])
                    self._cache[q] = parsed
                    return parsed
            except Exception:
                pass

        mocked = {
            'name': query,
            'calories': round(120 + abs(hash(query)) % 300, 1),
            'protein_g': round(2 + abs(hash(query)) % 12, 1),
            'fat_g': round(0.5 + abs(hash(query)) % 20, 2),
            'carbs_g': round(10 + abs(hash(query)) % 80, 1),
            'serving_size': '100 g',
            'match': query,
            'source': 'mock'
        }
        self._cache[q] = mocked
        return mocked
