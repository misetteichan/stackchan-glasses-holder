# Copyright (c) 2025 misetteichan
# Licensed under the MIT License. See LICENSE file for details.

from solid2 import *
import math

set_global_fn(100)

def avatar(width: int, height: int, depth: int, canvas_size: int):
    def eyes(h, r, width):
        e = cylinder(h=h, r=r).translate(-width / 4, 40, 0)
        return e + e.mirror(1, 0, 0)
    
    def face(width, height, depth):
        mouth = lambda w, h: cube(w, h, depth).translate(-(w / 2), -60, 0)
        e = eyes(depth, 25, width)
        f = e + mouth(120, 30)
        return f.translate(width / 2, height / 2, 0)

    def buttons(width, depth):
        w, h = 60, 30
        steps = (width - w) / 2 * 0.8
        button = cube(w, h, depth).translate(width/2 - w/2, h * 1.5, 0)
        return button + button.translate(-steps, 0, 0) + button.translate(steps, 0, 0)
    
    f = face(width, height, depth).translate((canvas_size - width) / 2, (canvas_size - height) / 2, 0)
    f += buttons(width, depth).translate((canvas_size - width) / 2, 0, 0)
    return f


def rounded_cube(width: int, height: int, depth: int, radius: int, round: list[bool] = [True, True, True, True]):
    w = width - radius * 2
    h = height - radius * 2
    body = cube(w, height, depth).translate(radius, 0, 0)
    body += cube(width, h, depth).translate(0, radius, 0)
    circle = cylinder(h=depth, r=radius).translate(radius, radius, 0)
    box = cube(radius * 2, radius * 2, depth).translate(0, 0, 0)
    body += circle if round[0] else box
    body += (circle if round[1] else box).translate(w, 0, 0)
    body += (circle if round[2] else box).translate(0, h, 0)
    body += (circle if round[3] else box).translate(w, h, 0)
    return body


def main(size: int, depth: int, tilt: int, stl: bool):
    canvas_size, canvas_depth, radius = 400, 5, 30

    scale = lambda obj, w = size, h = size, d = depth: obj.scale(w / canvas_size, h / canvas_size, d / canvas_depth)

    face = avatar(320, 240, canvas_depth, canvas_size).color('white')
    canvas = rounded_cube(canvas_size, canvas_size, canvas_depth, radius).color('black')
    canvas -= face.scaleZ(2).translateZ(-depth)

    canvas = scale(canvas)
    face = scale(face)

    # holes (fixed size)    
    mirror = lambda obj: (obj + obj.mirror(1, 0, 0)).translateX(size / 2)
    d = depth * 3
    hole_size = 19
    hole = cylinder(h=d, r=hole_size/2).translateX(-70)
    hole += cube(size, hole_size, d).translate(-size, -hole_size/2, 0).translateX(-70)
    hole_y = 400 - 138

    hole = mirror(hole).translateY(hole_y * size / canvas_size)
    notch_width = 5
    notch_height = 5
    notch = mirror(cube(notch_width, notch_height+10, d).translateY(-10).translateX(-(size / 2) * 0.6))

    canvas -= (hole + notch).translateZ(-d/2)

    stand_len = 80
    stand = rounded_cube(15, stand_len, notch_width, 5, [False, True, False, True]).rotateY(90).rotateX(90)
    stand -= cube(notch_width * 3, 15, depth+0.2).translate(-notch_width, 5, 10)
    stand = stand.translate(0, -5, -(stand_len - 10))
    stand -= cube(notch_width * 3, 15, depth+0.2).translateX(-notch_width).rotate(-tilt, 0, 0)

    support_height = (hole_y - hole_size) * math.cos(math.radians(tilt))
    support = scale(rounded_cube(canvas_size, support_height - 15, canvas_depth, radius), d=depth)
    support -= notch

    model = (canvas + face).rotateX(-tilt)
    model += mirror(stand.translateX(-(size / 2) * 0.6))
    model += support.color('gray').translateZ(-stand_len + 20)

    model.save_as_scad('model.scad')

    if stl:
        canvas.save_as_stl('_canvas.stl')
        face.save_as_stl('_face.stl')
        stand.save_as_stl(f'_stand_{tilt}.stl')
        support.save_as_stl(f'_support_{tilt}.stl')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--size', type=int, default=160)
    parser.add_argument('--depth', type=int, default=2)
    parser.add_argument('--tilt', type=int, default=15)
    parser.add_argument('--stl', action='store_true')
    args = parser.parse_args()

    main(size=args.size, depth=args.depth, tilt=args.tilt, stl=args.stl)
