import json
import re # On importe le "Cerveau Léger"
from http.server import BaseHTTPRequestHandler

# --- Cerveau V3 (Avec "Nettoyage Chirurgical") ---

def smart_cleaner_fr(text: str) -> str:
    
    # ÉTAPE 1: Nettoyage BÊTE (les mots toujours inutiles)
    # On cible le mot ET l'espace qui le suit
    fillers = r'\b(euh|bah|ben|hein|bon|voilà|enfin|en fait|tu vois|genre|style)\b[\s,]*'
    cleaned_text = re.sub(fillers, '', text, flags=re.IGNORECASE)
    
    # ÉTAPE 2: Nettoyage SMART (Contextuel)
    # On supprime "Donc," ou "Alors," en DÉBUT de phrase
    context_fillers_start = r'^\s*(donc|alors)[\s,]+'
    cleaned_text = re.sub(context_fillers_start, '', cleaned_text, count=1, flags=re.IGNORECASE | re.MULTILINE)

    # On supprime "Donc," ou "Alors," après un point.
    context_fillers_mid = r'([\.!?])\s+(donc|alors)[\s,]+'
    cleaned_text = re.sub(context_fillers_mid, r'\1 ', cleaned_text, flags=re.IGNORECASE)

    # --- ÉTAPE 3: LE NETTOYAGE FINAL (Le plus important) ---
    
    # 3a. Supprimer les virgules/espaces laissés au tout début
    cleaned_text = re.sub(r'^[\s,]+', '', cleaned_text)
    
    # 3b. Corriger les doubles virgules ou virgules/espaces (ex: " , ,")
    cleaned_text = re.sub(r'[\s,]{2,}', ' ', cleaned_text) # Remplace " , , " par " "
    
    # 3c. Corriger les "espace avant virgule" (ex: " mot , mot")
    cleaned_text = re.sub(r'\s+,', ',', cleaned_text)
    
    # 3d. Corriger les "espace avant point" (ex: " mot .")
    cleaned_text = re.sub(r'\s+\.', '.', cleaned_text)

    # 3e. Remettre un "capital" au début si on l'a supprimé
    if cleaned_text:
        cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]

    return cleaned_text.strip()

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
