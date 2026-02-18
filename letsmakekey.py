# generate_rsa_keys_print.py
from Crypto.PublicKey import RSA

code = "nooneknows"  # 비밀키 보호용 패스프레이즈
key = RSA.generate(2048)

# 비밀키(PKCS8 + scryptAndAES128-CBC)
private_key_pem = key.export_key(
    passphrase=code,
    pkcs=8,
    protection="scryptAndAES128-CBC",
)

# 공개키
public_key_pem = key.publickey().export_key()

print("PRIVATE_KEY_PEM = b'''")
print(private_key_pem.decode("utf-8").strip())
print("'''")
print()
print("PUBLIC_KEY_PEM = b'''")
print(public_key_pem.decode("utf-8").strip())
print("'''")
