print("Testing Enhanced Parser...")

try:
    import sys
    import os
    sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))
    
    from enhanced_smart_parser import EnhancedSmartDateTimeParser
    
    parser = EnhancedSmartDateTimeParser()
    
    test_text = "add appointment eat lunch with love at 3pm"
    result = parser.extract_appointment_info(test_text)
    
    print("SUCCESS! Parser is working.")
    print("Test input:", test_text)
    print("Result:")
    print("- Title:", result.get('appointment_title', ''))
    print("- Date:", result.get('date', ''))
    print("- Time:", result.get('time', ''))
    print("- Person:", result.get('contact_person', ''))
    print("- Confidence:", result.get('confidence', 0))
    
    print("\nNow testing with Thai text:")
    thai_text = "add lunch with love 3pm"
    result2 = parser.extract_appointment_info(thai_text)
    print("Thai result:")
    print("- Title:", result2.get('appointment_title', ''))
    print("- Time:", result2.get('time', ''))
    print("- Person:", result2.get('contact_person', ''))
    
except Exception as e:
    print("Error:", str(e))
    import traceback
    traceback.print_exc()

print("\nTo run GUI: double-click RUN_GUI.py or CLICK_TO_RUN.bat")