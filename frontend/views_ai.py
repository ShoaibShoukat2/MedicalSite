from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os
from datetime import datetime

# OpenAI client (v0.28.1 - old API format)
try:
    import openai
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        openai.api_key = api_key
        OPENAI_AVAILABLE = True
        print("OpenAI API key configured successfully.")
    else:
        OPENAI_AVAILABLE = False
        print("OpenAI API key not found. Using fallback responses only.")
except ImportError:
    OPENAI_AVAILABLE = False
    print("OpenAI not installed. Using fallback responses only.")
except Exception as e:
    OPENAI_AVAILABLE = False
    print(f"OpenAI initialization error: {e}. Using fallback responses only.")

@csrf_exempt
@require_http_methods(["POST"])
def ask_avatar(request):
    """
    Handle AI avatar questions with intelligent medical responses and language support
    """
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '')
        user_type = data.get('user_type', 'patient')
        language = data.get('language', 'en')  # Get language from request
        
        if not user_message:
            return JsonResponse({
                'success': False,
                'error': 'Message is required'
            }, status=400)
        
        # Generate AI response using OpenAI with language support
        ai_response = generate_ai_response(user_message, user_type, language)
        
        # Try to generate D-ID video
        video_url = None
        try:
            video_url = generate_did_video(ai_response)
        except Exception as e:
            print(f"D-ID video generation failed: {e}")
        
        response_data = {
            'success': True,
            'answer': ai_response,
            'message_type': 'text',
            'timestamp': str(datetime.now())
        }
        
        # Add video URL if available
        if video_url:
            response_data['video_url'] = video_url
            response_data['has_video'] = True
        else:
            response_data['has_video'] = False
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}',
            'answer': "I apologize, but I'm having trouble processing your request. Please try again."
        }, status=500)

