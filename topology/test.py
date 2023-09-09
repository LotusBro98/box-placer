import numpy as np

from topology.process import Items
from topology.display import Scene


def main():
    scene = Scene(
        np.array([1000, 1000]),
        np.array([
            [0, 0],
            [20, 20]
        ])
    )

    N_items = 7
    items = Items(
        mass=np.random.normal(loc=1, scale=0.01, size=(N_items,)),
        bbox=np.stack([
            [[0, 0, 0]] * N_items,
            np.random.normal(loc=(1, 2, 1), scale=0.2, size=(N_items, 3))
        ], axis=-2),
        main_bbox=np.array([
            [0, 0, 0],
            [3, 10, 10]
        ])
    )

    items.optimize(scene)


if __name__ == '__main__':
    main()
