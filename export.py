import os
import bpy
from typing import cast
import math
import pickle
from mathutils import Vector, Matrix
from os import path
from datetime import timedelta
import time
import sys

basepath = os.path.dirname(bpy.data.filepath)
if basepath  not in sys.path:
    sys.path.append(basepath)

from conversion_config import Config

config = Config()
config.sampling_rate = 44100
config.volume = 0.5
config.animation_fps = bpy.context.scene.render.fps
config.basepath = basepath

mult: int = 8

audio_signal_left: list[float] = []
audio_signal_right: list[float] = []

samples_per_frame = math.floor(config.sampling_rate / config.animation_fps)

gpencil_obj = cast(bpy.types.Object, bpy.data.objects.get("LineArt"))
bpy.ops.object.select_all(action="DESELECT")
bpy.context.view_layer.objects.active = gpencil_obj
gpencil_obj.select_set(True)
camera = bpy.context.scene.camera
stroke_name = "Lines"

gpencil_data = cast(bpy.types.GreasePencil, gpencil_obj.data)

camera_data = camera.data

frame_start = bpy.context.scene.frame_start
frame_end = bpy.context.scene.frame_end

camera_matrix = Matrix(camera.matrix_world).inverted()
projection_matrix = Matrix(camera.calc_matrix_camera(bpy.context.evaluated_depsgraph_get()))

def to_2d(point_3d: list[float] | tuple[float, float, float] | Vector) -> Vector:
    point_4d = Vector(camera_matrix @ Vector(point_3d))
    point_4d_homo = point_4d.to_4d()

    point_2d_homo = Vector(projection_matrix @ point_4d_homo)
    point_2d = Vector(((point_2d_homo.x / point_2d_homo.w), (point_2d_homo.y / point_2d_homo.w)))
    return point_2d

def get_stroke_len(points: bpy.types.GPencilStrokePoints) -> float:
    dist = 0

    for j in range(1, len(points)):
        i = j - 1
        i_2d = to_2d(points[i].co)
        j_2d = to_2d(points[j].co)
        dist += (j_2d - i_2d).length

    return dist

screen_coordinates = []

start_time = time.time()
# Iterate over each frame
for frame in range(frame_start, frame_end + 1):
    time_left = timedelta()
    if frame != frame_start:
        time_left = timedelta(seconds=(time.time() - start_time) / (frame - frame_start) * (frame_end - frame))
    print(f"\r{frame}/{frame_end} Time left: {time_left}          ", end="")

    bpy.context.scene.frame_set(frame)
    
    left = []
    right = []
    layer = gpencil_data.layers.active
    strokes = list(layer.active_frame.strokes)
    

    # get the total length of all strokes
    total_length = 0
    for stroke in strokes:
        if len(stroke.points) < 2:
            continue
        total_length += get_stroke_len(stroke.points)

    for i in range(max(mult - 1, 0)):
        strokes.extend(layer.active_frame.strokes)

    if mult > 1:
        total_length *= mult

    for stroke in strokes:
        points = stroke.points
        if len(stroke.points) < 2:
            continue

        new_point_count = math.floor(samples_per_frame * get_stroke_len(points) / total_length)
        
        # skip because they're too short to actually contribute to society
        if new_point_count < 2:
            continue

        step = (len(points) - 1) / (new_point_count - 1)
        
        for i in range(new_point_count):
            index1 = int(i * step)
            index2 = min(index1 + 1, len(points) - 1)
            alpha = i * step - index1
            
            coord = Vector(points[index1].co)
            coord = coord.lerp(points[index2].co, alpha)
            coord = to_2d(coord)

            audio_signal_left.append(coord.x * config.volume)
            audio_signal_right.append(coord.y * config.volume)

with open(path.join(basepath, "left.pickle"), "wb") as f:
    pickle.dump(audio_signal_left, f)
with open(path.join(basepath, "right.pickle"), "wb") as f:
    pickle.dump(audio_signal_right, f)
with open(path.join(basepath, "config.pickle"), "wb") as f:
    pickle.dump(config, f)

print(audio_signal_left)

print("\ndone!")
