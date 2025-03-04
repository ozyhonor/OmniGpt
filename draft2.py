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
        text = re.sub(r'\\\[(.*?)\\\]', r'\1', text)
        text = re.sub(r'\\\((.*?)\\\)', r'\1', text)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)  # Заменим ** на «...»
        text = text.replace('*', '⋅')  # Заменим * на ⋅
        text = re.sub(r'\\pmod\{(.*?)\}', r'mod \1', text)
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
    # Преобразуем текст вне блоков кода
    latex_text = re.sub(r'(?<=\w)_(?=\w{3,})', '＿', latex_text)  # Заменить _ на ＿ только для слов длиной 3 и более

    latex_text = process_text(latex_text)
    latex_text = await asyncio.to_thread(unicodeit.replace, latex_text)

    latex_text = latex_text.replace('`', '’')  # Заменим обратную кавычку на правую одинарную

    # Восстанавливаем блоки кода
    for i, code_block in enumerate(code_blocks):
        latex_text = latex_text.replace(markers[i], f'```{code_block}```')

    return latex_text

# Пример использования
latex_text = """
### Тема: Теория Категорий и Функторы

#### Математическое описание

Теория категорий — это область математики, изучающая абстрактные структуры и отношения между ними. Основные понятия теории категорий включают категории, функторы и натуральные преобразования.

1. **Категория** \( \mathcal{C} \) состоит из:
   - **Объектов** \( \text{Ob}(\mathcal{C}) \).
   - **Морфизмов** (или стрелок) \( \text{Hom}(A, B) \) для любых объектов \( A, B \in \text{Ob}(\mathcal{C}) \).
   - **Композиции** морфизмов: если \( f: A \to B \) и \( g: B \to C \), то существует композиция \( g \circ f: A \to C \).
   - **Тождественного морфизма** \( \text{id}_A: A \to A \) для каждого объекта \( A \).

   Эти элементы должны удовлетворять аксиомам:
   - Ассоциативность: \( h \circ (g \circ f) = (h \circ g) \circ f \).
   - Тождественность: \( \text{id}_B \circ f = f \) и \( g \circ \text{id}_A = g \).

2. **Функтор** \( F: \mathcal{C} \to \mathcal{D} \) между категориями \( \mathcal{C} \) и \( \mathcal{D} \) — это отображение, которое:
   - Каждому объекту \( A \in \text{Ob}(\mathcal{C}) \) сопоставляет объект \( F(A) \in \text{Ob}(\mathcal{D}) \).
   - Каждому морфизму \( f: A \to B \) сопоставляет морфизм \( F(f): F(A) \to F(B) \).
   - Сохраняет композицию и тождественные морфизмы: \( F(g \circ f) = F(g) \circ F(f) \) и \( F(\text{id}_A) = \text{id}_{F(A)} \).

3. **Натуральное преобразование** \( \eta: F \Rightarrow G \) между функторами \( F, G: \mathcal{C} \to \mathcal{D} \) — это семейство морфизмов \( \eta_A: F(A) \to G(A) \) для каждого объекта \( A \in \mathcal{C} \), такое что для любого морфизма \( f: A \to B \) в \( \mathcal{C} \) диаграмма коммутирует:
   \[
   G(f) \circ \eta_A = \eta_B \circ F(f)
   \]

#### Простое объяснение

Теория категорий — это как язык, который позволяет описывать и изучать структуры в математике на очень абстрактном уровне. Представьте, что у вас есть множество различных математических объектов, таких как группы, множества, векторные пространства и так далее. Теория категорий позволяет вам изучать не только сами эти объекты, но и отношения между ними.

- **Категория** — это как мир, в котором живут объекты и стрелки (морфизмы) между ними. Объекты — это как точки, а стрелки — это пути, которые соединяют эти точки.
- **Функтор** — это как карта, которая переводит один мир (категорию) в другой, сохраняя структуру. Он берет объекты и стрелки из одного мира и отображает их в объекты и стрелки другого мира.
- **Натуральное преобразование** — это способ сравнить два таких отображения (функторов) и сказать, насколько они "похожи" или "различны" в том, как они переводят один мир в другой.

Теория категорий используется для объединения различных областей математики, позволяя находить общие черты и закономерности в, казалось бы, несвязанных структурах. Это как универсальный язык для математиков, который помогает им общаться и находить новые идеи.
### Тема: Теория Категорий и Функторы

#### Математическое описание

Теория категорий — это область математики, изучающая абстрактные структуры и отношения между ними. Основные понятия теории категорий включают категории, функторы и натуральные преобразования.

1. **Категория** \( \mathcal{C} \) состоит из:
   - **Объектов** \( \text{Ob}(\mathcal{C}) \).
   - **Морфизмов** (или стрелок) \( \text{Hom}(A, B) \) для любых объектов \( A, B \in \text{Ob}(\mathcal{C}) \).
   - **Композиции** морфизмов: если \( f: A \to B \) и \( g: B \to C \), то существует композиция \( g \circ f: A \to C \).
   - **Тождественного морфизма** \( \text{id}_A: A \to A \) для каждого объекта \( A \).

   Эти элементы должны удовлетворять аксиомам:
   - Ассоциативность: \( h \circ (g \circ f) = (h \circ g) \circ f \).
   - Тождественность: \( \text{id}_B \circ f = f \) и \( g \circ \text{id}_A = g \).

2. **Функтор** \( F: \mathcal{C} \to \mathcal{D} \) между категориями \( \mathcal{C} \) и \( \mathcal{D} \) — это отображение, которое:
   - Каждому объекту \( A \in \text{Ob}(\mathcal{C}) \) сопоставляет объект \( F(A) \in \text{Ob}(\mathcal{D}) \).
   - Каждому морфизму \( f: A \to B \) сопоставляет морфизм \( F(f): F(A) \to F(B) \).
   - Сохраняет композицию и тождественные морфизмы: \( F(g \circ f) = F(g) \circ F(f) \) и \( F(\text{id}_A) = \text{id}_{F(A)} \).

3. **Натуральное преобразование** \( \eta: F \Rightarrow G \) между функторами \( F, G: \mathcal{C} \to \mathcal{D} \) — это семейство морфизмов \( \eta_A: F(A) \to G(A) \) для каждого объекта \( A \in \mathcal{C} \), такое что для любого морфизма \( f: A \to B \) в \( \mathcal{C} \) диаграмма коммутирует:
   \[
   G(f) \circ \eta_A = \eta_B \circ F(f)
   \]

#### Простое объяснение

Теория категорий — это как язык, который позволяет описывать и изучать структуры в математике на очень абстрактном уровне. Представьте, что у вас есть множество различных математических объектов, таких как группы, множества, векторные пространства и так далее. Теория категорий позволяет вам изучать не только сами эти объекты, но и отношения между ними.

- **Категория** — это как мир, в котором живут объекты и стрелки (морфизмы) между ними. Объекты — это как точки, а стрелки — это пути, которые соединяют эти точки.
- **Функтор** — это как карта, которая переводит один мир (категорию) в другой, сохраняя структуру. Он берет объекты и стрелки из одного мира и отображает их в объекты и стрелки другого мира.
- **Натуральное преобразование** — это способ сравнить два таких отображения (функторов) и сказать, насколько они "похожи" или "различны" в том, как они переводят один мир в другой.

Теория категорий используется для объединения различных областей математики, позволяя находить общие черты и закономерности в, казалось бы, несвязанных структурах. Это как универсальный язык для математиков, который помогает им общаться и находить новые идеи.

"""
result = asyncio.run(convert_latex_to_unicode(latex_text))
print(result)