from backend.utils.passwords import hash_password, verify_password

def test_hash_password():
    password = "StrongPassword123!"

    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password,password_hash) is True

def test_verify_password_rejects_wrong_password():
    password = "StrongPassword123!"
    wrong_password = "StrngPassword123!"
    password_hash = hash_password(password)

    assert verify_password(wrong_password, password_hash) is False

def test_salt_password():
    password = "String123"


    password_hash1 = hash_password(password)
    password_hash2 = hash_password(password)

    assert password_hash2 != password_hash1
    assert verify_password(password, password_hash1) == verify_password(password, password_hash2)