from typing import Sequence, TypeVar

T = TypeVar("T")


def create_keyboard_layout(buttons: Sequence[T], count: Sequence[int]) -> list[list[T]]:
    if sum(count) != len(buttons):
        raise ValueError("Buttons count are not fitted for schema")

    tmp_list: list[list[T]] = []
    btn_number = 0
    for a in count:
        tmp_list.append([])
        for _ in range(a):
            tmp_list[-1].append(buttons[btn_number])
            btn_number += 1

    return tmp_list
