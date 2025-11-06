import json
import re
from http.server import BaseHTTPRequestHandler

# --- Cerveau V4 (La méthode "brutale" qui marche) ---

def smart_cleaner_fr(text: str) -> str:
    
    # ÉTAPE 1: Remplacement "brutal"
    # On remplace TOUS les fillers par un simple ESPACE.
    
    # Mots bêtes (toujours mauvais)
    fillers_dumb = r'\b(euh|bah|ben|hein|bon|voilà|enfin|en fait|tu vois|genre|style)\b'
    cleaned_text = re.sub(fillers_dumb, ' ', text, flags=re.IGNORECASE)
    
    # Mots contextuels (mauvais au début ou après un point)
    context_fillers = r'(^|\.|\!|\?)\s*(donc|alors)\b'
    cleaned_text = re.sub(context_fillers, r'\1 ', cleaned_text, flags=re.IGNORECASE | re.MULTILINE)

    # --- ÉTAPE 2: LE NETTOYAGE FINAL (Chirurgical) ---
    
    # 2a. Corriger les "espace avant ponctuation" (ex: "mot ,")
    cleaned_text = re.sub(r'\s+([,\.])', r'\1', cleaned_text)
    
    # 2b. Corriger les "ponctuations multiples" (ex: ", ," ou ".,")
    cleaned_text = re.sub(r'[\s,]{2,}', ' ', cleaned_text)
    
    # 2c. Supprimer toute ponctuation ou espace au TOUT DÉBUT
    cleaned_text = re.sub(r'^[\s,]+', '', cleaned_text)

    # 2d. Corriger les doubles espaces
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    # 2e. Remettre une majuscule au début
    if cleaned_text:
        cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]

    return cleaned_text

# --- Le reste du serveur est identique ---

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data)
            text_to_clean = data.get('text')
            lang = data.get('lang')

            if not text_to_clean or not lang:
                self._send_error("Le 'text' et la 'lang' sont requis.", 400)
                return

            if lang == "fr":
                cleaned_text = smart_cleaner_fr(text_to_clean)
            else:
                cleaned_text = text_to_clean 

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {'cleaned_text': cleaned_text}
            self.wfile.write(json.dumps(response).encode('utf-8'))

        except Exception as e:
            self._send_error(f"Erreur serveur: {str(e)}", 500)

    def _send_error(self, message, code):
        self.send_response(code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'error': message}
        self.wfile.write(json.dumps(response).encode('utf-8'))
