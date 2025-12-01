## chainlit run apc.py


import chainlit as cl


@cl.on_message
async def main(message: cl.Message):
    # Verifică dacă utilizatorul vrea să genereze un act
    if "declarație" in message.content.lower() or "călătorie" in message.content.lower():
        # Cere detaliile necesare
        await cl.Message(
            content="""🌍 Pentru a genera declarația de călătorie, am nevoie de:

**Te rog completează:**
- Destinația: 
- Perioada:
- Însoțitor: 
- Nume minor:
- Nume tată:
- Nume mamă:

Sau poți încărca poze cu buletinele și completez eu automat!"""
        ).send()

    elif "contract" in message.content.lower():
        await cl.Message(content="📑 Vrei un contract de vânzare-cumpărare? Ce fel de bun?").send()

    else:
        await cl.Message(content="🏛️ Bun venit! Ce act notarial ai nevoie?").send()


@cl.on_chat_start
async def start():
    await cl.Message(content="Bun venit! Eu sunt asistentul tău notarial. Ce act dorești să generezi?").send()