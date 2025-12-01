from huggingface_hub import InferenceClient
from app.config import HF_TOKEN


def generate_text(context, question, model="openai/gpt-oss-20b:nebius", api_token=HF_TOKEN, max_tokens=500):
    """
    Funcție pentru generare text folosind InferenceClient - VERSIUNEA CARE MERGE
    """
    try:
        # Verifică dacă token-ul este setat
        if not api_token or api_token == "None":
            return "EROARE: Token-ul Hugging Face nu este setat. Verifică fișierul .env"

        # Initializează clientul cu base_url corect
        client = InferenceClient(
            api_key=api_token,
            base_url="https://router.huggingface.co"
        )

        # Construiește prompt-ul pentru generarea de act notarial
        prompt_content = f"""
EXEMPLU DE ACT NOTARIAL (declarație călătorie):
Subsemnatul George Ionescu, CNP 1234567890123, autorizez minorul Maria Ionescu, născută la 15.03.2010, să călătorească în Italia în perioada 01-15 August 2024, însoțită de mama sa, Elena Ionescu.

ACUM GENEREAZĂ PENTRU:
- Nume părinte: Ion Popescu
- CNP: 1987654321098  
- Nume minor: Andrei Popescu
- Data naștere minor: 10.07.2012
- Destinație: Spania
- Perioadă: 20-30 Iulie 2024
- Însoțitor: Tatăl (Ion Popescu)

Generează un act notarial complet și profesional:
"""

        messages = [
            {
                "role": "user",
                "content": prompt_content
            }
        ]

        print(f"🔗 Se conectează la modelul: {model}...")

        # Folosește chat.completions.create ca în funcția ta care merge
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.3
        )

        return completion.choices[0].message.content

    except Exception as e:
        return f"Eroare la generarea textului: {str(e)}"


def testeaza_cu_exemplu_real():
    """
    Testează generarea unui act notarial cu date noi
    """
    print("⏳ Se generează actul notarial...")

    act_generat = generate_text(
        context="",  # lasăm gol pentru că prompt-ul este deja în funcție
        question="",
        model="openai/gpt-oss-20b:nebius",  # folosește același model ca tine
        max_tokens=600,
        api_token=HF_TOKEN
    )

    return act_generat


def main():
    """
    Funcția principală care rulează testul
    """
    print("🚀 Testare generare act notarial cu GPT-OSS-20B")
    print("=" * 50)

    # Verifică dacă token-ul este setat
    if not HF_TOKEN:
        print("❌ EROARE: Token-ul nu este setat!")
        print("Verifică fișierul .env și asigură-te că conține:")
        print("OPENAI_API_KEY=tokenul_tau_hugging_face_aici")
        return

    print(f"✅ Token detectat: {HF_TOKEN[:10]}...")

    # Rulează testul
    rezultat = testeaza_cu_exemplu_real()

    print("\n📄 ACTUL GENERAT:")
    print("=" * 50)
    print(rezultat)
    print("=" * 50)


if __name__ == "__main__":
    main()