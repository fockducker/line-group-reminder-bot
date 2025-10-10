# PyThaiNLP Requirements and Setup Guide

## 📦 Dependencies for PyThaiNLP Integration

### Core Requirements
```
# PyThaiNLP and dependencies
pythainlp>=4.0.0
torch>=1.9.0
numpy>=1.21.0
scipy>=1.7.0

# Optional but recommended
pandas>=1.3.0  # for data processing
scikit-learn>=1.0.0  # for ML features
```

### PyThaiNLP Models to Download
```python
import pythainlp

# Essential models
pythainlp.corpus.download('thai2fit_wv')      # Thai word vectors
pythainlp.corpus.download('thai_stopwords')   # Thai stopwords
pythainlp.corpus.download('thai_negations')   # Negation words

# Advanced models (optional)
pythainlp.corpus.download('thai2transformers') # Transformer models
pythainlp.corpus.download('ner_thainer')      # Named Entity Recognition
pythainlp.corpus.download('pos_lst20')        # POS tagging model
```

## 🚀 Installation Commands

### For Development Environment
```bash
# Basic installation
pip install pythainlp

# With ML dependencies
pip install pythainlp[full]

# Or specific components
pip install pythainlp[ml,extra]
```

### For Production (Render/Heroku)
Add to `requirements.txt`:
```
pythainlp>=4.0.0
torch>=1.9.0
numpy>=1.21.0
```

## 📋 Setup Checklist

### Phase 1: Basic Setup
- [ ] Install PyThaiNLP package
- [ ] Download essential models
- [ ] Test basic tokenization
- [ ] Update Enhanced Parser to use PyThaiNLP

### Phase 2: Integration
- [ ] Integrate word_tokenize
- [ ] Add POS tagging
- [ ] Implement text normalization
- [ ] Test with existing appointment formats

### Phase 3: Advanced Features
- [ ] Named Entity Recognition
- [ ] Context-aware parsing
- [ ] Thai numeral conversion
- [ ] Confidence scoring

### Phase 4: Optimization
- [ ] Performance tuning
- [ ] Model size optimization
- [ ] Error handling
- [ ] Unit tests

## 🧪 Testing Script

### basic_pythainlp_test.py
```python
"""
Basic PyThaiNLP testing script
Run this after installation to verify everything works
"""

def test_pythainlp_basic():
    """Test basic PyThaiNLP functionality"""
    try:
        from pythainlp import word_tokenize
        from pythainlp.tag import pos_tag
        from pythainlp.util import normalize
        
        # Test text
        text = "นัดหมายพรุ่งนี้ ๑๔.๓๐ น. ที่โรงพยาบาลศิริราช"
        
        # Test tokenization
        tokens = word_tokenize(text, engine='newmm')
        print(f"Tokens: {tokens}")
        
        # Test POS tagging
        pos_tags = pos_tag(tokens, engine='perceptron')
        print(f"POS Tags: {pos_tags}")
        
        # Test normalization
        normalized = normalize(text)
        print(f"Normalized: {normalized}")
        
        print("✅ PyThaiNLP basic test passed!")
        return True
        
    except ImportError as e:
        print(f"❌ PyThaiNLP not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error testing PyThaiNLP: {e}")
        return False

def test_appointment_parsing():
    """Test appointment parsing with PyThaiNLP"""
    try:
        from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser
        
        parser = EnhancedSmartDateTimeParser()
        
        test_cases = [
            "นัดพรุ่งนี้ ๑๔.๓๐ น. ที่โรงพยาบาลศิริราช",
            "ประชุมวันจันทร์หน้า ๑๐ โมงเช้า ห้องประชุมใหญ่",
            "ไปหาหมอสมชาย คลินิกหัวใจ รพ.จุฬา วันอังคาร",
        ]
        
        for text in test_cases:
            result = parser.extract_appointment_info(text)
            print(f"\nInput: {text}")
            print(f"Result: {result}")
        
        print("✅ Appointment parsing test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in appointment parsing: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing PyThaiNLP Integration")
    print("=" * 50)
    
    # Test basic functionality
    basic_ok = test_pythainlp_basic()
    
    if basic_ok:
        # Test appointment parsing
        test_appointment_parsing()
    else:
        print("Please install PyThaiNLP first:")
        print("pip install pythainlp")
```

## 🎯 Implementation Roadmap

### Week 1: Foundation
```python
# Day 1-2: Installation and basic setup
pip install pythainlp
python -c "import pythainlp; print('PyThaiNLP installed successfully!')"

# Day 3-4: Download models
python -c "import pythainlp; pythainlp.corpus.download('thai2fit_wv')"

# Day 5-7: Basic integration with Enhanced Parser
# Enable PyThaiNLP in enhanced_smart_parser.py
# self.use_pythainlp = True
```

### Week 2: Core Features
```python
# Implement advanced preprocessing
def preprocess_text_advanced(self, text: str) -> Dict[str, Any]:
    from pythainlp import word_tokenize
    from pythainlp.tag import pos_tag
    from pythainlp.util import normalize
    
    # Implementation here...
```

### Week 3: Advanced Features
```python
# Add Named Entity Recognition
def extract_entities_advanced(self, text: str) -> List[Dict]:
    from pythainlp.tag import named_entity
    # Implementation here...

# Add context understanding
def understand_context_advanced(self, pos_tags: List, entities: List) -> Dict:
    # Implementation here...
```

### Week 4: Optimization and Testing
```python
# Performance optimization
# Error handling
# Comprehensive testing
# Documentation
```

## 💡 Usage Examples After Implementation

### Basic Usage
```python
from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

parser = EnhancedSmartDateTimeParser()
parser.use_pythainlp = True  # Enable PyThaiNLP

text = "นัดพรุ่งนี้ ๑๔.๓๐ น. ที่โรงพยาบาลศิริราช กับหมอสมชาย"
result = parser.extract_appointment_info(text)

print(result)
# Expected enhanced output with better accuracy
```

### Advanced Context Understanding
```python
# Medical context
medical_text = "ไปตรวจหัวใจ กับ พญ.สมหญิง ที่คลินิกหัวใจ รพ.จุฬา"
medical_result = parser.extract_appointment_info(medical_text)
# จะเข้าใจว่าเป็น medical appointment

# Business context  
business_text = "ประชุมคณะกรรมการ วันจันทร์หน้า ๑๐.๓๐ น. ห้องประชุมใหญ่"
business_result = parser.extract_appointment_info(business_text)
# จะเข้าใจว่าเป็น business meeting
```

## 🔧 Configuration Options

### Performance vs Accuracy Trade-offs
```python
# High accuracy (slower)
parser.config = {
    'tokenizer_engine': 'newmm',
    'pos_engine': 'perceptron', 
    'use_ml_models': True,
    'confidence_threshold': 0.8
}

# Balanced (recommended)
parser.config = {
    'tokenizer_engine': 'newmm',
    'pos_engine': 'perceptron',
    'use_ml_models': False,
    'confidence_threshold': 0.6
}

# High speed (less accurate)
parser.config = {
    'tokenizer_engine': 'longest',
    'pos_engine': 'perceptron',
    'use_ml_models': False, 
    'confidence_threshold': 0.4
}
```

พร้อมเริ่มติดตั้งและใช้งานเมื่อไหร่ก็บอกได้ครับ! 🚀