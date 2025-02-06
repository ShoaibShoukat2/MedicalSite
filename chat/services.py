from anthropic import Anthropic
import os

class HealthcareAIAgent:
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
        
    async def get_response(self, message_history, user_message):
        # Format message history for context
        formatted_history = []
        for msg in message_history:
            role = "user" if msg.sender_type == "patient" else "assistant"
            formatted_history.append({"role": role, "content": msg.content})
        
        try:
            response = await self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a medical AI assistant. Provide helpful information while:
                        - Making it clear you are an AI assistant
                        - Not providing specific medical diagnoses
                        - Encouraging consultation with healthcare professionals for specific medical advice
                        - Focusing on general health information and guidance"""
                    },
                    *formatted_history,
                    {"role": "user", "content": user_message}
                ]
            )
            return response.content[0].text
        except Exception as e:
            return "I apologize, but I'm having technical difficulties. Please try again later."
