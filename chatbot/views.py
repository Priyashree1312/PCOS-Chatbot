# chatbot/views.py - COMPLETE RAG + PINKY HYBRID
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .rag_engine import get_rag_engine  # RAG ACTIVATED!
import json
import re

def get_pinky_response(question):
    """🚀 FAST KEYWORD RESPONSES (instant for 80% common queries)"""
    q = question.lower().strip()
    
    # 🌍 INTERNATIONAL DIET (priority match)
    if any(word in q for word in ['international', 'global', 'mediterranean', 'western', 'foreign']):
        return """🌍 **International PCOS Diet (Mediterranean Style):**
• **Breakfast:** Greek yogurt + berries + almonds
• **Lunch:** Quinoa salad + grilled salmon + olive oil
• **Dinner:** Chicken breast + broccoli + sweet potato
• **Snacks:** Avocado, walnuts, dark chocolate (70%+) 🌟"""

    # 🇮🇳 INDIAN DIET
    elif re.search(r'\b(diet|food|eat|meal)\b', q):
        return """🥗 **Indian PCOS Diet (NO maida!):**
• **Breakfast:** Ragi porridge + sprouts + green tea
• **Lunch:** Jowar roti + dal + palak paneer
• **Dinner:** Grilled fish/chicken + cucumber raita
• **Snacks:** Roasted makhana, almonds 💚"""

    # 💕 SYMPTOMS
    elif re.search(r'\b(symptom|sign|problem)\b', q):
        return """💕 **PCOS Symptoms (Rotterdam criteria):**
• Irregular periods (<8/year or >35 days)
• Excess hair (hirsutism), acne
• Weight gain (abdomen)
• Polycystic ovaries (ultrasound) 🌸"""

    # ⚕️ TREATMENT
    elif re.search(r'\b(treat|medicine|med|pill|drug|supplement)\b', q):
        return """⚕️ **PCOS Treatments:**
• **Lifestyle:** 5-10% weight loss = 50% improvement!
• **Meds:** Metformin (insulin), OCPs (hormones)
• **Supplements:** Inositol, Vitamin D, Omega-3
• **Always consult doctor!** 🩺"""

    # 🧘 YOGA
    elif re.search(r'\b(yoga|exercise|pose|workout)\b', q):
        return """🧘‍♀️ **Best Yoga Poses (15 mins daily):**
• **Butterfly** (Baddha Konasana) - ovaries
• **Cobra** (Bhujangasana) - hormones
• **Bridge** (Setu Bandhasana) - thyroid
• **Cat-Cow** - stress relief 🌺"""

    # 📊 ROTTERDAM
    elif re.search(r'\brotterdam\b', q):
        return """📊 **Rotterdam Criteria (2/3 needed):**
1. **Irregular periods** (<8/year or >35 days)
2. **High androgens** (hirsutism/acne)
3. **Polycystic ovaries** (12+ follicles) 🔬"""

    return None  # RAG handles everything else!

def chat_view(request):
    """Render chat page"""
    return render(request, "chatbot/chat.html")

@csrf_exempt
@require_http_methods(["POST"])
def chat_api(request):
    """🎯 HYBRID: Pinky (0.05s) → RAG (2-3s)"""
    try:
        print(f"🌟 REQUEST: {request.content_type}")
        
        # Extract question
        if 'application/json' in request.content_type:
            data = json.loads(request.body)
            question = data.get('question', data.get('message', '')).strip()
        else:
            question = request.POST.get("question") or request.POST.get("message", "")
            question = question.strip()
        
        print(f"🔥 INPUT: '{question}'")
        
        # 1. FAST PINKY KEYWORDS FIRST
        pinky_response = get_pinky_response(question)
        if pinky_response:
            print("✅ PINKY: Instant keyword match!")
            source = "PINKY_FAST"
        else:
            # 2. RAG for complex questions
            print("🚀 RAG: FAISS + Llama3.2 activated...")
            rag_engine = get_rag_engine()
            pinky_response = rag_engine.chat(question)
            source = "FAISS_RAG"
        
        print(f"✅ {source}: {pinky_response[:50]}...")
        return JsonResponse({
            "answer": pinky_response,
            "source": source,
            "is_error": False
        }, status=200)
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return JsonResponse({
            "answer": "💕 Ask about **symptoms**, **diet**, **international diet**, **treatment**, **yoga**, or any PCOS question! 🌸",
            "is_error": True
        }, status=200)

def health_check(request):
    """Health check with RAG status"""
    try:
        rag_engine = get_rag_engine()
        return JsonResponse({
            "status": "healthy",
            "pinky": "active 💖",
            "rag": "ready 🚀",
            "llm": rag_engine.llm is not None,
            "faiss_docs": len(rag_engine.faiss.documents) if hasattr(rag_engine.faiss, 'documents') else 0
        })
    except Exception as e:
        return JsonResponse({
            "status": "warning",
            "pinky": "active 💖",
            "rag": f"needs_setup: {str(e)[:50]}"
        })

@csrf_exempt
@require_http_methods(["POST"])
def test_rag(request):
    """Test endpoint - required by urls.py"""
    try:
        data = json.loads(request.body)
        question = data.get('question', 'test PCOS').strip()
        
        # Test both systems
        pinky_response = get_pinky_response(question)
        rag_engine = get_rag_engine()
        rag_response = rag_engine.chat(question)
        
        return JsonResponse({
            "question": question,
            "pinky": pinky_response,
            "rag": rag_response,
            "pinky_used": pinky_response is not None,
            "works": True
        })
    except Exception as e:
        return JsonResponse({"error": str(e)})
