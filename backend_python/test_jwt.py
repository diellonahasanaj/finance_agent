#!/usr/bin/env python3
"""
Test JWT decode
"""
from app.utils.jwt import decode_access_token

def test_jwt():
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2OTlkNzJjYTJjYWFhN2Y1Yjg1NjVlZjEiLCJleHAiOjE3NzIwMjEyNTh9.Ekj4LDrImg1VZqeGJiRJBQC0OASM-9OfmZrr6DNDq9g"
    
    print(f"Testing token: {token}")
    payload = decode_access_token(token)
    print(f"Decoded payload: {payload}")
    
    if payload and "sub" in payload:
        print(f"User ID from token: {payload['sub']}")
    else:
        print("No sub in payload")

if __name__ == "__main__":
    test_jwt()
