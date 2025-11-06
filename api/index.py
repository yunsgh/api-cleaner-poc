import spacy
from http.server import BaseHTTPRequestHandler
import json

# Charger le modèle IA (léger) pour le français au démarrage
nlp = spacy.load("fr_core_news_sm")
print("Modèle 'fr' chargé.")
# Tu peux ajouter ici les autres modèles (en, es) si tu veux les supporter

# Définir nos listes de mots
FILLER_WORDS_FR = {"euh", "bah", "ben", "hein", "bon", "voilà", "enfin", "en fait"}
CONTEXT_WORDS_FR = {"donc", "alors", "genre"}

def smart_cleaner_fr(text: str) -> str:
    """
    Le "Nettoyeur Sémantique Contextuel".
    """
    doc = nlp(text)
    cleaned_tokens = []
    
    for token in doc:
        # 1. Nettoyage BÊTE
        if token.text.lower() in FILLER_WORDS_FR:
            continue

        # 2. Nettoyage SMART (Contextuel)
        if token.text.lower() in CONTEXT_WORDS_FR:
            # RÈGLE : Si "donc" est un ADVERBE (ADV) au début ou après ponctuation
            if (token.i == 0 or doc[token.i - 1].is_punct) and token.pos_ == "ADV":
                continue # C'est du remplissage, on saute

        cleaned_tokens.append(token.text_with_ws)

    return "".join(cleaned_tokens).strip()

# --- C'est la partie "Serveur" de Vercel ---
# Elle gère les requêtes web

class handler(BaseHTTPRequestHandler):
    
    def do_POST(self):
        # 1. Lire la requête du client
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            # On attend un JSON comme : {"text": "...", "lang": "fr"}
            data = json.loads(post_data)
            text_to_clean = data.get('text')
            lang = data.get('lang')

            if not text_to_clean or not lang:
                self._send_error("Le 'text' et la 'lang' sont requis.", 400)
                return

            # 2. Appeler notre "Cerveau"
            if lang == "fr":
                cleaned_text = smart_cleaner_fr(text_to_clean)
            else:
                # Pour l'instant, on ne gère que le FR
                # On renverra le texte original pour les autres langues
                cleaned_text = text_to_clean 

            # 3. Renvoyer la réponse (succès)
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
