from dataclasses import dataclass


@dataclass
class Shipment:
    pass


@dataclass
class Box(Shipment):
    dimensions: tuple[int, int, int]  # in millimeters
    weight: float  # in tons
    coords_of_cg: tuple[int, int, int] = (0, 0, 0)  # in millimeters. Coords of C.G. относительно торцевого борта

    @property
    def h_of_cg(self):
        return self.dimensions[2]/2+self.coords_of_cg[2]

    @property
    def s_side_surface_meters(self):
        return round(self.dimensions[0]/1000 * self.dimensions[1]/1000 * self.h_of_cg/1000, 2)


@dataclass
class Bar(Box):
    pass


@dataclass
class Carriage:
    floor_length: int  # in millimeters
    floor_width: int  # in millimeters
    weight: float  # in tons
    height_from_rails: int  # in millimeters
    cg_height_from_rails: int  # in millimeters. C.G. - center of gravity
    base_length: int  # in millimeters
    length_to_cg: int
    s_side_surface_meters: float


platform = Carriage(floor_length=13300, floor_width=2870, weight=21, height_from_rails=1310,
                    cg_height_from_rails=800, base_length=9720, length_to_cg=6650, s_side_surface_meters=7)
box1 = Box(coords_of_cg=(3055, 0, 25), dimensions=(3650, 3320, 1500), weight=6.670)
box2 = Box(coords_of_cg=(10915, 1000, 0), dimensions=(3870, 2890, 1020), weight=4.085)
box3 = Box(coords_of_cg=(690, 2000, 0), dimensions=(1080, 1580, 390), weight=0.395)
box4 = Box(coords_of_cg=(6930, 0, 0), dimensions=(4100, 1720, 1150), weight=1.865)

boxes = [box1, box2, box3, box4]
