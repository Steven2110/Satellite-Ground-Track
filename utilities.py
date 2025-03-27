import numpy as np  # Импортируем библиотеку NumPy для работы с массивами и математическими функциями
from astropy.time import Time  # Импортируем класс Time из библиотеки Astropy для работы с астрономическим временем

from constants import GM, W, SatelliteConfig  # Импортируем константы GM, W и класс SatelliteConstants из модуля constants

# Метод Ньютона для решения уравнения Кеплера
def solve_kepler_newton(M, e, tol=1e-15, max_iter=1000):
    # Задаём начальное приближение для эксцентрической аномалии, равное средней аномалии
    E = M
    for _ in range(max_iter):  # Запускаем цикл для итерационного решения до max_iter итераций
        # Вычисляем значение функции f(E) = E - e*sin(E) - M, преобразуя угол в радианы
        f_E = E - e * np.sin(np.radians(E)) - M
        # Вычисляем значение производной функции f'(E) = 1 - e*cos(E)
        f_prime_E = 1 - e * np.cos(np.radians(E))
        
        # Обновляем значение E по формуле метода Ньютона
        E_next = E - f_E / f_prime_E
        
        # Если изменение между текущим и старым значением меньше заданной точности tol то возвращаем текущее значение
        if abs(E - E_next) < tol:
            return E_next
        
        # Обновляем E для следующей итерации
        E = E_next
    # Возвращаем последнее значение E, если достигнуто максимальное число итераций
    return E

def calculate_coordinate(
    semi_major_axis: float, # Длина полуоси орбиты (в км)
    eccentricity: float, # Эксцентриситет орбиты
    longitude_of_ascending_node: float, # Долгота восходящего узла (в градусах)
    argument_pericenter: float, # Аргумент перицентра (в градусах)
    inclination: float, # Наклон орбиты (в градусах)
    mean_anomaly: float, # Средняя аномалия (в градусах)
    delta_t: float # Изменение времени от начального момента (в секундах)
):
    """Вычисляет координаты (x, y, z) на Кеплеровой орбите в момент времени t."""
    
    # Переводим углы из градусов в радианы для последующих вычислений
    i = np.radians(inclination)  # Наклон орбиты в радианах
    Ω = np.radians(longitude_of_ascending_node)  # Долгота восходящего узла в радианах
    ω = np.radians(argument_pericenter)  # Аргумент перицентра в радианах
    M0 = np.radians(mean_anomaly)  # Начальная средняя аномалия в радианах
    
    n = np.sqrt(GM / semi_major_axis**3)  # Вычисляем среднее движение орбиты (радиан/с) по формуле Кеплера
    
    M = M0 + n * delta_t  # Вычисляем среднюю аномалию в момент времени t, прибавляя прирост за время delta_t
    
    E = solve_kepler_newton(M, eccentricity)  # Решаем уравнение Кеплера для нахождения эксцентрической аномалии E с помощью метода Ньютона
    
    v = 2 * np.arctan(np.sqrt((1 + eccentricity) / (1 - eccentricity)) * np.tan(E / 2))  # Вычисляем истинную аномалию (v) через эксцентрическую аномалию
    
    r = semi_major_axis * (1 - eccentricity**2) / (1 + eccentricity * np.cos(v))  # Вычисляем радиальное расстояние от фокуса до спутника
    
    u = v + ω  # Вычисляем аргумент широты (u) как сумму истинной аномалии и аргумента перицентра
    
    x_orb = r * np.cos(u)  # Вычисляем x-координату в орбитальной плоскости
    y_orb = r * np.sin(u)  # Вычисляем y-координату в орбитальной плоскости
    
    # Преобразуем координаты из орбитальной плоскости в инерциальную систему координат (ECI)
    x = x_orb * np.cos(Ω) - y_orb * np.sin(Ω) * np.cos(i)  # Вычисляем x-компоненту в ECI
    y = x_orb * np.sin(Ω) + y_orb * np.cos(Ω) * np.cos(i)  # Вычисляем y-компоненту в ECI
    z = y_orb * np.sin(i)  # Вычисляем z-компоненту в ECI
    
    return x, y, z  # Возвращаем кортеж координат (x, y, z)

