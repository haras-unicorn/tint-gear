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

  primary, secondary, accent = determine_primary_secondary_accent(colors)

  def adjust_color_alternate(base_color, index, color_type):
    if color_type == 'black_white':
      alt_color, _ = determine_black_white(
        colors,
        is_light_theme,
        max_saturation=0.3,
        index=index + 1,
      )
      return alt_color
    elif color_type == 'semantic':
      return determine_semantic_color(
        base_color,
        colors,
        hue_nudge_degrees=20,
        saturation_decrease=0.2,
      )
    elif color_type == 'psa':
      primary_alt, secondary_alt, accent_alt = determine_primary_secondary_accent(
        colors,
        saturation_increase=0.4,
      )
      if base_color == primary:
        return primary_alt
      elif base_color == secondary:
        return secondary_alt
      elif base_color == accent:
        return accent_alt
      else:
        return base_color
    else:
      return base_color

  def create_color_object(
    base_color,
    invert=False,
    index=0,
    color_type='default',
  ):
    normal = adjust_contrast(
      base_color,
      average_luminance,
      is_light=not is_light_theme if invert else is_light_theme,
      invert=is_light_theme,
      high_contrast=high_contrast,
      k=k,
    )
    high_contrast_color = adjust_contrast(
      base_color,
      average_luminance,
      is_light=not is_light_theme if invert else is_light_theme,
      invert=is_light_theme,
      high_contrast=not high_contrast,
      k=k,
    )
    inverted = adjust_contrast(
      base_color,
      average_luminance,
      is_light=is_light_theme if invert else not is_light_theme,
      invert=is_light_theme,
      high_contrast=high_contrast,
      k=k,
    )
    alternate_color = adjust_contrast(
      adjust_color_alternate(
        base_color,
        index=index,
        color_type=color_type,
      ),
      average_luminance,
      is_light=not is_light_theme if invert else is_light_theme,
      invert=is_light_theme,
      high_contrast=high_contrast,
      k=k,
    )
    return {
      'normal': normal,
      'high_contrast': high_contrast_color,
      'inverted': inverted,
      'alternate': alternate_color,
    }

  bootstrap_colors = {}
  for name, color in zip(['primary', 'secondary', 'accent'],
                         [primary, secondary, accent]):
    bootstrap_colors[name] = create_color_object(
      color,
      color_type='psa',
      invert=True,
    )

  text_color, background_color = determine_black_white(
    colors,
    is_light_theme,
    max_saturation=0.1,
  )
  selection_color, text_selection_color = determine_black_white(
    colors,
    is_light_theme,
    max_saturation=0.3,
    index=2,
  )
  text_colors = {}
  for name, color, index in [
    ('text', text_color, 0),
    ('background', background_color, 0),
    ('textSelection', selection_color, 2),
    ('selection', selection_color, 2),
  ]:
    text_colors[name] = create_color_object(
      color,
      index=index,
      color_type='black_white',
      invert=(name == 'text' or name == 'textSelection'),
    )

  ansi_colors = {}
  ansi_black, ansi_white = background_color, text_color
  ansi_bright_black, ansi_bright_white = selection_color, text_selection_color
  ansi_colors['black'] = create_color_object(
    ansi_black,
    color_type='black_white',
  )
  ansi_colors['white'] = create_color_object(
    ansi_white,
    color_type='black_white',
    invert=True,
  )
  ansi_colors['brightBlack'] = create_color_object(
    ansi_bright_black,
    color_type='black_white',
  )
  ansi_colors['brightWhite'] = create_color_object(
    ansi_bright_white,
    color_type='black_white',
    invert=True,
  )
  default_colors = {
    'red': (0.8, 0.0, 0.0),
    'green': (0.0, 0.8, 0.0),
    'blue': (0.0, 0.0, 0.8),
    'yellow': (0.8, 0.8, 0.0),
    'magenta': (0.8, 0.0, 0.8),
    'cyan': (0.0, 0.8, 0.8),
  }
  for color_name, default_color in default_colors.items():
    color = determine_semantic_color(default_color, colors)
    ansi_colors[color_name] = create_color_object(
      color,
      color_type='semantic',
      invert=True,
    )
    bright_color = determine_semantic_color(default_color, colors)
    ansi_colors[f'bright{color_name.capitalize()}'] = create_color_object(
      bright_color,
      color_type='semantic',
      invert=True,
    )

  bootstrap_semantic_colors = {}
  for name, terminal_color_name in [
    ('danger', 'red'),
    ('warning', 'yellow'),
    ('info', 'cyan'),
    ('success', 'green'),
  ]:
    color_object = ansi_colors[terminal_color_name]
    bootstrap_semantic_colors[name] = color_object

  result = {
    'average_luminance': average_luminance,
    'average_saturation': average_saturation,
    'is_light_theme': is_light_theme,
    'colors': colors,
    'bootstrap': {
      **bootstrap_colors,
      **text_colors,
      **bootstrap_semantic_colors
    },
    'terminal': ansi_colors,
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
    print(f"Is light theme = {deserialized_colors['is_light_theme']}\n")

    print("Colors:")
    for index, color_tuple in enumerate(deserialized_colors['colors']):
      print(f"  {index}.: {srgb_to_hex(*color_tuple, pretty=True)}")

    print("\nBootstrap:")
    for key, color_object in deserialized_colors['bootstrap'].items():
      print(f"  {key.capitalize()}:")
      for subkey, value in color_object.items():
        if isinstance(value, tuple):
          print(f"    {subkey}: {srgb_to_hex(*value, pretty=True)}")
        elif isinstance(value, dict):
          print(f"    {subkey}:")
          for semantic_name, semantic_color in value.items():
            print(
              f"      {semantic_name}: {srgb_to_hex(*semantic_color, pretty=True)}"
            )
        else:
          print(f"    {subkey}: {value}")

    print("\nTerminal:")
    for key, color_object in deserialized_colors['terminal'].items():
      print(f"  {key}:")
      for subkey, value in color_object.items():
        if isinstance(value, tuple):
          print(f"    {subkey}: {srgb_to_hex(*value, pretty=True)}")
        elif isinstance(value, dict):
          print(f"    {subkey}:")
          for semantic_name, semantic_color in value.items():
            print(
              f"      {semantic_name}: {srgb_to_hex(*semantic_color, pretty=True)}"
            )
        else:
          print(f"    {subkey}: {value}")
  else:
    json.dump(
      {
        'isLightTheme': deserialized_colors['is_light_theme'],
        'colors': [srgb_to_hex(*x) for x in deserialized_colors['colors']],
        'bootstrap': {
          key: {
            subkey: (srgb_to_hex(*value) if isinstance(value, tuple) else {
              k: srgb_to_hex(*v)
              for k, v in value.items()
            } if isinstance(value, dict) else value)
            for subkey, value in color_object.items()
          }
          for key, color_object in deserialized_colors['bootstrap'].items()
        },
        'terminal': {
          key: {
            subkey: (srgb_to_hex(*value) if isinstance(value, tuple) else {
              k: srgb_to_hex(*v)
              for k, v in value.items()
            } if isinstance(value, dict) else value)
            for subkey, value in color_object.items()
          }
          for key, color_object in deserialized_colors['terminal'].items()
        }
      },
      sys.stdout,
      indent=(2 if pretty else None),
    )


if __name__ == '__main__':
  main()
