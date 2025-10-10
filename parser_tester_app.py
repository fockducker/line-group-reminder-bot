#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Smart Parser Testing App
แอป Tkinter สำหรับทดสอบ Enhanced Smart Parser
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import json
import os
from datetime import datetime
from pathlib import Path

# Import Enhanced Parser
try:
    from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser
except ImportError as e:
    print(f"Error importing Enhanced Parser: {e}")
    # Try alternative import path
    try:
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        from utils.enhanced_smart_parser import EnhancedSmartDateTimeParser
    except ImportError:
        print("Cannot import Enhanced Parser. Please check file path.")
        sys.exit(1)

class ParserTesterApp:
    """แอปทดสอบ Enhanced Smart Parser"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🤖 Enhanced Smart Parser Tester")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Initialize parser
        try:
            self.parser = EnhancedSmartDateTimeParser()
            print("✅ Enhanced Parser initialized successfully")
        except Exception as e:
            print(f"❌ Error initializing parser: {e}")
            messagebox.showerror("Error", f"Cannot initialize parser: {e}")
            return
        
        # Create GUI components
        self.create_widgets()
        
        # Test samples
        self.sample_texts = [
            "เพิ่มนัด กินข้าวเที่ยวกับที่รักบ่าย3โมง",
            "นัดหมาย ประชุมคณะกรรมการ พรุ่งนี้ 10 นาฬิกา",
            "ตั้งนัด ไปหาหมอสมชาย โรงพยาบาลศิริราช วันนี้ 14.30 น.",
            "เพิ่มนัด เจอกับลูกค้า ที่ออฟฟิศ ชั้น 5 บ่าย 2 โมง",
            "นัดกินข้าวกับเพื่อน ห้างสยามพารากอน เย็น 6 โมง"
        ]
        
        # Results history
        self.results_history = []
    
    def create_widgets(self):
        """สร้าง GUI components"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="🤖 Enhanced Smart Parser Tester", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="📝 Input Text", padding="10")
        input_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Text input
        ttk.Label(input_frame, text="พิมพ์ข้อความที่ต้องการทดสอบ:").grid(row=0, column=0, sticky=tk.W)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, width=70, height=4, 
                                                   font=('TH Sarabun New', 12))
        self.input_text.grid(row=1, column=0, columnspan=2, pady=(5, 10), sticky=(tk.W, tk.E))
        
        # Sample texts dropdown
        ttk.Label(input_frame, text="หรือเลือกตัวอย่าง:").grid(row=2, column=0, sticky=tk.W)
        
        self.sample_var = tk.StringVar(value="เลือกตัวอย่าง...")
        self.sample_combo = ttk.Combobox(input_frame, textvariable=self.sample_var, 
                                        values=self.sample_texts, width=60, 
                                        font=('TH Sarabun New', 10))
        self.sample_combo.grid(row=3, column=0, pady=(5, 10), sticky=(tk.W, tk.E))
        self.sample_combo.bind('<<ComboboxSelected>>', self.on_sample_selected)
        
        # Buttons frame
        button_frame = ttk.Frame(input_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10))
        
        # Parse button
        self.parse_button = ttk.Button(button_frame, text="🔍 Parse Text", 
                                      command=self.parse_text, style='Accent.TButton')
        self.parse_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Clear button
        self.clear_button = ttk.Button(button_frame, text="🗑️ Clear", 
                                      command=self.clear_input)
        self.clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Results section
        results_frame = ttk.LabelFrame(main_frame, text="📊 Parse Results", padding="10")
        results_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Results display
        self.results_text = scrolledtext.ScrolledText(results_frame, width=70, height=15, 
                                                     font=('Consolas', 10))
        self.results_text.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Export buttons frame
        export_frame = ttk.Frame(results_frame)
        export_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # Export JSON button
        self.export_json_button = ttk.Button(export_frame, text="💾 Export JSON", 
                                           command=self.export_json)
        self.export_json_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export Text button
        self.export_text_button = ttk.Button(export_frame, text="📄 Export Text", 
                                           command=self.export_text)
        self.export_text_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # View History button
        self.history_button = ttk.Button(export_frame, text="📋 View History", 
                                       command=self.view_history)
        self.history_button.pack(side=tk.LEFT)
        
        # Configure grid weights
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        results_frame.grid_rowconfigure(0, weight=1)
        results_frame.grid_columnconfigure(0, weight=1)
        input_frame.grid_columnconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="พร้อมใช้งาน")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, 
                              relief=tk.SUNKEN, anchor=tk.W)
        status_bar.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def on_sample_selected(self, event=None):
        """เมื่อเลือกตัวอย่างจาก dropdown"""
        selected_text = self.sample_var.get()
        if selected_text != "เลือกตัวอย่าง...":
            self.input_text.delete(1.0, tk.END)
            self.input_text.insert(1.0, selected_text)
    
    def clear_input(self):
        """Clear input text"""
        self.input_text.delete(1.0, tk.END)
        self.sample_var.set("เลือกตัวอย่าง...")
        self.status_var.set("Input cleared")
    
    def parse_text(self):
        """Parse input text และแสดงผลลัพธ์"""
        input_text = self.input_text.get(1.0, tk.END).strip()
        
        if not input_text:
            messagebox.showwarning("Warning", "กรุณาใส่ข้อความที่ต้องการ parse")
            return
        
        try:
            self.status_var.set("กำลัง parse ข้อความ...")
            self.root.update()
            
            # Parse with enhanced parser
            result = self.parser.extract_appointment_info(input_text)
            
            # Format result for display
            formatted_result = self.format_result(result)
            
            # Display result
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, formatted_result)
            
            # Add to history
            self.results_history.append({
                'timestamp': datetime.now().isoformat(),
                'input': input_text,
                'result': result
            })
            
            self.status_var.set(f"Parse สำเร็จ - Confidence: {result.get('confidence', 0):.2f}")
            
        except Exception as e:
            error_msg = f"❌ Error parsing text: {str(e)}"
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(1.0, error_msg)
            self.status_var.set("Parse failed")
            messagebox.showerror("Parse Error", str(e))
    
    def format_result(self, result):
        """Format parse result สำหรับการแสดงผล"""
        formatted = "🔍 PARSE RESULTS\n"
        formatted += "=" * 50 + "\n\n"
        
        # Original text
        formatted += f"📝 Original Text: {result.get('original_text', '')}\n\n"
        
        # Main results
        formatted += "📊 EXTRACTED DATA:\n"
        formatted += "-" * 30 + "\n"
        
        # Only show fields with values
        fields = [
            ('นัดหมาย', result.get('appointment_title', '')),
            ('วันที่', result.get('date', '')),
            ('เวลา', result.get('time', '')),
            ('สถานที่', result.get('location', '')),
            ('อาคาร/แผนก/ชั้น', result.get('building_dept', '')),
            ('บุคคล/ผู้ติดต่อ', result.get('contact_person', '')),
            ('เบอร์โทร', result.get('phone_number', ''))
        ]
        
        for field_name, field_value in fields:
            if field_value:  # Only show non-empty fields
                formatted += f"{field_name}: \"{field_value}\"\n"
        
        # Context and confidence
        formatted += "\n📈 ANALYSIS:\n"
        formatted += "-" * 30 + "\n"
        
        context = result.get('context', {})
        formatted += f"Context Type: {context.get('type', 'general')}\n"
        formatted += f"Confidence Score: {result.get('confidence', 0):.2f}\n"
        
        if context.get('medical_score', 0) > 0:
            formatted += f"Medical Score: {context.get('medical_score', 0)}\n"
        if context.get('business_score', 0) > 0:
            formatted += f"Business Score: {context.get('business_score', 0)}\n"
        
        # Raw datetime if available
        if result.get('datetime'):
            formatted += f"Raw DateTime: {result['datetime']}\n"
        
        # Debug info (collapsed)
        formatted += "\n🔧 DEBUG INFO (click to expand):\n"
        formatted += "-" * 30 + "\n"
        processed_data = result.get('processed_data', {})
        formatted += f"Normalized Text: {processed_data.get('normalized', '')}\n"
        formatted += f"Time Matches: {len(processed_data.get('time_matches', []))}\n"
        formatted += f"Location Matches: {len(processed_data.get('location_matches', []))}\n"
        formatted += f"Contact Matches: {len(processed_data.get('contact_matches', []))}\n"
        
        return formatted
    
    def export_json(self):
        """Export ผลลัพธ์เป็น JSON file"""
        if not self.results_history:
            messagebox.showwarning("Warning", "ไม่มีผลลัพธ์ให้ export")
            return
        
        try:
            # Get latest result
            latest_result = self.results_history[-1]
            
            # Clean up result for JSON export (remove non-serializable objects)
            export_data = {
                'timestamp': latest_result['timestamp'],
                'input_text': latest_result['input'],
                'results': {
                    'appointment_title': latest_result['result'].get('appointment_title', ''),
                    'date': latest_result['result'].get('date', ''),
                    'time': latest_result['result'].get('time', ''),
                    'location': latest_result['result'].get('location', ''),
                    'building_dept': latest_result['result'].get('building_dept', ''),
                    'contact_person': latest_result['result'].get('contact_person', ''),
                    'phone_number': latest_result['result'].get('phone_number', ''),
                    'confidence': latest_result['result'].get('confidence', 0)
                }
            }
            
            # Remove empty fields
            export_data['results'] = {k: v for k, v in export_data['results'].items() 
                                    if v and v != ''}
            
            # Choose file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Parse Results as JSON"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2)
                
                messagebox.showinfo("Success", f"Results exported to {filename}")
                self.status_var.set(f"Exported to {Path(filename).name}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export JSON: {str(e)}")
    
    def export_text(self):
        """Export ผลลัพธ์เป็น text file"""
        current_results = self.results_text.get(1.0, tk.END).strip()
        
        if not current_results:
            messagebox.showwarning("Warning", "ไม่มีผลลัพธ์ให้ export")
            return
        
        try:
            # Choose file location
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                title="Save Parse Results as Text"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(current_results)
                
                messagebox.showinfo("Success", f"Results exported to {filename}")
                self.status_var.set(f"Exported to {Path(filename).name}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export text: {str(e)}")
    
    def view_history(self):
        """แสดง history ของผลลัพธ์ทั้งหมด"""
        if not self.results_history:
            messagebox.showinfo("History", "ไม่มี history ให้แสดง")
            return
        
        # Create history window
        history_window = tk.Toplevel(self.root)
        history_window.title("📋 Parse History")
        history_window.geometry("800x600")
        
        # History text widget
        history_frame = ttk.Frame(history_window, padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        history_text = scrolledtext.ScrolledText(history_frame, font=('Consolas', 10))
        history_text.pack(fill=tk.BOTH, expand=True)
        
        # Format history
        history_content = "📋 PARSE HISTORY\n"
        history_content += "=" * 80 + "\n\n"
        
        for i, entry in enumerate(self.results_history, 1):
            history_content += f"[{i}] {entry['timestamp']}\n"
            history_content += f"Input: {entry['input']}\n"
            
            result = entry['result']
            history_content += "Results:\n"
            
            fields = [
                ('นัดหมาย', result.get('appointment_title', '')),
                ('วันที่', result.get('date', '')),
                ('เวลา', result.get('time', '')),
                ('สถานที่', result.get('location', '')),
                ('บุคคล/ผู้ติดต่อ', result.get('contact_person', '')),
            ]
            
            for field_name, field_value in fields:
                if field_value:
                    history_content += f"  {field_name}: {field_value}\n"
            
            history_content += f"  Confidence: {result.get('confidence', 0):.2f}\n"
            history_content += "-" * 80 + "\n\n"
        
        history_text.insert(1.0, history_content)
        history_text.config(state=tk.DISABLED)

def main():
    """Main function"""
    try:
        # Create main window
        root = tk.Tk()
        
        # Configure style for better appearance
        style = ttk.Style()
        style.theme_use('clam')
        
        # Create app
        app = ParserTesterApp(root)
        
        # Start GUI
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()