def calculate_siderial_time(initial_date, t):
    tu = (initial_date - 2451545.0) / 36525.0  # Вычисляем количество юлианских столетий, прошедших с эпохи J2000
    H0 = 24110.54841 + 8640184.812866 * tu + 0.093104 * tu**2 - 6.21e-6 * tu**3  # Вычисляем начальное звездное время (в секундах) для эпохи J2000
    
    H = H0 + W * t  # Корректируем звездное время с учетом прошедшего времени t
    return H  # Возвращаем вычисленное звездное время

def generate_transition_matrix(H):
    # Создаем матрицу перехода, которая осуществляет поворот координат на угол H вокруг оси Z
    return np.array([
        [np.cos(H), np.sin(H), 0],  # Компоненты новой оси x
        [-np.sin(H), np.cos(H), 0],  # Компоненты новой оси y
        [0, 0, 1]  # Ось z остаётся неизменной
    ])
    
def calculate_longitudes_latitudes(
    satellite: SatelliteConfig,  # Объект с параметрами спутника
    date: Time,  # Дата наблюдения (объект Time из Astropy)
    dt: float = 0.01  # Относительный шаг времени для дискретизации периода
):  
    T = satellite.T  # Получаем период орбиты спутника из объекта satellite
    time_steps = np.linspace(0, T, int(T / (dt * T)) + 1)  # Генерируем равномерно распределённые временные шаги от 0 до T
    
    all_longitudes = []  # Список для хранения долгот для всех вариантов орбитальных параметров
    all_latitudes = []  # Список для хранения широт для всех вариантов орбитальных параметров
    
    # Перебираем все значения долготы восходящего узла из спутниковых параметров
    for i in range(len(satellite.longitude_of_ascending_node)):
        # Перебираем все значения аргумента перицентра из спутниковых параметров
        for j in range(len(satellite.argument_pericenter)):
            longitudes_n = []  # Список долгот для текущей комбинации орбитальных параметров
            latitudes_n = []  # Список широт для текущей комбинации орбитальных параметров
            # Проходим по каждому временно шагу
            for time_step in time_steps:
                H = calculate_siderial_time(initial_date=date.jd, t=time_step)  # Вычисляем звездное время для текущего временного шага

                # Вычисляем координаты спутника в инерциальной системе координат по текущим орбитальным параметрам
                initial_coordinate = calculate_coordinate(
                    semi_major_axis=satellite.semi_major_axis,  # Полуось орбиты
                    eccentricity=satellite.eccentricity,  # Эксцентриситет орбиты
                    longitude_of_ascending_node=satellite.longitude_of_ascending_node[i],  # Текущая долгота восходящего узла
                    argument_pericenter=satellite.argument_pericenter[j],  # Текущий аргумент перицентра
                    inclination=satellite.inclination,  # Наклон орбиты
                    mean_anomaly=satellite.mean_anomaly,  # Средняя аномалия
                    delta_t=time_step  # Текущий временной шаг
                )
                
                # Генерируем матрицу перехода на основе звездного времени
                A = generate_transition_matrix(H=H)
                # Преобразуем координаты в инерциальную систему координат с помощью матричного умножения
                coordinate = A @ initial_coordinate

                x, y, z = coordinate[0], coordinate[1], coordinate[2]  # Извлекаем компоненты координат
                r = np.linalg.norm(coordinate)  # Вычисляем модуль вектора координат (расстояние от центра)
                longitude = np.degrees(np.arctan2(y, x))  # Вычисляем долготу, переводя результат из радиан в градусы
                latitude = np.degrees(np.arcsin(z / r))  # Вычисляем широту, переводя результат из радиан в градусы
                
                longitudes_n.append(longitude)  # Добавляем вычисленную долготу в список для данной комбинации параметров
                latitudes_n.append(latitude)  # Добавляем вычисленную широту в список для данной комбинации параметров

            all_longitudes.append(longitudes_n)  # Добавляем список долгот для текущей комбинации в общий список
            all_latitudes.append(latitudes_n)  # Добавляем список широт для текущей комбинации в общий список
        
    return all_longitudes, all_latitudes  # Возвращаем два списка: все вычисленные долготы и широты