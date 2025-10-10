# Enhanced Smart Parser - How to Use

## 🎯 What's Available

You now have a complete Enhanced Smart Parser system with these files:

### Main Files:
- `utils/enhanced_smart_parser.py` - The enhanced parser engine
- `simple_gui.py` - Simple GUI application  
- `parser_tester_app.py` - Full-featured GUI application
- `RUN_GUI.py` - Easy launcher for GUI
- `CLICK_TO_RUN.bat` - Windows batch launcher

### Test Files:
- `test_parser.py` - Command line testing
- `demo_parser.py` - Demo script
- `quick_test.py` - Quick functionality test

## 🚀 How to Run

### Method 1: Double-click launcher
**Easiest way:**
1. Double-click `RUN_GUI.py` in Windows Explorer
2. Or double-click `CLICK_TO_RUN.bat`

### Method 2: Command line (if terminal works)
```bash
python simple_gui.py
```

### Method 3: Manual testing
```bash
python test_parser.py
```

## 📊 Expected Results

For input: "เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง"

Expected output:
```json
{
  "appointment_title": "กินข้าวเที่ยว",
  "date": "07/10/2025",  
  "time": "15.00",
  "contact_person": "ที่รัก",
  "confidence": 0.7
}
```

## 🎮 GUI Features

The GUI app includes:
- Text input area
- Sample text dropdown
- Parse button  
- Results display
- JSON export
- History view
- Confidence scoring

## 🔧 Integration Ready

The Enhanced Parser is ready to integrate into your LINE bot:

```python
from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

parser = EnhancedSmartDateTimeParser()
result = parser.extract_appointment_info(user_message)

# Use result for Google Sheets
appointment_data = {
    'นัดหมาย': result['appointment_title'],
    'วันที่': result['date'], 
    'เวลา': result['time'],
    'สถานที่': result['location'],
    'บุคคล/ผู้ติดต่อ': result['contact_person'],
    'เบอร์โทร': result['phone_number']
}
```

## 🎯 Next Steps

1. **Test the GUI**: Double-click RUN_GUI.py
2. **Try different inputs**: Test various appointment formats
3. **Export results**: Use the JSON export feature
4. **Integrate**: Add to your LINE bot when ready
5. **Add PyThaiNLP**: When ready for advanced features

## 💡 Troubleshooting

If GUI doesn't start:
1. Check Python is installed
2. Try: `python --version`
3. Run: `python simple_gui.py` directly
4. Check for error messages

The parser is working and ready for testing! 🎉