import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Load credentials from environment variable
firebase_config = json.loads(os.getenv("FIREBASE_CREDENTIALS"))

cred = credentials.Certificate(firebase_config)
firebase_admin.initialize_app(cred)

db = firestore.client()
