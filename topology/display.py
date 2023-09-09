import numpy as np
import torch
import cv2 as cv

from topology.process import Items


class Scene:
    size: np.ndarray  # image size in pixels
    viewport: np.ndarray  # (2, 3)    (center, size)

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
    def draw_items(self, image, items: Items):
        bbox_all = items.get_abs_bbox().numpy()
        # dist = items.get_main_bbox_dist(main_bbox)
        for i, bbox in enumerate(bbox_all):
            self.draw_bbox(bbox, image, (0, 255, 0))
            # self.draw_text(bbox[0] - bbox[1] * (0.5, 0, 0), f"{losses[i]:.3f}", image, (0, 0, 255))

    @torch.no_grad()
    def draw_center_of_mass(self, image, items: Items):
        com = items.center_of_mass().numpy()
        self.draw_point(com, image, (255, 0, 0))

    def show(self, items: Items):
        image = np.zeros(tuple(self.size[::-1]) + (3,), dtype=np.uint8)
        self.draw_items(image, items)
        self.draw_bbox(items.main_bbox.numpy(), image, (0, 0, 255))
        self.draw_center_of_mass(image, items)
        cv.imshow("Scene", image)
        cv.waitKey(1)