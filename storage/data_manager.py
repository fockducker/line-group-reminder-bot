"""
Data Manager for LINE Group Reminder Bot
จัดการข้อมูลแยกระหว่าง Personal (1:1) และ Group Chat
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

class DataManager:
    """จัดการข้อมูลการนัดหมายแยกตาม context"""
    
    def __init__(self, data_file="appointments_data.json"):
        self.data_file = data_file
        self.data = self._load_data()
    
    def _load_data(self) -> Dict[str, Any]:
        """โหลดข้อมูลจากไฟล์ JSON"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                pass
        
        # ถ้าไม่มีไฟล์หรือไฟล์เสีย สร้างโครงสร้างใหม่
        return {
            "personal": {},      # user_id -> appointments
            "groups": {},        # group_id -> appointments  
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    def _save_data(self):
        """บันทึกข้อมูลลงไฟล์ JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving data: {e}")
    
    def get_appointments(self, context_type: str, context_id: str) -> List[Dict[str, Any]]:
        """
        ดึงรายการการนัดหมายตาม context
        
        Args:
            context_type: "personal" หรือ "group"
            context_id: user_id (สำหรับ personal) หรือ group_id (สำหรับ group)
        
        Returns:
            รายการการนัดหมาย
        """
        if context_type == "personal":
            return self.data["personal"].get(context_id, [])
        elif context_type == "group":
            return self.data["groups"].get(context_id, [])
        else:
            return []
    
    def add_appointment(self, context_type: str, context_id: str, user_id: str, 
                       appointment_data: Dict[str, Any]) -> str:
        """
        เพิ่มการนัดหมายใหม่
        
        Args:
            context_type: "personal" หรือ "group"
            context_id: user_id หรือ group_id
            user_id: ผู้ที่เพิ่มการนัดหมาย
            appointment_data: ข้อมูลการนัดหมาย
        
        Returns:
            ID ของการนัดหมายที่เพิ่ม
        """
        appointment_id = str(uuid.uuid4())[:8]
        
        appointment = {
            "id": appointment_id,
            "added_by": user_id,
            "created_at": datetime.now().isoformat(),
            **appointment_data
        }
        
        if context_type == "personal":
            if context_id not in self.data["personal"]:
                self.data["personal"][context_id] = []
            self.data["personal"][context_id].append(appointment)
            
        elif context_type == "group":
            if context_id not in self.data["groups"]:
                self.data["groups"][context_id] = []
            self.data["groups"][context_id].append(appointment)
        
        self._save_data()
        return appointment_id
    
    def delete_appointment(self, context_type: str, context_id: str, 
                          appointment_id: str) -> bool:
        """
        ลบการนัดหมาย
        
        Args:
            context_type: "personal" หรือ "group"
            context_id: user_id หรือ group_id
            appointment_id: ID ของการนัดหมาย
        
        Returns:
            True หากลบสำเร็จ
        """
        appointments = self.get_appointments(context_type, context_id)
        
        for i, apt in enumerate(appointments):
            if apt["id"] == appointment_id:
                if context_type == "personal":
                    self.data["personal"][context_id].pop(i)
                elif context_type == "group":
                    self.data["groups"][context_id].pop(i)
                
                self._save_data()
                return True
        
        return False
    
    def get_stats(self) -> Dict[str, Any]:
        """ดึงสถิติการใช้งาน"""
        personal_users = len(self.data["personal"])
        groups = len(self.data["groups"])
        
        total_personal_appointments = sum(
            len(appointments) for appointments in self.data["personal"].values()
        )
        total_group_appointments = sum(
            len(appointments) for appointments in self.data["groups"].values()
        )
        
        return {
            "personal_users": personal_users,
            "groups": groups,
            "total_personal_appointments": total_personal_appointments,
            "total_group_appointments": total_group_appointments,
            "total_appointments": total_personal_appointments + total_group_appointments
        }

# Global instance
data_manager = DataManager()