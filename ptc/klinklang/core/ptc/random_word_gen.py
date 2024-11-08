import os
import random
import re
import string
import uuid

SPECIAL_CHARS = ['"', "/", ":", ","]
this_dir = os.path.dirname(__file__)


class RandomWordGen:
    def __init__(self):
        self.words = self._load_words()
        print(f"Loaded {len(self.words)} words")

    @staticmethod
    def is_normal_characters(s):
        if not s:
            return False
        # Define the regular expression pattern for normal characters (letters and digits)
        pattern = re.compile(r"^[a-zA-Z0-9]+$")
        # Check if the string matches the pattern
        return bool(pattern.match(s))

    @staticmethod
    def _load_words():
        with open(os.path.join(this_dir, "words.txt")) as in_file:
            content = in_file.readlines()
        return [
            word.strip() for word in content if RandomWordGen.is_normal_characters(word)
        ]

    @staticmethod
    def random_part(lenght: int):
        part = f"{uuid.uuid4()}".replace("-", "")
        return part[:lenght]

    def generate_username(
        self, lower_limit=6, upper_limit=16, only_chars: bool = False
    ):
        username_parts = [self.random_part(5)]

        lenght = random.randint(lower_limit, upper_limit)

        while len("".join(username_parts)) < lenght:
            username_parts.append(random.choice(self.words).replace(" ", ""))

        random.shuffle(username_parts)
        username = "".join(username_parts)[:upper_limit]
        if only_chars:
            chars = []
            for char in username:
                if char.isdigit():
                    chars.append(random.choice(string.ascii_lowercase))
                    continue
                chars.append(char)
            return "".join(chars)
        return username

    @staticmethod
    def _id_generator(size=12, chars=string.ascii_uppercase + string.digits):
        generated = "".join(random.choice(chars) for _ in range(size))
        for character in SPECIAL_CHARS:
            generated = generated.replace(character, "")
        return generated

    def generate_password(self, lower_limit=6, upper_limit=32) -> str:
        password_lenght = random.randint(lower_limit, int(upper_limit - 4))

        generated = RandomWordGen._id_generator(
            size=password_lenght,
            chars=string.ascii_uppercase + string.ascii_lowercase + string.digits,
        )
        parts = [char for char in generated]
        parts.extend(["#", "0", "A", "a"])
        random.shuffle(parts)
        password = "".join(parts)

        return password[:upper_limit]
