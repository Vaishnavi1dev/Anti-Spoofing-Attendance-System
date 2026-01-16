#!/usr/bin/env python3
"""
Generate a secure JWT secret key for deployment
"""
import secrets

# Generate a secure random key (32 bytes = 64 hex characters)
jwt_secret = secrets.token_hex(32)

print("=" * 70)
print("🔐 JWT SECRET KEY GENERATED")
print("=" * 70)
print("\nCopy this key and use it as JWT_SECRET_KEY environment variable:")
print("\n" + jwt_secret)
print("\n" + "=" * 70)
print("\n⚠️  IMPORTANT: Keep this secret! Don't commit it to Git!")
print("=" * 70)
