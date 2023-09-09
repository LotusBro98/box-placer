import numpy as np
import torch
import cv2 as cv

torch.autograd.set_detect_anomaly(True)
class Items:
    pos: torch.Tensor     # (N, 3) positions of center of mass
    mass: torch.Tensor    # (N,) masses in kg
    bbox: torch.Tensor    # (N, 2, 3) -- ((x, y, z) relative to center, (Wx, Wy, Wz))

    def __init__(self, pos: np.ndarray, mass: np.ndarray, bbox: np.ndarray):
        self.pos = torch.tensor(pos, dtype=torch.float32)
        self.mass = torch.tensor(mass, dtype=torch.float32)
        self.bbox = torch.tensor(bbox, dtype=torch.float32)

    def get_abs_bbox(self):
        return torch.stack([
            self.pos + self.bbox[..., 0, :],
            self.bbox[..., 1, :]
        ], dim=-2)

    def get_box_dist(self) -> torch.Tensor:
        bbox = self.get_abs_bbox()

        dist = torch.abs(bbox[None, :, 0, :] - bbox[:, None, 0, :]) - (bbox[None, :, 1, :] + bbox[:, None, 1, :]) / 2
        dist = torch.max(dist, dim=-1).values

        return dist

    def get_center_dist(self) -> torch.Tensor:
        bbox = self.get_abs_bbox()

        dist = (
            torch.linalg.norm(bbox[None, :, 0, :] - bbox[:, None, 0, :], dim=-1, ord=2) -
            torch.linalg.norm(bbox[None, :, 1, :] - bbox[:, None, 1, :], dim=-1, ord=3) / 2
        )

        return dist

    def center_of_mass(self):
        return (self.mass[:, None] * self.pos).sum(dim=0) / self.mass.sum()

    @staticmethod
    def safe_exp_loss(x, x0, p1=7):
        return (
            torch.exp((x / x0).clip(None, p1)) +
            np.exp(p1) * ((x / x0) - p1).clip(0, None) +
            ((x / x0) - p1).clip(0, None).square() / 2
        )

    def collision_loss(self, safe_dist) -> torch.Tensor:
        N = self.pos.shape[0]

        box_dist = self.get_box_dist()
        center_dist = self.get_center_dist()
        loss = 0
        # loss = loss + safe_dist / box_dist
        loss = loss - 100 * safe_dist / center_dist.clip(1e-9, None)
        loss = loss + self.safe_exp_loss(-box_dist, safe_dist)
        # loss = loss + self.safe_exp_loss(-center_dist, safe_dist)
        # loss = loss + torch.exp(-center_dist / safe_dist)
        loss = loss[torch.eye(N) == 0]
        loss = loss.sum(dim=-1)
        return loss


class Scene:
    size: np.ndarray        # image size in pixels
    viewport: np.ndarray    # (2, 3)    (center, size)

    def __init__(self, size, viewport):
        self.size = size
        self.viewport = viewport

    def draw_bbox(self, bbox, image, color):
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
        cv.rectangle(image, bbox[0], bbox[1], color)

    # def draw_point(self, point, image, color):
    #     cv.drawMarker(image, )

    @torch.no_grad()
    def draw_items(self, image, items: Items):
        bbox_all = items.get_abs_bbox().numpy()
        for bbox in bbox_all:
            self.draw_bbox(bbox, image, (0, 255, 0))

        bbox_all = np.array([[0, 0, 0], [10, 10, 10]], dtype=np.float32)
        self.draw_bbox(bbox_all, image, (0, 0, 255))

    # @torch.no_grad()
    # def draw_center_of_mass(self, items: Items):
    #     com = items.center_of_mass()

    def show(self, items: Items):
        image = np.zeros(tuple(self.size[::-1]) + (3,), dtype=np.uint8)
        self.draw_items(image, items)
        cv.imshow("Scene", image)
        cv.waitKey(1)


def main():
    scene = Scene(
        np.array([1000, 1000]),
        np.array([
            [0, 0],
            [20, 20]
        ])
    )

    N_items = 20
    items = Items(
        pos=np.random.uniform(low=-5, high=5, size=(N_items, 3)) * [1, 1, 0],
        mass=np.random.normal(loc=1, scale=0.01, size=(N_items,)),
        bbox=np.stack([
            [[0, 0, 0]] * N_items,
            np.random.normal(loc=(1, 2, 1), scale=0.001, size=(N_items, 3))
        ], axis=-2)
    )
    params = [items.pos]
    for param in params:
        param.requires_grad = True

    optimizer = torch.optim.Adam(params, lr=0.1)
    safe_dist = 0.05

    i = 0
    while True:
        i += 1
        # safe_dist *= 1 - 0.001
        # print(safe_dist)
        # if i % 10 == 0:
        #     with torch.no_grad():
        #         items.pos += torch.randn(items.pos.shape) * safe_dist * 1

        optimizer.zero_grad()
        loss = 0
        loss = loss + items.collision_loss(safe_dist)
        loss = loss + 10 * items.safe_exp_loss(torch.abs(items.pos[:, 0]) - 5 + items.bbox[:, 1, 0] / 2, safe_dist)
        loss = loss + 10 * items.safe_exp_loss(torch.abs(items.pos[:, 1]) - 5 + items.bbox[:, 1, 1] / 2, safe_dist)
        loss = loss + 100 * items.pos[:, 0].abs()
        # loss = loss + torch.exp((torch.abs(items.pos[:, 0]) - 5 + items.bbox[:, 1, 0] / 2) / 0.1).mean() * 1
        # loss = loss + torch.exp((torch.abs(items.pos[:, 1]) - 5 + items.bbox[:, 1, 1] / 2) / 0.1).mean() * 1
        # loss += torch.linalg.norm(items.pos, dim=-1).mean()
        bad = torch.argwhere(loss > 1000)[:, 0]
        loss = loss.mean()

        print(items.center_of_mass())
        loss = loss + 1000 * items.center_of_mass().norm()

        loss.backward()
        optimizer.step()

        print(bad.shape)
        # with torch.no_grad():
        #     items.pos[bad] += torch.randn(items.pos[bad].shape) * safe_dist * 10

        scene.show(items)


if __name__ == '__main__':
    main()
