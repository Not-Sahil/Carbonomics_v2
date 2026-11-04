"""
Carbonomics v3 — JWT Authentication & RBAC Middleware
"""

import os
import datetime
from functools import wraps
from flask import request, jsonify
import jwt
from werkzeug.security import generate_password_hash, check_password_hash

JWT_SECRET = os.environ.get("JWT_SECRET", "carbonomics_enterprise_jwt_secret_2026_v3")
JWT_ALGORITHM = "HS256"


def create_token(user_id: int, username: str, role: str = "analyst") -> str:
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str):
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def get_current_user_payload():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    token = auth_header.split(" ")[1]
    return decode_token(token)


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = get_current_user_payload()
        if not payload:
            return jsonify({"error": "Authentication required", "code": "AUTH_REQUIRED"}), 401
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        payload = get_current_user_payload()
        if not payload or payload.get("role") != "admin":
            return jsonify({"error": "Admin privileges required", "code": "FORBIDDEN"}), 403
        return f(*args, **kwargs)
    return decorated
