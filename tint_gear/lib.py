import math
from typing import Tuple, List

EPSILON = 1e-6

RGB_MIN = 0.0
RGB_MAX = 1.0

HUE_MIN = 0.0
HUE_MAX = 360.0

SATURATION_MIN = 0.0
SATURATION_MAX = 1.0

LUMINANCE_MIN = 0.0
LUMINANCE_MAX = 1.0

LIGHTNESS_MIN = 0.0
LIGHTNESS_MAX = 1.0

AB_MIN = -1.0
AB_MAX = 1.0


def assert_rgb_component(value):
  assert isinstance(
    value, (float, int)), f"RGB component {value} must be a float or int."
  assert RGB_MIN <= value <= RGB_MAX, f"RGB component {value} is out of bounds."


def assert_rgb_color(r, g, b):
  assert_rgb_component(r)
  assert_rgb_component(g)
  assert_rgb_component(b)


def assert_list_of_rgb_colors(colors):
  for c in colors:
    assert_rgb_color(*c)


def assert_hue(value):
  assert isinstance(value, (float, int)), f"Hue {value} must be a float or int."
  assert HUE_MIN <= value <= HUE_MAX, f"Hue {value} is out of bounds."


def assert_saturation(value):
  assert isinstance(value,
                    (float, int)), f"Saturation {value} must be a float or int."
  assert SATURATION_MIN <= value <= SATURATION_MAX, f"Saturation {value} is out of bounds."


def assert_luminance(value):
  assert isinstance(value,
                    (float, int)), f"Luminance {value} must be a float or int."
  assert LUMINANCE_MIN <= value <= LUMINANCE_MAX, f"Luminance {value} is out of bounds."


def assert_lightness(value):
  assert isinstance(value,
                    (float, int)), f"Lightness {value} must be a float or int."
  assert LIGHTNESS_MIN <= value <= LIGHTNESS_MAX, f"Lightness {value} is out of bounds."


def assert_ab_component(value):
  assert isinstance(
    value, (float, int)), f"a or b component {value} must be a float or int."
  assert AB_MIN <= value <= AB_MAX, f"a or b component {value} is out of bounds."


def assert_oklab_color(L, a, b):
  assert_lightness(L)
  assert_ab_component(a)
  assert_ab_component(b)


