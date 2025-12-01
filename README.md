### hardware
LLaMA 3 8B
Mistral 7B
Phi-3 3.8B sau 14B pentru medium
LaMA 3 8B

---
RoGemma‑7B — un model open‑source optimizat pentru limba română, parte din inițiativa OpenLLM‑Ro.
RoLlama2‑7B — un alt LLM orientat spre română, bazat pe Llama, conceput pentru sarcini de NLP/generare text în română
RoQLlama‑7B — un model „lightweight” adaptat românei, construit pentru sarcini de NLP în română, cu consum redus de memorie prin quantizare.

https://huggingface.co/OpenLLM-Ro
Acestea rulează fluent pe 4070 Ti fără quantizare.
De exemplu, pentru LLM-uri, mulți consideră ca “sweet‑spot” o placă ca RTX 3060 / 4070 Ti cu 12 GB VRAM — suficientă pentru modele 7B–13B.

[Aplicatie Angular / desktop] 
          |
       HTTP
          |
[API server local (FastAPI / Flask)]
          |
       GPU 4070 Ti
          |
[Model LLM local (ex: LLaMA 3 8B, Mistral 7B)]

Componente principale + preț estimativ (2025, România)
Componentă	Specificație recomandată	Preț estimativ RON	Observații
GPU	NVIDIA RTX 4070 Ti 12 GB	5.000–5.500	Esențial pentru rularea LLM pe GPU.
GIGABYTE nVidia GeForce RTX 5060 Ti EAGLE OC 16GB, GDDR7, 128 bit
https://www.cel.ro/pc-gaming-diaxxa-advanced-gamer-intel-core-i9-14900kf-32gb-ddr5-ssd-1tb-m-2-nvme-nvidia-geforce-rtx-5060-ti-16gb-gddr7-128-bit-dlss-4-pMCIxNzEpPiU-l/?gad_source=1&gad_campaignid=11056484145&gbraid=0AAAAAD_GOs9xpDBKTAI-jYNC3G0_a9bBL&gclid=CjwKCAiA86_JBhAIEiwA4i9Ju3FWy-69GYStLqFw1UWyW_pOomysy7fObSxP0WTVS00A7Udof9-x3xoCz2AQAvD_BwE
https://www.cel.ro/pc-gaming-diaxxa-advanced-gamer-amd-ryzen-7-5800x-32gb-ddr4-ssd-1tb-nvidia-geforce-rtx-5060-ti-16gb-gddr7-128-bit-dlss-4-pOCIzPTIrMA-l/
CPU	AMD Ryzen 9 7900 sau Intel Core i7 13th gen	1.200–1.800	Suficient pentru backend și procesare complementară.
RAM	32–64 GB DDR5	800–1.600	Mai mult RAM = mai multă stabilitate pentru multitasking.
SSD	NVMe 1 TB / 2 TB	400–900	Modele + sistem + date notariale.
Placă de bază	Compatibilă cu CPU & GPU	600–1.000	Cu slot PCIe x16 pentru GPU.
Carcasă + sursă + răcire	Sursă 750W+, airflow bun	800–1.200	Necesită răcire bună pentru GPU în sarcină continuă.
Altele / periferice	Monitor, tastatură, UPS mic	500–1.000	Pentru uz birou + protecție curent.
2️⃣ Total estimativ

Buget minim: ~8.000 RON (~1.600 €)
(GPU + CPU + RAM 32GB + SSD 1TB + carcasă și răcire decente)

Buget confortabil / recomandat: ~10.500–12.000 RON (~2.000–2.400 €)
(GPU + CPU performant, RAM 64GB, SSD 2TB, răcire și UPS bune, stabil pentru uz zilnic)

### excelent cu easyocr
Using CPU. Note: This module is much faster with a GPU.
Downloading detection model, please wait. This may take several minutes depending upon your network connection.
C:\Users\Harry\.EasyOCR\model

##cu tesseract

pip install pytesseract Pillow opencv-python

#####
1. Recunoașterea Buletinelor (OCR) - Sâmburele de ML
Aceasta este cea mai evidentă aplicație a ML-ului.

OCR Clasic vs. OCR cu ML:

Un OCR simplu (ca Tesseract folosit "de bază") poate citi text, dar se descurcă prost cu layout-uri complexe, fonturi neobișnuite, unghiuri de poză, lumina proastă sau fundaluri încâlcite.

ML (în special Computer Vision) face minuni aici:

Detecția documentului: Poate identifica și "decupa" automat buletinul din poză, chiar dacă acesta este pe o masă sau este doar o parte a imaginii.