def generate_ai_response(user_message, user_type='patient', language='en'):
    """
    Generate intelligent AI response using OpenAI GPT (New API v1.0+) with language support
    """
    # Try OpenAI first if available
    if OPENAI_AVAILABLE:
        try:
            # Language-specific system prompts
            language_prompts = {
                'en': """You are Dr. Amanda, a helpful and empathetic AI medical assistant. 
                Your role is to:
                - Provide general health information and guidance
                - Help patients understand symptoms and conditions
                - Assist with appointment scheduling questions
                - Offer wellness tips and preventive care advice
                - Be warm, professional, and reassuring
                
                Important guidelines:
                - Never diagnose or prescribe medication
                - Always recommend consulting with a healthcare professional for serious concerns
                - Be concise but informative (2-3 sentences)
                - Use simple, easy-to-understand language
                - Show empathy and understanding
                - Respond in English""",
                
                'ur': """آپ ڈاکٹر امانڈا ہیں، ایک مددگار اور ہمدرد AI طبی معاون۔
                آپ کا کردار:
                - عمومی صحت کی معلومات اور رہنمائی فراہم کرنا
                - مریضوں کو علامات اور حالات سمجھنے میں مدد کرنا
                - اپائنٹمنٹ شیڈولنگ کے سوالات میں مدد کرنا
                - صحت کے لیے مشورے اور احتیاطی تدابیر پیش کرنا
                - گرم، پیشہ ورانہ اور اطمینان بخش ہونا
                
                اہم رہنمائی:
                - کبھی تشخیص یا دوا تجویز نہ کریں
                - ہمیشہ سنگین مسائل کے لیے صحت کی دیکھ بھال کرنے والے پیشہ ور سے مشورہ کرنے کی سفارش کریں
                - مختصر لیکن معلوماتی جواب دیں (2-3 جملے)
                - سادہ، آسان زبان استعمال کریں
                - ہمدردی اور سمجھ بوجھ دکھائیں
                - اردو میں جواب دیں""",
                
                'ar': """أنت الدكتورة أماندا، مساعدة طبية ذكية مفيدة ومتعاطفة.
                دورك هو:
                - تقديم المعلومات والإرشادات الصحية العامة
                - مساعدة المرضى على فهم الأعراض والحالات
                - المساعدة في أسئلة جدولة المواعيد
                - تقديم نصائح العافية والرعاية الوقائية
                - كوني دافئة ومهنية ومطمئنة
                
                إرشادات مهمة:
                - لا تشخصي أبداً أو تصفي الأدوية
                - انصحي دائماً بالتشاور مع أخصائي رعاية صحية للمخاوف الجدية
                - كوني موجزة ولكن مفيدة (2-3 جمل)
                - استخدمي لغة بسيطة وسهلة الفهم
                - أظهري التعاطف والفهم
                - أجيبي باللغة العربية""",
                
                'hi': """आप डॉ. अमांडा हैं, एक सहायक और सहानुभूतिपूर्ण AI चिकित्सा सहायक।
                आपकी भूमिका:
                - सामान्य स्वास्थ्य जानकारी और मार्गदर्शन प्रदान करना
                - मरीजों को लक्षण और स्थितियों को समझने में मदद करना
                - अपॉइंटमेंट शेड्यूलिंग के प्रश्नों में सहायता करना
                - कल्याण सुझाव और निवारक देखभाल सलाह देना
                - गर्मजोशी, पेशेवर और आश्वस्त करने वाली होना
                
                महत्वपूर्ण दिशानिर्देश:
                - कभी भी निदान या दवा न लिखें
                - गंभीर चिंताओं के लिए हमेशा स्वास्थ्य सेवा पेशेवर से सलाह लेने की सिफारिश करें
                - संक्षिप्त लेकिन जानकारीपूर्ण रहें (2-3 वाक्य)
                - सरल, समझने योग्य भाषा का उपयोग करें
                - सहानुभूति और समझ दिखाएं
                - हिंदी में उत्तर दें"""
            }
            
            system_prompt = language_prompts.get(language, language_prompts['en'])
            
            # Call OpenAI API with old format
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            ai_answer = response.choices[0].message.content.strip()
            return ai_answer
            
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            # Fall through to fallback responses
    
    # Fallback to rule-based responses
    return get_fallback_response(user_message)

