from PIL import Image, ImageDraw, ImageFont


def create_life_calendar_image(
        passed_weeks,
        weeks_per_year=52,
        total_years=100,
        cell_size=10,
        gap=8,
        margin=10
):
    """
    Создаёт изображение календаря жизни с учётом последних правок:
     1) менее яркий красный для прожитых недель;
     2) «недели»: метки 1, 5, 10, ... (каждые 5), увеличенные в 2× и жирные;
     3) «возраст»: метки 0, 5, 10, ... (каждые 5), увеличенные в 2× и жирные;
     4) слова «недели» и «возраст» жирным и в 3× больше cell_size;
     5) слово «Возраст» рисуется обычным, но повернутым на 90° вдоль сетки слева;
     6) стрелки чуть короче (примерно 60% от длины/высоты сетки).
    """
    # ────── Шрифты ──────
    try:
        font_label = ImageFont.truetype("arialbd.ttf", cell_size * 3)
    except IOError:
        font_label = ImageFont.truetype("DejaVuSans-Bold.ttf", cell_size * 3)

    try:
        font_numbers = ImageFont.truetype("arialbd.ttf", cell_size * 2)
    except IOError:
        font_numbers = ImageFont.truetype("DejaVuSans-Bold.ttf", cell_size * 2)

    # ────── Функция для измерения текста через font.getbbox ──────
    def text_size(font_obj, text: str):
        bbox = font_obj.getbbox(text)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    # ────── Замеряем ключевые тексты ──────
    label_weeks = "Недели"
    tw_label, th_label = text_size(font_label, label_weeks)

    label_age = "Возраст"
    w_age_label, h_age_label = text_size(font_label, label_age)

    sample_num = "100"
    w_num, h_num = text_size(font_numbers, sample_num)

    # ────── Задаём «защитные» расстояния для цифр и текста ──────
    gap1_h = 5  # вертикальный gap между «Неделя» и цифрами недель
    gap2_h = 5  # вертикальный gap между цифрами недель и сеткой
    gap1_v = 5  # горизонтальный gap между «Возраст» и цифрами возраста
    gap2_v = 5  # горизонтальный gap между цифрами возраста и сеткой

    # ────── Доработки по поднятию текста/цифр ──────
    raise_week_nums = 5  # поднять цифры недель чуть-чуть
    raise_week_label = 15  # поднять слово «Неделя» выше
    raise_age_nums = 2  # поднять цифры возраста

    # ────── Вычисляем, сколько места нужно слева для «Возраст» и цифр возраста ──────
    rotated_age_width = h_age_label
    extra_left = rotated_age_width + w_num + gap2_v

    # ────── Padding со всех сторон ──────
    padding = margin + extra_left

    # ────── Размеры сетки ──────
    grid_width = weeks_per_year * cell_size + (weeks_per_year - 1) * gap
    grid_height = total_years * cell_size + (total_years - 1) * gap

    # ────── Координаты начала сетки ──────
    grid_start_x = padding
    grid_start_y = padding

    # ────── Итоговый размер холста ──────
    img_width = grid_start_x + grid_width + padding
    img_height = grid_start_y + grid_height + padding

    im = Image.new("RGB", (img_width, img_height), "white")
    draw = ImageDraw.Draw(im)

    # ────── Цвета и радиус скругления квадратиков ──────
    passed_color = "#cc6f6c"
    future_color = "lightgrey"
    border_color = "black"
    radius = max(1, cell_size // 5)

    # ────── 1) Рисуем повернутое «Возраст» слева от сетки ──────
    text_age_img = Image.new("RGBA", (w_age_label, h_age_label), (0, 0, 0, 0))
    draw_age = ImageDraw.Draw(text_age_img)
    draw_age.text((0, 0), label_age, font=font_label, fill="black")
    rotated_age = text_age_img.rotate(90, expand=True)
    age_x = margin
    age_y = grid_start_y  # буква «т» на уровне верхней границы первой клетки
    im.paste(rotated_age, (int(age_x), int(age_y)), rotated_age)

    # ────── 1a) Рисуем длинную стрелку вниз под «Возраст» ──────
    arrow_length_v = cell_size * 10  # длина стрелки в 5× больше
    head_wh = cell_size  # размер основания треугольника (по вертикали)
    shaft_w = max(1, cell_size // 4)  # ещё тоньше «ствол»
    # Центр слова «Возраст» по горизонтали с небольшим сдвигом вправо
    center_x = age_x + rotated_age.width / 2 + 2
    # Начало стрелки:
    arrow_start_y = age_y + rotated_age.height + 2
    # Конец стрелки (остриё):
    tip_y = arrow_start_y + arrow_length_v
    pts_down = [
        (center_x - shaft_w / 2, arrow_start_y),  # верх левый ствол
        (center_x + shaft_w / 2, arrow_start_y),  # верх правый ствол
        (center_x + shaft_w / 2, tip_y - head_wh),  # правая точка основания треугольника
        (center_x + head_wh / 2, tip_y - head_wh),  # правая внутренняя точка
        (center_x, tip_y),  # остриё стрелки
        (center_x - head_wh / 2, tip_y - head_wh),  # левая внутренняя точка
        (center_x - shaft_w / 2, tip_y - head_wh),  # левая точка основания треугольника
    ]
    draw.polygon(pts_down, fill="black")

    # ────── 2) Цифры возраста (0, 5, 10, ..., 100) жирным и крупным ──────
    for age in range(0, total_years + 1, 5):
        age_str = str(age)
        tw_a, th_a = text_size(font_numbers, age_str)
        if age < total_years:
            y_a = (
                    grid_start_y
                    + age * (cell_size + gap)
                    + (cell_size - th_a) / 2
                    - (gap2_v // 2)
                    - raise_age_nums
            )
        else:
            y_a = grid_start_y + grid_height + 1 - (gap2_v // 2) - raise_age_nums
        x_a = grid_start_x - gap2_v - tw_a
        draw.text((x_a, y_a), age_str, font=font_numbers, fill="black")

    # ────── 3) Цифры недель (1, 5, 10, ..., до конца строки) жирным и крупным ──────
    numbers_y = grid_start_y - gap2_h - h_num - raise_week_nums
    week_positions = [1] + [i for i in range(5, weeks_per_year + 1, 5) if i != 1]
    for week_num in week_positions:
        label = str(week_num)
        tw_i, th_i = text_size(font_numbers, label)
        col_index = week_num - 1
        x_i = grid_start_x + col_index * (cell_size + gap) + (cell_size - tw_i) / 2
        y_i = numbers_y
        draw.text((x_i, y_i), label, font=font_numbers, fill="black")

    # ────── 4) Слово «Неделя» (жирным 3×) над цифрами с длинной стрелкой вправо ──────
    text_weeks_x = grid_start_x
    text_weeks_y = numbers_y - gap1_h - th_label - raise_week_label
    draw.text((text_weeks_x, text_weeks_y), label_weeks, font=font_label, fill="black")

    # ────── 4a) Рисуем длинную стрелку вправо рядом с «Неделя» ──────
    arrow_length_h = cell_size * 10  # длина стрелки в 5× больше
    head_w = cell_size  # размер основания треугольника (по горизонтали)
    shaft_h = max(1, cell_size // 4)  # ещё тонкий «ствол»
    # Центр слова «Неделя» по вертикали с большим сдвигом вниз
    center_y = text_weeks_y + th_label / 2 + 7
    # Начало стрелки:
    arrow_start_x = text_weeks_x + tw_label + 5
    # Конец стрелки (остриё):
    tip_x = arrow_start_x + arrow_length_h
    pts_right = [
        (arrow_start_x, center_y - shaft_h / 2),  # верх левый ствол
        (arrow_start_x, center_y + shaft_h / 2),  # ниж левый ствол
        (tip_x - head_w, center_y + shaft_h / 2),  # правая точка основания треугольника
        (tip_x - head_w, center_y + head_w / 2),  # правая внутренняя точка
        (tip_x, center_y),  # остриё стрелки
        (tip_x - head_w, center_y - head_w / 2),  # левая внутренняя точка
        (tip_x - head_w, center_y - shaft_h / 2),  # левая точка основания треугольника
    ]
    draw.polygon(pts_right, fill="black")

    # ────── 5) Рисуем сами квадратики с закруглёнными углами ──────
    for row in range(total_years):
        for col in range(weeks_per_year):
            index = row * weeks_per_year + col
            fill_color = passed_color if index < passed_weeks else future_color
            x0 = grid_start_x + col * (cell_size + gap)
            y0 = grid_start_y + row * (cell_size + gap)
            x1 = x0 + cell_size
            y1 = y0 + cell_size
            draw.rounded_rectangle(
                [(x0, y0), (x1, y1)],
                radius=radius,
                fill=fill_color,
                outline=border_color
            )

    return im