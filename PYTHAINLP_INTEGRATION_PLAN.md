# PyThaiNLP Integration Plan for SmartDateTimeParser

## 🎯 วัตถุประสงค์
เพิ่มความฉลาดให้ SmartDateTimeParser ด้วย PyThaiNLP เพื่อ:
- ประมวลผลภาษาไทยได้ดีขึ้น
- เข้าใจบริบทและความหมายของข้อความ
- จัดการกับรูปแบบการใช้ภาษาที่หลากหลาย

## 📚 PyThaiNLP Features ที่จะใช้

### 1. **Word Segmentation (การตัดคำ)**
```python
from pythainlp import word_tokenize
from pythainlp.corpus import thai_stopwords

# ตัดคำและกรองคำหยุด
def smart_tokenize(text):
    tokens = word_tokenize(text, engine='newmm')
    stopwords = thai_stopwords()
    return [token for token in tokens if token not in stopwords]
```

### 2. **Part-of-Speech Tagging (การติดป้ายคำ)**
```python
from pythainlp.tag import pos_tag

# ระบุชนิดของคำ (คำนาม, กริยา, เวลา)
def analyze_pos(text):
    tokens = word_tokenize(text)
    pos_tags = pos_tag(tokens, engine='perceptron')
    return pos_tags
```

### 3. **Named Entity Recognition (การจำแนกหน่วยชื่อ)**
```python
from pythainlp.tag import named_entity

# จำแนกชื่อสถานที่, โรงพยาบาล, ชื่อคน
def extract_entities(text):
    entities = named_entity(text)
    return entities
```

### 4. **Text Normalization (การปรับปรุงข้อความ)**
```python
from pythainlp.util import normalize

# ปรับปรุงข้อความ เช่น แปลงเลขไทยเป็นอารบิก
def normalize_text(text):
    return normalize(text)
```

## 🔧 แผนการ Implementation

### Phase 1: Setup และ Basic Integration
```python
class EnhancedSmartDateTimeParser(SmartDateTimeParser):
    def __init__(self):
        super().__init__()
        self.setup_pythainlp()
    
    def setup_pythainlp(self):
        """ตั้งค่า PyThaiNLP components"""
        # Download required models if needed
        import pythainlp
        pythainlp.corpus.download('thai2fit_wv')
        pythainlp.corpus.download('thai_stopwords')
```

### Phase 2: Enhanced Text Processing
```python
def preprocess_text(self, text: str) -> dict:
    """ประมวลผลข้อความเบื้องต้นด้วย PyThaiNLP"""
    # 1. Normalize text
    normalized = normalize(text)
    
    # 2. Tokenize
    tokens = word_tokenize(normalized, engine='newmm')
    
    # 3. POS tagging
    pos_tags = pos_tag(tokens, engine='perceptron')
    
    # 4. Extract entities
    entities = named_entity(normalized)
    
    return {
        'original': text,
        'normalized': normalized,
        'tokens': tokens,
        'pos_tags': pos_tags,
        'entities': entities
    }
```

### Phase 3: Smart Date/Time Extraction
```python
def extract_datetime_smart(self, processed_text: dict) -> Optional[datetime]:
    """ใช้ PyThaiNLP หาวันเวลาอย่างฉลาด"""
    
    # หาคำที่เกี่ยวกับเวลา
    time_related_pos = ['NOUN', 'NUM', 'ADV']  # คำนาม, ตัวเลข, กริยาวิเศษณ์
    time_tokens = []
    
    for token, pos in processed_text['pos_tags']:
        if pos in time_related_pos and self.is_time_related(token):
            time_tokens.append(token)
    
    # ประมวลผลต่อ...
    return self._parse_datetime_from_tokens(time_tokens)
```

### Phase 4: Smart Location/Hospital Detection
```python
def extract_location_smart(self, processed_text: dict) -> str:
    """ใช้ PyThaiNLP หาสถานที่อย่างฉลาด"""
    
    # หาจาก Named Entities
    locations = []
    for entity in processed_text['entities']:
        if entity['type'] in ['LOCATION', 'ORGANIZATION']:
            locations.append(entity['text'])
    
    # หาจาก Pattern และ Context
    hospital_patterns = ['โรงพยาบาล', 'รพ.', 'คลินิก', 'ศูนย์การแพทย์']
    # ... logic ต่อ
```