def get_fallback_response(user_message):
    """
    Enhanced fallback responses when AI API is unavailable
    """
    message_lower = user_message.lower()
    
    # Specific symptoms
    if any(word in message_lower for word in ['headache', 'migraine']):
        return "Headaches can have various causes including stress, dehydration, or tension. Try resting in a quiet, dark room and staying hydrated. If headaches persist or are severe, please consult with one of our healthcare providers for proper evaluation."
    
    elif any(word in message_lower for word in ['fever', 'temperature', 'hot']):
        return "A fever is often your body's way of fighting infection. Stay hydrated, rest, and monitor your temperature. If fever exceeds 101°F (38.3°C) or persists for more than 3 days, please seek medical attention."
    
    elif any(word in message_lower for word in ['cough', 'cold', 'flu']):
        return "Cold and flu symptoms can be managed with rest, fluids, and over-the-counter medications. However, if you experience difficulty breathing, persistent high fever, or symptoms worsen, please contact our healthcare team immediately."
    
    # General pain
    elif any(word in message_lower for word in ['pain', 'hurt', 'ache', 'sore']):
        return "I understand you're experiencing discomfort. Pain can have many causes and proper evaluation is important. I recommend scheduling an appointment with one of our healthcare providers for accurate diagnosis and treatment. Would you like help booking an appointment?"
    
    # Mental health
    elif any(word in message_lower for word in ['stress', 'anxiety', 'depression', 'mental']):
        return "Mental health is just as important as physical health. We offer counseling services and can connect you with mental health professionals. If you're experiencing a crisis, please call our 24/7 support line or emergency services."
    
    # Appointments
    elif any(word in message_lower for word in ['appointment', 'book', 'schedule', 'visit']):
        return "I'd be happy to help you schedule an appointment! You can book online through our patient portal, call our scheduling team, or I can guide you through the process. What type of care do you need?"
    
    # Medications
    elif any(word in message_lower for word in ['medicine', 'medication', 'prescription', 'drug', 'pill']):
        return "For questions about medications, dosages, or side effects, please consult with your healthcare provider or pharmacist. They have access to your medical history and can provide safe, personalized guidance."
    
    # Preventive care
    elif any(word in message_lower for word in ['checkup', 'screening', 'vaccine', 'prevention']):
        return "Regular preventive care is essential for maintaining good health. We offer comprehensive checkups, screenings, and vaccinations. I can help you schedule your next preventive care appointment."
    
    # Emergency
    elif any(word in message_lower for word in ['emergency', 'urgent', 'severe', 'serious', 'chest pain', 'breathing']):
        return "If you're experiencing a medical emergency, please call 911 or visit your nearest emergency room immediately. For urgent but non-emergency concerns, we offer same-day appointments and urgent care services."
    
    # Insurance/billing
    elif any(word in message_lower for word in ['insurance', 'cost', 'billing', 'payment', 'price']):
        return "For questions about insurance coverage, billing, or payment options, please contact our billing department. We accept most major insurance plans and offer payment assistance programs."
    
    # Greeting
    elif any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon']):
        return "Hello! I'm your AI medical assistant. I'm here to help answer your health questions, provide information about our services, and assist with appointment scheduling. How can I help you today?"
    
    # Thanks
    elif any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return "You're very welcome! I'm here to help whenever you need assistance with your healthcare needs. Is there anything else I can help you with today?"
    
    # Default
    else:
        return "Thank you for your question. I'm here to help with general health information and appointment scheduling. For specific medical advice, I always recommend consulting with one of our qualified healthcare professionals. How else can I assist you?"

def generate_did_video(text):
    """
    Generate D-ID talking avatar video
    """
    import requests
    import time
    
    # D-ID API configuration
    DID_API_KEY = os.getenv('DID_API_KEY', 'your-did-api-key')
    
    if DID_API_KEY == 'your-did-api-key':
        print("D-ID API key not configured")
        return None
    
    # D-ID API endpoint
    url = "https://api.d-id.com/talks"
    
    # Avatar image URL (use your avatar image)
    avatar_image = "https://res.cloudinary.com/dovwzsl4v/image/upload/v1752823658/avatar_zfdfcr.jpg"
    
    # Request payload
    payload = {
        "source_url": avatar_image,
        "script": {
            "type": "text",
            "input": text,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-AriaNeural"  # Female medical voice
            }
        },
        "config": {
            "fluent": True,
            "pad_audio": 0.0,
            "stitch": True
        }
    }
    
    headers = {
        "Authorization": f"Basic {DID_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        # Create talk
        print(f"Creating D-ID video for: {text[:50]}...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        talk_id = response.json()["id"]
        print(f"D-ID talk created: {talk_id}")
        
        # Poll for completion (max 30 seconds)
        for i in range(15):  # 15 attempts, 2 seconds each = 30 seconds max
            time.sleep(2)
            
            # Check status
            status_response = requests.get(f"{url}/{talk_id}", headers=headers, timeout=10)
            status_response.raise_for_status()
            
            status_data = status_response.json()
            status = status_data.get("status")
            
            print(f"D-ID status check {i+1}: {status}")
            
            if status == "done":
                video_url = status_data.get("result_url")
                print(f"D-ID video ready: {video_url}")
                return video_url
            elif status == "error":
                print(f"D-ID error: {status_data.get('error', 'Unknown error')}")
                return None
        
        print("D-ID video generation timeout")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"D-ID API request error: {e}")
        return None
    except Exception as e:
        print(f"D-ID generation error: {e}")
        return None

from datetime import datetime