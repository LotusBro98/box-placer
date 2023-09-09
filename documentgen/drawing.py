import enum
import drawsvg as draw
import numpy as np

from validation.models import Box


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
    def from_box(box: Box):
        if isinstance(box, DrawBox):
            return box

        return DrawBox(
            pos=np.array(box.coords_of_cg, dtype=np.float32) / 1000,
            center_of_mass=np.array([0, 0, 0]),
            mass=box.weight*1000,
            dimensions=np.array(box.dimensions, dtype=np.float32) / 1000
        )

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

    side_points = np.array([
        [-0.5, 0], [0.5, 0], [0.5, 0.5], [0.3, 0.5], [0.2, 1], [-0.2, 1], [-0.3, 0.5], [-0.5, 0.5]
    ])
    top_points = np.array([
        [-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]
    ])
    front_points = np.array([
        [-0.5, 0], [0.5, 0], [0.5, 1], [-0.5, 1]
    ])

    def __init__(self, wx, wy, wz):
        self.dimensions = np.array([wx, wy, wz])

    def draw_side(self, scene: "Scene"):
        dims = scene.project_size(self.dimensions)
        pts = self.side_points * dims + scene.origin
        polygon = draw.Lines(*pts.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        scene.drawing.append(polygon)

    def draw_top(self, scene: "Scene"):
        dims = scene.project_size(self.dimensions)
        pts = self.top_points * dims + scene.origin
        polygon = draw.Lines(*pts.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        scene.drawing.append(polygon)

    def draw_front(self, scene: "Scene"):
        dims = scene.project_size(self.dimensions)
        pts = self.front_points * dims + scene.origin
        polygon = draw.Lines(*pts.reshape((-1,)).tolist(), close=True, stroke=DrawColor.PLATFORM_COLOR, fill="white")
        scene.drawing.append(polygon)

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
        (Projection.SIDE,  [-600, -250]),
        (Projection.TOP,   [-600, 250]),
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


def generate_drawing(boxes: list[Box], f):
    scene = Scene(2500, 1500, scale=100)

    boxes = [DrawBox.from_box(box) for box in boxes]
    for i, box in enumerate(boxes):
        box.id = i + 1

    scene.elements += boxes
    scene.elements += [Platform(3, 10, 1)]
    scene.draw(f)


def main():
    boxes = [
        DrawBox(pos=[0.6282564, 0.6489718, 0.91460556 / 2], center_of_mass=[-0., -0., -0.], dimensions=[0.84325385, 1.878874, 0.91460556], mass=1.0019923),
        DrawBox(pos=[0.469371, -2.5151227, 0.8584385 / 2], center_of_mass=[-0., -0., -0.], dimensions=[0.60296875, 2.231534, 0.8584385], mass=0.9971901),
        DrawBox(pos=[-0.5457087, 0.60900295, 1.0836259 / 2], center_of_mass=[-0., -0., -0.], dimensions=[1.0683688, 2.0711808, 1.0836259], mass=1.0106633),
        DrawBox(pos=[-1.1298192e-03, 3.2741010e+00, 1.0053426 / 2], center_of_mass=[-0., -0., -0.], dimensions=[1.0839309, 2.3033555, 1.0053426], mass=0.98005784),
        DrawBox(pos=[-0.5369451, -1.9809812, 1.207738 / 2], center_of_mass=[-0., -0., -0.], dimensions=[0.8571644, 2.0065832, 1.207738], mass=1.0089228),
    ]

    with open("drawing.svg", "wt+", encoding="utf-8") as f:
        generate_drawing(boxes, f)


if __name__ == '__main__':
    main()
