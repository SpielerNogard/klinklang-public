import os
import random
import re
import string
import uuid

SPECIAL_CHARS = ['"', "/", ":", ",", "@", "#", "$", "%", "&"]
this_dir = os.path.dirname(__file__)

class RandomWordGen:
    def __init__(self):
        self.words = self._load_words()
        print(f"Loaded {len(self.words)} words")

    @staticmethod
    def is_normal_characters(s):
        if not s:
            return False
        pattern = re.compile(r"^[a-zA-Z0-9]+$")
        return bool(pattern.match(s))

    @staticmethod
    def _load_words():
        with open(os.path.join(this_dir, "words.txt")) as in_file:
            content = in_file.readlines()
        return [
            word.strip() for word in content if RandomWordGen.is_normal_characters(word)
        ]

    @staticmethod
    def random_part(length: int):
        part = ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))
        return part

    def generate_username(self, lower_limit=6, upper_limit=16):
        word1 = random.choice(self.words).replace(" ", "")
        word2 = random.choice(self.words).replace(" ", "")
        
        random_number = random.randint(1, 999)

        username = f"{word1}{random_number}{word2}"

        while len(username) < lower_limit:
            username += random.choice(self.words).replace(" ", "")
        username = username[:upper_limit]

        return username

    @staticmethod
    def _id_generator(size=12, chars=string.ascii_uppercase + string.digits):
        generated = "".join(random.choice(chars) for _ in range(size))
        for character in SPECIAL_CHARS:
            generated = generated.replace(character, "")
        return generated

    def generate_password(self, username=None, lower_limit=13, upper_limit=32) -> str:
        if username is None:
            username = self.generate_username()

        base_username = username.split()[0]
        random_number = random.randint(10, 99)
        special_char = random.choice(SPECIAL_CHARS)
        random_upper = random.choice(string.ascii_uppercase)
    
        password = f"{base_username}{random_number}{special_char}{random_upper}"

        while len(password) < lower_limit:
            password += random.choice(string.ascii_letters + string.digits)

        password = password[:upper_limit]

        return password
