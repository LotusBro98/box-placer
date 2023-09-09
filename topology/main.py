import numpy as np
import torch
import cv2 as cv


class Item:
    pos: torch.Tensor     # position of center of mass
    mass: float         # mass in kg
    bbox: torch.Tensor    # (2, 3) -- ((x, y, z) relative to center, (Wx, Wy, Wz))

    def __init__(self, pos: np.ndarray, mass: float, bbox: np.ndarray):
        self.pos = torch.tensor(pos, dtype=torch.float32)
        self.mass = mass
        self.bbox = torch.tensor(bbox, dtype=torch.float32)

    def get_abs_bbox(self):
        return torch.stack([
            self.pos + self.bbox[0],
            self.bbox[1]
        ], dim=0)

    @staticmethod
    def get_min_dist(a: "Item", b: "Item") -> torch.Tensor:
        bbox1 = a.get_abs_bbox()
        bbox2 = b.get_abs_bbox()

        dist = torch.abs(bbox1[0] - bbox2[0]) - (bbox1[1] + bbox2[1]) / 2
        dist = torch.max(dist, dim=-1).values

        return dist

    @staticmethod
    def collision_loss(a: "Item", b: "Item", safe_dist) -> torch.Tensor:
        dist = Item.get_min_dist(a, b)
        loss = torch.exp(-dist / safe_dist)
        return loss



class Scene:

    size: np.ndarray        # image size in pixels
    viewport: np.ndarray    # (2, 3)    (center, size)

    def __init__(self, size, viewport):
        self.size = size
        self.viewport = viewport

    @torch.no_grad()
    def draw_item(self, image, item: Item):
        bbox = item.get_abs_bbox().numpy()
        bbox = bbox[:, :2]
        bbox[0] -= self.viewport[0]
        bbox /= self.viewport[1]
        bbox[0] += 0.5
        bbox *= self.size
        bbox = np.int32(bbox)
        bbox = np.int32(np.stack([
            bbox[0] - bbox[1] / 2,
            bbox[0] + bbox[1] / 2,
        ], axis=0))
        cv.rectangle(image, bbox[0], bbox[1], (0, 255, 0))

    def show(self, items: list[Item]):
        image = np.zeros(tuple(self.size[::-1]) + (3,), dtype=np.uint8)
        for item in items:
            self.draw_item(image, item)
        print(np.max(image), np.min(image), image.shape)
        cv.imshow("Scene", image)
        cv.waitKey(1)


def main():
    item1 = Item(
        [1, 0, 0],
        1,
        [
            [0, 0, 0],
            [2, 1, 1]
        ]
    )

    item2 = Item(
        [-10, 0, 0],
        1,
        [
            [0, 0, 0],
            [3, 1, 1]
        ]
    )

    scene = Scene(
        np.array([500, 500]),
        np.array([
            [0, 0],
            [20, 20]
        ])
    )

    items = [
        Item(
            pos=np.array(np.random.normal(loc=0, scale=7, size=(3,))) * [1, 1, 0],
            mass=1,
            bbox=np.array([
                [0, 0, 0],
                np.random.normal(loc=(1, 2, 1), scale=0.01, size=(3,))
            ])
        )
        for i in range(20)
    ]
    params = [item.pos for item in items]
    for param in params:
        param.requires_grad = True

    optimizer = torch.optim.Adam(params, lr=0.01)
    safe_dist = 0.1

    i = 0
    while True:
        i += 1
        with torch.no_grad():
            for item in items:
                item.pos[-1] = 0
        safe_dist *= 1 - 0.001

        optimizer.zero_grad()
        loss: torch.Tensor = 0
        for item1 in items:
            for item2 in items:
                if item1 == item2:
                    continue
                with torch.no_grad():
                    dist = torch.linalg.norm(item1.pos - item2.pos)
                    mindist = torch.linalg.norm(item1.bbox[1]) + torch.linalg.norm(item2.bbox[1])

                if dist > mindist:
                    continue

                loss += Item.collision_loss(item1, item2, safe_dist)

            loss += torch.linalg.norm(item1.pos)
        loss.backward()
        optimizer.step()
        if i % 10 == 0:
            scene.show(items)


if __name__ == '__main__':
    main()
