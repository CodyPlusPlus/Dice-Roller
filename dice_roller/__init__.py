import os, sys, math, random

APP_DIR = "/system/apps/dice_roller"

sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

# Fonts
font_big = pixel_font.load("/system/assets/fonts/ignore.ppf")
font_small = rom_font.sins

# -----------------------------
# HSV to RGB
# -----------------------------
def hsv_to_rgb(h, s, v):
  i = int(h * 6)
  f = (h * 6) - i
  p = int(255 * v * (1 - s))
  q = int(255 * v * (1 - s * f))
  t = int(255 * v * (1 - s * (1 - f)))
  vi = int(255 * v)
  i %= 6
  if i == 0: return (vi, t, p)
  if i == 1: return (q, vi, p)
  if i == 2: return (p, vi, t)
  if i == 3: return (p, q, vi)
  if i == 4: return (t, p, vi)
  return (vi, p, q)

# -----------------------------
# 3D Meshes
# -----------------------------
def shape_coin_d2():
  n = 12
  radius = 1.0
  height = 0.1
  verts = []
  for i in range(n):
    theta = 2 * math.pi * i / n
    verts.append((radius * math.cos(theta), height / 2, radius * math.sin(theta)))
  for i in range(n):
    theta = 2 * math.pi * i / n
    verts.append((radius * math.cos(theta), -height / 2, radius * math.sin(theta)))
  edges = []
  for i in range(n):
    edges.append((i, (i + 1) % n))
    edges.append((n + i, n + ((i + 1) % n)))
    edges.append((i, n + i))
  return (verts, edges)

def shape_prism_d3():
  # triangular bipyramid ("crystal"/spindle), 6 faces
  radius = 1.0
  height = 1.2
  verts = []
  for i in range(3):
    theta = 2 * math.pi * i / 3
    verts.append((radius * math.cos(theta), 0, radius * math.sin(theta)))
  top = (0, height, 0)
  bottom = (0, -height, 0)
  verts.append(top)
  verts.append(bottom)
  edges = []
  for i in range(3):
    edges.append((i, (i + 1) % 3))
    edges.append((i, 3))
    edges.append((i, 4))
  return (verts, edges)

def shape_tetra_d4():
  verts = [(1,1,1),(1,-1,-1),(-1,1,-1),(-1,-1,1)]
  edges = []
  for i in range(4):
    for j in range(i + 1, 4):
      edges.append((i, j))
  return (verts, edges)

def shape_cube_d6():
  verts = []
  for dx in [-1,1]:
    for dy in [-1,1]:
      for dz in [-1,1]:
        verts.append((dx, dy, dz))
  edges = []
  for i in range(len(verts)):
    x1,y1,z1 = verts[i]
    for j in range(i + 1, len(verts)):
      x2,y2,z2 = verts[j]
      if abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2) == 2:
        edges.append((i, j))
  return (verts, edges)

def shape_octa_d8():
  s = 1.5
  verts = [( s,0,0),(-s,0,0),(0, s,0),(0,-s,0),(0,0, s),(0,0,-s)]
  edges = []
  ideal_sq = 2 * (s ** 2)
  for i in range(len(verts)):
    x1,y1,z1 = verts[i]
    for j in range(i + 1, len(verts)):
      x2,y2,z2 = verts[j]
      d2 = (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2
      if abs(d2 - ideal_sq) < 0.01:
        edges.append((i, j))
  return (verts, edges)

def shape_pentabip_d10():
  n = 5
  ring_r = 1.5
  top_y = 1.8
  bot_y = -1.8
  ring_verts = []
  for i in range(n):
    theta = 2 * math.pi * i / n
    ring_verts.append((ring_r * math.cos(theta), 0, ring_r * math.sin(theta)))
  top = (0, top_y, 0)
  bot = (0, bot_y, 0)
  verts = [top] + ring_verts + [bot]
  edges = []
  for i in range(n):
    edges.append((1 + i, 1 + ((i + 1) % n)))
    edges.append((0, 1 + i))
    edges.append((1 + n, 1 + i))
  return (verts, edges)

def shape_dodeca_d12():
  phi = (1 + math.sqrt(5)) / 2
  base_verts = [
    (1,1,1),(1,1,-1),(1,-1,1),(1,-1,-1),
    (-1,1,1),(-1,1,-1),(-1,-1,1),(-1,-1,-1),
    (0,1/phi,phi),(0,1/phi,-phi),(0,-1/phi,phi),(0,-1/phi,-phi),
    (1/phi,phi,0),(-1/phi,phi,0),(1/phi,-phi,0),(-1/phi,-phi,0),
    (phi,0,1/phi),(-phi,0,1/phi),(phi,0,-1/phi),(-phi,0,-1/phi)
  ]
  dists = []
  for i in range(len(base_verts)):
    for j in range(i + 1, len(base_verts)):
      x1,y1,z1 = base_verts[i]
      x2,y2,z2 = base_verts[j]
      dists.append(math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))
  mn = sorted(set(round(x, 5) for x in dists if x > 0))[0]
  edges = []
  for i in range(len(base_verts)):
    for j in range(i + 1, len(base_verts)):
      x1,y1,z1 = base_verts[i]
      x2,y2,z2 = base_verts[j]
      dd = math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
      if abs(dd - mn) < 1e-3:
        edges.append((i, j))
  return (base_verts, edges)

