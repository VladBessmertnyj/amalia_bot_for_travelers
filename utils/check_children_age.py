from typing import List


def check_children_age(age_list: List) -> bool:
    """Проверяет, состоит ли возраст из цифр, не является отрицательным и не больше 17."""

    for age in age_list:
        if not age.isdigit() or 0 >= int(age) > 17:
            return False
    return True
