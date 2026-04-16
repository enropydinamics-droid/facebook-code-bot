import requests
import time
import re
from typing import Optional, List, Dict

class GmailnatorClient:
    def __init__(self, api_key: str, api_host: str):
        self.base_url = "https://gmailnator.p.rapidapi.com"
        self.headers = {
            "X-RapidAPI-Key": api_key,
            "X-RapidAPI-Host": api_host,
            "Content-Type": "application/json"
        }
    
    def get_inbox(self, email: str) -> List[Dict]:
        """Получение списка входящих писем"""
        try:
            response = requests.post(
                f"{self.base_url}/api/inbox",
                json={"email": email},
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'success':
                return data.get('messages', [])
            return []
        except Exception as e:
            print(f"Ошибка получения списка писем: {e}")
            return []
    
    def get_message_content(self, message_id: str) -> Optional[Dict]:
        """Получение полного содержимого письма по ID"""
        try:
            response = requests.get(
                f"{self.base_url}/api/inbox/{message_id}",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Ошибка получения содержимого письма: {e}")
            return None
    
    def find_verification_code(self, email: str, attempts: int = 2, interval_first: int = 7, interval_second: int = 8) -> Optional[str]:
        """
        Поиск кода подтверждения от Facebook в почтовом ящике
        Делает 2 попытки: через 7 секунд и через 15 секунд
        """
        facebook_senders = [
            'facebookmail.com',
            'notification@facebookmail.com'
        ]
        
        intervals = [interval_first, interval_second]
        
        for attempt in range(1, attempts + 1):
            print(f"[Попытка {attempt}/{attempts}] Проверяю почту {email}...")
            messages = self.get_inbox(email)
            
            for message in messages:
                sender = message.get('from', '').lower()
                subject = message.get('subject', '').lower()
                
                # Проверяем, что письмо от Facebook и тема "Verify your business email"
                is_facebook = any(fb_sender in sender for fb_sender in facebook_senders)
                is_verify_email = 'verify your business email' in subject or 'verify your email' in subject
                
                if is_facebook and is_verify_email:
                    message_id = message.get('id')
                    if not message_id:
                        continue
                    
                    print(f"📧 Найдено письмо с кодом! Отправитель: {sender}")
                    print(f"   Тема: {subject}")
                    
                    message_data = self.get_message_content(message_id)
                    if message_data:
                        content = message_data.get('content', '')
                        verification_code = self._extract_verification_code(content)
                        if verification_code:
                            print(f"✅ Код найден на попытке {attempt}: {verification_code}")
                            return verification_code
                        else:
                            print("⚠️ Код не найден в содержимом")
            
            if attempt < attempts:
                wait_time = intervals[attempt - 1]
                print(f"⏳ Писем с кодом нет. Следующая проверка через {wait_time} сек...")
                time.sleep(wait_time)
        
        print(f"❌ Код не обнаружен после {attempts} попыток")
        return None
    
    def _extract_verification_code(self, content: str) -> Optional[str]:
        """
        Извлечение 6-значного кода подтверждения из содержимого письма
        """
        if not content:
            return None
        
        # Паттерны для поиска 6-значного кода
        patterns = [
            r'Verification code:\s*(\d{6})',
            r'verification code:\s*(\d{6})',
            r'code:\s*(\d{6})',
            r'(\d{6})',  # просто 6 цифр (как запасной вариант)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Проверяем, что это похоже на код (не часть другой информации)
                code = matches[0]
                if len(code) == 6 and code.isdigit():
                    return code
        
        return None