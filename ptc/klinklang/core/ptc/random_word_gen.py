import os
import random
import re
import string
import uuid

SPECIAL_CHARS = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '_', '+']
this_dir = os.path.dirname(__file__)

class RandomWordGen:

    @staticmethod
    def is_normal_characters(s):
        if not s:
            return False
        pattern = re.compile(r"^[a-zA-Z0-9]+$")
        return bool(pattern.match(s))

    @staticmethod
    def generate_syllables(length=3):
        vowels = "aeiou"
        consonants = "bcdfghjklmnpqrstvwxyz"
        syllables = []
        for _ in range(length):
            syllable = random.choice(consonants) + random.choice(vowels)
            syllables.append(syllable)
        return "".join(syllables)

    @staticmethod
    def add_random_digits(name, num_digits=4):
        name_list = list(name)
        for _ in range(num_digits):
            digit = str(random.randint(0, 9))
            pos = random.randint(1, len(name_list) - 1)
            name_list.insert(pos, digit)
        return "".join(name_list)

    @staticmethod
    def generate_password(lower_limit=12, upper_limit=24):
        length = random.randint(lower_limit, upper_limit)
        all_chars = string.ascii_letters + string.digits + "".join(SPECIAL_CHARS)
        
       
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice(SPECIAL_CHARS)
        ]
        
        password += [random.choice(all_chars) for _ in range(length - 4)]
        random.shuffle(password)
        return "".join(password)

    @staticmethod
    def generate_username():
        num_syllables = random.randint(3, 6)
        
        base_name = "".join([RandomWordGen.generate_syllables() for _ in range(num_syllables)])

        random_digits_count = random.randint(1, 3)
        base_name = RandomWordGen.add_random_digits(base_name, random_digits_count)
        
        while len(base_name) < 10:
            base_name += random.choice(string.ascii_lowercase)
        
        if len(base_name) > 16:
            base_name = base_name[:16]
        
        return base_name


if __name__ == "__main__":
    random_word_gen = RandomWordGen()
    username = random_word_gen.generate_username()
    password = random_word_gen.generate_password()
