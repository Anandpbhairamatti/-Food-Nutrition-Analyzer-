"""
Utilities to filter detections to FOOD-ONLY.

We apply two layers:
1) An allow-list of canonical food labels (exact match).
2) A keyword-based fuzzy check to capture common regional food names.

Use: filtered = filter_food_detections(preds)
"""
from typing import List, Dict
import os

# Canonical COCO-style food labels (exact match, lowercase)
ALLOWED_FOOD_LABELS = {
    "apple","banana","orange","broccoli","carrot","hot dog","pizza","donut","cake","sandwich",
    "grape","strawberry","watermelon","tomato","potato","cucumber","mushroom","lettuce","corn",
    "onion","garlic","pepper","chili","chilli","cauliflower","egg","eggs","omelette","noodles",
    "pasta","spaghetti","burger","hamburger","fries","french fries","rice","fried rice","biryani",
    "dosa","idli","poha","paratha","chapati","roti","naan","paneer","curry","dal","lentil","samosa",
    "kebab","chicken","fish","mutton","beef","pork","shrimp","prawn","salad","cheese","butter",
    "yogurt","curd","milk","ice cream","pudding","cookie","biscuit","chocolate","sweet","dessert",
    "papaya","mango","pineapple","peach","pear","blueberry","blackberry","kiwi","juice","soup"
}

# Keyword-based fuzzy allow (substring, lowercase)
FOOD_KEYWORDS = [
    "rice","noodle","pasta","pizza","burger","sandwich","roll","wrap","taco","burrito",
    "cake","donut","cookie","biscuit","sweet","dessert","ice cream","laddu","gulab","jalebi",
    "halwa","barfi","kheer","payasam","rasgulla","chocolate","fries","fry","fried","biryani",
    "dosa","idli","vada","sambar","rasam","poha","paratha","chapati","roti","naan","paneer",
    "curry","dal","lentil","samosa","kebab","cutlet","pakoda","bhaji","chutney","pickle",
    "salad","soup","omelette","egg","eggs","chicken","mutton","beef","pork","fish","shrimp","prawn",
    "paneer","tofu","cheese","yogurt","curd","milk","butter","ghee",
    "apple","banana","mango","orange","grape","berry","strawberry","watermelon","melon","pineapple",
    "papaya","guava","pear","peach","plum","kiwi","lychee","litchi","pomegranate",
    "broccoli","carrot","cucumber","lettuce","spinach","cauliflower","tomato","onion","garlic","pepper",
]

# Explicit blocklist for common container/utensil objects
BLOCKLIST = {
    "person","bowl","cup","plate","bottle","wine glass","glass","fork","knife","spoon","table",
    "dining table","chair","oven","microwave","refrigerator","sink","tv","laptop","cell phone",
    "remote","book","clock","vase","toothbrush","scissors","towel","napkin","tray","pot","pan"
}

def _env_overrides():
    """Allow overrides via env vars (comma-separated)."""
    allow_extra = {s.strip().lower() for s in os.getenv("FOOD_ALLOW_EXTRA","").split(",") if s.strip()}
    block_extra = {s.strip().lower() for s in os.getenv("FOOD_BLOCK_EXTRA","").split(",") if s.strip()}
    return allow_extra, block_extra

def is_food_label(label: str) -> bool:
    if not label:
        return False
    name = str(label).strip().lower()
    if name in BLOCKLIST:
        return False
    allow_extra, block_extra = _env_overrides()
    if name in block_extra:
        return False
    if name in ALLOWED_FOOD_LABELS or any(k in name for k in FOOD_KEYWORDS) or name in allow_extra:
        return True
    return False

def filter_food_detections(preds: List[Dict]) -> List[Dict]:
    """Keep only detections whose 'label' passes is_food_label."""
    filtered = []
    for p in preds or []:
        label = p.get("label","")
        if is_food_label(label):
            filtered.append(p)
    return filtered
