import os
import requests
from flask import Flask, redirect, request, session, url_for, render_template
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # Cambia esto por algo más seguro
load_dotenv()

# Configuración de LinkedIn
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
API_URL = "https://api.linkedin.com/v2/adLibrary"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login')
def login():
    # Redirigir al usuario a la página de autenticación de LinkedIn
    params = {
        'response_type': 'code',
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': 'r_ads',  # Permiso necesario para acceder a la API de anuncios
    }
    auth_url = f"{AUTH_URL}?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=r_ads"
    return redirect(auth_url)

@app.route('/callback')
def callback():
    # Obtener el código de autorización de la URL
    code = request.args.get('code')
    
    # Intercambiar el código de autorización por un token de acceso
    token_data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    token_response = requests.post(TOKEN_URL, data=token_data)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    
    # Guardar el token de acceso en la sesión
    session['access_token'] = access_token
    
    return redirect(url_for('get_ad_data'))

@app.route('/get_ad_data')
def get_ad_data():
    access_token = session.get('access_token')
    
    if access_token:
        headers = {
            'Authorization': f'Bearer {access_token}',
        }
        # Realizar la solicitud a la API de LinkedIn Ad Library
        params = {'q': 'search', 'searchTerms': 'your_search_terms'}
        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code == 200:
            ad_data = response.json()
            return render_template('ad_data.html', ad_data=ad_data)
        else:
            return f"<h1>Error al obtener datos de anuncios: {response.status_code}</h1>"
    else:
        return '<h1>No se pudo autenticar al usuario.</h1>'

if __name__ == '__main__':
    app.run(debug=True)
