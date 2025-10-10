🚀 วิธีรัน Enhanced Smart Parser
====================================

## 📱 วิธีที่ 1: รัน GUI App (แนะนำ!)

### A. Double-click ไฟล์ (ง่ายที่สุด)
1. เปิด Windows Explorer
2. ไปที่โฟลเดอร์ `c:\Users\fermi\line-group-reminder-bot`
3. **Double-click** ไฟล์ `RUN_GUI.py`
   หรือ **Double-click** ไฟล์ `CLICK_TO_RUN.bat`

### B. ผ่าน Terminal
```bash
cd c:\Users\fermi\line-group-reminder-bot
python simple_gui.py
```

### C. ผ่าน VS Code Terminal  
1. เปิด Terminal ใน VS Code (Ctrl + `)
2. พิมพ์:
```
python simple_gui.py
```

## 🧪 วิธีที่ 2: รันการทดสอบ

### ทดสอบพื้นฐาน
```bash
python test_parser.py
```

### ทดสอบครอบคลุม
```bash  
python test_comprehensive.py
```

### ทดสอบเร็ว
```bash
python quick_test.py
```

## 🎯 วิธีที่ 3: ใช้ใน Python Code

```python
from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser

# สร้าง parser
parser = EnhancedSmartDateTimeParser()

# ทดสอบ
result = parser.extract_appointment_info("เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง")
print(result)
```

## 🔧 แก้ไขปัญหา

### ถ้า GUI ไม่เปิด:
1. ตรวจสอบ Python:
```bash
python --version
```

2. ลองรันผ่าน Command Prompt:
```cmd
cd c:\Users\fermi\line-group-reminder-bot
python simple_gui.py
```

### ถ้าเจอ Import Error:
```bash
# ตรวจสอบว่าไฟล์อยู่ที่ถูกต้อง
dir utils\enhanced_smart_parser.py
```

## 📊 สิ่งที่จะเห็นใน GUI:

1. **Input Box** - พิมพ์ข้อความ เช่น "เพิ่มนัด กินข้าวบ่าย3โมง"
2. **Sample Dropdown** - เลือกตัวอย่างพร้อมใช้
3. **Parse Button** - กดเพื่อ parse ข้อความ
4. **Results Area** - ดูผลลัพธ์ที่แยกได้
5. **Export JSON** - ส่งออกเป็นไฟล์ JSON

## 🎮 ตัวอย่างการใช้งาน:

### Input:
```
เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง
```

### Expected Output:
```
นัดหมาย: "กินข้าวเที่ยว"
วันที่: "07/10/2025"
เวลา: "15.00"
บุคคล/ผู้ติดต่อ: "ที่รัก"
Confidence: 0.30
```

## 🆘 ถ้ายังไม่ได้:

1. **ลองใช้ Command Prompt แทน PowerShell:**
   - กด Win + R
   - พิมพ์ `cmd`
   - เปลี่ยนไปที่โฟลเดอร์โปรเจ็กต์
   - รัน `python simple_gui.py`

2. **ลองใช้ Python launcher:**
   ```bash
   py simple_gui.py
   ```

3. **รันแบบ module:**
   ```bash
   python -m simple_gui
   ```

## 💡 Quick Start:

**วิธีเร็วที่สุด:**
1. เปิด Windows Explorer
2. ไปที่ `c:\Users\fermi\line-group-reminder-bot`  
3. Double-click `RUN_GUI.py`
4. รอสักครู่แล้ว GUI จะเปิดขึ้นมา
5. ลองพิมพ์: "เพิ่มนัด กินข้าวบ่าย3โมง"
6. กด "Parse Text"
7. ดูผลลัพธ์! 🎉

อย่าลืม: หน้าต่าง GUI อาจจะเปิดด้านหลังหน้าต่างอื่น ให้ดูใน taskbar ครับ!