
def __is_string(string):
    if (not isinstance(string, str)) or (not string.strip()):
        return False
    return True

def question(obj):
    errors = []
    if not __is_string(obj.question):
        errors.append("Question should be a string.")
    if not __is_string(obj.answer):
        errors.append("Answer should be a string.")
    if not isinstance(obj.category, int):
        errors.append("Category should be an integer.")
    if not isinstance(obj.difficulty, int):
        errors.append("Difficulty should be an integer.")
    if errors:
        return errors
    return True
