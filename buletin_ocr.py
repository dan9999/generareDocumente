"""
Extractor de date din buletine românești folosind OCR
Necesită: pip install pytesseract Pillow opencv-python
Pentru Windows: descarcă Tesseract de la https://github.com/UB-Mannheim/tesseract/wiki
"""

import pytesseract
#from PIL import Image
import cv2
import re
import json
from datetime import datetime
import numpy as np

# Configurare path Tesseract (modifică în funcție de instalare)
# Windows:

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Linux/Mac: de obicei funcționează automat după instalare


class BuletinExtractor:
    def __init__(self):
        self.date_extrase = {}

    def preprocesseaza_imagine(self, cale_imagine):
        """Îmbunătățește imaginea pentru OCR mai bun"""
        # Citește imaginea
        img = cv2.imread(cale_imagine)

        # Convertește în grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Aplică threshold pentru contrast mai bun
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        # Reduce noise
        denoised = cv2.fastNlMeansDenoising(thresh)

        return denoised

    def extrage_text_ocr(self, cale_imagine):
        """Extrage text din imagine folosind Tesseract OCR"""
        try:
            # Preprocessare imagine
            img_procesata = self.preprocesseaza_imagine(cale_imagine)

            # Extrage text cu configurare pentru limba română
            config = '--oem 3 --psm 6 -l ron+eng'
            text = pytesseract.image_to_string(img_procesata, config=config)

            return text
        except Exception as e:
            print(f"Eroare la OCR: {e}")
            return ""

    def extrage_cnp(self, text):
        """Extrage CNP-ul din text"""
        # Caută în zona MRZ mai întâi (mai fiabil)
        # Format MRZ: 7409071M2809078 (după cod țară ROU)
        mrz_cnp_pattern = r'R[O0]U(\d{7})[MF](\d{6})'
        match = re.search(mrz_cnp_pattern, text)
        if match:
            # Reconstruiește CNP-ul complet (primele 7 + ultimele 6 cifre)
            cnp_partial = match.group(1) + match.group(2)
            # Caută CNP complet în text (13 cifre)
            full_cnp_pattern = r'\b[1-8]' + cnp_partial[:5] + r'\d{7}\b'
            full_match = re.search(full_cnp_pattern, text)
            if full_match:
                return full_match.group(0)

        # Fallback: caută pattern de 13 cifre direct
        pattern = r'\b[1-8]\d{12}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else None

    def extrage_nume(self, text):
        """Extrage numele din text sau din zona MRZ"""
        # Prioritate 1: Extrage din zona MRZ (Machine Readable Zone) - CEL MAI FIABIL!
        # Format MRZ: IDROUOPREA<<DAN<KHARRY
        mrz_pattern = r'IDR[O0]U([A-Z]+)<<'
        match = re.search(mrz_pattern, text)
        if match:
            nume = match.group(1).strip()
            # Verifică că nu e prea scurt (minim 2 caractere)
            if len(nume) >= 2:
                return nume

        # Prioritate 2: Caută pattern alternativ în MRZ
        # Uneori apare ca: TDROUOPREA<<
        mrz_alt = r'[TI]DR[O0]U([A-Z]{3,})<<'
        match = re.search(mrz_alt, text)
        if match:
            return match.group(1).strip()

        # Fallback: caută după cuvinte cheie în text normal (MAI PUȚIN FIABIL)
        patterns = [
            r'Last\s+name[:\s]+([A-ZĂÂÎȘȚ]{3,})',
            r'Nume[:/\s]+([A-ZĂÂÎȘȚ]{3,})',
            r'NUME[:/\s]+([A-ZĂÂÎȘȚ]{3,})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                # Exclude cuvinte comune (Nom, Name, etc)
                nume = match.group(1).strip()
                if nume not in ['NOM', 'NAME', 'LAST', 'NUME']:
                    return nume
        return None

    def extrage_prenume(self, text):
        """Extrage prenumele din text sau din zona MRZ"""
        # Încearcă să extragă din zona MRZ (Machine Readable Zone)
        # Format MRZ: IDROUOPREA<<DAN<KHARRY sau OPREA<<DAN<HARRY
        mrz_pattern = r'<<([A-Z]+)<+([A-Z]+)'
        match = re.search(mrz_pattern, text)
        if match:
            # Returnează primul prenume și al doilea (dacă există)
            prenume1 = match.group(1).strip()
            prenume2 = match.group(2).strip() if match.group(2) else ''
            return f"{prenume1} {prenume2}".strip()

        # Fallback: caută după cuvinte cheie
        patterns = [
            r'Prenume[:/\s]+([A-ZĂÂÎȘȚ\s]+?)(?=\n|Nationalit|Data)',
            r'PRENUME[:/\s]+([A-ZĂÂÎȘȚ\s]+?)(?=\n|NATIONALIT|DATA)',
            r'First\s+name[:\s]+([A-ZĂÂÎȘȚ\s]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def extrage_data_nastere(self, cnp):
        """Extrage data nașterii din CNP"""
        if not cnp or len(cnp) != 13:
            return None

        try:
            an = int(cnp[1:3])
            luna = int(cnp[3:5])
            zi = int(cnp[5:7])

            # Determină secolul
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
        """Extrage seria și numărul buletinului"""
        # Prioritate 1: Caută în linia cu SERIA și numărul
        # Ex: "RK Nn 187008" sau "RK 187008"
        seria_pattern = r'\bSERIA.*?([A-Z]{2})\s*[Nn]*\s*(\d{6})'
        match = re.search(seria_pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)} {match.group(2)}"

        # Prioritate 2: Caută în zona MRZ
        # Format: R8K187008 sau similar (linia a doua MRZ)
        mrz_pattern = r'\b([A-Z])[\s]*([0-9][A-Z0-9])\s*(\d{6})<'
        match = re.search(mrz_pattern, text)
        if match:
            serie = match.group(1) + match.group(2).replace(' ', '')
            numar = match.group(3)
            return f"{serie} {numar}"

        # Fallback: Pattern standard (2-3 litere + 6 cifre)
        pattern = r'\b([A-Z]{2,3})\s*(\d{6})\b'
        match = re.search(pattern, text)
        if match:
            return f"{match.group(1)} {match.group(2)}"
        return None

    def valideaza_cnp(self, cnp):
        """Validează CNP-ul folosind algoritmul de control"""
        if not cnp or len(cnp) != 13:
            return False

        try:
            # Verifică că sunt toate cifre
            if not cnp.isdigit():
                return False

            # Cheia de validare
            key = [2, 7, 9, 1, 4, 6, 3, 5, 8, 2, 7, 9]

            # Calculează suma
            suma = sum(int(cnp[i]) * key[i] for i in range(12))
            rest = suma % 11

            # Cifra de control
            cifra_control = 1 if rest == 10 else rest

            # Validează ultima cifră
            valid = int(cnp[12]) == cifra_control

            # Validare suplimentară: verifică luna și ziua
            luna = int(cnp[3:5])
            zi = int(cnp[5:7])

            if not (1 <= luna <= 12 and 1 <= zi <= 31):
                return False

            return valid
        except:
            return False

    def calculeaza_varsta(self, data_nastere):
        """Calculează vârsta din data nașterii"""
        try:
            zi, luna, an = map(int, data_nastere.split('.'))
            data_n = datetime(an, luna, zi)
            azi = datetime.now()
            varsta = azi.year - data_n.year - ((azi.month, azi.day) < (data_n.month, data_n.day))
            return varsta
        except:
            return None

    def proceseaza_buletin(self, cale_imagine):
        """Procesează imaginea buletinului și extrage toate datele"""
        print(f"Procesez buletinul: {cale_imagine}")

        # Extrage text
        text_complet = self.extrage_text_ocr(cale_imagine)
        print("\n=== TEXT EXTRAS (pentru debug) ===")
        print(text_complet)
        print("=" * 50)

        # Extrage date
        cnp = self.extrage_cnp(text_complet)
        nume = self.extrage_nume(text_complet)
        prenume = self.extrage_prenume(text_complet)
        serie_numar = self.extrage_serie_numar(text_complet)

        # Extrage data nașterii din CNP
        data_nastere = self.extrage_data_nastere(cnp) if cnp else None
        varsta = self.calculeaza_varsta(data_nastere) if data_nastere else None

        # Validează CNP
        cnp_valid = self.valideaza_cnp(cnp) if cnp else False

        self.date_extrase = {
            'nume': nume,
            'prenume': prenume,
            'cnp': cnp,
            'cnp_valid': cnp_valid,
            'data_nastere': data_nastere,
            'varsta': varsta,
            'serie_numar': serie_numar,
            'text_complet': text_complet
        }

        return self.date_extrase

    def salveaza_txt(self, cale_output="date_buletin.txt"):
        """Salvează datele extrase într-un fișier text"""
        with open(cale_output, 'w', encoding='utf-8') as f:
            f.write("=== DATE EXTRASE DIN BULETIN ===\n\n")
            f.write(f"Nume: {self.date_extrase.get('nume', 'N/A')}\n")
            f.write(f"Prenume: {self.date_extrase.get('prenume', 'N/A')}\n")
            f.write(f"CNP: {self.date_extrase.get('cnp', 'N/A')}\n")
            f.write(f"CNP Valid: {'Da' if self.date_extrase.get('cnp_valid') else 'Nu'}\n")
            f.write(f"Data naștere: {self.date_extrase.get('data_nastere', 'N/A')}\n")
            f.write(f"Vârsta: {self.date_extrase.get('varsta', 'N/A')} ani\n")
            f.write(f"Serie/Număr: {self.date_extrase.get('serie_numar', 'N/A')}\n")
            f.write(f"\n=== TEXT COMPLET EXTRAS ===\n")
            f.write(self.date_extrase.get('text_complet', ''))

        print(f"\n✓ Date salvate în: {cale_output}")

    def salveaza_json(self, cale_output="date_buletin.json"):
        """Salvează datele extrase în format JSON"""
        date_export = {k: v for k, v in self.date_extrase.items() if k != 'text_complet'}

        with open(cale_output, 'w', encoding='utf-8') as f:
            json.dump(date_export, f, ensure_ascii=False, indent=2)

        print(f"✓ Date salvate în: {cale_output}")


# Exemplu de utilizare
if __name__ == "__main__":
    # Inițializează extractorul
    extractor = BuletinExtractor()

    # Modifică cu calea către imaginea ta
    cale_buletin = "C:/Users/Harry/Documents/Buletine/CI_Oprea_Dan.jpg"  # sau .png, .jpeg

    try:
        # Procesează buletinul
        date = extractor.proceseaza_buletin(cale_buletin)

        # Afișează rezultatele
        print("\n=== REZULTATE ===")
        print(f"Nume: {date.get('nume', 'N/A')}")
        print(f"Prenume: {date.get('prenume', 'N/A')}")
        print(f"CNP: {date.get('cnp', 'N/A')}")
        print(f"CNP Valid: {'✓ Da' if date.get('cnp_valid') else '✗ Nu'}")
        print(f"Data naștere: {date.get('data_nastere', 'N/A')}")
        print(f"Vârsta: {date.get('varsta', 'N/A')} ani")
        print(f"Serie/Număr: {date.get('serie_numar', 'N/A')}")

        # Salvează rezultatele
        extractor.salveaza_txt("date_buletin.txt")
        extractor.salveaza_json("date_buletin.json")

    except FileNotFoundError:
        print(f"⚠ Eroare: Fișierul '{cale_buletin}' nu a fost găsit!")
        print("Asigură-te că ai o imagine a buletinului în același folder cu scriptul.")
    except Exception as e:
        print(f"⚠ Eroare: {e}")
