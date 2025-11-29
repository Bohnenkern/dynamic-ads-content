from typing import Dict, Any, List, Optional
import logging
import os
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service für OpenAI API-Integration"""
    
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.client = None
        self.user_prompts: Dict[int, str] = {}
        
        if self.api_key:
            self.client = AsyncOpenAI(api_key=self.api_key)
            logger.info("OpenAI Client initialisiert")
        else:
            logger.warning("OPENAI_API_KEY nicht gesetzt - OpenAI-Features deaktiviert")
    
    async def generate_prompt_for_user(
        self, 
        user_data: Dict[str, Any], 
        matched_interests: List[Dict[str, Any]]
    ) -> str:
        """
        Generiert einen personalisierten Prompt basierend auf
        User-Daten und gematchten Interessen
        """
        if not self.client:
            # Fallback: Generiere Prompt ohne OpenAI
            return self._generate_fallback_prompt(user_data, matched_interests)
        
        try:
            # Erstelle Kontext für OpenAI
            interests_text = ", ".join([m["interest"] for m in matched_interests])
            categories_text = ", ".join(list(set([m["category"] for m in matched_interests])))
            
            system_message = """Du bist ein Experte für personalisierte Werbekampagnen. 
            Erstelle einen prägnanten, kreativen Prompt für die Generierung von Werbeinhalten, 
            der die Interessen und demografischen Daten der Person berücksichtigt."""
            
            user_message = f"""
            Erstelle einen Werbe-Prompt für folgende Person:
            
            Name: {user_data['name']}
            Alter: {user_data['age']}
            Beruf: {user_data['demographics']['occupation']}
            Standort: {user_data['location']}
            
            Passende Trend-Interessen: {interests_text}
            Trend-Kategorien: {categories_text}
            
            Der Prompt soll später verwendet werden, um personalisierte Werbeinhalte zu generieren.
            Halte den Prompt präzise und fokussiert auf die stärksten Interessen.
            """
            
            response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            generated_prompt = response.choices[0].message.content.strip()
            
            # Cache den generierten Prompt
            self.user_prompts[user_data['id']] = generated_prompt
            
            logger.info(f"Prompt für User {user_data['name']} (ID: {user_data['id']}) generiert")
            return generated_prompt
            
        except Exception as e:
            logger.error(f"Fehler bei OpenAI API-Aufruf: {str(e)}")
            return self._generate_fallback_prompt(user_data, matched_interests)
    
    def _generate_fallback_prompt(
        self, 
        user_data: Dict[str, Any], 
        matched_interests: List[Dict[str, Any]]
    ) -> str:
        """
        Generiert einen Fallback-Prompt ohne OpenAI API
        """
        if not matched_interests:
            return f"Erstelle Werbeinhalte für {user_data['name']}, {user_data['age']} Jahre, {user_data['demographics']['occupation']}."
        
        interests_text = ", ".join([m["interest"] for m in matched_interests[:3]])
        
        prompt = f"""Erstelle ansprechende Werbeinhalte für {user_data['name']}, 
{user_data['age']} Jahre, {user_data['demographics']['occupation']} aus {user_data['location']}.
Fokussiere auf folgende Interessen: {interests_text}.
Berücksichtige die aktuelle Popularität dieser Trends und erstelle emotionale, 
zielgruppengerechte Inhalte."""
        
        # Cache den generierten Prompt
        self.user_prompts[user_data['id']] = prompt
        
        return prompt
    
    async def generate_prompts_for_all_users(
        self, 
        match_results: List[Dict[str, Any]]
    ) -> Dict[int, str]:
        """
        Generiert Prompts für alle User mit Match-Ergebnissen
        """
        from services.user_data import user_service
        
        results = {}
        
        for match_result in match_results:
            if match_result.get("matched_interests"):
                user_id = match_result["user_id"]
                user_data = user_service.get_user_by_id(user_id)
                
                if user_data:
                    prompt = await self.generate_prompt_for_user(
                        user_data, 
                        match_result["matched_interests"]
                    )
                    results[user_id] = prompt
        
        logger.info(f"Prompts für {len(results)} User generiert")
        return results
    
    def get_cached_prompt(self, user_id: int) -> Optional[str]:
        """Gibt gecachten Prompt zurück"""
        return self.user_prompts.get(user_id)
    
    def get_all_cached_prompts(self) -> Dict[int, str]:
        """Gibt alle gecachten Prompts zurück"""
        return self.user_prompts


# Singleton-Instanz
openai_service = OpenAIService()
