
import os
import random
import sys

import cv2
import numpy as np
import pygame

from hand_tracking import Camera, HandTracker


pygame.init()

GAME_WIDTH = 600
GAME_HEIGHT = 600
PANEL_WIDTH = 300
SCREEN_WIDTH = GAME_WIDTH + PANEL_WIDTH
SCREEN_HEIGHT = GAME_HEIGHT

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fruity Catch")

clock = pygame.time.Clock()
FPS = 45

GAME_DURATION = 40
STARTING_LIVES = 5

WHITE = (255, 255, 255)
BLACK = (35, 38, 45)
DARK_BLUE = (35, 55, 85)
PALE_BLUE = (225, 244, 255)
GREEN = (103, 180, 110)
DARK_GREEN = (55, 130, 75)
BROWN = (135, 83, 48)
LIGHT_BROWN = (190, 130, 75)
RED = (230, 65, 75)
YELLOW = (255, 210, 80)
GRAY = (125, 130, 140)
LIGHT_GRAY = (225, 228, 233)

font_title = pygame.font.SysFont("Arial", 38, bold=True)
font_large = pygame.font.SysFont("Arial", 30, bold=True)
font_medium = pygame.font.SysFont("Arial", 23, bold=True)
font_small = pygame.font.SysFont("Arial", 17)
font_tiny = pygame.font.SysFont("Arial", 14)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSET_DIR = os.path.join(BASE_DIR, "assets")


def asset_path(filename):
    in_assets = os.path.join(ASSET_DIR, filename)
    beside_game = os.path.join(BASE_DIR, filename)

    if os.path.isfile(in_assets):
        return in_assets

    if os.path.isfile(beside_game):
        return beside_game

    raise FileNotFoundError(
        f"File '{filename}' tidak ditemukan. "
        "Periksa folder assets atau folder game.py."
    )


def load_image(filename, size):
    image = pygame.image.load(asset_path(filename)).convert_alpha()
    return pygame.transform.smoothscale(image, size)


try:
    background_image = pygame.image.load(
        asset_path("background.png")
    ).convert()

    background_image = pygame.transform.smoothscale(
        background_image,
        (GAME_WIDTH, GAME_HEIGHT)
    )

    basket_image = load_image("keranjang.png", (120, 55))

    FRUIT_FILES = [
        "manggis.png",
        "mangga.png",
        "apel.png",
        "pir.png",
        "jeruk.png",
        "anggur.png"
    ]

    FRUIT_SIZE = (44, 44)

    fruit_images = {
        filename: load_image(filename, FRUIT_SIZE)
        for filename in FRUIT_FILES
    }

except (FileNotFoundError, pygame.error) as error:
    print(f"Gagal memuat gambar: {error}")
    print("Periksa nama dan lokasi semua file gambar.")
    pygame.quit()
    raise SystemExit(1)


BASKET_WIDTH = basket_image.get_width()
BASKET_HEIGHT = basket_image.get_height()

BASKET_Y = GAME_HEIGHT - BASKET_HEIGHT - 18
BASKET_KEYBOARD_SPEED = 420

MIN_FRUIT_SPEED = 70
MAX_FRUIT_SPEED = 150

SPAWN_INTERVAL_MIN = 1.0
SPAWN_INTERVAL_MAX = 1.8

MAX_FRUITS = 8

camera = None
tracker = None
camera_active = False

try:
    camera = Camera(
        index=0,
        width=640,
        height=480,
        mirror=True
    ).open()

    tracker = HandTracker()
    camera_active = True

    print("Kamera berhasil dibuka.")
    print("Klik warna sarung tangan di panel kamera untuk kalibrasi.")
    print("Tekan C untuk mengulang kalibrasi.")

except Exception as error:
    print(f"Kamera tidak tersedia: {error}")
    print("Game akan menggunakan keyboard.")

    if tracker is not None:
        try:
            tracker.close()
        except Exception:
            pass
        tracker = None

    if camera is not None:
        camera.release()
        camera = None


CAMERA_RECT = pygame.Rect(
    GAME_WIDTH + 18,
    112,
    PANEL_WIDTH - 36,
    150
)

MASK_RECT = pygame.Rect(
    GAME_WIDTH + 18,
    326,
    PANEL_WIDTH - 36,
    150
)


