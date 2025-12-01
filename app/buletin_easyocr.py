"""
Extractor de date din buletine românești folosind EasyOCR
Necesită: pip install easyocr Pillow opencv-python numpy
"""

import easyocr
from PIL import Image
import cv2
import re
import json
from datetime import datetime
import numpy as np


class BuletinExtractor:
    def __init__(self):
        self.date_extrase = {}
        self.reader = easyocr.Reader(['ro', 'en'], gpu=False)

    def preproceseaza_imagine(self, cale_buletin):
        img = cv2.imread(cale_buletin)
        height, width = img.shape[:2]

        if width < 2500 or height < 2000:
            img = cv2.resize(img, None, fx=1.7, fy=1.7, interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.convertScaleAbs(gray, alpha=1.6, beta=10)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)

        thresh = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31, 10
        )

        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        sharp = cv2.filter2D(thresh, -1, kernel)
        return sharp

    def extrage_text_ocr(self, cale_imagine):
        try:
            img_procesata = self.preproceseaza_imagine(cale_imagine)
            img_rgb = cv2.cvtColor(img_procesata, cv2.COLOR_GRAY2RGB)
            rezultat = self.reader.readtext(img_rgb, detail=0)
            text = '\n'.join(rezultat)
            return text
        except Exception as e:
            print(f"Eroare la OCR: {e}")
            return ""

    def extrage_cnp(self, text):
        lines = text.splitlines()
        mrz = None
        for l in lines:
            l_stripped = l.strip().replace(" ", "")
            if len(l_stripped) in range(30, 37):
                mrz = l_stripped
                break
        if mrz:
            m = re.search(r'R[O0]U([0-9]{13})', mrz)
            if m:
                return m.group(1)
        m = re.search(r'\b[1-8]\d{12}\b', text)
        return m.group(0) if m else None

    def extrage_nume_prenume(self, text):
        """
        Extrage numele și prenumele din MRZ, cu fallback pe textul explicit.
        Returnează tuple: (nume, prenume)
        """
        # Încearcă MRZ
        mrz_match = re.search(r'ROU([A-Z<]+)<<', text.replace(" ", "").replace("#", ""))
        if mrz_match:
            raw = mrz_match.group(1)
            raw = raw.replace('<', ' ')
            raw = re.sub(r'[^A-ZĂÂÎȘȚ\s-]', '', raw)
            parts = [p for p in raw.split() if p.strip()]
            if len(parts) >= 2:
                nume = parts[0]
                prenume = ' '.join(parts[1:])
                return nume, prenume
            elif parts:
                return parts[0], None

        # Fallback: caută în liniile explicite de pe buletin
        lines = text.splitlines()
        nume = prenume = None
        for i, line in enumerate(lines):
            line_clean = line.strip()
            if "NumelNomlLast name" in line_clean and i + 1 < len(lines):
                nume_line = lines[i + 1].strip()
                nume_line = re.sub(r'[^A-ZĂÂÎȘȚ\s-]', '', nume_line)
                nume = nume_line
            if "PrenumelPrenomlFirst name" in line_clean and i + 1 < len(lines):
                prenume_line = lines[i + 1].strip()
                prenume_line = re.sub(r'[^A-ZĂÂÎȘȚ\s-]', '', prenume_line)
                prenume = prenume_line

        return nume, prenume

    def extrage_loc_nastere(self, text: str) -> str | None:
        lines = text.splitlines()

        for i, line in enumerate(lines):
            l = line.lower()

            if 'loc' not in l:
                continue

            if ('naște' in l or 'naste' in l or 'nașter' in l or 'nastc' in l) or \
                    ('lieu' in l and 'naiss' in l) or \
                    ('place' in l and 'birth' in l):

                location_parts = []

                for j in range(1, 5):
                    if i + j >= len(lines):
                        break

                    candidate_line = lines[i + j]
                    candidate_lower = candidate_line.lower().strip()

                    # Verificare SIMPLĂ - dacă începe cu "dom" sau "adr"
                    if candidate_lower.startswith(('dom', 'adr', 'cnp', 'ser')):
                        break

                    candidate_clean = candidate_line.strip()
                    if len(candidate_clean) > 2:
                        candidate = re.sub(r'[^a-zA-Z0-9ăâîșțĂÂÎȘȚ\s.,-]', '', candidate_clean)
                        candidate = re.sub(r'\s+', ' ', candidate).strip()

                        if len(candidate) > 2:
                            location_parts.append(candidate)

                if location_parts:
                    return " ".join(location_parts)

        return None

    def extrage_domiciliu(self, text):
        """
        Extrage adresa de domiciliu - varianta robustă pentru OCR corupt.
        """
        lines = text.splitlines()

        for i, line in enumerate(lines):
            line_lower = line.lower().replace(' ', '')

            # Verifică doar primele caractere pentru a detecta variante corupte
            if line_lower.startswith(('dom', 'adr')):
                rezultate = []

                # Colectează următoarele 4-5 linii (adresa poate fi mai lungă)
                for k in range(1, 6):
                    if i + k >= len(lines):
                        break

                    candidate_line = lines[i + k].strip()
                    candidate_lower = candidate_line.lower()

                    # Oprim dacă apare următorul câmp
                    if any(stop_word in candidate_lower for stop_word in
                           ['emisa', 'delivree', 'issued', 'valabil', 'valid', 'cnp', 'serie']):
                        break

                    if candidate_line:
                        clean_line = re.sub(r'[^A-Za-z0-9ĂÂÎȘȚăâîșț\s\.,/-]', '', candidate_line).strip()
                        if clean_line and len(clean_line) > 2:
                            rezultate.append(clean_line)

                if rezultate:
                    return ", ".join(rezultate)

        return None

    def extrage_data_nastere(self, cnp):
        if not cnp or len(cnp) != 13:
            return None
        try:
            an = int(cnp[1:3])
            luna = int(cnp[3:5])
            zi = int(cnp[5:7])
            sex = int(cnp[0])
            if sex in [1, 2]:
                an += 1900
            elif sex in [3, 4]:
                an += 1800
            elif sex in [5, 6]:
                an += 2000
            return f"{zi:02d}.{luna:02d}.{an}"
        except:
            return None

    def extrage_serie_numar(self, text):
        match = re.search(r'\b([A-Z]{2})\s*\w*\s*(\d{6})\b', text, re.IGNORECASE)
        if match:
            serie = match.group(1).upper()
            numar = match.group(2)
            return f"{serie} {numar}"
        match_mrz = re.search(r'\b([A-Z])[0-9A-Z]?(\d{6})<', text)
        if match_mrz:
            serie = match_mrz.group(1)
            numar = match_mrz.group(2)
            return f"{serie} {numar}"
        return None

    def valideaza_cnp(self, cnp):
        if not cnp or len(cnp) != 13 or not cnp.isdigit():
            return False
        key = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]
        suma = sum(int(cnp[i]) * key[i] for i in range(12))
        rest = suma % 11
        cifra_control = 1 if rest == 10 else rest
        if int(cnp[12]) != cifra_control:
            return False
        luna = int(cnp[3:5])
        zi = int(cnp[5:7])
        return 1 <= luna <= 12 and 1 <= zi <= 31

    def calculeaza_varsta(self, data_nastere):
        try:
            zi, luna, an = map(int, data_nastere.split('.'))
            data_n = datetime(an, luna, zi)
            azi = datetime.now()
            varsta = azi.year - data_n.year - ((azi.month, azi.day) < (data_n.month, data_n.day))
            return varsta
        except:
            return None

    def extrage_emisa_si_ladata(self, text: str) -> tuple[str | None, str | None]:
        lines = text.splitlines()
        emisa = None
        ladata = None

        # Cuvinte cheie pentru "emisă" - variante corecte și corupte
        emis_keywords = ['emis', 'deliv', 'issu', 'deli', 'em}', 'em', 'emi', 'ems', 'detdeli']

        # Cuvinte cheie pentru "valabilitate" - variante corecte și corupte
        valab_keywords = ['valab', 'valid', 'vulab', 'valb', 'vlab', 'vlid', 'valldito', 'valldlty']

        for i, line in enumerate(lines):
            line_lower = line.lower().strip()

            # Verifică doar pentru cuvinte de "emisă" (nu și pentru valabilitate)
            found_emis_keyword = any(keyword in line_lower for keyword in emis_keywords)

            if found_emis_keyword:
                print(f"DEBUG: Found emis keyword in line {i}: {line}")

                # Caută în următoarele 2-4 linii
                for j in range(1, 5):
                    if i + j >= len(lines):
                        break

                    candidate_line = lines[i + j].strip()
                    if not candidate_line:
                        continue

                    print(f"DEBUG: Checking line {i + j}: {candidate_line}")

                    # Verifică dacă e dată (prioritate 1)
                    if not ladata:
                        date_match = re.search(r'\b\d{1,2}\.\d{1,2}\.\d{2,4}\b', candidate_line)
                        if date_match:
                            ladata = date_match.group()
                            print(f"DEBUG: Found date: {ladata}")
                            continue

                    # Verifică dacă e autoritate emitentă (prioritate 2)
                    if not emisa:
                        # Exclude linii care conțin cuvinte de valabilitate sau alte cuvinte cheie
                        if (any(kw in candidate_line.lower() for kw in valab_keywords) or
                                any(kw in candidate_line.lower() for kw in emis_keywords) or
                                re.search(r'\b\d{1,2}\.\d{1,2}\.\d{2,4}\b', candidate_line) or
                                any(word in candidate_line.lower() for word in ['domiciliu', 'adres', 'address'])):
                            continue

                        # Dacă linia are cel puțin 3 caractere și arată ca text normal
                        if len(candidate_line) >= 3 and any(c.isalpha() for c in candidate_line):
                            # Curăță textul
                            clean_text = re.sub(r'[^a-zA-Z0-9ăâîșțĂÂÎȘȚ\s.,-]', '', candidate_line).strip()
                            if len(clean_text) >= 3:
                                emisa = clean_text
                                print(f"DEBUG: Found emisa: {emisa}")

        return emisa, ladata












    def proceseaza_buletin(self, cale_imagine):
        print(f"Procesez buletinul: {cale_imagine}")
        text_complet = self.extrage_text_ocr(cale_imagine)
        print("\n=== TEXT EXTRAS (pentru debug) ===")
        print(text_complet)
        print("=" * 50)

        cnp = self.extrage_cnp(text_complet)
        nume, prenume = self.extrage_nume_prenume(text_complet)
        loc_nastere = self.extrage_loc_nastere(text_complet)
        domiciliu = self.extrage_domiciliu(text_complet)

        # nume = self.extrage_nume(text_complet)
        # prenume = self.extrage_prenume(text_complet)
        serie_numar = self.extrage_serie_numar(text_complet)
        data_nastere = self.extrage_data_nastere(cnp) if cnp else None
        varsta = self.calculeaza_varsta(data_nastere) if data_nastere else None
        emisa, ladata = self.extrage_emisa_si_ladata(text_complet)

        cnp_valid = self.valideaza_cnp(cnp) if cnp else False

        self.date_extrase = {
            'nume': nume,
            'prenume': prenume,
            'loc_nastere': loc_nastere,
            'domiciliu': domiciliu,
            'cnp': cnp,
            'cnp_valid': cnp_valid,
            'data_nastere': data_nastere,
            'varsta': varsta,
            'serie_numar': serie_numar,
            'emisa' : emisa,
            'ladata': ladata,
            'text_complet': text_complet
        }

        return self.date_extrase

    def salveaza_txt(self, cale_output="date_buletin.txt"):
        with open(cale_output, 'w', encoding='utf-8') as f:
            f.write("=== DATE EXTRASE DIN BULETIN ===\n\n")
            f.write(f"Nume: {self.date_extrase.get('nume', 'N/A')}\n")
            f.write(f"Prenume: {self.date_extrase.get('prenume', 'N/A')}\n")
            f.write(f"Loc nastere: {self.date_extrase.get('loc_nastere', 'N/A')}\n")
            f.write(f"Domiciliu: {self.date_extrase.get('domiciliu', 'N/A')}\n")
            f.write(f"CNP: {self.date_extrase.get('cnp', 'N/A')}\n")
            f.write(f"CNP Valid: {'Da' if self.date_extrase.get('cnp_valid') else 'Nu'}\n")
            f.write(f"Data naștere: {self.date_extrase.get('data_nastere', 'N/A')}\n")
            f.write(f"Vârsta: {self.date_extrase.get('varsta', 'N/A')} ani\n")
            f.write(f"Emisa de: {self.date_extrase.get('emisa', 'N/A')} ani\n")
            f.write(f"La data: {self.date_extrase.get('ladata', 'N/A')} ani\n")
            f.write(f"Serie/Număr: {self.date_extrase.get('serie_numar', 'N/A')}\n")
            f.write(f"\n=== TEXT COMPLET EXTRAS ===\n")
            f.write(self.date_extrase.get('text_complet', ''))
        print(f"\n✓ Date salvate în: {cale_output}")

    def salveaza_json(self, cale_output="date_buletin.json"):
        date_export = {k: v for k, v in self.date_extrase.items() if k != 'text_complet'}
        with open(cale_output, 'w', encoding='utf-8') as f:
            json.dump(date_export, f, ensure_ascii=False, indent=2)
        print(f"✓ Date salvate în: {cale_output}")


