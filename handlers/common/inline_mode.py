from typing import Callable, Optional

from aiogram import types

MAX_INLINE_RESULT = 50


class InlineHandlers:
    @staticmethod
    async def generate_inline_list(callback: types.InlineQuery, data: list, render_func: Callable):
        offset = int(callback.offset or "0")

        results = InlineHandlers._markup_inline_list(data, offset, render_func)

        if len(data) > offset + MAX_INLINE_RESULT:
            next_offset = str(offset + MAX_INLINE_RESULT)
        else:
            next_offset = None

        await callback.answer(results=results, next_offset=next_offset, cache_time=2)

    @staticmethod
    def _markup_inline_list(data: list, offset: Optional[int], render_func: Callable):
        results = []

        if offset is not None:
            for item in data[offset: offset + MAX_INLINE_RESULT - 1]:
                results.append(render_func(item))

        else:
            for item in data:
                results.append(render_func(item))

        return results
