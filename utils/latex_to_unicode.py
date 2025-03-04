import re
import unicodeit
import asyncio

async def convert_latex_to_unicode(latex_text):
    # Шаблон для поиска блоков кода
    code_block_pattern = re.compile(r'```(.*?)```', re.DOTALL)

    # Извлекаем блоки кода
    code_blocks = code_block_pattern.findall(latex_text)

    # Заменяем блоки кода на временные маркеры
    markers = [f'CODE=BLOCK={i}' for i in range(len(code_blocks))]
    for i, code_block in enumerate(code_blocks):
        latex_text = latex_text.replace(f'```{code_block}```', markers[i])

    # Выполняем преобразования на остальной части текста

    def process_text(text):
        text = re.sub(r'\\\[(.*?)\\\]', r'\1', text, flags=re.DOTALL)
        text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Заменим ** на «...»
        text = text.replace('*', '⋅')  # Заменим * на ⋅
        text = re.sub(r'\\pmod\{(.*?)\}', r'mod \1', text)
        text = text.replace('\mod', 'mod')
        text = re.sub(r'\\frac\{(.*?)\}\{(.*?)\}', r'⟮\1 ÷ \2⟯', text)
        text = re.sub(r'\\left(.*?)\\right', r'\1', text)

        def bold_replacement(match):
            text = match.group(1)
            return ''.join(
                chr(ord(c) + 0x1D400 - ord('A')) if 'A' <= c <= 'Z' else
                chr(ord(c) + 0x1D41A - ord('a')) if 'a' <= c <= 'z' else c
                for c in text
            )

        # Преобразование текста в жирный
        text = re.sub(r'\\text\{(.*?)\}', bold_replacement, text)
        return text

    latex_text = re.sub(r'(\w+)_+(\w+)', lambda m: m.group(0).replace('_', '＿'), latex_text)
    latex_text = re.sub(r'(?<=\w)_(?=\w{3,})', '＿', latex_text)  # Заменить _ на ＿ только для слов длиной 3 и более

    latex_text = latex_text.replace(r'\xrightarrow', '→')

    latex_text = process_text(latex_text)
    latex_text = await asyncio.to_thread(unicodeit.replace, latex_text)

    latex_text = latex_text.replace('_', '＿')
    latex_text = latex_text.replace('`', '’')  # Заменим обратную кавычку на правую одинарную

    # Восстанавливаем блоки кода
    for i, code_block in enumerate(code_blocks):
        latex_text = latex_text.replace(markers[i], f'```{code_block}```')

    return latex_text

