import base64
import hashlib
import os
import re

import requests

code_verifier = base64.urlsafe_b64encode(os.urandom(40)).decode("utf-8")
code_verifier = re.sub("[^a-zA-Z0-9]+", "", code_verifier)
code_challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
code_challenge = base64.urlsafe_b64encode(code_challenge).decode("utf-8")
code_challenge = code_challenge.replace("=", "")
state = base64.urlsafe_b64encode(os.urandom(20)).decode("utf-8")

url = f"https://accounts.google.com/o/oauth2/v2/auth/oauthchooseaccount?state={state}&scope=openid%20email%20profile&redirect_uri=com.googleusercontent.apps.848232511240-dmrj3gba506c9svge2p9gq35p1fg654p%3A%2Foauth2redirect&client_id=848232511240-dmrj3gba506c9svge2p9gq35p1fg654p.apps.googleusercontent.com&response_type=code&code_challenge={code_challenge}&code_challenge_method=S256&service=lso&o2v=2&ddm=0&flowName=GeneralOAuthFlow"

r = requests.post(
    "http://localhost:8000/api/v1/login",
    json={
        "url": url,
        "username": "redeyesboltropes2a354prepoliti@gmail.com",
        "password": "lv0IM0yeBvaRW#A",
    },
)

print(r)
print(r.text)
