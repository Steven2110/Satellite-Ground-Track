import tkinter as tk  # Импортируем модуль tkinter для создания графического интерфейса
from tkinter import ttk  # Импортируем ttk для использования стилизованных виджетов
import matplotlib.pyplot as plt  # Импортируем pyplot для построения графиков с matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg  # Импортируем класс для встраивания matplotlib графиков в Tkinter
import matplotlib.cm as cm  # Импортируем модуль colormap для работы с цветовыми схемами
import numpy as np  # Импортируем библиотеку NumPy для работы с массивами и математическими функциями
from astropy.time import Time  # Импортируем класс Time для работы с астрономическим временем
from datetime import datetime, timedelta  # Импортируем datetime и timedelta для работы с датами и временем
import matplotlib.animation as animation  # Импортируем модуль анимаций из matplotlib

from constants import TIME_STEPS, SATELLITES  # Импортируем константы TIME_STEPS и SATELLITES из модуля constants
from utilities import calculate_longitudes_latitudes  # Импортируем функцию вычисления долгот и широт из модуля utilities

# Класс приложения для отображения следа спутника (Ground Track)
class SatelliteGroundTrackApp:
    def __init__(self, root):
        self.root = root  # Сохраняем ссылку на корневое окно
        self.root.title("Satellite Selector")  # Устанавливаем заголовок окна
        self.root.geometry("600x400")  # Задаем размеры окна

        # Создаем основной фрейм для размещения виджетов
        self.main_frame = tk.Frame(root)  # Создаем фрейм внутри корневого окна
        self.main_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)  # Размещаем фрейм с отступами и растягиваем его

        # Создаем выпадающий список для выбора спутниковой системы
        self.sat_label = tk.Label(self.main_frame, text="Select Satellite System:")  # Создаем метку для выбора системы спутников
        self.sat_label.grid(row=0, column=0, padx=5, pady=5)  # Размещаем метку в сетке (строка 0, колонка 0)
        self.sat_var = tk.StringVar()  # Создаем строковую переменную для хранения выбранного значения
        self.sat_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.sat_var,  # Привязываем переменную к виджету
            values=list(SATELLITES.keys()),  # Заполняем список ключами из словаря SATELLITES
            state='readonly'  # Запрещаем редактирование значения пользователем
        )
        self.sat_dropdown.grid(row=0, column=1, padx=5, pady=5)  # Размещаем выпадающий список (строка 0, колонка 1)
        self.sat_dropdown.bind("<<ComboboxSelected>>", self.display_satellite_info)  # Привязываем событие выбора к методу отображения информации

        # Создаем выпадающий список для выбора временного шага
        self.time_label = tk.Label(self.main_frame, text="Select Time Step:")  # Создаем метку для выбора временного шага
        self.time_label.grid(row=1, column=0, padx=5, pady=5)  # Размещаем метку (строка 1, колонка 0)
        self.time_var = tk.DoubleVar(value=0.01)  # Создаем переменную типа double с начальным значением 0.01
        self.time_dropdown = ttk.Combobox(
            self.main_frame,
            textvariable=self.time_var,  # Привязываем переменную к виджету
            values=TIME_STEPS,  # Заполняем список значениями из константы TIME_STEPS
            state='readonly'  # Запрещаем редактирование значения
        )
        self.time_dropdown.grid(row=1, column=1, padx=5, pady=5)  # Размещаем выпадающий список (строка 1, колонка 1)

        # Разделитель для визуального разделения секций
        self.divider = ttk.Separator(self.main_frame, orient='horizontal')  # Создаем горизонтальный разделитель
        self.divider.grid(row=2, column=0, columnspan=2, sticky='ew', pady=10)  # Размещаем разделитель на две колонки

        # Область для отображения информации о параметрах спутника
        self.info_label = tk.Label(self.main_frame, text="Satellite Parameters:")  # Создаем метку для параметров спутника
        self.info_label.grid(row=3, column=0, columnspan=2, padx=5, pady=5)  # Размещаем метку, объединяя две колонки
        self.info_text = tk.Text(self.main_frame, height=15, width=80, state='disabled')  # Создаем текстовое поле для информации (только для чтения)
        self.info_text.grid(row=4, column=0, columnspan=2, padx=5, pady=5)  # Размещаем текстовое поле

        # Кнопка "Go" для запуска построения орбиты
        self.go_button = tk.Button(self.main_frame, text="Go", command=self.plot_orbit)  # Создаем кнопку, которая вызывает метод plot_orbit при нажатии
        self.go_button.grid(row=5, column=0, columnspan=2, pady=10)  # Размещаем кнопку, объединяя две колонки

        # Инициализируем переменные для анимации и графических объектов
        self.current_frame = 0  # Номер текущего кадра анимации
        self.ani = None  # Переменная для хранения объекта анимации
        self.fig = None  # Переменная для фигуры matplotlib
        self.canvas = None  # Переменная для холста (canvas) в Tkinter

    def display_satellite_info(self, event):
        """Отображает информацию о всех спутниках выбранной системы."""
        sat_key = self.sat_var.get()  # Получаем ключ выбранной системы спутников
        if sat_key in SATELLITES:  # Если такой ключ присутствует в SATELLITES
            sat_item = SATELLITES[sat_key]  # Получаем объект(ы) спутника(ов)
            if isinstance(sat_item, list):  # Если полученный объект является списком (несколько спутников)
                info = ""  # Инициализируем пустую строку для информации
                for s in sat_item:  # Проходим по каждому спутнику в списке
                    info += s.info() + "\n"  # Добавляем информацию о спутнике и перевод строки
            else:
                info = sat_item.info()  # Если объект не список, получаем информацию напрямую
            self.info_text.config(state='normal')  # Делаем текстовое поле доступным для редактирования
            self.info_text.delete("1.0", tk.END)  # Очищаем текстовое поле
            self.info_text.insert(tk.END, info)  # Вставляем информацию о спутнике
            self.info_text.config(state='disabled')  # Делам текстовое поле только для чтения

    def plot_orbit(self):
        """Открывает новое окно с анимацией следа спутника на Земле, сгруппированного по плоскостям орбиты (Ω)."""
        sat_key = self.sat_var.get()  # Получаем выбранную систему спутников
        dt = self.time_var.get()  # Получаем выбранный временной шаг
        if sat_key not in SATELLITES or dt == 0:  # Если система не выбрана или временной шаг равен 0, выходим из функции
            return

        sat_item = SATELLITES[sat_key]  # Получаем объект(ы) спутника(ов) по ключу
        sats = sat_item if isinstance(sat_item, list) else [sat_item]  # Если объект не список, оборачиваем его в список

        # Создаем новое окно для отображения карты следа спутника
        map_window = tk.Toplevel(self.root)  # Создаем новое окно поверх главного
        map_window.title(f"{sat_key} Ground Track Animation")  # Устанавливаем заголовок нового окна
        map_window.geometry("1680x1050")  # Задаем размеры нового окна

        self.fig, ax = plt.subplots(figsize=(10, 6))  # Создаем фигуру и ось для графика с заданным размером
        try:
            img = plt.imread("Word300dpi.jpg")  # Пытаемся загрузить изображение для фона
        except Exception:
            img = np.ones((600, 1200, 3))  # Если загрузка не удалась, создаем белое изображение
        ax.imshow(img, extent=[-180, 180, -90, 90])  # Отображаем изображение, задавая диапазон координат (долгота и широта)
        ax.set_xlabel("Longitude")  # Устанавливаем подпись оси X
        ax.set_ylabel("Latitude")  # Устанавливаем подпись оси Y
        ax.set_title(f"{sat_key} Ground Track")  # Устанавливаем заголовок графика

        reference_datetime = datetime(2025, 2, 27, 0, 0, 0)  # Опорное время для отсчета (год, месяц, день, час, минута, секунда)
        date = Time("2025-02-27 00:00:00", format="iso", scale="utc")  # Создаем объект времени Astropy

        T_common = sats[0].T  # Получаем период орбиты первого спутника
        time_steps = np.linspace(0, T_common, int(T_common / (dt * T_common)) + 1)  # Генерируем равномерные временные шаги от 0 до T
        all_datetimes = [reference_datetime + timedelta(seconds=t) for t in time_steps]  # Формируем список дат для каждого временного шага

        # Вычисляем следы спутников: долготы и широты
        all_longitudes = []  # Список для хранения долгот траекторий
        all_latitudes = []  # Список для хранения широт траекторий
        sat_labels = []  # Список меток для каждого подспутника
        plane_indices = []  # Список индексов плоскостей для каждого подспутника

        plane_columns = []  # Список для хранения информации о плоскостях орбиты
        for obj_idx, s in enumerate(sats):  # Перебираем спутники с индексами
            num_planes = len(s.longitude_of_ascending_node) or 1  # Определяем число плоскостей (если отсутствуют, считаем 1)
            for p_idx in range(num_planes):  # Перебираем плоскости
                plane_omega = s.longitude_of_ascending_node[p_idx] if p_idx < len(s.longitude_of_ascending_node) else "?"  # Получаем значение Ω для плоскости
                plane_label = f"Plane {p_idx+1}: (Ω = {plane_omega}°)"  # Формируем метку для плоскости
                plane_columns.append((obj_idx, p_idx, plane_label))  # Сохраняем информацию о плоскости

        for obj_idx, s in enumerate(sats):  # Для каждого спутника
            lons, lats = calculate_longitudes_latitudes(satellite=s, date=date, dt=dt)  # Вычисляем траектории (долготы и широты)
            num_planes = len(s.longitude_of_ascending_node) or 1  # Число плоскостей
            num_args = len(s.argument_pericenter) or 1  # Число значений аргумента перицентра
            for sub_idx in range(len(lons)):  # Перебираем каждую траекторию
                plane_idx = sub_idx // num_args  # Определяем индекс плоскости для данной траектории
                all_longitudes.append(lons[sub_idx])  # Сохраняем долготу
                all_latitudes.append(lats[sub_idx])  # Сохраняем широту
                sat_labels.append(f"{s.satellite_name} {sub_idx+1}")  # Формируем метку для спутника с номером траектории
                plane_indices.append((obj_idx, plane_idx))  # Сохраняем индексы спутника и плоскости

        total_sub_sats = len(all_longitudes)  # Определяем общее количество подспутников (траекторий)

        # Подготавливаем scatter-графики для отображения точек на графике
        scatters = []  # Список для хранения объектов scatter
        colors = cm.plasma(np.linspace(0, 1, total_sub_sats))  # Генерируем цвета для каждого подспутника из цветовой схемы plasma
        for i in range(total_sub_sats):
            scatter, = ax.plot([], [], 'o', markersize=4, color=colors[i])  # Создаем scatter-график без начальных данных
            scatter.set_label(sat_labels[i])  # Устанавливаем метку для легенды
            scatters.append(scatter)  # Добавляем scatter в список

        # Добавляем текстовую аннотацию для отображения времени на графике
        datetime_text = self.fig.text(
            0.2, 0.925, "",  # Координаты и начальный текст
            transform=self.fig.transFigure,  # Привязка к координатной системе фигуры
            ha="left", va="top",  # Выравнивание по левому краю и верху
            fontsize=10, bbox=dict(facecolor='white', alpha=0.7)  # Размер шрифта и оформление фона аннотации
        )

        self.current_frame = 0  # Сбрасываем текущий кадр анимации

        # Настройки для управления сеткой и анимацией
        animation_on_var = tk.BooleanVar(value=True)  # Булевая переменная для включения/выключения анимации (по умолчанию True)
        grid_step_var = tk.IntVar(value=30)  # Переменная для выбора шага сетки (по умолчанию 30°)
        grid_on = True  # Флаг отображения сетки
        grid_lines = []  # Список для хранения линий сетки

        # Функция для отрисовки линий сетки на графике
        def draw_grid_lines(step, visible=True):
            nonlocal grid_lines  # Используем внешнюю переменную grid_lines
            for line in grid_lines:  # Удаляем предыдущие линии сетки
                line.remove()
            grid_lines.clear()  # Очищаем список линий
            long_ticks = np.unique(np.concatenate([np.arange(-180, 181, step), [0]]))  # Вычисляем метки для долготы
            if step == 60:
                lat_ticks = np.array([-90, -60, 0, 60, 90])  # Для шага 60 задаем фиксированные метки для широты
            else:
                lat_ticks = np.unique(np.concatenate([np.arange(-90, 91, step), [0]]))  # Иначе вычисляем метки для широты
            for lat in lat_ticks:  # Рисуем горизонтальные линии для каждой метки широты
                line = ax.axhline(lat, color='gray', linestyle='--', linewidth=0.5)
                line.set_visible(visible)  # Устанавливаем видимость линии
                grid_lines.append(line)  # Добавляем линию в список
            for lon in long_ticks:  # Рисуем вертикальные линии для каждой метки долготы
                line = ax.axvline(lon, color='gray', linestyle='--', linewidth=0.5)
                line.set_visible(visible)
                grid_lines.append(line)
            ax.set_xticks(long_ticks)  # Устанавливаем метки оси X
            ax.set_yticks(lat_ticks)  # Устанавливаем метки оси Y
            lon_labels = [f"{abs(l)}°{'W' if l<0 else 'E' if l>0 else ''}" for l in long_ticks]  # Формируем подписи для долготы
            lat_labels = [f"{abs(l)}°{'S' if l<0 else 'N' if l>0 else ''}" for l in lat_ticks]  # Формируем подписи для широты
            ax.set_xticklabels(lon_labels)  # Устанавливаем подписи для оси X
            ax.set_yticklabels(lat_labels)  # Устанавливаем подписи для оси Y

        draw_grid_lines(grid_step_var.get(), visible=grid_on)  # Рисуем линии сетки с выбранным шагом

        # ----------------- Создаем область для флажков (Checkbuttons) по плоскостям орбиты ----------------- #
        # Создаем контейнер с возможностью вертикальной прокрутки для размещения флажков
        check_frame_container = tk.Frame(map_window)  # Создаем фрейм-контейнер внутри окна карты
        check_frame_container.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)  # Размещаем контейнер в нижней части окна
        scroll_canvas = tk.Canvas(check_frame_container)  # Создаем холст для прокрутки
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)  # Размещаем холст слева
        scrollbar = ttk.Scrollbar(check_frame_container, orient='vertical', command=scroll_canvas.yview)  # Создаем вертикальную полосу прокрутки
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)  # Размещаем полосу справа
        check_frame = tk.Frame(scroll_canvas)  # Создаем фрейм внутри холста для размещения флажков
        check_frame.bind("<Configure>", lambda event: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all")))  # Настраиваем область прокрутки при изменении размера
        scroll_canvas.create_window((0, 0), window=check_frame, anchor="nw")  # Встраиваем фрейм в холст
        scroll_canvas.configure(yscrollcommand=scrollbar.set)  # Привязываем полосу прокрутки к холсту

        # Создаем флажки для выбора отображения каждого подспутника
        check_vars = [tk.BooleanVar(value=True) for _ in range(total_sub_sats)]  # Список булевых переменных для каждого подспутника (по умолчанию включены)
        select_all_plane_vars = [tk.BooleanVar(value=True) for _ in plane_columns]  # Булевые переменные для выбора всех подспутников в каждой плоскости
        plane_subsat_indices = [[] for _ in plane_columns]  # Список для хранения индексов подспутников по каждой плоскости

        # Строим словарь для сопоставления плоскости с её индексом
        plane_lookup = {}  # Инициализируем пустой словарь
        for plane_idx, (o_i, p_i, plane_lbl) in enumerate(plane_columns):  # Перебираем плоскости с индексами
            plane_lookup[(o_i, p_i)] = plane_idx  # Сохраняем индекс для ключа (индекс спутника, индекс плоскости)

        for i in range(total_sub_sats):  # Для каждого подспутника
            obj_i, p_i = plane_indices[i]  # Получаем индексы спутника и плоскости
            plane_idx = plane_lookup[(obj_i, p_i)]  # Определяем индекс плоскости из словаря
            plane_subsat_indices[plane_idx].append(i)  # Добавляем индекс подспутника в соответствующую группу

        # Функция для перерисовки графика после изменения состояния флажков
        def draw_after_toggling():
            if animation_on_var.get():  # Если анимация включена
                draw_current_frame()  # Рисуем текущий кадр анимации
            else:
                draw_static_plot()  # Рисуем статичный график

        # Размещаем флажки для каждой плоскости в отдельных строках
        for row_i, (obj_i, p_i, plane_lbl) in enumerate(plane_columns):
            # Создаем метку для плоскости в первом столбце
            plane_label = tk.Label(check_frame, text=plane_lbl, font=("TkDefaultFont", 14, "bold"))
            plane_label.grid(row=row_i, column=0, padx=5, pady=2, sticky='w')
            # Флажок "Select All" для плоскости во втором столбце
            def make_plane_select_all_command(plane_index=row_i):
                def command():
                    val = select_all_plane_vars[plane_index].get()  # Получаем текущее состояние флажка "Select All"
                    for sub_i in plane_subsat_indices[plane_index]:  # Для каждого подспутника в данной плоскости
                        check_vars[sub_i].set(val)  # Устанавливаем состояние флажка согласно значению "Select All"
                    draw_after_toggling()  # Перерисовываем график
                return command
            cb_plane_all = tk.Checkbutton(check_frame, text="Select All", variable=select_all_plane_vars[row_i],
                                          command=make_plane_select_all_command(row_i))  # Создаем флажок "Select All" для плоскости
            cb_plane_all.grid(row=row_i, column=1, padx=5, pady=2)  # Размещаем флажок
            # Размещаем индивидуальные флажки для подспутников, начиная со столбца 2
            col_offset = 2  # Смещение для размещения флажков подспутников
            for idx_in_plane, sub_i in enumerate(plane_subsat_indices[row_i]):
                cb_text = sat_labels[sub_i]  # Получаем метку для подспутника
                def on_checkbox_toggled(*args, index=sub_i):
                    draw_after_toggling()  # При изменении состояния флажка перерисовываем график
                check_vars[sub_i].trace_add("write", on_checkbox_toggled)  # Привязываем функцию перерисовки к изменению переменной флажка
                cb = tk.Checkbutton(check_frame, text=cb_text, variable=check_vars[sub_i])  # Создаем флажок для подспутника
                cb.grid(row=row_i, column=col_offset + idx_in_plane, padx=2, pady=2)  # Размещаем флажок в нужной колонке

        # ----------------- Фрейм управления анимацией и сеткой ----------------- #
        control_frame = tk.Frame(map_window)  # Создаем фрейм для элементов управления анимацией
        control_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=5)  # Размещаем фрейм в нижней части окна, растягивая по горизонтали

        # Функция для переключения видимости сетки
        def toggle_grid():
            nonlocal grid_on  # Используем внешнюю переменную grid_on
            grid_on = not grid_on  # Инвертируем значение флага видимости сетки
            for line in grid_lines:  # Для каждой линии сетки
                line.set_visible(grid_on)  # Устанавливаем видимость в соответствии с флагом
            self.canvas.draw()  # Обновляем канву

        toggle_grid_button = tk.Button(control_frame, text="Toggle Grid", command=toggle_grid)  # Создаем кнопку для переключения сетки
        toggle_grid_button.grid(row=0, column=0, padx=5)  # Размещаем кнопку
        grid_step_label = tk.Label(control_frame, text="Grid Step:")  # Создаем метку для выбора шага сетки
        grid_step_label.grid(row=0, column=1, padx=5)  # Размещаем метку
        def on_grid_step_changed(event=None):
            draw_grid_lines(grid_step_var.get(), visible=grid_on)  # Перерисовываем сетку с новым шагом
            if animation_on_var.get():
                draw_current_frame()  # Если анимация включена, рисуем текущий кадр
            else:
                draw_static_plot()  # Иначе рисуем статичный график
            self.canvas.draw()  # Обновляем канву
        grid_step_dropdown = ttk.Combobox(control_frame, textvariable=grid_step_var, values=[15, 30, 45, 60, 90], state='readonly')  # Создаем выпадающий список для шага сетки
        grid_step_dropdown.grid(row=0, column=2, padx=5)  # Размещаем выпадающий список
        grid_step_dropdown.bind("<<ComboboxSelected>>", on_grid_step_changed)  # Привязываем событие выбора к функции изменения шага сетки
        animation_cb = tk.Checkbutton(control_frame, text="Animation", variable=animation_on_var)  # Создаем флажок для включения/выключения анимации
        animation_cb.grid(row=0, column=3, padx=5)  # Размещаем флажок
        stop_button = tk.Button(control_frame, text="Stop", command=self.stop_animation)  # Создаем кнопку для остановки анимации
        stop_button.grid(row=0, column=4, padx=5)  # Размещаем кнопку
        play_button = tk.Button(control_frame, text="Play",
                                command=lambda: self.play_animation(all_datetimes, scatters, check_vars,
                                                                    all_longitudes, all_latitudes, datetime_text, ax))  # Создаем кнопку для запуска анимации
        play_button.grid(row=0, column=5, padx=5)  # Размещаем кнопку
        reset_button = tk.Button(control_frame, text="Reset",
                                 command=lambda: self.reset_animation(scatters, all_longitudes, all_latitudes,
                                                                      check_vars, all_datetimes, datetime_text))  # Создаем кнопку для сброса анимации
        reset_button.grid(row=0, column=6, padx=5)  # Размещаем кнопку
        quit_button = tk.Button(control_frame, text="Quit", command=map_window.destroy)  # Создаем кнопку для закрытия окна карты
        quit_button.grid(row=0, column=7, padx=5)  # Размещаем кнопку

        # Функция, вызываемая при переключении состояния анимации
        def on_animation_toggled(*args):
            if animation_on_var.get():
                stop_button.grid()  # Отображаем кнопку "Stop"
                play_button.grid()  # Отображаем кнопку "Play"
                reset_button.grid()  # Отображаем кнопку "Reset"
                self.stop_animation()  # Останавливаем предыдущую анимацию (если была)
                draw_current_frame()  # Рисуем текущий кадр
            else:
                stop_button.grid_remove()  # Скрываем кнопку "Stop"
                play_button.grid_remove()  # Скрываем кнопку "Play"
                reset_button.grid_remove()  # Скрываем кнопку "Reset"
                self.stop_animation()  # Останавливаем анимацию
                draw_static_plot()  # Рисуем статичный график
        animation_on_var.trace_add("write", on_animation_toggled)  # Привязываем изменение состояния анимации к функции

        # ----------------- Функции для отрисовки графика ----------------- #
        def refresh_legend():
            visible_scatters = [sc for sc in scatters if len(sc.get_xdata()) > 0]  # Находим scatter-объекты с данными
            if visible_scatters:
                ax.legend(handles=visible_scatters, loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')  # Обновляем легенду с видимыми объектами
            else:
                legend = ax.get_legend()  # Если объектов нет, получаем текущую легенду
                if legend:
                    legend.remove()  # Удаляем легенду

        def draw_static_plot():
            for i in range(total_sub_sats):
                if check_vars[i].get():
                    scatters[i].set_data(all_longitudes[i], all_latitudes[i])  # Если флажок включен, отображаем полную траекторию
                else:
                    scatters[i].set_data([], [])  # Иначе очищаем данные
            refresh_legend()  # Обновляем легенду
            datetime_text.set_text(f"Time: {all_datetimes[-1].strftime('%Y-%m-%d %H:%M:%S')}")  # Отображаем последнее время из списка
            self.canvas.draw()  # Обновляем канву

        def draw_current_frame():
            self.update_frame(self.current_frame, all_datetimes, scatters, check_vars,
                              all_longitudes, all_latitudes, datetime_text, ax)  # Обновляем данные для текущего кадра
            self.canvas.draw()  # Рисуем канву

        # Инициализируем scatter-объекты данными для первого кадра
        for i in range(total_sub_sats):
            if check_vars[i].get() and len(all_longitudes[i]) > 0:
                scatters[i].set_data([all_longitudes[i][0]], [all_latitudes[i][0]])  # Устанавливаем первую точку траектории
            else:
                scatters[i].set_data([], [])
        datetime_text.set_text(f"Time: {reference_datetime.strftime('%Y-%m-%d %H:%M:%S')}")  # Отображаем начальное время

        self.canvas = FigureCanvasTkAgg(self.fig, master=map_window)  # Встраиваем фигуру matplotlib в окно карты
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # Размещаем виджет канвы в верхней части окна
        refresh_legend()  # Обновляем легенду
        self.canvas.draw()  # Рисуем канву

        if not animation_on_var.get():
            on_animation_toggled()  # Если анимация выключена, переключаем режим отображения

    # ------------------ Вспомогательные функции для анимации ------------------ #
    def update_frame(self, frame, all_datetimes, scatters, check_vars,
                     all_longitudes, all_latitudes, datetime_text, ax):
        self.current_frame = frame  # Обновляем текущий кадр
        for i, sc in enumerate(scatters):  # Для каждого scatter-объекта
            if check_vars[i].get():  # Если флажок для данного подспутника включен
                if frame < len(all_longitudes[i]):
                    sc.set_data(all_longitudes[i][:frame], all_latitudes[i][:frame])  # Отображаем данные до текущего кадра
                else:
                    sc.set_data([], [])  # Если кадр превышает длину данных, очищаем scatter
            else:
                sc.set_data([], [])
        visible_scatters = [sc for sc in scatters if len(sc.get_xdata()) > 0]  # Находим scatter-объекты с данными
        if visible_scatters:
            ax.legend(handles=visible_scatters, loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')  # Обновляем легенду
        else:
            legend = ax.get_legend()
            if legend:
                legend.remove()  # Удаляем легенду, если данных нет
        if frame < len(all_datetimes):
            datetime_text.set_text(f"Time: {all_datetimes[frame].strftime('%Y-%m-%d %H:%M:%S')}")  # Обновляем текст временной метки
        else:
            datetime_text.set_text("")  # Если кадр вне диапазона, очищаем текст

    def play_animation(self, all_datetimes, scatters, check_vars,
                       all_longitudes, all_latitudes, datetime_text, ax):
        # Создаем новую анимацию, чтобы избежать использования устаревшего event_source
        self.ani = animation.FuncAnimation(
            self.fig,  # Фигура для анимации
            lambda f: self.update_frame(f, all_datetimes, scatters, check_vars,
                                          all_longitudes, all_latitudes, datetime_text, ax),  # Функция обновления кадра
            frames=len(all_datetimes),  # Количество кадров равно числу временных меток
            interval=500,  # Интервал между кадрами (в миллисекундах)
            blit=False,  # Не используем blit для перерисовки
            repeat=False  # Анимация не повторяется после завершения
        )
        if self.ani.event_source is not None:
            self.ani.event_source.start()  # Запускаем event_source анимации
        self.canvas.draw()  # Обновляем канву

    def stop_animation(self):
        if self.ani is not None and hasattr(self.ani, 'event_source') and self.ani.event_source:
            self.ani.event_source.stop()  # Останавливаем анимацию

    def reset_animation(self, scatters, all_longitudes, all_latitudes, check_vars,
                        all_datetimes, datetime_text):
        if self.ani is not None:
            self.ani.event_source.stop()  # Останавливаем текущую анимацию
            self.ani.frame_seq = self.ani.new_frame_seq()  # Сбрасываем последовательность кадров
        self.current_frame = 0  # Сбрасываем текущий кадр
        for i, sc in enumerate(scatters):
            if check_vars[i].get() and len(all_longitudes[i]) > 0:
                sc.set_data([all_longitudes[i][0]], [all_latitudes[i][0]])  # Устанавливаем начальные данные
            else:
                sc.set_data([], [])
        datetime_text.set_text(f"Time: {all_datetimes[0].strftime('%Y-%m-%d %H:%M:%S')}")  # Обновляем временную метку
        self.canvas.draw()  # Обновляем канву

if __name__ == "__main__":
    root = tk.Tk()  # Создаем корневое окно приложения
    app = SatelliteGroundTrackApp(root)  # Создаем экземпляр приложения, передавая корневое окно
    root.mainloop()  # Запускаем главный цикл обработки событий Tkinter
