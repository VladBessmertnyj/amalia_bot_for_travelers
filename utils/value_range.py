from typing import List, Tuple


def value_range(text: str) -> Tuple | ValueError:
    """
    Проверяет строку со значениями диапазона на правильность написания, в случае успеха проверки возвращает кортеж
    со значениями, иначе выбрасывает исключение.

    """

    val_range: List = text.split('-')
    if len(val_range) == 2:
        if val_range[0].isdigit() and val_range[1].isdigit():
            if int(val_range[0]) < int(val_range[1]):
                for index, val in enumerate(val_range):
                    val_range[index] = int(val)
                return tuple(val_range)
    raise ValueError
