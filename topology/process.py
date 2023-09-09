import numpy as np
import torch


class Items:
    pos: torch.Tensor  # (N, 3) positions of center of mass
    mass: torch.Tensor  # (N,) masses in kg
    bbox: torch.Tensor  # (N, 2, 3) -- ((x, y, z) relative to center, (Wx, Wy, Wz))

    main_bbox: torch.Tensor

    def __init__(
            self,
            pos: np.ndarray,
            mass: np.ndarray,
            bbox: np.ndarray,
            main_bbox: np.ndarray,
            safe_dist: float = 0.1
    ):
        self.pos = torch.tensor(pos, dtype=torch.float32)
        self.mass = torch.tensor(mass, dtype=torch.float32)
        self.bbox = torch.tensor(bbox, dtype=torch.float32)
        self.main_bbox = torch.tensor(main_bbox, dtype=torch.float32)
        self.safe_dist = safe_dist

    def optimize(self, scene: "Scene" = None, stop_p=1e-3):
        prev_loss = [self.get_all_loss()]
        N_history = 100

        params = [self.pos]
        for param in params:
            param.requires_grad = True
        optimizer = torch.optim.Adam(params, lr=self.safe_dist, betas=(0.9, 0.999), eps=1e-8)

        while len(prev_loss) < N_history or np.std(prev_loss) > stop_p * np.average(prev_loss):
            optimizer.zero_grad()
            loss = self.get_all_loss()
            loss.backward()
            optimizer.step()

            prev_loss += [loss.item()]
            prev_loss = prev_loss[-N_history:]

            if scene is not None:
                scene.show(self)

        for param in params:
            param.requires_grad = False

    def get_all_loss(self):
        loss = 0

        # collision
        loss = loss + self.collision_loss()

        # collision with bounding overall box
        loss = loss + 10 * self.main_bbox_loss()

        # to stick every box to center axis
        loss = loss + self.pos[:, 0].abs()

        # summarize loss over all boxes
        loss = loss.mean()

        # stick center of mass to center of platform
        loss = loss + 10 * self.center_of_mass().norm()

        return loss

    def get_abs_bbox(self):
        return torch.stack([
            self.pos + self.bbox[..., 0, :],
            self.bbox[..., 1, :]
        ], dim=-2)

    def get_box_dist(self) -> torch.Tensor:
        bbox = self.get_abs_bbox()

        dist = torch.abs(bbox[None, :, 0, :] - bbox[:, None, 0, :]) - (bbox[None, :, 1, :] + bbox[:, None, 1, :]) / 2

        dist_max = torch.max(dist, dim=-1).values
        dist_sum = dist.prod(dim=-1)
        dist_far = dist.clip(1e-12, None).square().sum(dim=-1).sqrt()
        mask = dist_max > 0

        dist = dist_sum * ~mask + dist_far * mask
        return dist

    def get_main_bbox_dist(self, main_bbox) -> torch.Tensor:
        bbox = self.get_abs_bbox()

        dist = torch.abs(main_bbox[None, 0, :] - bbox[:, 0, :]) - (main_bbox[None, 1, :] - bbox[:, 1, :]) / 2
        dist = torch.max(dist, dim=-1).values
        dist = -dist

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

    def collision_loss(self) -> torch.Tensor:
        box_dist = self.get_box_dist()
        loss = self.safe_exp_loss(-box_dist, self.safe_dist)
        loss = loss.sum(dim=-1)
        return loss

    def main_bbox_loss(self):
        box_dist = self.get_main_bbox_dist(self.main_bbox)
        loss = self.safe_exp_loss(-box_dist, self.safe_dist)
        return loss