def clamp_with_epsilon(
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


def linear_srgb_to_oklab(
  r: float,
  g: float,
  b: float,
) -> Tuple[float, float, float]:
  assert_rgb_color(r, g, b)

  l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
  m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
  s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b

  l_ = l**(1 / 3)
  m_ = m**(1 / 3)
  s_ = s**(1 / 3)

  L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
  a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
  b = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_

  L = clamp_with_epsilon(L, LIGHTNESS_MIN, LIGHTNESS_MAX, epsilon=1e-1)
  a = clamp_with_epsilon(a, AB_MIN, AB_MAX, epsilon=1e-1)
  b = clamp_with_epsilon(b, AB_MIN, AB_MAX, epsilon=1e-1)

  return L, a, b


def oklab_to_linear_srgb(
  L: float,
  a: float,
  b: float,
) -> Tuple[float, float, float]:
  assert_oklab_color(L, a, b)

  l_ = L + 0.3963377774 * a + 0.2158037573 * b
  m_ = L - 0.1055613458 * a - 0.0638541728 * b
  s_ = L - 0.0894841775 * a - 1.2914855480 * b

  l = l_**3
  m = m_**3
  s = s_**3

  r = +4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
  g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
  b = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s

  r = clamp_with_epsilon(r, RGB_MIN, RGB_MAX, epsilon=1e1)
  g = clamp_with_epsilon(g, RGB_MIN, RGB_MAX, epsilon=1e1)
  b = clamp_with_epsilon(b, RGB_MIN, RGB_MAX, epsilon=1e1)

  return r, g, b


def linear_srgb_to_srgb(
  linear_r: float,
  linear_g: float,
  linear_b: float,
) -> Tuple[float, float, float]:
  assert_rgb_color(linear_r, linear_g, linear_b)

  def gamma_correct(value: float) -> float:
    if value <= 0.0031308:
      return 12.92 * value
    else:
      return 1.055 * (value**(1 / 2.4)) - 0.055

  r = gamma_correct(linear_r)
  g = gamma_correct(linear_g)
  b = gamma_correct(linear_b)

  r = clamp_with_epsilon(r, RGB_MIN, RGB_MAX)
  g = clamp_with_epsilon(g, RGB_MIN, RGB_MAX)
  b = clamp_with_epsilon(b, RGB_MIN, RGB_MAX)

  return r, g, b


def srgb_to_linear_srgb(
  srgb_r: float,
  srgb_g: float,
  srgb_b: float,
) -> Tuple[float, float, float]:
  assert_rgb_color(srgb_r, srgb_g, srgb_b)

  def inverse_gamma_correct(value: float) -> float:
    if value <= 0.04045:
      return value / 12.92
    else:
      return ((value + 0.055) / 1.055)**2.4

  r = inverse_gamma_correct(srgb_r)
  g = inverse_gamma_correct(srgb_g)
  b = inverse_gamma_correct(srgb_b)

  r = clamp_with_epsilon(r, RGB_MIN, RGB_MAX)
  g = clamp_with_epsilon(g, RGB_MIN, RGB_MAX)
  b = clamp_with_epsilon(b, RGB_MIN, RGB_MAX)

  return r, g, b


def srgb_to_hex(
  r: float,
  g: float,
  b: float,
  pretty: bool = False,
) -> str:
  assert_rgb_color(r, g, b)

  hex_value = "#{:02x}{:02x}{:02x}".format(
    int(clamp_with_epsilon(r, RGB_MIN, RGB_MAX) * 255),
    int(clamp_with_epsilon(g, RGB_MIN, RGB_MAX) * 255),
    int(clamp_with_epsilon(b, RGB_MIN, RGB_MAX) * 255),
  )

  if pretty:
    ansi_color = f"\033[38;2;{int(r * 255)};{int(g * 255)};{int(b * 255)}m"
    reset = "\033[0m"
    return f"{ansi_color}{hex_value}{reset}"

  return hex_value


def hex_to_srgb(hex_color: str) -> Tuple[float, float, float]:
  hex_color = hex_color.strip()
  if hex_color.startswith("\033["):
    hex_color = hex_color.split("m")[-1]

  hex_color = hex_color.lstrip('#')
  r, g, b = int(
    hex_color[0:2],
    16,
  ), int(
    hex_color[2:4],
    16,
  ), int(
    hex_color[4:6],
    16,
  )

  return (
    clamp_with_epsilon(r / 255.0, RGB_MIN, RGB_MAX),
    clamp_with_epsilon(g / 255.0, RGB_MIN, RGB_MAX),
    clamp_with_epsilon(b / 255.0, RGB_MIN, RGB_MAX),
  )


def get_hue(
  r: float,
  g: float,
  b: float,
) -> float:
  assert_rgb_color(r, g, b)

  linear_r, linear_g, linear_b = srgb_to_linear_srgb(r, g, b)
  _, a, b = linear_srgb_to_oklab(linear_r, linear_g, linear_b)

  hue = math.atan2(b, a) * (180 / math.pi)
  if hue < 0:
    hue += 360

  return clamp_with_epsilon(hue, HUE_MIN, HUE_MAX)


def set_hue(
  r: float,
  g: float,
  b: float,
  target_hue: float,
) -> Tuple[float, float, float]:
  assert_rgb_color(r, g, b)
  assert_hue(target_hue)

  linear_r, linear_g, linear_b = srgb_to_linear_srgb(r, g, b)
  L, a, b = linear_srgb_to_oklab(linear_r, linear_g, linear_b)

  target_hue_rad = target_hue * (math.pi / 180)
  chroma = math.sqrt(a**2 + b**2)
  new_a = chroma * math.cos(target_hue_rad)
  new_b = chroma * math.sin(target_hue_rad)

  new_linear_r, new_linear_g, new_linear_b = oklab_to_linear_srgb(
    L, new_a, new_b)
  new_r, new_g, new_b = linear_srgb_to_srgb(
    new_linear_r,
    new_linear_g,
    new_linear_b,
  )

  return (
    clamp_with_epsilon(new_r, RGB_MIN, RGB_MAX),
    clamp_with_epsilon(new_g, RGB_MIN, RGB_MAX),
    clamp_with_epsilon(new_b, RGB_MIN, RGB_MAX),
  )


def get_saturation(
  r: float,
  g: float,
  b: float,
) -> float:
  assert_rgb_color(r, g, b)

  linear_r, linear_g, linear_b = srgb_to_linear_srgb(r, g, b)
  _, a, b = linear_srgb_to_oklab(linear_r, linear_g, linear_b)

  saturation = math.sqrt(a**2 + b**2)

  return clamp_with_epsilon(saturation, SATURATION_MIN, SATURATION_MAX)


def set_saturation(
  r: float,
  g: float,
  b: float,
  target_saturation: float,
) -> Tuple[float, float, float]:
  assert_rgb_color(r, g, b)
  assert_saturation(target_saturation)

  linear_r, linear_g, linear_b = srgb_to_linear_srgb(r, g, b)
  L, a, b = linear_srgb_to_oklab(linear_r, linear_g, linear_b)

  current_saturation = math.sqrt(a**2 + b**2)
  if current_saturation == 0:
    new_a = clamp_with_epsilon(
      target_saturation,
      SATURATION_MIN,
      SATURATION_MAX,
    )
    new_b = 0
  else:
    scale = clamp_with_epsilon(
      target_saturation,
      SATURATION_MIN,
      SATURATION_MAX,
    ) / current_saturation
    new_a = a * scale
    new_b = b * scale

  new_linear_r, new_linear_g, new_linear_b = oklab_to_linear_srgb(
    L,
    new_a,
    new_b,
  )
  new_r, new_g, new_b = linear_srgb_to_srgb(
    new_linear_r,
    new_linear_g,
    new_linear_b,
  )

  return (
    clamp_with_epsilon(new_r, RGB_MIN, RGB_MAX),
    clamp_with_epsilon(new_g, RGB_MIN, RGB_MAX),
    clamp_with_epsilon(new_b, RGB_MIN, RGB_MAX),
  )


def get_luminance(
  r: float,
  g: float,
  b: float,
) -> float:
  assert_rgb_color(r, g, b)

  linear_r, linear_g, linear_b = srgb_to_linear_srgb(r, g, b)
  luminance = 0.2126 * linear_r + 0.7152 * linear_g + 0.0722 * linear_b

  return clamp_with_epsilon(luminance, LUMINANCE_MIN, LUMINANCE_MAX)


def set_luminance(
  r: float,
  g: float,
  b: float,
  target_luminance: float,
  increment: float = 0.01,
) -> Tuple[float, float, float]:
  assert_rgb_color(r, g, b)
  assert_luminance(target_luminance)

  new_r, new_g, new_b = r, g, b

  linear_r, linear_g, linear_b = srgb_to_linear_srgb(new_r, new_g, new_b)
  L, a, b = linear_srgb_to_oklab(linear_r, linear_g, linear_b)
  current_luminance = get_luminance(new_r, new_g, new_b)
  new_L = L

  if current_luminance < target_luminance:
    adjust_lightness = increment
  else:
    adjust_lightness = -increment

  iteration = 0
  while iteration < (1 / increment):
    new_L = new_L + adjust_lightness
    if not LIGHTNESS_MIN <= new_L <= LIGHTNESS_MAX:
      break

    new_linear_r, new_linear_g, new_linear_b = oklab_to_linear_srgb(new_L, a, b)
    new_r, new_g, new_b = linear_srgb_to_srgb(
      new_linear_r,
      new_linear_g,
      new_linear_b,
    )
    current_luminance = get_luminance(new_r, new_g, new_b)

    if ((adjust_lightness > 0 and current_luminance >= target_luminance)
        or (adjust_lightness < 0 and current_luminance <= target_luminance)):
      break

    iteration += 1

  return (clamp_with_epsilon(new_r, RGB_MIN, RGB_MAX),
          clamp_with_epsilon(new_g, RGB_MIN, RGB_MAX),
          clamp_with_epsilon(new_b, RGB_MIN, RGB_MAX))


def calculate_average_luminance(
  colors: List[Tuple[float, float, float]], ) -> float:
  assert_list_of_rgb_colors(colors)

  total_luminance = 0
  for r, g, b in colors:
    total_luminance += get_luminance(r, g, b)
  average_luminance = total_luminance / len(colors)

  return clamp_with_epsilon(
    average_luminance,
    LUMINANCE_MIN,
    LUMINANCE_MAX,
  )


def calculate_average_saturation(
  colors: List[Tuple[float, float, float]], ) -> float:
  assert_list_of_rgb_colors(colors)

  total_saturation = 0
  for r, g, b in colors:
    total_saturation += get_saturation(r, g, b)
  average_saturation = total_saturation / len(colors)

  return clamp_with_epsilon(
    average_saturation,
    SATURATION_MIN,
    SATURATION_MAX,
  )


def determine_theme_light_or_dark(
  average_luminance: float,
  threshold: float = 0.25,
  alternate: bool = False,
) -> bool:
  assert_luminance(average_luminance)

  return (average_luminance < threshold
          if alternate else average_luminance > threshold)


def determine_primary_secondary_accent(
  colors: List[Tuple[float, float, float]],
  saturation_increase: float = 0.2,
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[
    float, float, float]]:
  assert_list_of_rgb_colors(colors)

  colors = sorted(
    colors,
    key=lambda x: get_saturation(*x),
    reverse=True,
  )

  primary = colors[0]

  primary_hue = get_hue(*primary)
  hue_differences = []

  for color in colors[1:]:
    hue = get_hue(*color)
    hue_diff = abs(primary_hue - hue)
    hue_diff = min(hue_diff, 360 - hue_diff)
    hue_differences.append((hue_diff, color))

  hue_differences.sort(reverse=True, key=lambda x: x[0])

  accent = hue_differences[0][1]
  secondary = hue_differences[1][1]

  primary = set_saturation(
    *primary,
    clamp_with_epsilon(
      get_saturation(*primary) + saturation_increase,
      min_value=SATURATION_MIN,
      max_value=SATURATION_MAX,
      epsilon=0.5,
    ),
  )

  secondary = set_saturation(
    secondary[0],
    secondary[1],
    secondary[2],
    clamp_with_epsilon(
      get_saturation(*secondary) + 0.2,
      min_value=SATURATION_MIN,
      max_value=SATURATION_MAX,
      epsilon=0.5,
    ),
  )

  accent = set_saturation(
    accent[0],
    accent[1],
    accent[2],
    clamp_with_epsilon(
      get_saturation(*accent) + 0.2,
      min_value=SATURATION_MIN,
      max_value=SATURATION_MAX,
      epsilon=0.5,
    ),
  )

  return primary, secondary, accent


def determine_black_white(
  colors: List[Tuple[float, float, float]],
  is_light_theme: bool,
  max_saturation: float,
  index: int = 0
) -> Tuple[Tuple[float, float, float], Tuple[float, float, float]]:
  assert_list_of_rgb_colors(colors)
  assert isinstance(is_light_theme, bool), "is_light_theme must be a boolean."
  assert_saturation(max_saturation)

  if is_light_theme:
    black_color = sorted(colors, key=lambda color: get_luminance(*color))[index]
    white_color = list(
      reversed(sorted(colors, key=lambda color: get_luminance(*color))))[index]
  else:
    black_color = list(
      reversed(sorted(colors, key=lambda color: get_luminance(*color))))[index]
    white_color = sorted(colors, key=lambda color: get_luminance(*color))[index]

  bg_r, bg_g, bg_b = black_color
  bg_saturation = min(get_saturation(bg_r, bg_g, bg_b), max_saturation)
  black_color = set_saturation(bg_r, bg_g, bg_b, bg_saturation)

  text_r, text_g, text_b = white_color
  text_saturation = min(get_saturation(text_r, text_g, text_b), max_saturation)
  white_color = set_saturation(text_r, text_g, text_b, text_saturation)

  if is_light_theme:
    white_color = set_luminance(
      *white_color,
      min(get_luminance(*white_color) + 0.4, LUMINANCE_MAX),
    )
  else:
    black_color = set_luminance(
      *black_color,
      min(get_luminance(*black_color) + 0.4, LUMINANCE_MAX),
    )

  return black_color, white_color


def determine_semantic_color(
  default_color: Tuple[float, float, float],
  colors: List[Tuple[float, float, float]],
  hue_nudge_degrees: float = 10,
  saturation_decrease: float = 0.1,
) -> Tuple[float, float, float]:
  assert_rgb_color(*default_color)
  assert_list_of_rgb_colors(colors)
  assert_hue(hue_nudge_degrees)
  assert_saturation(saturation_decrease)

  default_r, default_g, default_b = default_color
  default_hue = get_hue(*default_color)

  closest_color = min(
    colors,
    key=lambda color: abs(get_hue(*color) - default_hue),
  )

  closest_hue = get_hue(*closest_color)

  hue_difference = abs(default_hue - closest_hue)
  hue_difference = min(hue_difference, 360 - hue_difference)

  adjusted_color = default_color
  if hue_difference <= 60:
    nudged_hue = (default_hue + 2 * hue_nudge_degrees) % 360
    adjusted_color = set_hue(default_r, default_g, default_b, nudged_hue)
  elif 60 < hue_difference <= 120:
    nudged_hue = (default_hue + hue_nudge_degrees) % 360
    adjusted_color = set_hue(default_r, default_g, default_b, nudged_hue)
    current_saturation = get_saturation(*adjusted_color)
    new_saturation = max(
      current_saturation - saturation_decrease,
      SATURATION_MIN,
    )
    adjusted_color = set_saturation(*adjusted_color, new_saturation)
  elif 120 < hue_difference <= 180:
    adjusted_color = default_color
    adjusted_r, adjusted_g, adjusted_b = adjusted_color
    current_saturation = get_saturation(*adjusted_color)
    new_saturation = max(
      current_saturation - 2 * saturation_decrease,
      SATURATION_MIN,
    )
    adjusted_color = set_saturation(
      adjusted_r,
      adjusted_g,
      adjusted_b,
      new_saturation,
    )

  return adjusted_color


def adjust_contrast(
  color: Tuple[float, float, float],
  average_luminance: float,
  is_light: bool,
  invert: bool,
  high_contrast: bool,
  k: float,
) -> Tuple[float, float, float]:
  assert_rgb_color(*color)
  assert_luminance(average_luminance)
  assert isinstance(is_light, bool), "is_light must be a boolean."
  assert isinstance(high_contrast, bool), "high_contrast must be a boolean."

  r, g, b = color

  current_luminance = get_luminance(r, g, b)
  color_luminance_diff = current_luminance - average_luminance

  range_min = clamp_with_epsilon(
    (1 / (8.0 if high_contrast else 5.0)) *
    (1 - math.exp(-k * average_luminance)),
    LUMINANCE_MIN,
    LUMINANCE_MAX,
  )
  range_max = clamp_with_epsilon(
    range_min * (7.0 if high_contrast else 4.5),
    LUMINANCE_MIN,
    LUMINANCE_MAX,
  )

  if invert:
    range_min = 1 - range_min
    range_max = 1 - range_max

  current_luminance = get_luminance(*color)
  if is_light:
    proportional_luminance_light = (average_luminance * (1 - range_max) +
                                    range_max)
    proportional_luminance_diff_ligth = (1 - range_max) * color_luminance_diff
    final_luminance = proportional_luminance_light + proportional_luminance_diff_ligth
  else:
    proportional_luminance_dark = average_luminance * range_min
    proportional_luminance_diff_dark = range_min * color_luminance_diff
    final_luminance = proportional_luminance_dark + proportional_luminance_diff_dark

  final_luminance = clamp_with_epsilon(
    final_luminance,
    LUMINANCE_MIN,
    LUMINANCE_MAX,
    epsilon=1e-1,
  )

  adjusted_color = set_luminance(r, g, b, final_luminance)
  return adjusted_color
