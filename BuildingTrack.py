import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, sin, cos, pi, atan2, degrees, atan

# Константы
R = 6371
w_earth = 7.29 * (10 ** (-5))

# Зададим орбиту с помощью кеплеровских элементов
a = 26557.559030
e = 0.6910996
i = (63.5089 / 180) * pi
raan = (213.8149 / 180) * pi
w = (281.3930 / 180) * pi


def plot_spherical_points(fi_1, fi_2, radius, point_color='red'):
    fi_1_rad = np.radians(fi_1)  # radians для каждого элемента массива (долгота)
    fi_2_rad = np.radians(fi_2)  # пересчитывает градусы в радианы      (широта)

    # считаем декартовые координаты точек (x, y, z), которые отображают проекцию спутника в данный момент на сферу
    x = radius * np.cos(fi_2_rad) * np.cos(fi_1_rad)
    y = radius * np.cos(fi_2_rad) * np.sin(fi_1_rad)
    z = radius * np.sin(fi_2_rad)

    # plt.figure - функция, которая создаёт новый объект фигуры, который содержит все элементы графика: оси, точки, линии, объекты

    fig = plt.figure(figsize=(20, 16))  # параметр "figsize" задает размер фигуры в дюймах
    # функиця fig.add_subplot добавляет к созданной фигуре подграфик и настраивает его как трехмерный, создается объект Axes3D
    ax = fig.add_subplot(111, projection='3d')

    u = np.linspace(0, 2 * np.pi, 100)  # создаём массив для первой сферической координаты на отрезке [0; 2*pi]
    v = np.linspace(0, np.pi, 100)  # создаем массив для второй сферической координаты на отрезке [0; pi]
    # вычисляется для каждой заданной в предыдущих массивах точки координата x (используется аппарат внешнего произведения, т. е. создается массив 100 на 100)
    sphere_x = radius * np.outer(np.cos(u), np.sin(v))
    # аналогично вычисляется y                                                 (в этом массиве a[i][j] = u[i] * v[j])
    sphere_y = radius * np.outer(np.sin(u), np.sin(v))
    # для координаты z искуственно задаётся массив из 100 единиц np.ones размером с массив u, дальше как и раньше
    sphere_z = radius * np.outer(np.ones(np.size(u)), np.cos(v))

    ax.plot_surface(sphere_x, sphere_y, sphere_z, color='yellow', alpha=0.35, edgecolor='none')

    # метод plot_surface объекта Axes3D строит трехмерную поверхность: первые три аргумента это ранее заданные координаты точек сферы
    # alpha - параметр прозрачности (35%)

    # используя метод scatter объекта Axes3D строим точки, которые посчитаны решением уравнения Эйлера; параметр s=50 задаёт размер точек
    ax.scatter(x, y, z, color=point_color, s=50)

    ax.set_xlabel('X')  # название осей координат: X, Y и Z соответственно
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.set_title('Подспутниковая трасса Молния 3-50 на сферическую Землю')  # а также название самого рисунка

    ax.grid(True)  # отражаем сетку

    ax.set_box_aspect([1, 1, 1])  # для равных масштабов по всем осям устанавливаем соотношение

    plt.show()  # выводим результат на экран


def orbit_to_geocentric(orbit_coords, i, raan, w):

    # найдем нужные компоненты для матрицы поворота

    cos_O = cos(-raan)
    sin_O = sin(-raan)
    cos_i = cos(-i)
    sin_i = sin(-i)
    cos_w = cos(-w)
    sin_w = sin(-w)

    # запишем формулу матрицы поворота вокруг трёх осей X, Y, Z

    rotation_matrix = np.array([
        [cos_O * cos_w - sin_O * sin_w * cos_i, -cos_O * sin_w - sin_O * cos_w * cos_i, sin_O * sin_i],
        [sin_O * cos_w + cos_O * sin_w * cos_i, -sin_O * sin_w + cos_O * cos_w * cos_i, -cos_O * sin_i],
        [sin_w * sin_i, cos_w * sin_i, cos_i]
    ])

    geocen_coords = rotation_matrix @ orbit_coords

    return geocen_coords


# Функция для вычисления географических координат из геоцентрических
def geocentric_to_geografh(r_geo, t):
    x, y, z = r_geo
    # функция degrees переводит значения углов из радиан в градусы; делением на 360 приводит градусы к (-360; 360)
    fi_1 = (degrees(atan2(y, x)) - degrees(w_earth * t)) % 360
    fi_2 = degrees(atan(z / sqrt(x**2 + y**2)))
    return fi_2, fi_1

if __name__ == "__main__":

    fi_2 = []  # широта
    fi_1 = []  # долгота

    with open("File_Nu.txt", "r") as file:
        str = file.readline()
        while str != '':
            index = str.find(' ')
            t, true_anomaly = float(str[:index]), float(str[index + 1:-1])
            r = a * (1 - e ** 2) / (1 + e * cos(true_anomaly))

            # координаты в орбитальной системе системе
            orbit_coords = np.array([r * cos(true_anomaly), r * sin(true_anomaly), 0])

            # координаты в геоцентрической системе координат
            geocen_coords = orbit_to_geocentric(orbit_coords, i, raan, w)

            # в конце переведём геоцентрические координаты в географические
            curr_fi_2, curr_fi_1 = geocentric_to_geografh(geocen_coords, t)
            fi_2.append(curr_fi_2)
            fi_1.append(curr_fi_1)

            str = file.readline()

    plot_spherical_points(fi_1, fi_2, radius=R, point_color='red')