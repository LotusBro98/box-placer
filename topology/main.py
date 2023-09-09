import numpy as np
import torch
import cv2 as cv


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
        # dist = torch.max(dist, dim=-1).values
        dist_max = torch.max(dist, dim=-1).values
        dist_sum = dist.prod(dim=-1)
        dist_far = dist.clip(1e-12, None).square().sum(dim=-1).sqrt()
        mask = dist_max > 0

        dist = dist_sum * ~mask + dist_far * mask
        return dist

    def get_main_bbox_dist(self, main_bbox) -> torch.Tensor:
        bbox = self.get_abs_bbox()

        # torch.abs(items.pos[:, 0]) - 5 + items.bbox[:, 1, 0] / 2
        dist = torch.abs(main_bbox[None, 0, :] - bbox[:, 0, :]) - (main_bbox[None, 1, :] - bbox[:, 1, :]) / 2
        dist = torch.max(dist, dim=-1).values
        dist = -dist
        # print(dist)

        return dist

    def get_center_dist(self) -> torch.Tensor:
        bbox = self.get_abs_bbox()

        dist = (
            torch.linalg.norm(bbox[None, :, 0, :] - bbox[:, None, 0, :], dim=-1, ord=2)# -
            # torch.linalg.norm(bbox[None, :, 1, :] - bbox[:, None, 1, :], dim=-1, ord=3) / 2
        )

        return dist

    def center_of_mass(self):
        return (self.mass[:, None] * self.pos).sum(dim=0) / self.mass.sum()

    @staticmethod
    def safe_exp_loss(x, x0, p1=1):
        return (
            torch.exp((x / x0).clip(None, p1)) +
            np.exp(p1) * ((x / x0) - p1).clip(0, None) +
            ((x / x0) - p1).clip(0, None).square() / 2
        )

    def collision_loss(self, safe_dist) -> torch.Tensor:
        box_dist = self.get_box_dist()
        loss = self.safe_exp_loss(-box_dist, safe_dist)
        loss = loss.sum(dim=-1)
        return loss

    def main_bbox_loss(self, main_bbox, safe_dist):
        box_dist = self.get_main_bbox_dist(main_bbox)
        loss = self.safe_exp_loss(-box_dist, safe_dist)
        return loss


class Scene:
    size: np.ndarray        # image size in pixels
    viewport: np.ndarray    # (2, 3)    (center, size)

    def __init__(self, size, viewport):
        self.size = size
        self.viewport = viewport

    def draw_bbox(self, bbox, image, color):
        bbox = bbox[:, :2].copy()
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

    def draw_text(self, pt, text, image, color):
        pt = pt[:2].copy()
        pt -= self.viewport[0]
        pt /= self.viewport[1]
        pt += 0.5
        pt *= self.size
        pt = np.int32(pt)
        cv.putText(image, text, pt, cv.FONT_HERSHEY_SIMPLEX, 0.5, color)

    def draw_point(self, point, image, color):
        pt = point[:2].copy()
        pt -= self.viewport[0]
        pt /= self.viewport[1]
        pt += 0.5
        pt *= self.size
        pt = np.int32(pt)
        cv.drawMarker(image, pt, color, markerType=cv.MARKER_CROSS, markerSize=20)

    @torch.no_grad()
    def draw_items(self, image, items: Items, losses):
        bbox_all = items.get_abs_bbox().numpy()
        # dist = items.get_main_bbox_dist(main_bbox)
        for i, bbox in enumerate(bbox_all):
            self.draw_bbox(bbox, image, (0, 255, 0))
            self.draw_text(bbox[0] - bbox[1]*(0.5, 0, 0), f"{losses[i]:.3f}", image, (0, 0, 255))

    @torch.no_grad()
    def draw_center_of_mass(self, image, items: Items):
        com = items.center_of_mass().numpy()
        self.draw_point(com, image, (255, 0, 0))

    def show(self, items: Items, main_bbox, losses):
        image = np.zeros(tuple(self.size[::-1]) + (3,), dtype=np.uint8)
        self.draw_items(image, items, losses)
        self.draw_bbox(main_bbox.numpy(), image, (0, 0, 255))
        self.draw_center_of_mass(image, items)
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

    main_bbox = torch.tensor([
        [0, 0, 0],
        [3, 10, 10]
    ], dtype=torch.float32)

    N_items = 7
    items = Items(
        pos=np.random.uniform(low=-5, high=5, size=(N_items, 3)) * [1, 1, 0],
        mass=np.random.normal(loc=1, scale=0.01, size=(N_items,)),
        bbox=np.stack([
            [[0, 0, 0]] * N_items,
            np.random.normal(loc=(1, 2, 1), scale=0.2, size=(N_items, 3))
        ], axis=-2)
    )
    params = [items.pos]
    for param in params:
        param.requires_grad = True

    safe_dist = 0.1
    optimizer = torch.optim.Adam(params, lr=safe_dist, betas=(0.9, 0.999), eps=1e-8)

    while True:
        optimizer.zero_grad()
        loss = 0
        loss = loss + items.collision_loss(safe_dist)
        loss = loss + 10 * items.main_bbox_loss(main_bbox, safe_dist)
        loss = loss + 1 * items.pos[:, 0].abs()
        # loss = loss + 10 * items.pos[:, 1].abs()
        # loss += torch.linalg.norm(items.pos, dim=-1).mean()

        # bad = torch.argwhere((loss > (loss.mean() * 1.1)))[:, 0]
        losses = loss / loss.mean()
        loss = loss.mean()

        # print(items.center_of_mass())
        loss = loss + 10 * items.center_of_mass().norm()

        loss.backward()
        optimizer.step()

        # print(bad.shape)
        # with torch.no_grad():
        #     shift = torch.randn(items.pos[bad].shape) * safe_dist * 5
        #     shift *= np.array([1, 1, 0])
        #     items.pos[bad] += shift

        scene.show(items, main_bbox, losses)

    with torch.no_grad():
        pos = items.pos.numpy()
        center = items.bbox[:, 0].numpy()
        pos, center = pos + center, -center
        dims = items.bbox[:, 1].numpy()
        mass = items.mass.numpy()
        for i in range(len(items.pos)):
            print(pos[i], center[i], dims[i], mass[i])


if __name__ == '__main__':
    main()
