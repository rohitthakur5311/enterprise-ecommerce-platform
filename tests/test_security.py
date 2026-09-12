from shared.security import hash_password, verify_password, create_access_token, decode_token

def test_password_hash_and_verify():
    password = "StrongPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong", hashed)

def test_access_token_roundtrip():
    token = create_access_token("42", "admin")
    payload = decode_token(token)
    assert payload["sub"] == "42"
    assert payload["role"] == "admin"
    assert payload["type"] == "access"