Clasificarea zonelor: Învață că într-un buletin românesc, numele este întotdeauna în partea stângă, iar CNP-ul este întotdeauna sub prenume. Acest lucru permite extracția structurată a datelor (câmp cu câmp: Nume, Prenume, CNP, etc.), nu doar un teanc de text.

Precizie crescută: Modelele antrenate pe sute de imagini de buletine devin extrem de precise în a recunoaște caracterele, chiar și în condiții nefavorabile.

Soluție practică: Poți folosi un serviciu cloud specializat în documente (de exemplu, Google Document AI, Microsoft Azure Form Recognizer, Amazon Textract). Acestea au deja modele pre-antrenate pentru buletine/acte de identitate din multe țări (inclusiv România, cel mai probabil). Ele returnează datele direct sub formă de JSON cu câmpuri structurate (firstName, lastName, idNumber etc.). Acesta este cel mai rapid și eficient mod de a începe.

2. Corectarea Automată a Greșelilor - Pure ML/NLP
Aceasta este o altă zonă unde ML strălucește.

Model de Limbaj (NLP): Poți folosi un model (de exemplu, unul pre-antrenat pe text în română) care să acționeze ca un "corector inteligent".

Cum ar funcționa:

OCR-ul extrage "STAFAN" din poză.

Sistemul tău știe că acest câmp este "Prenume".

Modelul de NLP analizează "STAFAN" și, bazându-se pe probabilități statistice din limba română, sugerează corectarea în "STEFAN".

Acest lucru se poate aplica și la nume de localități ("BUCURESTI" -> "BUCUREȘTI") sau alte cuvinte comune.

Acest lucru reduce dramatic nevoia de intervenție manuală.

3. Generarea Automată a Actelor - AI Generative
Aici intervine partea cea mai "inteligentă". Aceasta nu este doar un simplu "search și replace".

Problemă: Un act ca "Declarația de acord pentru călătoria minorului" nu este un simplu formular. Are părți standard, dar și părți care depind de context (de exemplu, dacă călătoria este în străinătate sau în țară, durata, etc.).

Soluția cu AI:

Poți folosi un sistem de template-uri inteligente alimentat de un model de limbaj generative (ca GPT-4, Llama 3 sau un model open-source specializat pe text juridic în română).

Fluxul ar putea arăta astfel:

Utilizatorul (notarul) selectează buletinele părinților și ale copilului din interfața ta.

Alege template-ul "Declarație acord călătorie minor".

Aplicația extrage automat datele din buletine (nume, CNP-uri, etc.) și le introduce în template.

Aplicația folosește un model de AI pentru a completa automat părțile libere ale textului, bazându-se pe datele extrase și pe un "prompt" bine definit. De exemplu: "Scrie un paragraf pentru o declarație de călătorie a unui minor, cu numele [NUME_COPIL], având ca însoțitor pe [NUME_PARINTE], călătorind în [ȚARA_DESTINATIE] pentru o perioadă de [DURATA]."


Acest lucru nu doar că automatizează complet procesul, dar și asigură că textul generat este coerent, corect gramatical și adaptat situației specifice.

### PASUL 1 Completează detaliile specifice actului:
┌─────────────────────────────────────────┐
│ 🌍 Detalii călătorie minor              │
├─────────────────────────────────────────┤
│ Destinația: [Franța    ▼]               │
│ Perioada: [15.07.2024] - [30.07.2024]   │
│ Însoțitor: [Maria Popescu    ▼]         │
│ Scop: [Vacanță           ▼]             │
│ Mijloc transport: [Avion     ▼]         │
│ Țări tranzit: [Italia, Elveția]         │
└─────────────────────────────────────────┘

## Pasul 2 Alege buletinele (copil: Matei Ilie, mama: Ana de burbon, tata: Gigi Chitaristu)
 (se extrag automat nume, CNP, etc.)
 
## PASUL 3  Aplicația construiește promptul cu TOATE datele:

prompt = f"""
Scrie o declarație pentru călătoria minorului conform datelor:

DATE EXTRACTE DIN ACTE:
- Minor: {nume_copil}, născut(ă) la {data_nastere_copil}
- Părinte care dă acordul: {nume_parinte}, CNP: {cnp_parinte}

DETALII CĂLĂTORIE (completate de notar):
- Destinație: {destinatie}
- Perioadă: {perioada_start} - {perioada_sfarsit}  
- Însoțitor: {nume_insotitor}
- Scop: {scop_calatorie}
- Mijloc transport: {mijloc_transport}
- Țări tranzit: {tari_tranzit}

Cerințe: [textul actului...]
"""