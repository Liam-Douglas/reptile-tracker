"""
Receipt OCR Module
Uses Tesseract OCR to extract text from receipt images and parse food items
"""

import re
from typing import List, Dict, Optional, Tuple
from PIL import Image
import pytesseract

class ReceiptOCR:
    """Handle OCR processing and parsing of receipt images"""
    
    def __init__(self):
        """Initialize the OCR processor"""
        # Common food item keywords for reptile food
        self.food_keywords = [
            'rat', 'rats', 'mouse', 'mice', 'cricket', 'crickets',
            'dubia', 'roach', 'roaches', 'mealworm', 'mealworms',
            'superworm', 'superworms', 'hornworm', 'hornworms',
            'waxworm', 'waxworms', 'pinkie', 'pinkies', 'fuzzy', 'fuzzies',
            'hopper', 'hoppers', 'small', 'medium', 'large', 'xl', 'jumbo',
            'adult', 'baby', 'juvenile', 'feeder'
        ]
        
        # Size keywords
        self.size_keywords = [
            'small', 'medium', 'large', 'xl', 'extra large', 'jumbo',
            'pinkie', 'fuzzy', 'hopper', 'adult', 'baby', 'juvenile',
            'xs', 'sm', 'md', 'lg'
        ]
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from receipt image using Tesseract OCR
        
        Args:
            image_path: Path to the receipt image file
            
        Returns:
            Extracted text from the image
        """
        try:
            # Open and preprocess image
            image = Image.open(image_path)
            
            # Convert to RGB first (handles various formats)
            if image.mode not in ('RGB', 'L'):
                image = image.convert('RGB')
            
            # Convert to grayscale for better OCR
            image = image.convert('L')
            
            # Enhance image for better OCR
            from PIL import ImageEnhance, ImageFilter
            
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Sharpen image
            image = image.filter(ImageFilter.SHARPEN)
            
            # Use Tesseract to extract text with custom config
            # --psm 6: Assume a single uniform block of text
            # --oem 3: Use both legacy and LSTM OCR engines
            custom_config = r'--oem 3 --psm 6'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            if not text or len(text.strip()) < 10:
                # Try again with different PSM mode if first attempt failed
                custom_config = r'--oem 3 --psm 4'  # Assume single column of text
                text = pytesseract.image_to_string(image, config=custom_config)
            
            return text
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            import traceback
            traceback.print_exc()
            return ""
    
    def parse_receipt(self, text: str) -> Dict:
        """
        Parse receipt text to extract structured data
        
        Args:
            text: Raw text extracted from receipt
            
        Returns:
            Dictionary containing parsed receipt data
        """
        lines = text.split('\n')
        
        # Initialize result
        result = {
            'supplier': self._extract_supplier(lines),
            'date': self._extract_date(lines),
            'items': self._extract_items(lines),
            'total': self._extract_total(lines),
            'raw_text': text
        }
        
        return result
    
    def _extract_supplier(self, lines: List[str]) -> Optional[str]:
        """Extract supplier/store name from receipt (usually first few lines)"""
        # Look in first 5 lines for store name
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and not re.match(r'^\d', line):
                # Skip lines that are just numbers or dates
                if not re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', line):
                    return line
        return None
    
    def _extract_date(self, lines: List[str]) -> Optional[str]:
        """Extract date from receipt"""
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY or DD/MM/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',    # YYYY-MM-DD
            r'[A-Za-z]{3,9}\s+\d{1,2},?\s+\d{4}',  # Month DD, YYYY
        ]
        
        for line in lines:
            for pattern in date_patterns:
                match = re.search(pattern, line)
                if match:
                    return match.group(0)
        return None
    
    def _extract_items(self, lines: List[str]) -> List[Dict]:
        """
        Extract food items from receipt lines
        
        Returns:
            List of dictionaries with item details
        """
        items = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Check if line contains food keywords
            if any(keyword in line_lower for keyword in self.food_keywords):
                item = self._parse_item_line(line)
                if item:
                    items.append(item)
        
        return items
    
    def _parse_item_line(self, line: str) -> Optional[Dict]:
        """
        Parse a single line to extract item details
        
        Expected formats:
        - "Rat Large 10 $2.50 $25.00"
        - "Medium Mouse x5 $15.00"
        - "Crickets (100) $10.00"
        """
        line_lower = line.lower()
        
        # Extract food type
        food_type = None
        for keyword in self.food_keywords:
            if keyword in line_lower and keyword not in self.size_keywords:
                food_type = keyword.capitalize()
                break
        
        if not food_type:
            return None
        
        # Extract size
        food_size = None
        for size in self.size_keywords:
            if size in line_lower:
                food_size = size.capitalize()
                break
        
        # Extract quantity (look for numbers, x5, (10), etc.)
        quantity = 1
        qty_patterns = [
            r'x\s*(\d+)',           # x5, x 10
            r'\((\d+)\)',           # (100)
            r'qty:?\s*(\d+)',       # qty: 5, qty 10
            r'\b(\d+)\s*(?:pcs?|pieces?|count|ct)\b',  # 10 pcs, 5 pieces
        ]
        
        for pattern in qty_patterns:
            match = re.search(pattern, line_lower)
            if match:
                quantity = int(match.group(1))
                break
        
        # If no explicit quantity marker, look for standalone numbers
        if quantity == 1:
            # Look for numbers that might be quantity (not prices)
            numbers = re.findall(r'\b(\d+)\b', line)
            for num in numbers:
                num_int = int(num)
                # Assume quantities are typically 1-1000
                if 1 < num_int <= 1000:
                    quantity = num_int
                    break
        
        # Extract prices (look for $X.XX format)
        prices = re.findall(r'\$\s*(\d+\.?\d*)', line)
        
        cost_per_unit = None
        total_cost = None
        
        if len(prices) >= 2:
            # If we have 2+ prices, assume first is unit price, last is total
            cost_per_unit = float(prices[0])
            total_cost = float(prices[-1])
        elif len(prices) == 1:
            # If only one price, assume it's the total
            total_cost = float(prices[0])
            if quantity > 1:
                cost_per_unit = total_cost / quantity
        
        return {
            'food_type': food_type,
            'food_size': food_size or 'Medium',  # Default to Medium if not specified
            'quantity': quantity,
            'cost_per_unit': cost_per_unit,
            'total_cost': total_cost,
            'raw_line': line.strip()
        }
    
    def _extract_total(self, lines: List[str]) -> Optional[float]:
        """Extract total amount from receipt"""
        total_patterns = [
            r'total:?\s*\$?\s*(\d+\.?\d*)',
            r'amount:?\s*\$?\s*(\d+\.?\d*)',
            r'grand\s+total:?\s*\$?\s*(\d+\.?\d*)',
        ]
        
        # Search from bottom up (total usually at end)
        for line in reversed(lines):
            line_lower = line.lower()
            for pattern in total_patterns:
                match = re.search(pattern, line_lower)
                if match:
                    return float(match.group(1))
        
        return None
    
    def process_receipt_image(self, image_path: str) -> Dict:
        """
        Complete pipeline: extract text and parse receipt
        
        Args:
            image_path: Path to receipt image
            
        Returns:
            Parsed receipt data
        """
        # Extract text using OCR
        text = self.extract_text(image_path)
        
        if not text:
            return {
                'success': False,
                'error': 'Could not extract text from image',
                'items': []
            }
        
        # Parse the extracted text
        parsed_data = self.parse_receipt(text)
        parsed_data['success'] = True
        
        return parsed_data


def test_ocr():
    """Test function for development"""
    ocr = ReceiptOCR()
    
    # Test with sample text
    sample_text = """
    PetSmart
    123 Main St
    01/15/2024
    
    Large Rat           5    $3.50    $17.50
    Medium Mouse x10         $2.00    $20.00
    Crickets (100)                    $10.00
    
    Subtotal:                         $47.50
    Tax:                              $3.80
    Total:                            $51.30
    """
    
    result = ocr.parse_receipt(sample_text)
    print("Parsed Receipt:")
    print(f"Supplier: {result['supplier']}")
    print(f"Date: {result['date']}")
    print(f"Total: ${result['total']}")
    print(f"\nItems found: {len(result['items'])}")
    for item in result['items']:
        print(f"  - {item['food_type']} {item['food_size']}: {item['quantity']} @ ${item['cost_per_unit']} = ${item['total_cost']}")


if __name__ == '__main__':
    test_ocr()

# Made with Bob
