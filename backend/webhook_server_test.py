"""
Serveur webhook local pour tester les webhooks
Lance un serveur Flask sur http://localhost:5001/webhook
"""
from flask import Flask, request, jsonify
import hmac
import hashlib
import json
from datetime import datetime

app = Flask(__name__)

# Secret de l'entreprise de test (depuis la DB)
WEBHOOK_SECRET = "whsec_LQ07yMxTpeFOMh9x_LeK6WnYos5Eo2igJ8BQuGQ_L44"

received_webhooks = []


def verify_signature(payload, signature):
    """Vérifie la signature HMAC du webhook"""
    payload_str = json.dumps(payload, sort_keys=True)
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)


@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint webhook"""
    signature = request.headers.get('X-Webhook-Signature')
    payload = request.json
    
    print("\n" + "="*60)
    print(f"Webhook recu a {datetime.now().strftime('%H:%M:%S')}")
    print("="*60)
    print(f"Event: {payload.get('event')}")
    print(f"Verification ID: {payload.get('verification_id')}")
    print(f"Status: {payload.get('status')}")
    print(f"Signature: {signature[:20]}..." if signature else "Pas de signature")
    
    # Vérifier signature
    if signature and verify_signature(payload, signature):
        print("Signature: VALIDE")
        received_webhooks.append({
            'timestamp': datetime.now().isoformat(),
            'payload': payload,
            'signature_valid': True
        })
        return jsonify({'status': 'ok', 'message': 'Webhook received'}), 200
    else:
        print("Signature: INVALIDE")
        received_webhooks.append({
            'timestamp': datetime.now().isoformat(),
            'payload': payload,
            'signature_valid': False
        })
        return jsonify({'error': 'Invalid signature'}), 401


@app.route('/webhooks', methods=['GET'])
def list_webhooks():
    """Liste tous les webhooks reçus"""
    return jsonify({
        'count': len(received_webhooks),
        'webhooks': received_webhooks
    })


@app.route('/', methods=['GET'])
def home():
    """Page d'accueil"""
    return f"""
    <html>
    <head><title>Webhook Test Server</title></head>
    <body style="font-family: Arial; padding: 20px;">
        <h1>Serveur Webhook Test</h1>
        <p><strong>Endpoint:</strong> <code>http://localhost:5001/webhook</code></p>
        <p><strong>Webhooks recus:</strong> {len(received_webhooks)}</p>
        <p><a href="/webhooks">Voir tous les webhooks</a></p>
        <hr>
        <h3>Configuration entreprise:</h3>
        <pre>webhook_url = "http://localhost:5001/webhook"</pre>
    </body>
    </html>
    """


if __name__ == '__main__':
    print("\n" + "="*60)
    print("Serveur Webhook Test")
    print("="*60)
    print("\nEndpoint: http://localhost:5001/webhook")
    print("Dashboard: http://localhost:5001")
    print("\nEn attente de webhooks...")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5001, debug=False)
