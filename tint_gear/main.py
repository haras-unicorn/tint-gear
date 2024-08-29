import sys
import json
import argparse
from tint_gear.extract import extract_prominent_colors
from tint_gear.lib import (
  calculate_average_luminance,
  calculate_average_saturation,
  determine_theme_light_or_dark,
  determine_primary_secondary_accent,
  determine_black_white,
  determine_semantic_color,
  adjust_contrast,
  srgb_to_hex,
)


def main():
  parsed_args = parse_args()

  deserialized_colors = process(
    image_path=parsed_args.image_path,
    light_theme_threshold=parsed_args.light_theme_threshold,
    alternate=parsed_args.alternate,
    k=parsed_args.k,
    num_colors=parsed_args.num_colors,
    high_contrast=parsed_args.high_contrast,
  )

  print_colors(
    deserialized_colors,
    parsed_args.pretty,
    parsed_args.json,
  )


def process(
  image_path: str,
  light_theme_threshold: float = 0.25,
  alternate: bool = False,
  k: float = 4.0,
  num_colors: int = 8,
  high_contrast: bool = False,
) -> dict:
  colors = extract_prominent_colors(image_path, num_colors)

  average_luminance = calculate_average_luminance(colors)
  average_saturation = calculate_average_saturation(colors)
  is_light_theme = determine_theme_light_or_dark(
    average_luminance,
    light_theme_threshold,
    alternate,
  )

  primary, secondary, accent = determine_primary_secondary_accent(
    colors, average_saturation)

  text_color, background_color = determine_black_white(
    colors,
    is_light_theme,
    max_saturation=0.1,
  )
  text_color_2, background_color_2 = determine_black_white(
    colors,
    is_light_theme,
    max_saturation=0.3,
    index=1,
  )
  selection_color, _ = determine_black_white(
    colors,
    is_light_theme,
    max_saturation=0.3,
    index=2,
  )

  ansi_black, ansi_white = background_color, text_color
  ansi_bright_black, ansi_bright_white = background_color_2, text_color_2

  default_colors = {
    'red': (0.8, 0.0, 0.0),
    'green': (0.0, 0.8, 0.0),
    'blue': (0.0, 0.0, 0.8),
    'yellow': (0.8, 0.8, 0.0),
    'magenta': (0.8, 0.0, 0.8),
    'cyan': (0.0, 0.8, 0.8),
  }
  terminal_colors = {}
  for color_name, default_color in default_colors.items():
    terminal_colors[color_name] = determine_semantic_color(
      default_color,
      colors,
    )

    terminal_colors[
      f'bright{color_name.capitalize()}'] = determine_semantic_color(
        default_color,
        colors,
      )

  result = {
    'average_luminance': average_luminance,
    'average_saturation': average_saturation,
    'is_light_theme': is_light_theme,
    'colors': colors,
    'bootstrap': {
      'primary':
      adjust_contrast(
        primary,
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'secondary':
      adjust_contrast(
        secondary,
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'accent':
      adjust_contrast(
        accent,
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'background':
      adjust_contrast(
        background_color,
        average_luminance,
        is_light=is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'backgroundAlternate':
      adjust_contrast(
        background_color_2,
        average_luminance,
        is_light=is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'selection':
      adjust_contrast(
        selection_color,
        average_luminance,
        is_light=is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'text':
      adjust_contrast(
        text_color,
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'textAlternate':
      adjust_contrast(
        text_color_2,
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'danger':
      adjust_contrast(
        terminal_colors['red'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'warning':
      adjust_contrast(
        terminal_colors['yellow'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'info':
      adjust_contrast(
        terminal_colors['cyan'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'success':
      adjust_contrast(
        terminal_colors['green'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
    },
    'terminal': {
      'black':
      adjust_contrast(
        ansi_black,
        average_luminance,
        is_light=is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'white':
      adjust_contrast(
        ansi_white,
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightBlack':
      adjust_contrast(
        ansi_bright_black,
        average_luminance,
        is_light=is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightWhite':
      adjust_contrast(
        ansi_bright_white,
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'red':
      adjust_contrast(
        terminal_colors['red'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'green':
      adjust_contrast(
        terminal_colors['green'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'blue':
      adjust_contrast(
        terminal_colors['blue'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'yellow':
      adjust_contrast(
        terminal_colors['yellow'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'magenta':
      adjust_contrast(
        terminal_colors['magenta'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'cyan':
      adjust_contrast(
        terminal_colors['cyan'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightRed':
      adjust_contrast(
        terminal_colors['brightRed'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightGreen':
      adjust_contrast(
        terminal_colors['brightGreen'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightBlue':
      adjust_contrast(
        terminal_colors['brightBlue'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightYellow':
      adjust_contrast(
        terminal_colors['brightYellow'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightMagenta':
      adjust_contrast(
        terminal_colors['brightMagenta'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
      'brightCyan':
      adjust_contrast(
        terminal_colors['brightCyan'],
        average_luminance,
        is_light=not is_light_theme,
        invert=is_light_theme,
        high_contrast=high_contrast,
        k=k,
      ),
    }
  }
  return result


def parse_args():
  parser = argparse.ArgumentParser(description="Tint Gear")

  parser.add_argument(
    'image_path',
    type=str,
    help="Path to the image file.",
  )

  parser.add_argument(
    '-k',
    type=float,
    default=4.0,
    help="Contrast gap slope",
  )

  parser.add_argument(
    '--light_theme_threshold',
    type=float,
    default=0.25,
    help="Light theme lightness threshold",
    choices=[round(val * 0.01, 2) for val in range(0, 101)],
  )

  parser.add_argument(
    '--num_colors',
    type=int,
    default=8,
    help="Number of colors to generate for intermediate steps",
    choices=range(1, 17),
  )

  parser.add_argument(
    '--alternate',
    action='store_true',
    help="Alternate color mode",
  )

  parser.add_argument(
    '--high-contrast',
    action='store_true',
    help="High contrast mode",
  )

  parser.add_argument(
    '--pretty',
    action='store_true',
    help="Pretty print all colors",
  )

  parser.add_argument(
    '--json',
    action='store_true',
    help="When pretty printing, print indented json instead",
  )

  return parser.parse_args()


def print_colors(deserialized_colors, pretty=False, in_json=False):
  if pretty and not in_json:
    print(f"Average luminance = {deserialized_colors['average_luminance']}")
    print(f"Average saturation = {deserialized_colors['average_saturation']}")
    print(f"Is light theme = {deserialized_colors['is_light_theme']}")

    print("\nColors:")
    for key, color_tuple in enumerate(deserialized_colors['colors']):
      print(f"  {key}.: {srgb_to_hex(*color_tuple, pretty=True)}")

    print("\nBootstrap:")
    for key, color_tuple in deserialized_colors['bootstrap'].items():
      print(f"  {key.capitalize()}: {srgb_to_hex(*color_tuple, pretty=True)}")

    print("\nTerminal:")
    for key, color_tuple in deserialized_colors['terminal'].items():
      print(f"  {key}:  {srgb_to_hex(*color_tuple, pretty=True)}")
  else:
    json.dump(
      {
        'isLightTheme': deserialized_colors['is_light_theme'],
        'colors': [srgb_to_hex(*x) for x in deserialized_colors['colors']],
        'bootstrap': {
          key: srgb_to_hex(*value)
          for key, value in deserialized_colors['bootstrap'].items()
        },
        'terminal': {
          key: srgb_to_hex(*value)
          for key, value in deserialized_colors['terminal'].items()
        }
      },
      sys.stdout,
      indent=(2 if pretty else None),
    )


if __name__ == '__main__':
  main()
