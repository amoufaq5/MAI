import random

def make_human_response(drug, confidence, side_effects):
    side = side_effects if side_effects else "no major known issues"

    templates = [
        f"Thanks for the info! From everything you shared, I’d suggest **{drug}**. It's shown to help in similar cases.",
        f"It sounds like **{drug}** would be a good fit for your symptoms. Confidence is {confidence:.1f}%.",
        f"Based on your responses, I recommend **{drug}**. It’s an OTC option that may relieve what you're experiencing.",
        f"✅ You can try **{drug}** — it matches your symptoms well. Be aware of possible side effects like: {side}.",
        f"After reviewing your answers, **{drug}** seems appropriate. Confidence: {confidence:.1f}%. Common side effects: {side}.",
        f"You’ve described symptoms commonly treated with **{drug}**. Let me know if you need dosage help too.",
        f"I’d recommend giving **{drug}** a try. Just note: {side}. Confidence in this match is {confidence:.1f}%."
    ]

    return random.choice(templates)
