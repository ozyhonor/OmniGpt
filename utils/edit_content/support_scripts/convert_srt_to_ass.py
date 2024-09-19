import pysubs2
from db.database import db
import os
from setup_logger import logger


async def srt_to_ass(srt_file, user_id, marginv=0):

    base_name = os.path.splitext(srt_file)[0]
    output_subtitles = f'{base_name}.ass'

    # Загружаем субтитры из .srt файла
    subs = pysubs2.load(srt_file, encoding="utf-8")


    primary_color = await db.get_user_setting('primary_color', user_id)
    primary_r, primary_g, primary_b, primary_a = map(int, primary_color.split(','))

    second_color = await db.get_user_setting('second_color', user_id)
    second_r, second_g, second_b, second_a = map(int, second_color.split(','))

    outline_color = await db.get_user_setting('outline_color', user_id)
    outline_r, outline_g, outline_b, outline_a = map(int, outline_color.split(','))

    background_color = await db.get_user_setting('background_color', user_id)
    background_r, background_g, background_b, background_a = map(int, background_color.split(','))


    # Настраиваем стиль


    style = pysubs2.SSAStyle()
    fontsize = await db.get_user_setting('font_size', user_id)
    style.fontname = await db.get_user_setting('font', user_id)
    if marginv != 0:
        style.fontsize = fontsize-2
        style.marginv = fontsize * 1.2 * 3
        style.primarycolor = pysubs2.Color(255, 182, 155, 0)
        style.secondarycolor = pysubs2.Color(255, 182, 155, 0)
    else:
        style.fontsize = fontsize
        style.primarycolor = pysubs2.Color(primary_r, primary_g, primary_b, primary_a)
        style.secondarycolor = pysubs2.Color(second_r, second_g, second_b, second_a)

    style.outlinecolor = pysubs2.Color(outline_r, outline_g, outline_b, outline_a)
    style.backcolor = pysubs2.Color(background_r, background_g, background_b, background_a)

    style.outline = await db.get_user_setting('outline_size', user_id)
    translated = await db.get_user_setting('translator', user_id)

    style.alignment = pysubs2.Alignment.BOTTOM_CENTER # настроить позицию

    # Применяем стиль к субтитрам
    subs.styles["Default"] = style

    # Сохраняем субтитры в .ass формате
    subs.save(output_subtitles)

    logger.info(f'Convert srt to ass successful complite with filename {output_subtitles}')
    return output_subtitles