def create_fruit():
    filename = random.choice(FRUIT_FILES)
    width, height = FRUIT_SIZE

    return {
        "name": filename,
        "x": random.randint(0, GAME_WIDTH - width),
        "y": -height,
        "speed": random.uniform(
            MIN_FRUIT_SPEED,
            MAX_FRUIT_SPEED
        )
    }

game_started = False
countdown_start_ticks = None
countdown_active = False

def reset_game():
    global basket_x, score, lives
    global start_ticks, time_left
    global game_over, gesture_status
    global fruits, next_spawn_time
    global game_started, countdown_start_ticks, countdown_active

    basket_x = (GAME_WIDTH - BASKET_WIDTH) // 2
    score = 0
    lives = STARTING_LIVES
    start_ticks = pygame.time.get_ticks()
    time_left = GAME_DURATION
    game_over = False
    gesture_status = "Klik kamera untuk kalibrasi"

    fruits = [create_fruit()]

    next_spawn_time = random.uniform(
        SPAWN_INTERVAL_MIN,
        SPAWN_INTERVAL_MAX
    )
    game_started = not camera_active
    countdown_start_ticks = None
    countdown_active = False


def draw_text(text, font, color, x, y):
    image = font.render(text, True, color)
    screen.blit(image, (x, y))


def draw_centered(text, font, color, center_x, center_y):
    image = font.render(text, True, color)
    rect = image.get_rect(center=(center_x, center_y))
    screen.blit(image, rect)