### Phase 5: Context-Aware Parsing
```python
def understand_context(self, processed_text: dict) -> dict:
    """เข้าใจบริบทของข้อความ"""
    
    context = {
        'is_medical': False,
        'is_formal': False,
        'urgency_level': 'normal',
        'appointment_type': 'general'
    }
    
    # ตรวจสอบคำที่บ่งบอกบริบท
    medical_keywords = ['หมอ', 'แพทย์', 'ตรวจ', 'รักษา', 'โรงพยาบาล']
    formal_patterns = ['นัดหมาย', 'การประชุม', 'พบ']
    
    # ... logic การวิเคราะห์บริบท
    return context
```

## 📦 Dependencies ที่ต้องเพิ่ม

### requirements.txt
```
pythainlp>=4.0.0
torch>=1.9.0  # สำหรับ ML models
numpy>=1.21.0
scipy>=1.7.0
```

### Optional Models
```python
# Models ที่อาจต้อง download
pythainlp.corpus.download('thai2fit_wv')      # Word vectors
pythainlp.corpus.download('thai_stopwords')   # Stop words
pythainlp.corpus.download('thai2transformers') # Transformer models
```

## 🎯 Expected Improvements

### 1. **Better Date/Time Recognition**
```
"นัดพรุ่งนี้บ่ายสองโมงครึ่ง" ✅ จะแปลงเป็น datetime ได้
"วันอังคารหน้าตอนเช้า" ✅ จะหาวันที่ที่ถูกต้อง
"สัปดาหน้าวันศุกร์" ✅ จะคำนวณได้แม่นยำ
```

### 2. **Smart Location Extraction**
```
"รพ.ศิริราช" ✅ จะรู้ว่าเป็นโรงพยาบาลศิริราช
"รามาธิบดี" ✅ จะรู้ว่าเป็นโรงพยาบาล
"คลินิกหมอสมชาย เจริญกรุง" ✅ จะแยกชื่อคลินิกและที่อยู่ได้
```

### 3. **Context Understanding**
```
"ไปหาหมอ" → medical context
"ประชุมงาน" → business context  
"เจอกัน" → casual context
```

### 4. **Flexible Input Handling**
```
"๑๕ ตุลาคม ๒๕๖๘" ✅ แปลงเลขไทยเป็นอารบิก
"ส่วนโน้ม" ✅ เข้าใจคำไทยโบราณ
"เสาร์อาทิตย์นี้" ✅ เข้าใจคำผสม
```

## 🚀 Implementation Timeline

### Week 1: Setup และ Basic Integration
- เพิ่ม PyThaiNLP dependencies
- สร้าง EnhancedSmartDateTimeParser class
- Test basic tokenization และ POS tagging

### Week 2: Date/Time Enhancement  
- ปรับปรุง date/time parsing ด้วย PyThaiNLP
- เพิ่ม Thai numeral conversion
- Test กับ edge cases

### Week 3: Location และ Entity Recognition
- เพิ่ม smart location detection
- Hospital/clinic name recognition
- Person name extraction

### Week 4: Context และ Advanced Features
- Context-aware parsing
- Confidence scoring
- Performance optimization

## 📊 Expected Performance Gains

- **Accuracy**: +25-30% ในการ parse ข้อความไทยที่ซับซ้อน
- **Flexibility**: รองรับรูปแบบการใช้ภาษาที่หลากหลาย  
- **Robustness**: จัดการกับ typos และ informal text ได้ดีขึ้น
- **User Experience**: เข้าใจเจตนาของผู้ใช้ได้ดีขึ้น

## 🎭 Example Use Cases

```python
# ตัวอย่างการใช้งานใหม่
parser = EnhancedSmartDateTimeParser()

# Case 1: Complex Thai text
text1 = "นัดพรุ่งนี้บ่ายโมงครึ่ง ไปหาหมอหัวใจที่ศิริราช"
result1 = parser.extract_appointment_info(text1)
# จะได้ datetime ที่ถูกต้อง + location + medical context

# Case 2: Mixed formal/informal
text2 = "ประชุมวันพุธหน้า 14.30 น. ห้องประชุมชั้น 5"
result2 = parser.extract_appointment_info(text2)
# จะเข้าใจว่าเป็น business meeting

# Case 3: Thai numerals
text3 = "นัดวันที่ ๑๕ กุมภาพันธ์ ๒๕๖๘ เวลา ๑๔.๓๐ น."
result3 = parser.extract_appointment_info(text3)
# จะแปลงเลขไทยเป็นอารบิกได้
```

พร้อมเริ่มต้น implementation เมื่อไหร่ก็บอกได้ครับ! 🚀