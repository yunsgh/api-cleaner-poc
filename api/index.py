import json
import re
from http.server import BaseHTTPRequestHandler

# --- Cerveau V12 (Test "Canari") ---
# On ignore toute la logique de nettoyage.
# On renvoie juste une réponse test.

def smart_cleaner_fr(text: str) -> str:
    
    # ON NE FAIT RIEN, ON RETOURNE UN TEST
    return "TEST V12 OK"

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
                # Ça va appeler notre fonction test
                cleaned_text = smart_cleaner_fr(text_to_clean)
            else:
                cleaned_text = "TEST V12 NON-FR"

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
