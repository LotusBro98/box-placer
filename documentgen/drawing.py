import enum
import shutil
from io import StringIO, BytesIO

import drawsvg as draw
import numpy as np

from validation.models import Box, Carriage


class Projection(enum.Enum):
    FRONT = ((0, 2, 1), (-1, -1, 1))
    BACK = ((0, 2, 1), (1, -1, -1))
    TOP = ((1, 0, 2), (-1, 1, -1))
    SIDE = ((1, 2, 0), (-1, -1, -1))


class DrawColor:
    BOX_COLOR = '#0000ff'
    PLATFORM_COLOR = "#000000"
    CENTER_OF_MASS_COLOR = "#ff0000"


class DrawBox:
    pos: np.ndarray             # meters
    center_of_mass: np.ndarray  # meters, relative to pos
    mass: float                 # kg
    dimensions: np.ndarray      # meters
    id: int = 0

    def __init__(self, pos, center_of_mass, mass, dimensions):
        self.pos = np.array(pos)
        self.center_of_mass = np.array(center_of_mass)
        self.dimensions = np.array(dimensions)
        self.mass = mass

    @staticmethod
    def from_box(box: Box, platform: Carriage):
        if isinstance(box, DrawBox):
            return box

        drawbox = DrawBox(
            pos=np.array(box.coords_of_cg, dtype=np.float32)[[1, 0, 2]] / 1000,
            center_of_mass=np.array([0, 0, 0]),
            mass=box.weight*1000,
            dimensions=np.array(box.dimensions, dtype=np.float32)[[1, 0, 2]] / 1000
        )
        drawbox.pos[1] = platform.floor_length / 1000 / 2 - drawbox.pos[1]
        return drawbox

    def draw_center(self, scene: "Scene"):
        pos = scene.project(self.pos + self.center_of_mass)

        radius = 0.05 * scene.scale
        circle = draw.Circle(
            pos[0], pos[1], radius,
            stroke=DrawColor.CENTER_OF_MASS_COLOR, stroke_width=3, fill="transparent"
        )
        line1 = draw.Line(
            pos[0], pos[1] - radius, pos[0], pos[1] + radius,
            stroke=DrawColor.CENTER_OF_MASS_COLOR, stroke_width=3, fill="transparent"
        )
        line2 = draw.Line(
            pos[0] - radius, pos[1], pos[0] + radius, pos[1],
            stroke=DrawColor.CENTER_OF_MASS_COLOR, stroke_width=3, fill="transparent"
        )
        scene.drawing.append(circle)
        scene.drawing.append(line1)
        scene.drawing.append(line2)

    def draw_dimension(self, scene: "Scene"):
        center = scene.project(self.pos)
        dims = scene.project_size(self.dimensions)
        left = center[0] - dims[0] / 2
        right = center[0] + dims[0] / 2

    def draw_label(self, scene: "Scene"):
        pos = scene.project(self.pos + self.center_of_mass)
        text = f"ЦТгр{self.id}"
        offset = np.array([0.1, -0.1]) * scene.scale
        pos += offset
        size = 0.2 * scene.scale
        text_fig = draw.Text(text, size, pos[0], pos[1], stroke=DrawColor.BOX_COLOR, font_family="Arial", font_style="italic")
        scene.drawing.append(text_fig)

    def draw_box(self, scene: "Scene"):
        pos = scene.project(self.pos)
        dims = scene.project_size(self.dimensions)
        pos = pos - dims / 2
        bbox = draw.Rectangle(pos[0], pos[1], dims[0], dims[1], stroke=DrawColor.BOX_COLOR, fill='white', stroke_width=2)
        scene.drawing.append(bbox)

    def draw(self, scene: "Scene"):
        self.draw_box(scene)
        self.draw_center(scene)
        self.draw_label(scene)


