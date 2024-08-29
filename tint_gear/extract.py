import os
from colorthief import ColorThief
from typing import List, Tuple

RGB_MIN = 0.0
RGB_MAX = 1.0
EPSILON = 1e-6


def clamp_value(
  value: float,
  min_value: float,
  max_value: float,
  epsilon: float = EPSILON,
) -> float:
  if value < min_value - epsilon or value > max_value + epsilon:
    raise AssertionError(
      f"Value {value} is out of bounds! Expected range: [{min_value}, {max_value}]"
    )
  return max(min_value, min(value, max_value))


def assert_image_path(image_path):
  if not isinstance(image_path, str):
    raise TypeError("image_path must be a string.")
  if not os.path.isfile(image_path):
    raise ValueError("The provided image path does not exist or is not a file.")


def assert_num_colors(num_colors):
  if not isinstance(num_colors, int):
    raise TypeError("num_colors must be an integer.")
  if num_colors <= 0:
    raise ValueError("num_colors must be a positive integer.")


def extract_prominent_colors(
  image_path: str,
  num_colors: int = 8,
) -> List[Tuple[float, float, float]]:
  assert_image_path(image_path)
  assert_num_colors(num_colors)

  color_thief = ColorThief(image_path)
  palette = color_thief.get_palette(color_count=num_colors)

  clamped_palette = [(
    clamp_value(r / 255.0, RGB_MIN, RGB_MAX),
    clamp_value(g / 255.0, RGB_MIN, RGB_MAX),
    clamp_value(b / 255.0, RGB_MIN, RGB_MAX),
  ) for r, g, b in palette]

  return clamped_palette
