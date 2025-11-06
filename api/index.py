import json
import re
from http.server import BaseHTTPRequestHandler

# --- Cerveau V10 (Logique inverse) ---

def smart_cleaner_fr(text: str) -> str:
    
    # ÉTAPE 1: NETTOYAGE CHIRURGICAL (La nouvelle clé)
    # On chasse les virgules/espaces inutiles AVANT de supprimer les mots.
    
    # 1a. Remplace les "virgules multiples" (le bug ", ,") par une seule virgule + espace
    # C'est la ligne qui corrige le bug.
    cleaned_text = re.sub(r'[\s,]{2,}', ', ', text)
    
    # 1b. Supprime les "espaces avant" virgule ou point.
    cleaned_text = re.sub(r'\s+([,\.])', r'\1', cleaned_text)
    
    # 1c. Supprime toute ponctuation/espace au TOUT DÉBUT.
    cleaned_text = re.sub(r'^[\s,]+', '', cleaned_text)

    # ÉTAPE 2: Suppression des mots (Maintenant que c'est propre)
    
    # Mots bêtes (toujours mauvais) -> Remplacer par RIEN
    # On cible aussi la virgule/espace qui suit.
    fillers_dumb = r'\b(euh|bah|ben|hein|bon|voilà|enfin|en fait|tu vois|genre|style)\b[\s,]*'
    cleaned_text = re.sub(fillers_dumb, '', cleaned_text, flags=re.IGNORECASE)
    
    # Mots contextuels (mauvais au début ou après un point)
    context_fillers = r'(^|\.|\!|\?)\s*(donc|alors)\b[\s,]*'
    cleaned_text = re.sub(context_fillers, r'\1', cleaned_text, flags=re.IGNORECASE | re.MULTILINE)

    # ÉTAPE 3: Nettoyage final post-suppression
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    
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
