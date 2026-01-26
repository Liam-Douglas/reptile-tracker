"""
AI-powered food recognition for reptile feeding logs
Uses OpenAI Vision API to identify food items from photos
"""

import os
import base64
from openai import OpenAI

def analyze_food_image(image_data):
    """
    Analyze a food image and identify the food items
    
    Args:
        image_data: Base64 encoded image data or file path
        
    Returns:
        dict: {
            'food_items': list of identified food items,
            'food_type': primary food type,
            'confidence': confidence level,
            'description': detailed description
        }
    """
    try:
        # Initialize OpenAI client
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            return {
                'error': 'OpenAI API key not configured',
                'food_items': [],
                'food_type': 'Unknown',
                'confidence': 'low'
            }
        
        client = OpenAI(api_key=api_key)
        
        # Prepare the image data
        if image_data.startswith('data:image'):
            # Already base64 encoded with data URI
            image_url = image_data
        else:
            # Assume it's raw base64
            image_url = f"data:image/jpeg;base64,{image_data}"
        
        # Create the prompt for food identification
        prompt = """Analyze this image of reptile food and identify all food items present.
        
Please provide:
1. A list of all food items you can identify (fruits, vegetables, insects, etc.)
2. The primary food type category (Insects, Vegetables, Fruits, Mixed, Mouse, Rat, etc.)
3. Your confidence level (high, medium, low)
4. A brief description of what you see

Format your response as JSON:
{
    "food_items": ["item1", "item2", ...],
    "food_type": "primary category",
    "confidence": "high/medium/low",
    "description": "brief description"
}

Focus on identifying common reptile foods like:
- Insects: crickets, mealworms, dubia roaches, hornworms, superworms
- Vegetables: collard greens, mustard greens, squash, carrots, bell peppers
- Fruits: berries, melon, mango, papaya
- Protein: mice, rats, chicks
"""
        
        # Call OpenAI Vision API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url,
                                "detail": "low"  # Use low detail for faster/cheaper processing
                            }
                        }
                    ]
                }
            ],
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        import json
        result = json.loads(response.choices[0].message.content)
        
        return {
            'food_items': result.get('food_items', []),
            'food_type': result.get('food_type', 'Mixed'),
            'confidence': result.get('confidence', 'medium'),
            'description': result.get('description', ''),
            'success': True
        }
        
    except Exception as e:
        print(f"Error analyzing food image: {str(e)}")
        return {
            'error': str(e),
            'food_items': [],
            'food_type': 'Unknown',
            'confidence': 'low',
            'success': False
        }


def get_food_suggestions(food_items):
    """
    Get food size suggestions based on identified items
    
    Args:
        food_items: List of identified food items
        
    Returns:
        str: Suggested food size
    """
    # Map common food items to sizes
    size_mapping = {
        'cricket': 'Small',
        'mealworm': 'Small',
        'superworm': 'Medium',
        'dubia roach': 'Medium',
        'hornworm': 'Large',
        'mouse': 'Varies',
        'rat': 'Varies',
        'pinkie': 'Pinkie',
        'fuzzy': 'Fuzzy',
        'hopper': 'Hopper',
    }
    
    # Check for matches
    for item in food_items:
        item_lower = item.lower()
        for key, size in size_mapping.items():
            if key in item_lower:
                return size
    
    return 'Medium'  # Default


def format_food_description(food_items):
    """
    Format food items into a readable description
    
    Args:
        food_items: List of food items
        
    Returns:
        str: Formatted description
    """
    if not food_items:
        return "No food items identified"
    
    if len(food_items) == 1:
        return food_items[0]
    elif len(food_items) == 2:
        return f"{food_items[0]} and {food_items[1]}"
    else:
        return f"{', '.join(food_items[:-1])}, and {food_items[-1]}"

# Made with Bob