def shape_icosa_d20():
  phi = (1 + math.sqrt(5)) / 2
  base_verts = [
    (0,1,phi),(0,-1,phi),(0,1,-phi),(0,-1,-phi),
    (1,phi,0),(-1,phi,0),(1,-phi,0),(-1,-phi,0),
    (phi,0,1),(phi,0,-1),(-phi,0,1),(-phi,0,-1)
  ]
  dists = []
  for i in range(len(base_verts)):
    for j in range(i + 1, len(base_verts)):
      x1,y1,z1 = base_verts[i]
      x2,y2,z2 = base_verts[j]
      dists.append(math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2))
  mn = sorted(set(round(x, 5) for x in dists if x > 0))[0]
  edges = []
  for i in range(len(base_verts)):
    for j in range(i + 1, len(base_verts)):
      x1,y1,z1 = base_verts[i]
      x2,y2,z2 = base_verts[j]
      dd = math.sqrt((x1-x2)**2+(y1-y2)**2+(z1-z2)**2)
      if abs(dd - mn) < 1e-3:
        edges.append((i, j))
  return (base_verts, edges)

def shape_sphere_d100():
  lat_steps = 6
  lon_steps = 8
  radius = 1.2
  verts = []
  for i in range(lat_steps + 1):
    lat = math.pi * (i / lat_steps - 0.5)
    y = radius * math.sin(lat)
    r_ring = radius * math.cos(lat)
    for j in range(lon_steps):
      lon = 2 * math.pi * (j / lon_steps)
      x = r_ring * math.cos(lon)
      z = r_ring * math.sin(lon)
      verts.append((x, y, z))
  edges = []
  def idx(a, b): return a * lon_steps + b
  for a in range(lat_steps + 1):
    for b in range(lon_steps):
      b2 = (b + 1) % lon_steps
      edges.append((idx(a, b), idx(a, b2)))
      if a < lat_steps:
        edges.append((idx(a, b), idx(a + 1, b)))
  return (verts, edges)

def get_shape_for_die(d):
  if d == 2: return shape_coin_d2()
  if d == 3: return shape_prism_d3()
  if d == 4: return shape_tetra_d4()
  if d == 6: return shape_cube_d6()
  if d == 8: return shape_octa_d8()
  if d == 10: return shape_pentabip_d10()
  if d == 12: return shape_dodeca_d12()
  if d == 20: return shape_icosa_d20()
  if d == 100: return shape_sphere_d100()
  return shape_icosa_d20()

# Dice state
dice_sizes = [2,3,4,6,8,10,12,20,100]
dice_index = 7
quantity = 1
roll_total = None
rolls_list = []
prev_roll_total = None

current_verts, current_edges = shape_icosa_d20()
proj_points = []

# Roll control
HOLD_THRESHOLD = 1000
b_pressed_start = None
b_long_press_done = False
b_was_pressed = False

