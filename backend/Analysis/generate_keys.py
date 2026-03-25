# ======================================================
# SIGNALCHECK — KEY GENERATOR (PORTABLE VERSION)
# ======================================================

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from pathlib import Path


# --------------------------------------------------
# CONFIG
# --------------------------------------------------

OUTPUT_DIR = Path(__file__).parent  # mismo directorio del script


def generate_keys():

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # RSA 2048 (suficiente para este caso)
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )

    private_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    public_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    private_path = OUTPUT_DIR / "private.pem"
    public_path = OUTPUT_DIR / "public.pem"

    private_path.write_bytes(private_pem)
    public_path.write_bytes(public_pem)

    print("✔ Private key:", private_path)
    print("✔ Public key:", public_path)


# --------------------------------------------------
# EXEC
# --------------------------------------------------

if __name__ == "__main__":
    generate_keys()