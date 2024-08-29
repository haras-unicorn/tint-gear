from hypothesis import given, settings, strategies as st

from tint_gear.lib import (
  linear_srgb_to_oklab,
  oklab_to_linear_srgb,
  linear_srgb_to_srgb,
  srgb_to_linear_srgb,
  srgb_to_hex,
  hex_to_srgb,
  get_hue,
  set_hue,
  get_saturation,
  set_saturation,
  get_luminance,
  set_luminance,
  determine_theme_light_or_dark,
  determine_primary_secondary_accent,
  determine_black_white,
  determine_semantic_color,
  adjust_contrast,
)

MAX_SAMPLES = 10
DEADLINE = 100
EPSILON = 1e-6

LIGHTNESS_MIN = 0.0
LIGHTNESS_MAX = 1.0
AB_MIN = -1.0
AB_MAX = 1.0

RGB_MIN = 0.0
RGB_MAX = 1.0

HUE_MIN = 0.0
HUE_MAX = 360.0

SATURATION_MIN = 0.0
SATURATION_MAX = 1.0

LUMINANCE_MIN = 0.0
LUMINANCE_MAX = 1.0

rgb_values = st.floats(min_value=RGB_MIN, max_value=RGB_MAX)
hue_values = st.floats(min_value=HUE_MIN, max_value=HUE_MAX)
saturation_values = st.floats(
  min_value=SATURATION_MIN,
  max_value=SATURATION_MAX,
)
luminance_values = st.floats(min_value=LUMINANCE_MIN, max_value=LUMINANCE_MAX)


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
)
def test_linear_srgb_to_oklab_and_back(r, g, b):
  L, a, b_val = linear_srgb_to_oklab(r, g, b)

  assert LIGHTNESS_MIN <= L <= LIGHTNESS_MAX
  assert AB_MIN <= a <= AB_MAX
  assert AB_MIN <= b_val <= AB_MAX

  r_back, g_back, b_back = oklab_to_linear_srgb(L, a, b_val)

  assert RGB_MIN <= r_back <= RGB_MAX
  assert RGB_MIN <= g_back <= RGB_MAX
  assert RGB_MIN <= b_back <= RGB_MAX

  assert abs(r - r_back) <= EPSILON
  assert abs(g - g_back) <= EPSILON
  assert abs(b - b_back) <= EPSILON


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
)
def test_srgb_to_linear_srgb_and_back(r, g, b):
  linear_r, linear_g, linear_b = srgb_to_linear_srgb(r, g, b)

  assert RGB_MIN <= linear_r <= RGB_MAX
  assert RGB_MIN <= linear_g <= RGB_MAX
  assert RGB_MIN <= linear_b <= RGB_MAX

  r_back, g_back, b_back = linear_srgb_to_srgb(linear_r, linear_g, linear_b)

  assert RGB_MIN <= r_back <= RGB_MAX
  assert RGB_MIN <= g_back <= RGB_MAX
  assert RGB_MIN <= b_back <= RGB_MAX

  assert abs(r - r_back) <= EPSILON
  assert abs(g - g_back) <= EPSILON
  assert abs(b - b_back) <= EPSILON


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
)
def test_srgb_to_hex_and_back(r, g, b):
  hex_value = srgb_to_hex(r, g, b)

  r_back, g_back, b_back = hex_to_srgb(hex_value)

  assert RGB_MIN <= r_back <= RGB_MAX
  assert RGB_MIN <= g_back <= RGB_MAX
  assert RGB_MIN <= b_back <= RGB_MAX

  assert abs(r - r_back) <= 1e-1
  assert abs(g - g_back) <= 1e-1
  assert abs(b - b_back) <= 1e-1


@settings(max_examples=MAX_SAMPLES)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
)
def test_get_hue(r, g, b):
  hue = get_hue(r, g, b)

  assert HUE_MIN <= hue <= HUE_MAX


