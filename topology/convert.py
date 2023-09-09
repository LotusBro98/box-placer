import numpy as np

from topology.process import Items
from validation.models import Carriage, Box

PLATFORM_HEIGHT = 5


def build_items(platform: Carriage, boxes: list[Box]) -> Items:
    main_bbox = np.array([
        [0, 0, 0],
        [
            platform.floor_width / 1000,
            platform.floor_length / 1000,
            PLATFORM_HEIGHT * 2
        ]
    ])

    dimensions = np.stack([np.array(box.dimensions, np.float32) for box in boxes], axis=0)
    bbox = np.stack([
        np.zeros_like(dimensions),
        dimensions[..., [1, 0, 2]] / 1000
    ], axis=-2)

    masses = np.stack([box.weight for box in boxes], axis=0)
    masses = masses * 1000

    items = Items(masses, bbox, main_bbox)
    return items


def fill_boxes_positions(items: Items, boxes: list[Box]):
    positions = items.pos.numpy()
    centers = items.bbox[:, 0].numpy()
    dimensions = items.bbox[:, 1].numpy()
    main_bbox = items.main_bbox.numpy()

    # positions - geometrical center, center - relative center of mass
    positions, centers = positions + centers, -centers
    positions[..., 2] = dimensions[..., 2] / 2
    positions[..., 1] = positions[..., 1] - main_bbox[0][1] + main_bbox[1][1] / 2
    positions = positions[..., [1, 0, 2]] * 1000

    for box, pos in zip(boxes, positions):
        box.coords_of_cg = tuple(np.int32(pos).tolist())
        print(box)
