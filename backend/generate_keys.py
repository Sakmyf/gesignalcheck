# C:\Candado\backend\generate_keys.py
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path

out = Path(r"C:\Candado\backend")
out.mkdir(parents=True, exist_ok=True)

# 2048-bit RSA
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
private_pem = key.private_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PrivateFormat.PKCS8,  # moderno y portable
    encryption_algorithm=serialization.NoEncryption(),
)
public_pem = key.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

(out / "private.pem").write_bytes(private_pem)
(out / "public.pem").write_bytes(public_pem)

print("OK ->", out / "private.pem")
print("OK ->", out / "public.pem")
