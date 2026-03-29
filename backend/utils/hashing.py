import hashlib

def hash_input(text: str) -> str:
    return hashlib.sha256(text.lower().strip().encode()).hexdigest()