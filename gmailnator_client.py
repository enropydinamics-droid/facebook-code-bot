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
        Поиск 6-значного кода подтверждения в любом письме от Facebook.
        Не проверяет тему письма – только отправителя.
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
                is_facebook = any(fb_sender in sender for fb_sender in facebook_senders)
                if not is_facebook:
                    continue
                
                message_id = message.get('id')
                if not message_id:
                    continue
                
                print(f"📧 Найдено письмо от Facebook! Отправитель: {sender}")
                message_data = self.get_message_content(message_id)
                if not message_data:
                    continue
                
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
        Извлечение 6-значного кода из HTML/текста.
        Сначала ищет коды рядом с ключевыми словами (разные языки),
        затем просто любые 6 цифр.
        """
        if not content:
            return None
        
        # Паттерны с ключевыми словами (можно расширять)
        patterns_with_keywords = [
            r'Verification code:\s*(\d{6})',
            r'verification code:\s*(\d{6})',
            r'code:\s*(\d{6})',
            r'驗證碼[：:]\s*(\d{6})',      # китайский
            r'код подтверждения[:\s]*(\d{6})',  # русский
            r'código de verificación[:\s]*(\d{6})', # испанский
            r'code de vérification[:\s]*(\d{6})',  # французский
        ]
        
        for pattern in patterns_with_keywords:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                code = match.group(1)
                if len(code) == 6 and code.isdigit():
                    return code
        
        # Запасной вариант: любые 6 цифр (на случай, если ключевые слова не распознаны)
        # Ищем первое вхождение ровно 6 цифр
        simple_pattern = r'\b(\d{6})\b'
        matches = re.findall(simple_pattern, content)
        if matches:
            return matches[0]  # берём первый найденный 6-значный блок
        
        return None