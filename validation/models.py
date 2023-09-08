from dataclasses import dataclass


@dataclass
class Box:
    coords_of_cg: tuple[int, int, int]  # in millimeters. Coords of C.G. относительно торцевого борта
    dimensions: tuple[int, int, int]  # in millimeters
    weight: float  # in tons


@dataclass
class Bar(Box):
    pass


@dataclass
class Platform:
    floor_length: int  # in millimeters
    floor_width: int  # in millimeters
    tare_weight: int  # in tons
    height_from_rails: int  # in millimeters
    cg_height_from_rails: int  # in millimeters. C.G. - center of gravity
    base_length: int  # in millimeters


platform = Platform(floor_length=13300, floor_width=2870, tare_weight=21, height_from_rails=1310,
                    cg_height_from_rails=800, base_length=9720)
box1 = Box(coords_of_cg=(3055, 0, 0), dimensions=(3650, 3320, 1500), weight=6670)
box2 = Box(coords_of_cg=(10915, 1000, 0), dimensions=(3870, 2890, 1020), weight=4085)
box3 = Box(coords_of_cg=(690, 2000, 0), dimensions=(1080, 1580, 390), weight=395)
box4 = Box(coords_of_cg=(6930, 0, 0), dimensions=(4100, 1720, 1150), weight=1865)

boxes = [box1, box2, box3, box4]
