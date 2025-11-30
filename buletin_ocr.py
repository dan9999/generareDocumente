"""
Extractor de date din buletine românești folosind OCR
Necesită: pip install pytesseract Pillow opencv-python
Pentru Windows: descarcă Tesseract de la https://github.com/UB-Mannheim/tesseract/wiki
"""

import pytesseract
from PIL import Image
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

    def preproceseaza_imagine(self,cale_buletin):
        img = cv2.imread(cale_buletin)
        height, width = img.shape[:2]

        # Dacă imaginea e mică, upscale și procesare agresivă
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

        # Dacă imaginea e deja mare, preprocesare simplă
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        denoised = cv2.fastNlMeansDenoising(thresh)
        return denoised

    def extrage_text_ocr(self, cale_imagine):
        """Extrage text din imagine folosind Tesseract OCR"""
        try:
            # Preprocessare imagine
            img_procesata = self.preproceseaza_imagine(cale_imagine)

            # Extrage text cu configurare pentru limba română
            config = '--oem 3 --psm 6 -l ron+eng'
            text = pytesseract.image_to_string(img_procesata, config=config)

            return text
        except Exception as e:
            print(f"Eroare la OCR: {e}")
            return ""

    def extrage_cnp(self, text):
        """
        Extrage CNP din linia MRZ (cea mai sigură metodă).
        MRZ linia 2 (format CI România):
        PFFFFF<1ROUYYYYMMDDCEXPDDMMYYY...
        """
        # găsește linia MRZ cu 30–36 caractere
        lines = text.splitlines()
        mrz = None
        for l in lines:
            l_stripped = l.strip().replace(" ", "")
            if len(l_stripped) in range(30, 37):
                mrz = l_stripped
                break

        if mrz:
            # caută secvența ROU + CNP 13 cifre aproximat
            m = re.search(r'R[O0]U([0-9]{13})', mrz)
            if m:
                return m.group(1)

        # fallback: pattern direct 13 cifre
        m = re.search(r'\b[1-8]\d{12}\b', text)
        return m.group(0) if m else None

    def extrage_nume(self, text):
        """Extrage numele din zona MRZ mai robust"""
        mrz_match = re.search(r'IDR[O0]U([A-Z<]+)<<', text)
        if mrz_match:
            raw = mrz_match.group(1)
            # Înlocuiește < cu spațiu și curăță eventualele caractere nealfabetice
            nume = re.sub(r'[^A-ZĂÂÎȘȚ\s]', '', raw.replace('<', ' ')).strip()
            # Ia doar primul segment (nume de familie)
            nume = nume.split()[0] if nume else None
            return nume
        return None

    def extrage_prenume(self, text):
        """Extrage prenumele din MRZ mai robust, fără să returneze None din cauza artefactelor OCR"""
        # Caută zona MRZ a prenumelor după << (după nume de familie)
        mrz_match = re.search(r'<<([A-Z<]+)', text)
        if mrz_match:
            raw = mrz_match.group(1)
            # Înlocuiește toate < cu spațiu
            raw = raw.replace('<', ' ')
            # Curăță caractere nealfabetice generate de OCR
            raw = re.sub(r'[^A-ZĂÂÎȘȚ\s]', '', raw)
            # Împarte la spații și elimină cuvintele goale
            parts = [p.strip() for p in raw.split() if p.strip()]
            # Returnează prenumele concatenate
            if parts:
                return ' '.join(parts)
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
        """
        Extrage seria și numărul buletinului din text,
        ignorând eventuale erori OCR precum 'np'.
        """
        # caută pattern: 2 litere + orice text + 6 cifre
        match = re.search(r'\b([A-Z]{2})\s*\w*\s*(\d{6})\b', text, re.IGNORECASE)
        if match:
            serie = match.group(1).upper()
            numar = match.group(2)
            return f"{serie} {numar}"

        # fallback MRZ: prima literă + cifra/litera + 6 cifre
        match_mrz = re.search(r'\b([A-Z])[0-9A-Z]?(\d{6})<', text)
        if match_mrz:
            serie = match_mrz.group(1)
            numar = match_mrz.group(2)
            return f"{serie} {numar}"

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
        img = Image.open(cale_buletin)
        # Afișează rezultatele
        print("\n=== REZOLUTIE ===")
        print(f"Rezoluția imaginii: {img.width} x {img.height} pixeli")
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
