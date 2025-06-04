import hashlib
import sys

if len(sys.argv) < 2:
    print("Usage: enc_pswd password")
else:
    password = sys.argv[1]

    answer = hashlib.sha256(password.encode()).hexdigest()
    print(answer)
