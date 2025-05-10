import pyray as ray
import numpy as np
from pyray import Color
from enum import Enum

class GridPointType(Enum):
    DEFAULT = 0
    SOLID = 1
    ORIGIN = 2
    TARGET = 3
    CHECKED = 4

class GridPoint:
    type: GridPointType
    distance_to_origin = np.inf
    distance_to_target = np.inf
    cost = np.inf

    def __init__(self, type: GridPointType = GridPointType.DEFAULT):
        self.type = type


def setup():
    global grid_size, grid, origin, target, reached_target
    grid_size = calculate_grid_size()
    grid = [[GridPoint() for _ in range(grid_size[1])] for _ in range(grid_size[0])]

    origin = np.array([-1, -1])
    target = np.array([-1, -1])

    reached_target = False

def calculate_grid_size():
    size = window_size // circle_spacing
    
    return np.array([size[0] - 1, size[1] - 1])

def screen_to_grid(position):
    return ((position - (circle_spacing / 2)) // circle_spacing).astype(int)

def get_point_neighbors(point):
    x, y = point

    points = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size[0] and 0 <= ny < grid_size[1]:
            points.append(np.array([nx, ny]))
    
    return points

def calculate_path():
    path_points.clear()
    
    neighbors = get_point_neighbors(origin)
    for pos in neighbors:
        point = pos

def step():
    global reached_target, closest_point_pos
    
    closest_point = None
    for pos in potential_path_point_pos:
        point = grid[pos[0]][pos[1]]

        if ((closest_point == None) or 
           (closest_point.cost >= point.cost and 
            closest_point.distance_to_target > point.distance_to_target)):
            closest_point = point
            closest_point_pos = pos
    
    points = get_point_neighbors(closest_point_pos)

    added_new_points = False
    for point_pos in points:
        point = grid[point_pos[0]][point_pos[1]]
        if point.type == GridPointType.TARGET:
            reached_target = True
            break

        if point.type != GridPointType.DEFAULT or point.type == GridPointType.SOLID:
            continue
        
        point.distance_to_origin = grid[closest_point_pos[0]][closest_point_pos[1]].distance_to_origin + 1
        point.distance_to_target = np.sum(np.abs(point_pos - target))
        point.cost = point.distance_to_origin + point.distance_to_target

        if point.type == GridPointType.DEFAULT:
            point.type = GridPointType.CHECKED
            potential_path_point_pos.add(tuple(point_pos))
            added_new_points = True
    
    if not added_new_points:
        potential_path_point_pos.remove(tuple(closest_point_pos))


def display_text(value, text_pos):
    if value == np.inf:
        return
    
    stringified = str(value)
    text_width = ray.measure_text(stringified, 20) // 2
    ray.draw_text(stringified, text_pos[0] - (text_width // 2), text_pos[1], 20, ray.WHITE)

def draw_grid():
    for x in range(1, grid_size[0] + 1):
        for y in range(1, grid_size[1] + 1):
            circle_position = (circle_spacing * x, circle_spacing * y)

            point = grid[x - 1][y - 1]
            color: Color
            match point.type:
                case GridPointType.DEFAULT:
                    color = Color(150, 150, 150, 255)
                case GridPointType.SOLID:
                    color = Color(0, 0, 0, 255)
                case GridPointType.ORIGIN:
                    color = Color(150, 255, 150, 255)
                case GridPointType.TARGET:
                    color = Color(255, 150, 150, 255)
                case GridPointType.CHECKED:
                    color = Color(255, 150, 255, 255)
                #case GridPointType.PATH:
                #    color = Color(255, 255, 150, 255)

            ray.draw_circle(circle_position[0], circle_position[1], circle_radius, color)

            display_text(point.distance_to_origin, circle_position + np.array([0, 10]))
            display_text(point.distance_to_target, circle_position + np.array([0, -6]))

window_size = np.array([640, 480])
ray.set_config_flags(ray.ConfigFlags.FLAG_WINDOW_RESIZABLE)
ray.init_window(window_size[0], window_size[1], "pathfinding x3")
grid_padding = 8
circle_radius = 25
circle_spacing = (circle_radius * 2) + grid_padding

grid_size = np.zeros(2)
grid = [[]]

path_points = []
closest_point_pos = None
potential_path_point_pos = set()

origin = np.zeros(2)
target = np.zeros(2)

reached_target = False

setup()

while not ray.window_should_close():
    ray.begin_drawing()
    ray.clear_background(Color(255, 255, 255))

    draw_grid()

    ray.end_drawing()
    
    if ray.is_mouse_button_pressed(ray.MouseButton.MOUSE_BUTTON_LEFT):
        grid_pos = screen_to_grid(np.array([ray.get_mouse_x(), ray.get_mouse_y()]))
        point = grid[grid_pos[0]][grid_pos[1]]
        
        if point.type == GridPointType.DEFAULT:
            point.type = GridPointType.SOLID
        elif point.type == GridPointType.SOLID:
            point.type = GridPointType.DEFAULT

    if ray.is_mouse_button_pressed(ray.MouseButton.MOUSE_BUTTON_RIGHT):
        grid_pos = screen_to_grid(np.array([ray.get_mouse_x(), ray.get_mouse_y()]))
        if np.all(origin == -1):
            origin = grid_pos
            grid[grid_pos[0]][grid_pos[1]] = GridPoint(GridPointType.ORIGIN)
            potential_path_point_pos.add(tuple(grid_pos))
        elif np.all(target == -1):
            target = grid_pos
            grid[grid_pos[0]][grid_pos[1]] = GridPoint(GridPointType.TARGET)
        
    if ray.is_key_pressed(ray.KeyboardKey.KEY_SPACE):
        if np.all(target != -1) and not reached_target:
            step()

    if ray.is_key_pressed(ray.KeyboardKey.KEY_R):
        window_size = np.array([ray.get_screen_width(), ray.get_screen_height()])
        setup()

ray.close_window()