# --- Exemplu de utilizare fara streamlit direct ca si script---
# if __name__ == "__main__":
#     extractor = BuletinExtractor()
#     cale_buletin = "C:/Users/Harry/Documents/Buletine/popescu.jpeg"  # sau .png/.jpeg
#
#     try:
#         date = extractor.proceseaza_buletin(cale_buletin)
#         img = Image.open(cale_buletin)
#         print("\n=== REZOLUTIE ===")
#         print(f"Rezoluția imaginii: {img.width} x {img.height} pixeli")
#         print("\n=== REZULTATE ===")
#         print(f"Nume: {date.get('nume', 'N/A')}")
#         print(f"Prenume: {date.get('prenume', 'N/A')}")
#         print(f"Loc nastere: {date.get('loc_nastere', 'N/A')}")
#         print(f"Domiciliu: {date.get('domiciliu', 'N/A')}")
#         print(f"CNP: {date.get('cnp', 'N/A')}")
#         print(f"CNP Valid: {'✓ Da' if date.get('cnp_valid') else '✗ Nu'}")
#         print(f"Data naștere: {date.get('data_nastere', 'N/A')}")
#         print(f"Vârsta: {date.get('varsta', 'N/A')} ani")
#         print(f"Emisa de: {date.get('emisa', 'N/A')}")
#         print(f"La data: {date.get('ladata', 'N/A')}")
#         print(f"Serie/Număr: {date.get('serie_numar', 'N/A')}")
#
#         extractor.salveaza_txt("date_buletin.txt")
#         extractor.salveaza_json("date_buletin.json")

    # except FileNotFoundError:
    #     print(f"⚠ Eroare: Fișierul '{cale_buletin}' nu a fost găsit!")
    #     print("Asigură-te că ai o imagine a buletinului în același folder cu scriptul.")
    # except Exception as e:
    #     print(f"⚠ Eroare: {e}")
