import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

# Создаем фигуру и трехмерную область для отображения
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Определяем вершины и грани параллелепипедов
# В этом примере определим два параллелепипеда

# Параллелепипед 1
vertices1 = np.array([
    [0, 0, 0],
    [1, 0, 0],
    [1, 1, 0],
    [0, 1, 0],
    [0, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 1, 1]
])

faces1 = [
    [vertices1[0], vertices1[1], vertices1[2], vertices1[3]],
    [vertices1[4], vertices1[5], vertices1[6], vertices1[7]],
    [vertices1[0], vertices1[1], vertices1[5], vertices1[4]],
    [vertices1[2], vertices1[3], vertices1[7], vertices1[6]],
    [vertices1[0], vertices1[3], vertices1[7], vertices1[4]],
    [vertices1[1], vertices1[2], vertices1[6], vertices1[5]]
]

# Параллелепипед 2
vertices2 = vertices1 + [2, 2, 2]  # Сдвигаем вершины для второго параллелепипеда

faces2 = [
    [vertices2[0], vertices2[1], vertices2[2], vertices2[3]],
    [vertices2[4], vertices2[5], vertices2[6], vertices2[7]],
    [vertices2[0], vertices2[1], vertices2[5], vertices2[4]],
    [vertices2[2], vertices2[3], vertices2[7], vertices2[6]],
    [vertices2[0], vertices2[3], vertices2[7], vertices2[4]],
    [vertices2[1], vertices2[2], vertices2[6], vertices2[5]]
]

# Создаем Poly3DCollection для обоих параллелепипедов
poly1 = Poly3DCollection(faces1, alpha=0.25, linewidths=1, edgecolors='r', facecolors='b')
poly2 = Poly3DCollection(faces2, alpha=0.25, linewidths=1, edgecolors='g', facecolors='y')

# Добавляем Poly3DCollection на график
ax.add_collection3d(poly1)
ax.add_collection3d(poly2)

# Настраиваем оси и лимиты графика
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_xlim(0, 5)
ax.set_ylim(0, 5)
ax.set_zlim(0, 5)

plt.show()
