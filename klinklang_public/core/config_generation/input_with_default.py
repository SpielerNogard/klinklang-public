def input_with_default(prompt, default):
    result = input(f"{prompt}({default=})")
    if not result:
        return default
    return result