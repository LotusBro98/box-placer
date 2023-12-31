import numpy as np

from documentgen.drawing import generate_drawing
from topology.convert import build_items, fill_boxes_positions
from topology.process import Items
from topology.display import Scene
from validation.models import Carriage, Box


def calculate_optimal_placement(platform: Carriage, boxes: list[Box], visualise=False):
    if visualise:
        scene = Scene(
            np.array([1000, 1000]),
            np.array([[0, 0], [20, 20]])
        )
    else:
        scene = None

    items = build_items(platform, boxes)
    items.optimize(scene)
    fill_boxes_positions(items, boxes)


def main():
    platform = Carriage(floor_length=13300, floor_width=2870, weight=21, height_from_rails=1310,
                        cg_height_from_rails=800, base_length=9720, length_to_cg=6650, s_side_surface_meters=7)
    boxes = [
        Box(coords_of_cg=(3055, 0, 1500 / 2), dimensions=(3650, 3320, 1500), weight=6.670),
        Box(coords_of_cg=(10915, 0, 1020 / 2), dimensions=(3870, 2890, 1020), weight=4.085),
        Box(coords_of_cg=(690, 0, 390 / 2), dimensions=(1080, 1580, 390), weight=0.395),
        Box(coords_of_cg=(6930, 0, 1150 / 2), dimensions=(4100, 1720, 1150), weight=1.865),
    ]

    calculate_optimal_placement(platform, boxes, visualise=True)

    b = generate_drawing(platform, boxes)
    with open("out.svg", "wb+") as f:
        f.write(b)


if __name__ == '__main__':
    main()