roll_end_time = 0
NORMAL_SPIN_SPEED = 0.02
FAST_SPIN_SPEED = 0.12
SPIN_DURATION_MS = 1000
DEMO_HOLD_THRESHOLD = 3000
DEMO_CYCLE_MS = 8000

angle_x = 0.0
angle_y = 0.0
hue = 0.0

# Demo mode
demo_mode = False
demo_hold_start = None
demo_hold_done = False
demo_start_time = 0
demo_index = -1
demo_order = [4, 6, 8, 10, 12, 20]

# Scaled roll text cache
roll_cache_text = ""
roll_cache_img = None

def do_roll(ds, qt):
  rolls = []
  for _ in range(qt):
    rolls.append(random.randint(1, ds))
  return rolls


def draw_text_with_shadow(txt, x, y):
  screen.pen = color.rgb(0, 0, 0)
  screen.text(txt, x + 2, y + 2)
  screen.pen = color.rgb(255, 255, 255)
  screen.text(txt, x, y)


def get_roll_image(text):
  global roll_cache_text, roll_cache_img
  if text == roll_cache_text and roll_cache_img:
    return roll_cache_img
  screen.font = font_big
  w, h = screen.measure_text(text)
  img = image(int(w) + 4, int(h) + 4)
  img.font = font_big
  img.pen = color.rgb(0, 0, 0, 0)
  img.clear()
  img.pen = color.rgb(0, 0, 0)
  img.text(text, 2, 2)
  img.pen = color.rgb(255, 255, 255)
  img.text(text, 0, 0)
  roll_cache_text = text
  roll_cache_img = img
  return img


def ensure_proj_points():
  global proj_points
  n = len(current_verts)
  if len(proj_points) != n:
    proj_points = [[0.0, 0.0] for _ in range(n)]


