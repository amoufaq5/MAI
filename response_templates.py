import random

def make_human_response(drug, confidence, side_effects, lang="en"):
    side = side_effects if side_effects else {
        "en": "no major known issues",
        "ar": "لا توجد أعراض جانبية معروفة"
    }[lang]

    if lang == "ar":
        templates = [
            f"بناءً على إجاباتك، أنصح بـ **{drug}**.",
            f"أنصحك باستخدام **{drug}** لتخفيف الأعراض. الثقة: {confidence:.1f}٪.",
            f"**{drug}** يبدو مناسبًا لحالتك. الأعراض الجانبية المتوقعة: {side}",
            f"يمكنك تجربة **{drug}**، فهو دواء بدون وصفة يتوافق مع الأعراض التي ذكرتها.",
            f"تشير الأعراض التي قدمتها إلى أن **{drug}** قد يساعدك. نسبة الثقة: {confidence:.1f}٪."
        ]
    else:
        templates = [
            f"Thanks for the info! From everything you shared, I’d suggest **{drug}**. It's shown to help in similar cases.",
            f"It sounds like **{drug}** would be a good fit for your symptoms. Confidence is {confidence:.1f}%.",
            f"Based on your responses, I recommend **{drug}**. It’s an OTC option that may relieve what you're experiencing.",
            f"✅ You can try **{drug}** — it matches your symptoms well. Be aware of possible side effects like: {side}.",
            f"After reviewing your answers, **{drug}** seems appropriate. Confidence: {confidence:.1f}%. Common side effects: {side}.",
        ]

    return random.choice(templates)
