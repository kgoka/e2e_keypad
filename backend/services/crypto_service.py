# backend/services/crypto_service.py
import json
from base64 import b64decode

from Crypto.Cipher import PKCS1_OAEP
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

PASSPHRASE = "nooneknows"

PRIVATE_KEY_PEM = b"""-----BEGIN ENCRYPTED PRIVATE KEY-----
...MIIFJTBPBgkqhkiG9w0BBQ0wQjAhBgkrBgEEAdpHBAswFAQI5axcVzNv4YgCAkAA
AgEIAgEBMB0GCWCGSAFlAwQBAgQQMP6RoA2oedjVObsrdYZiFQSCBNC+7zFN42pr
6Tv962cDr6beaZzGQ9odbuyoyet75nkqf38Cu4jFxQ/H7wG/zeprVlivJxCOoImd
fvlnFwBhz4m4MoIyKxncyOueLMN7fcdRFY+kyOFBP1aNstCFb4oOEE7cs8dKV+4G
VFKeK3qqd7p2tzFhB59wvzAkEvHG3EliLoTb+aZBztnRS/3PbBdkC5n4BOCe/xfT
+INRHgpgtdhU4/+hAe9HiYPm1qROTv8z2m3umjB6dMFD3Q9X6GuQORnjMWvVgrgS
XBWD+VAmU5ljUz96+a8wlNo9nb8bHluiDVYcU/y4p3iiHWpBGrhYMDRXFihond/e
pF1sczSdRvKRiDjKJTnZUQfl4dGlD0fGAtrjPnDUoBZYy8XI/3hwLMRLiViQCpys
YZH6ACWpxjizAZX8FmlvcMjoYtqtHc/xAnItzBm02pVdKUtSEPE+i1tK/tKtBTuC
F4KaMzoHb6E7LIF+CyCVHPiEfDtl8P6yVf3mRXbeT4ABFDgDav1628BJSnDzjyCb
PRzi6X/YzkZd9PrjhSWOwg5B34kYhrdF5YY30FKIfG4w+OSAHTIwJd13F0i/1sgg
wB1VPp1Fyo4Lcy+Tk4m558D4AIZCFi3Onsrdl9gzaPpJW7eRozJ7GzyJttslmSLI
TC/ucgZov6X1zIoqIMItMGXe3syjJk4VGGVZuPxeWtzDRUUPRZEmAmKmmseMUSSu
SbSkzR/mxB89Sj8UHHKRLG0lK5IsX61QGRzsgFTVJpSnxm9QFx5mqkUbtwGRQSft
Fu8jc/il6vzyv60zpXVLDBRmwAuUXw0kjW/pxtG6LIvBkJtPy1SYzujj53WfgzCG
nFqmh1l4jm/trwYG1TRisOaMoDIG9BBea72epku8Qsr9Vk11Y1iUkpCqllsNnFcv
NKZclYAXEMGh13vUd5ayhYjXVXuO9hH1qVgoGUBrk6dSirfCc/q71EbBKJbZYcKI
kPgTl+VfCrgovOEarBYSBbx89z50HW9Iu/h0zTG5UTF10YAcE24G8nRgHgqoQZ5M
jELYB57GxtvdbMOxXEfvt3YC3Gv29sUi8IgVHgbuQmcUnw0jEbg+TAlPy4JZaQiX
gQPjLKmkg/zTz5jyBOZI8g6TWOUJwScO0pj4e4JYwJQLTU+OFcylV5oT1TeKRbUg
q0QL1GhHL9zzBOVQ7YnROmYLJv03lpTgxwvPmXH56wKNty2Vi6ETWXg1Wvyv78c9
DSf5ed39bveBkIpHcL4FEy/WBOnuEpJwruyrq/zHX7w8w5XCJJHjZF30jTowJ7LF
ZarIMnzppV5ldqktsMFV8NxeQR84qAKRcrVM/1KnJFSlrKlE/4qprkoMa26xz8GH
YlEN615NUk9ImEwPl9Gu1mpfExseaKa7T0UgANaMc3E1BD+LZ08w9HmX4qtlxQKL
2a1S4N2o/L5YgYo5ABT+DYz2Qdm8PPkeqQsnpoQHNgu9UnIDRjnCQygQ1QmaXeAk
BBUvFeCMUhBXxNc5wWVs5LUSynPfFGqlccAzJqf/5K9casSfGQTg5eLGAhnZNevQ
QiaipdqjA72yVzWJ/lOEhJzBZ+/KielYOq10ra7nFLPs8DzV8kjMvXLJkK0FxJ08
lVLc6h8sIMlAS/Eg4MxjX/D+IdjXRiRBKw==...
-----END ENCRYPTED PRIVATE KEY-----"""

PUBLIC_KEY_PEM = b"""-----BEGIN PUBLIC KEY-----
...MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlwJ1nCMMze6Z7TiILqBt
OMsi5vXG5GO77Jz07U27JzwKOUzbnSig4+iRAaqizXwRGAKrctcMDhVjRuX1r/0o
AZpWMQN+q+VaWnhB0Mk/NXwPfB//42Q7iQvZGp6dbje0sLv9aIgzuogDU4DB9BFF
zLN91AmR4rDl5R19P747srZoWoxK2Gb8dv5DMF/d8z7Ncqz/Bewn5K9HRLr1IO3q
0ye8gGssSjy4XYUoJANXdM8o+WSdovKUPTKerSwJCAVIXmsmL08hHKgGBtCdme/r
/tRUbzZrGcSETVk0Up1P02B7ZgYefdSycwg9sWJGJbNXhZjyo+tcKFoUp5RdZ4UP
DwIDAQAB...
-----END PUBLIC KEY-----"""

_private_key = RSA.import_key(PRIVATE_KEY_PEM, passphrase=PASSPHRASE)
_public_key = RSA.import_key(PUBLIC_KEY_PEM)


def get_public_key_pem() -> str:
    pem_text = PUBLIC_KEY_PEM.decode("utf-8").strip()
    lines = pem_text.splitlines()
    if len(lines) < 3:
        return pem_text

    header = lines[0]
    footer = lines[-1]
    body = [line.replace(".", "") for line in lines[1:-1]]
    return "\n".join([header, *body, footer])


def decrypt_ciphertext_b64(ciphertext_b64: str) -> str:
    ciphertext = b64decode(ciphertext_b64)
    cipher = PKCS1_OAEP.new(_private_key, hashAlgo=SHA256)
    plaintext = cipher.decrypt(ciphertext)
    return plaintext.decode("utf-8")


def decrypt_payload_b64(ciphertext_b64: str) -> dict:
    plaintext = decrypt_ciphertext_b64(ciphertext_b64)
    return json.loads(plaintext)