def draw_ui(w, h):
  screen.font = font_small
  desc = f"{quantity}x d{dice_sizes[dice_index]}"
  w_desc, _ = screen.measure_text(desc)
  x_desc = (w - w_desc) // 2
  y_desc = int(h * 0.85)
  draw_text_with_shadow(desc, x_desc, y_desc)

  if roll_total is not None:
    s_val = str(roll_total) +"!"
    roll_img = get_roll_image(s_val)
    scale = 2
    w_val = roll_img.width * scale
    h_val = roll_img.height * scale
    x_val = (w - w_val) // 2
    y_val = int(0.30 * (h - h_val))
    screen.blit(roll_img, rect(x_val, y_val, w_val, h_val))

  if len(rolls_list) > 1: # dont need to show if there is only one die
    screen.font = font_small
    top_y = int(h * 0.05)
    rolls_text = "+".join(str(v) for v in rolls_list) + "="
    w_rolls, _ = screen.measure_text(rolls_text)
    if w_rolls > int(w * 0.90):
      rolls_text = " . . . "
      w_rolls, _ = screen.measure_text(rolls_text)
    x_rolls = (w - w_rolls) // 2
    draw_text_with_shadow(rolls_text, x_rolls, top_y)

  if prev_roll_total is not None:
    s_val =  str(prev_roll_total) + "<<"
    roll_img = get_roll_image(s_val)
    scale = 1
    w_val = roll_img.width * scale
    h_val = roll_img.height * scale
    x_val = ((w - w_val) // 2)
    y_val =int( 0.80 * (h - h_val))
    screen.blit(roll_img, rect(x_val, y_val, w_val, h_val))

def rotate_and_draw(w, h, scale, now_ms, show_ui=True):
  global angle_x, angle_y, hue
  spin = FAST_SPIN_SPEED if (now_ms < roll_end_time) else NORMAL_SPIN_SPEED

  angle_x += spin
  angle_y += spin * 0.7

  screen.pen = color.rgb(0, 0, 0)
  screen.clear()

  hue = (hue + 0.003) % 1.0
  r, g, b = hsv_to_rgb(hue, 1, 1)
  screen.pen = color.rgb(r, g, b)

  cosx = math.cos(angle_x)
  sinx = math.sin(angle_x)
  cosy = math.cos(angle_y)
  siny = math.sin(angle_y)
  cam = 4.0

  cx = w / 2
  cy = h / 2
  ensure_proj_points()
  for idx, (vx, vy, vz) in enumerate(current_verts):
    y2 = vy * cosx - vz * sinx
    z2 = vy * sinx + vz * cosx
    x3 = vx * cosy + z2 * siny
    z3 = -vx * siny + z2 * cosy
    f = cam / (cam + z3)
    sx = x3 * f * scale + cx
    sy = y2 * f * scale + cy
    proj_points[idx][0] = sx
    proj_points[idx][1] = sy

  for (i, j) in current_edges:
    x1, y1 = proj_points[i]
    x2, y2 = proj_points[j]
    screen.line(int(x1), int(y1), int(x2), int(y2))

  if show_ui:
    draw_ui(w, h)

def reset_rolls():
  global roll_total, prev_roll_total, rolls_list
  roll_total = None
  prev_roll_total = None
  rolls_list = []

def update():
  global dice_index, quantity, roll_total, prev_roll_total, rolls_list
  global b_pressed_start, b_long_press_done, b_was_pressed
  global current_verts, current_edges, roll_end_time
  global demo_mode, demo_hold_start, demo_hold_done, demo_start_time, demo_index

  w = screen.width
  h = screen.height
  scale = min(w, h) * 0.23
  now_ms = io.ticks

  # UP + DOWN: hold to toggle demo mode
  demo_combo_now = (io.BUTTON_UP in io.held) and (io.BUTTON_DOWN in io.held)
  if demo_combo_now:
    if demo_hold_start is None:
      demo_hold_start = now_ms
      demo_hold_done = False
    elif not demo_hold_done and (now_ms - demo_hold_start) >= DEMO_HOLD_THRESHOLD:
      demo_mode = not demo_mode
      demo_hold_done = True
      if demo_mode:
        demo_start_time = now_ms
        demo_index = -1
      else:
        current_verts, current_edges = get_shape_for_die(dice_sizes[dice_index])
  else:
    demo_hold_start = None
    demo_hold_done = False

  if demo_mode:
    elapsed = now_ms - demo_start_time
    next_index = (elapsed // DEMO_CYCLE_MS) % len(demo_order)
    if next_index != demo_index:
      demo_index = next_index
      current_verts, current_edges = get_shape_for_die(demo_order[demo_index])
    rotate_and_draw(w, h, scale, now_ms, show_ui=False)
    return

  # Buttons (edge-triggered)
  if io.BUTTON_C in io.pressed:
    dice_index = (dice_index + 1) % len(dice_sizes)
    current_verts, current_edges = get_shape_for_die(dice_sizes[dice_index])
    reset_rolls()

  if io.BUTTON_A in io.pressed:
    dice_index -= 1
    if dice_index < 0:
      dice_index = len(dice_sizes) - 1
    current_verts, current_edges = get_shape_for_die(dice_sizes[dice_index])
    reset_rolls()

  if io.BUTTON_UP in io.pressed:
    quantity += 1
    reset_rolls()

  if io.BUTTON_DOWN in io.pressed:
    quantity -= 1
    if quantity < 1:
      quantity = 1
    reset_rolls()

  # B: short roll, long reset
  b_now = io.BUTTON_B in io.held
  if b_now:
    if not b_was_pressed:
      b_pressed_start = now_ms
      b_was_pressed = True
      b_long_press_done = False
    elif not b_long_press_done:
      if (now_ms - b_pressed_start) >= HOLD_THRESHOLD:
        quantity = 1
        dice_index = dice_sizes.index(20)
        reset_rolls()
        current_verts, current_edges = shape_icosa_d20()
        b_long_press_done = True
  else:
    if b_was_pressed:
      if not b_long_press_done:
        ds = dice_sizes[dice_index]
        if roll_total is None:
          rolls_list = do_roll(ds, quantity)
          roll_total = sum(rolls_list)
        else:
          prev_roll_total = roll_total
          rolls_list = do_roll(ds, quantity)
          roll_total = sum(rolls_list)
        roll_end_time = now_ms + SPIN_DURATION_MS
      b_was_pressed = False

  rotate_and_draw(w, h, scale, now_ms)


def on_exit():
  pass


if __name__ == "__main__":
  run(update)