@settings(max_examples=MAX_SAMPLES)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
  target_hue=hue_values,
)
def test_set_hue(r, g, b, target_hue):
  r_new, g_new, b_new = set_hue(r, g, b, target_hue)

  assert RGB_MIN <= r_new <= RGB_MAX
  assert RGB_MIN <= g_new <= RGB_MAX
  assert RGB_MIN <= b_new <= RGB_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
)
def test_get_saturation(r, g, b):
  saturation = get_saturation(r, g, b)

  assert SATURATION_MIN <= saturation <= SATURATION_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
  target_saturation=saturation_values,
)
def test_set_saturation(r, g, b, target_saturation):
  r_new, g_new, b_new = set_saturation(r, g, b, target_saturation)

  assert RGB_MIN <= r_new <= RGB_MAX
  assert RGB_MIN <= g_new <= RGB_MAX
  assert RGB_MIN <= b_new <= RGB_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
)
def test_get_luminance(r, g, b):
  luminance = get_luminance(r, g, b)

  assert LUMINANCE_MIN <= luminance <= LUMINANCE_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  r=rgb_values,
  g=rgb_values,
  b=rgb_values,
  target_luminance=luminance_values,
)
def test_set_luminance(r, g, b, target_luminance):
  r_new, g_new, b_new = set_luminance(r, g, b, target_luminance)

  assert RGB_MIN <= r_new <= RGB_MAX
  assert RGB_MIN <= g_new <= RGB_MAX
  assert RGB_MIN <= b_new <= RGB_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(average_luminance=luminance_values, )
def test_determine_theme_light_or_dark(average_luminance) -> None:
  is_light_theme = determine_theme_light_or_dark(average_luminance)

  assert isinstance(is_light_theme, bool)


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  colors=st.lists(
    st.tuples(rgb_values, rgb_values, rgb_values),
    min_size=3,
    max_size=3,
  ),
  average_saturation=saturation_values,
)
def test_determine_primary_secondary_accent(colors, average_saturation) -> None:
  primary, secondary, accent = determine_primary_secondary_accent(
    colors,
    average_saturation,
  )

  assert RGB_MIN <= primary[0] <= RGB_MAX
  assert RGB_MIN <= primary[1] <= RGB_MAX
  assert RGB_MIN <= primary[2] <= RGB_MAX

  assert RGB_MIN <= secondary[0] <= RGB_MAX
  assert RGB_MIN <= secondary[1] <= RGB_MAX
  assert RGB_MIN <= secondary[2] <= RGB_MAX

  assert RGB_MIN <= accent[0] <= RGB_MAX
  assert RGB_MIN <= accent[1] <= RGB_MAX
  assert RGB_MIN <= accent[2] <= RGB_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  colors=st.lists(
    st.tuples(rgb_values, rgb_values, rgb_values),
    min_size=3,
  ),
  is_light_theme=st.booleans(),
  max_saturation=saturation_values,
)
def test_determine_black_white_colors(colors, is_light_theme, max_saturation):
  background_color, text_color = determine_black_white(colors, is_light_theme,
                                                       max_saturation)

  assert RGB_MIN <= background_color[0] <= RGB_MAX
  assert RGB_MIN <= background_color[1] <= RGB_MAX
  assert RGB_MIN <= background_color[2] <= RGB_MAX

  assert RGB_MIN <= text_color[0] <= RGB_MAX
  assert RGB_MIN <= text_color[1] <= RGB_MAX
  assert RGB_MIN <= text_color[2] <= RGB_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  default_color=st.tuples(
    rgb_values,
    rgb_values,
    rgb_values,
  ),
  colors=st.lists(
    st.tuples(rgb_values, rgb_values, rgb_values),
    min_size=3,
  ),
  hue_nudge_degrees=hue_values,
  saturation_decrease=saturation_values,
)
def test_determine_semantic_color(
  default_color,
  colors,
  hue_nudge_degrees,
  saturation_decrease,
):
  adjusted_color = determine_semantic_color(
    default_color,
    colors,
    hue_nudge_degrees,
    saturation_decrease,
  )

  assert RGB_MIN <= adjusted_color[0] <= RGB_MAX
  assert RGB_MIN <= adjusted_color[1] <= RGB_MAX
  assert RGB_MIN <= adjusted_color[2] <= RGB_MAX


@settings(max_examples=MAX_SAMPLES, deadline=DEADLINE)
@given(
  color=st.tuples(
    rgb_values,
    rgb_values,
    rgb_values,
  ),
  average_luminance=luminance_values,
  is_light_theme=st.booleans(),
  invert=st.booleans(),
  high_contrast=st.booleans(),
  k=st.floats(min_value=0, max_value=100),
)
def test_adjust_contrast(
  color,
  average_luminance,
  is_light_theme,
  invert,
  high_contrast,
  k,
):
  adjusted_color = adjust_contrast(
    color,
    average_luminance,
    is_light_theme,
    invert,
    high_contrast,
    k,
  )

  assert RGB_MIN <= adjusted_color[0] <= RGB_MAX
  assert RGB_MIN <= adjusted_color[1] <= RGB_MAX
  assert RGB_MIN <= adjusted_color[2] <= RGB_MAX