class Platform:
    pos = np.array([0, 0, -0.1])
    dimensions: np.ndarray

    side_points = np.array([[-0.5, 0], [0.5, 0], [0.5, 0.3], [0.25, 0.3], [0.15, 0.6], [-0.15, 0.6], [-0.25, 0.3], [-0.5, 0.3]])
    top_points = np.array([[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]])
    front_points = np.array([[-0.5, 0], [0.5, 0], [0.5, 0.3], [-0.5, 0.3]])
    front_wheel1 = np.array([[-0.3, 0.3], [-0.2, 0.3], [-0.2, 1], [-0.3, 1]])
    front_wheel2 = np.array([[0.3, 0.3], [0.2, 0.3], [0.2, 1], [0.3, 1]])
    side_wheels = np.array([[-0.43, 0.65], [-0.30, 0.65], [0.30, 0.65], [0.43, 0.65]])

    def __init__(self, wx, wy, wz):
        self.dimensions = np.array([wx, wy, wz])

    @staticmethod
    def from_carriage(carriage: Carriage):
        return Platform(
            wx=carriage.floor_width / 1000,
            wy=carriage.floor_length / 1000,
            wz=carriage.height_from_rails / 1000
        )

    def draw_side(self, scene: "Scene"):
        dims = scene.project_size(self.dimensions)
        pts = self.side_points * dims + scene.origin
        pts_wheels = self.side_wheels * dims + scene.origin
        wheel_radius = 0.35 * dims[1]
        polygon = draw.Lines(*pts.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        for pt in pts_wheels:
            wheel = draw.Circle(pt[0], pt[1], wheel_radius, stroke=DrawColor.PLATFORM_COLOR, fill="white")
            scene.drawing.append(wheel)
        scene.drawing.append(polygon)

    def draw_top(self, scene: "Scene"):
        dims = scene.project_size(self.dimensions)
        pts = self.top_points * dims + scene.origin
        polygon = draw.Lines(*pts.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        scene.drawing.append(polygon)

    def draw_front(self, scene: "Scene"):
        dims = scene.project_size(self.dimensions)
        pts = self.front_points * dims + scene.origin
        pts_wheel1 = self.front_wheel1 * dims + scene.origin
        pts_wheel2 = self.front_wheel2 * dims + scene.origin
        polygon = draw.Lines(*pts.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        polygon_wheel1 = draw.Lines(*pts_wheel1.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        polygon_wheel2 = draw.Lines(*pts_wheel2.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        scene.drawing.append(polygon)
        scene.drawing.append(polygon_wheel1)
        scene.drawing.append(polygon_wheel2)

    def draw(self, scene: "Scene"):
        draw_fns = {
            Projection.SIDE: self.draw_side,
            Projection.BACK: self.draw_front,
            Projection.FRONT: self.draw_front,
            Projection.TOP: self.draw_top,
        }
        draw_fn = draw_fns[scene.projection]
        draw_fn(scene)


class Scene:
    projections = [
        (Projection.SIDE,  [-500, -250]),
        (Projection.TOP,   [-500, 250]),
        (Projection.FRONT, [700, 250]),
        (Projection.BACK,  [700, -250]),
    ]

    def __init__(self, width, height, scale, path=None):
        self.drawing = draw.Drawing(width, height, origin='center')
        self.scale = scale
        self.path = path
        self.elements = []
        self.origin = np.array([0, 0], np.float32)
        self.projection = Projection.TOP

    def project(self, point):
        pos = point[np.array(self.projection.value[0])][:2]
        pos *= self.projection.value[1][:2]
        pos = pos * self.scale + self.origin
        return pos

    def project_size(self, size):
        dims = size[np.array(self.projection.value[0])][:2] * self.scale
        return dims

    def set_origin(self, origin):
        self.origin[:] = origin

    def set_projection(self, projection):
        self.projection = projection

    def draw_projection(self, projection, origin):
        elems = [elem for elem in self.elements]
        elems = sorted(elems, key=lambda e: e.pos[np.array(projection.value[0])][2] * projection.value[1][2], reverse=True)
        self.set_origin(origin)
        self.set_projection(projection)
        for elem in elems:
            elem.draw(self)

    def draw(self, f=None):
        self.drawing.clear()
        for proj in self.projections:
            self.draw_projection(projection=proj[0], origin=proj[1])
        self.save(f)

    def save(self, f=None):
        if f is None:
            self.drawing.save_svg(self.path)
        else:
            self.drawing.as_svg(output_file=f)


def generate_drawing(carriage: Carriage, boxes: list[Box]) -> BytesIO:
    scene = Scene(2500, 1500, scale=100)

    boxes = [DrawBox.from_box(box, carriage) for box in boxes]
    for i, box in enumerate(boxes):
        box.id = i + 1

    platform = Platform.from_carriage(carriage)

    scene.elements += boxes
    scene.elements += [platform]

    sio = StringIO()
    scene.draw(sio)
    sio.seek(0)

    b = sio.read().encode()
    bio = BytesIO()
    bio.write(b)

    return bio


def main():
    platform = Carriage(floor_length=13300, floor_width=2870, weight=21, height_from_rails=1310,
                        cg_height_from_rails=800, base_length=9720, length_to_cg=6650, s_side_surface_meters=7)
    boxes = [
        Box(coords_of_cg=(3055, 0, 1500 / 2), dimensions=(3650, 3320, 1500), weight=6.670),
        Box(coords_of_cg=(10915, 0, 1020 / 2), dimensions=(3870, 2890, 1020), weight=4.085),
        Box(coords_of_cg=(690, 0, 390 / 2), dimensions=(1080, 1580, 390), weight=0.395),
        Box(coords_of_cg=(6930, 0, 1150 / 2), dimensions=(4100, 1720, 1150), weight=1.865),
    ]

    f_bytes = generate_drawing(platform, boxes)
    with open("drawing.svg", "wb+") as f:
        f_bytes.seek(0)
        shutil.copyfileobj(f_bytes, f)


if __name__ == '__main__':
    main()
