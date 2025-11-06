import json
import re # On importe le "Cerveau Léger"
from http.server import BaseHTTPRequestHandler

# --- C'est notre nouveau "cerveau" (poids: 0 Ko) ---

def smart_cleaner_fr(text: str) -> str:
    # 1. Nettoyage BÊTE (les mots toujours inutiles)
    # On supprime les "euh", "bah", "ben", "en fait", etc.
    # \b = s'assure que c'est un mot entier (pas "bah" dans "baha")
    # re.IGNORECASE = ignore la majuscule/minuscule
    fillers = r'\b(euh|bah|ben|hein|bon|voilà|enfin|en fait|tu vois|genre|style)\b'
    cleaned_text = re.sub(fillers, '', text, flags=re.IGNORECASE)
    
    # 2. Nettoyage SMART (les mots contextuels)
    # On supprime "Donc," ou "Alors," en DÉBUT de phrase.
    # ^ = début de la chaîne
    # \s* = n'importe quel espace (ou pas)
    # ,? = une virgule optionnelle
    context_fillers_start = r'^\s*(donc|alors),?\s*'
    cleaned_text = re.sub(context_fillers_start, '', cleaned_text, count=1, flags=re.IGNORECASE)

    # 3. Nettoyage SMART (après un point)
    # On supprime "Donc," ou "Alors," après un point.
    # ([\.!?]) = capture le point/!/?
    # \s+ = au moins un espace
    # On remplace par le point + un espace (ex: ". Donc," -> ". ")
    context_fillers_mid = r'([\.!?])\s+(donc|alors),?\s*'
    cleaned_text = re.sub(context_fillers_mid, r'\1 ', cleaned_text, flags=re.IGNORECASE)

    # 4. Nettoyer les espaces doubles créés par la suppression
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
    # Nettoyer les doubles virgules ou virgules erronées
    cleaned_text = re.sub(r'\s*,\s*', ', ', cleaned_text)
    cleaned_text = re.sub(r'\s+\.', '.', cleaned_text)

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
                cleaned_text = text_to_clean # On ne gère que FR pour l'instant

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