def draw_heart(x, y, size, color):
    r = size // 4

    pygame.draw.circle(
        screen,
        color,
        (x - r, y - r // 2),
        r
    )

    pygame.draw.circle(
        screen,
        color,
        (x + r, y - r // 2),
        r
    )

    points = [
        (x - 2 * r, y - r // 3),
        (x + 2 * r, y - r // 3),
        (x, y + 2 * r)
    ]

    pygame.draw.polygon(screen, color, points)


def draw_lives():
    draw_text("NYAWA", font_tiny, DARK_BLUE, 165, 24)

    for i in range(STARTING_LIVES):
        heart_color = RED if i < lives else LIGHT_GRAY
        draw_heart(180 + i * 26, 62, 20, heart_color)


def draw_background():
    screen.blit(background_image, (0, 0))


def draw_hud():
    pygame.draw.rect(
        screen,
        WHITE,
        (15, 15, 380, 82),
        border_radius=12
    )

    draw_text(
        f"SKOR  {score}",
        font_medium,
        DARK_BLUE,
        28,
        25
    )

    timer_color = DARK_GREEN if time_left > 5 else RED

    draw_text(
        f"WAKTU  {time_left}s",
        font_small,
        timer_color,
        29,
        63
    )

    draw_lives()


def draw_camera_panel(camera_surface, mask_surface, status):
    panel_x = GAME_WIDTH

    pygame.draw.rect(
        screen,
        PALE_BLUE,
        (panel_x, 0, PANEL_WIDTH, SCREEN_HEIGHT)
    )

    pygame.draw.rect(
        screen,
        DARK_BLUE,
        (panel_x, 0, PANEL_WIDTH, 65)
    )

    draw_text(
        "FRUITY CATCH",
        font_medium,
        WHITE,
        panel_x + 20,
        10
    )

    draw_text(
        "COLOR TRACKING",
        font_tiny,
        LIGHT_GRAY,
        panel_x + 22,
        39
    )

    draw_text(
        "DETEKSI KAMERA",
        font_small,
        DARK_BLUE,
        panel_x + 18,
        82
    )

    pygame.draw.rect(
        screen,
        BLACK,
        CAMERA_RECT.inflate(6, 6),
        border_radius=8
    )

    if camera_surface is not None:
        fitted_camera = pygame.transform.smoothscale(
            camera_surface,
            CAMERA_RECT.size
        )

        screen.blit(fitted_camera, CAMERA_RECT)

    else:
        pygame.draw.rect(
            screen,
            LIGHT_GRAY,
            CAMERA_RECT,
            border_radius=5
        )

        draw_centered(
            "Kamera tidak tersedia",
            font_tiny,
            GRAY,
            CAMERA_RECT.centerx,
            CAMERA_RECT.centery
        )

    draw_text(
        "MASKING",
        font_small,
        DARK_BLUE,
        panel_x + 18,
        296
    )

    pygame.draw.rect(
        screen,
        BLACK,
        MASK_RECT.inflate(6, 6),
        border_radius=8
    )

    if mask_surface is not None:
        fitted_mask = pygame.transform.smoothscale(
            mask_surface,
            MASK_RECT.size
        )

        screen.blit(fitted_mask, MASK_RECT)

    else:
        pygame.draw.rect(
            screen,
            BLACK,
            MASK_RECT,
            border_radius=5
        )

    draw_text(
        "STATUS",
        font_small,
        DARK_BLUE,
        panel_x + 18,
        491
    )

    pygame.draw.rect(
        screen,
        WHITE,
        (panel_x + 18, 516, PANEL_WIDTH - 36, 34),
        border_radius=8
    )

    if (
        camera_active
        and tracker is not None
        and tracker.has_hand()
    ):
        status_color = DARK_GREEN
    else:
        status_color = RED

    draw_text(
        status[:29],
        font_tiny,
        status_color,
        panel_x + 27,
        526
    )

    draw_text(
        "Klik kamera: kalibrasi warna",
        font_tiny,
        BLACK,
        panel_x + 18,
        558
    )

    draw_text(
        "C: kalibrasi ulang  |  ESC: keluar",
        font_tiny,
        GRAY,
        panel_x + 18,
        579
    )


def draw_game_over():
    overlay = pygame.Surface(
        (GAME_WIDTH, GAME_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((20, 35, 55, 190))
    screen.blit(overlay, (0, 0))

    title = "NYAWA HABIS!" if lives <= 0 else "WAKTU HABIS!"

    draw_centered(
        title,
        font_title,
        WHITE,
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 - 75
    )

    draw_centered(
        f"Skor akhir: {score}",
        font_large,
        (255, 210, 80),
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 - 15
    )

    draw_centered(
        f"Sisa nyawa: {lives}",
        font_medium,
        WHITE,
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 + 30
    )

    draw_centered(
        "Tekan R untuk bermain lagi",
        font_small,
        WHITE,
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 + 80
    )

def draw_countdown():
    if not countdown_active:
        return

    overlay = pygame.Surface(
        (GAME_WIDTH, GAME_HEIGHT),
        pygame.SRCALPHA
    )
    overlay.fill((20, 35, 55, 150))
    screen.blit(overlay, (0, 0))

    elapsed = (
        pygame.time.get_ticks() - countdown_start_ticks
    ) / 1000.0

    number = max(1, 3 - int(elapsed))

    draw_centered(
        "BERSIAP!",
        font_large,
        WHITE,
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 - 55
    )

    draw_centered(
        str(number),
        font_title,
        YELLOW,
        GAME_WIDTH // 2,
        GAME_HEIGHT // 2 + 10
    )

reset_game()

running = True
camera_surface = None
mask_surface = None
latest_frame = None

try:
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_c:
                    if tracker is not None:
                        tracker.reset_calibration()
                        countdown_start_ticks = None
                        countdown_active = False
                        game_started = False
                        gesture_status = "Klik warna target untuk kalibrasi"

                elif game_over and event.key == pygame.K_r:
                    reset_game()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if (
                    event.button == 1
                    and camera_active
                    and tracker is not None
                    and latest_frame is not None
                    and CAMERA_RECT.collidepoint(event.pos)
                ):
                    mouse_x, mouse_y = event.pos

                    frame_x = int(
                        (mouse_x - CAMERA_RECT.x)
                        * latest_frame.shape[1]
                        / CAMERA_RECT.width
                    )

                    frame_y = int(
                        (mouse_y - CAMERA_RECT.y)
                        * latest_frame.shape[0]
                        / CAMERA_RECT.height
                    )

                    if tracker.calibrate(
                        latest_frame,
                        frame_x,
                        frame_y
                    ):
                        color = tracker.target_color

                        gesture_status = (
                            "Warna berhasil dikalibrasi"
                        )

                        print(
                            "Kalibrasi berhasil: "
                            f"HSV=({int(color[0])}, "
                            f"{int(color[1])}, "
                            f"{int(color[2])})"
                        )
                        countdown_start_ticks = pygame.time.get_ticks()
                        countdown_active = True
                        countdown_value = 3
                        game_started = False

        keys = pygame.key.get_pressed()
        use_keyboard = True

        if (
            camera_active
            and camera is not None
            and tracker is not None
        ):
            try:
                ok, frame = camera.read()

                if ok:
                    latest_frame = frame.copy()

                    processed_frame = tracker.process(
                        frame,
                        draw=True
                    )

                    camera_rgb = cv2.cvtColor(
                        processed_frame,
                        cv2.COLOR_BGR2RGB
                    )

                    camera_surface = pygame.surfarray.make_surface(
                        camera_rgb.swapaxes(0, 1)
                    )

                    mask = tracker.get_mask()

                    if mask is not None:
                        mask_rgb = cv2.cvtColor(
                            mask,
                            cv2.COLOR_GRAY2RGB
                        )

                        mask_surface = pygame.surfarray.make_surface(
                            mask_rgb.swapaxes(0, 1)
                        )

                    else:
                        mask_surface = None

                    if tracker.has_hand():
                        position = tracker.get_position()

                        if position is not None:
                            target_x = position[0]

                            basket_x = int(
                                target_x
                                / frame.shape[1]
                                * GAME_WIDTH
                                - BASKET_WIDTH / 2
                            )

                            basket_x = max(
                                0,
                                min(
                                    basket_x,
                                    GAME_WIDTH - BASKET_WIDTH
                                )
                            )

                            gesture_status = (
                                "Warna target terdeteksi"
                            )

                            use_keyboard = False

                    else:
                        gesture_status = "Target tidak terdeteksi"

                else:
                    gesture_status = (
                        "Kamera gagal membaca gambar"
                    )

            except Exception as error:
                print(f"Kesalahan kamera: {error}")
                gesture_status = "Kamera bermasalah"

        if use_keyboard:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                basket_x -= BASKET_KEYBOARD_SPEED * dt

            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                basket_x += BASKET_KEYBOARD_SPEED * dt

            basket_x = max(
                0,
                min(
                    basket_x,
                    GAME_WIDTH - BASKET_WIDTH
                )
            )

            if not camera_active:
                gesture_status = "Mode keyboard"

        if countdown_active and countdown_start_ticks is not None:
            elapsed = (
                pygame.time.get_ticks() - countdown_start_ticks
            ) / 1000.0

            countdown_value = max(1, 3 - int(elapsed))

            if elapsed >= 3:
                countdown_active = False
                game_started = True
                start_ticks = pygame.time.get_ticks()
                time_left = GAME_DURATION

        if not game_over and game_started:
            seconds_passed = (
                pygame.time.get_ticks() - start_ticks
            ) // 1000

            time_left = max(
                0,
                GAME_DURATION - seconds_passed
            )

            next_spawn_time -= dt

            if next_spawn_time <= 0:
                if len(fruits) < MAX_FRUITS:
                    fruits.append(create_fruit())

                next_spawn_time = random.uniform(
                    SPAWN_INTERVAL_MIN,
                    SPAWN_INTERVAL_MAX
                )

            basket_rect = pygame.Rect(
                int(basket_x),
                BASKET_Y,
                BASKET_WIDTH,
                BASKET_HEIGHT
            )

            for fruit in fruits[:]:
                fruit["y"] += fruit["speed"] * dt

                fruit_rect = pygame.Rect(
                    int(fruit["x"]),
                    int(fruit["y"]),
                    FRUIT_SIZE[0],
                    FRUIT_SIZE[1]
                )

                if basket_rect.colliderect(fruit_rect):
                    score += 10
                    fruits.remove(fruit)

                elif fruit["y"] > GAME_HEIGHT:
                    lives -= 1
                    fruits.remove(fruit)

            if time_left <= 0 or lives <= 0:
                game_over = True

        draw_background()

        if not game_over:
            for fruit in fruits:
                screen.blit(
                    fruit_images[fruit["name"]],
                    (
                        int(fruit["x"]),
                        int(fruit["y"])
                    )
                )

            screen.blit(
                basket_image,
                (int(basket_x), BASKET_Y)
            )

        draw_hud()

        if game_over:
            draw_game_over()
        elif countdown_active:
            draw_countdown()
        elif not game_started:
            draw_centered(
                "Kalibrasikan warna target",
                font_medium,
                DARK_BLUE,
                GAME_WIDTH // 2,
                GAME_HEIGHT // 2
            )

        draw_camera_panel(
            camera_surface,
            mask_surface,
            gesture_status
        )

        pygame.display.flip()

finally:
    if tracker is not None:
        try:
            tracker.close()
        except Exception:
            pass

    if camera is not None:
        camera.release()

    pygame.quit()

sys.exit()