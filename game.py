import pygame
import random
import sys
import cv2

from hand_tracking import Camera, HandTracker

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Fruity Catch")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (230, 57, 70)
BLUE = (69, 123, 157)
BROWN = (107, 68, 35)
GREEN = (100, 180, 100)
LIGHT_BLUE = (220, 240, 255)
ORANGE = (240, 160, 50)

clock = pygame.time.Clock()
FPS = 60

font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 28)
font_small = pygame.font.SysFont("Arial", 18)

basket_width = 100
basket_height = 20
basket_y = SCREEN_HEIGHT - 50
basket_speed = 8

fruit_radius = 15
fruit_speed = 6

GAME_DURATION = 30

camera = None
tracker = None
camera_active = False

try:
    camera = Camera(index=0).open()
    tracker = HandTracker()
    camera_active = True
    print("Kamera berhasil dibuka.")
except Exception as error:
    print(f"Kamera tidak tersedia: {error}")
    print("Game akan menggunakan keyboard.")

    if camera is not None:
        camera.release()
        camera = None

    if tracker is not None:
        tracker.close()
        tracker = None

def reset_fruit():
    global fruit_x, fruit_y

    fruit_x = random.randint(
        fruit_radius,
        SCREEN_WIDTH - fruit_radius
    )
    fruit_y = -fruit_radius


def reset_game():
    global basket_x, score, start_ticks
    global game_over, time_left, catch_enabled

    basket_x = (SCREEN_WIDTH - basket_width) // 2
    score = 0
    start_ticks = pygame.time.get_ticks()
    time_left = GAME_DURATION
    game_over = False
    catch_enabled = True

    reset_fruit()


def draw_text(text, font, color, x, y):
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

reset_game()

running = True
gesture_status = "Mode keyboard"

try:
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_r:
                    reset_game()

        keys = pygame.key.get_pressed()

        hand_detected = False
        use_keyboard = True

        if camera_active and camera is not None and tracker is not None:
            try:
                ok, frame = camera.read()

                if ok:
                    frame = tracker.process(frame, draw=True)

                    if tracker.has_hand():
                        landmarks = tracker.get_landmarks(frame.shape)

                        if landmarks:
                            hand_detected = True
                            use_keyboard = False

                            if tracker.is_open_hand(landmarks):
                                points = {
                                    i: (x, y)
                                    for i, x, y in landmarks
                                }

                                wrist_x = points[0][0]

                                basket_x = int(
                                    (wrist_x / frame.shape[1])
                                    * SCREEN_WIDTH
                                    - basket_width / 2
                                )

                                basket_x = max(
                                    0,
                                    min(
                                        basket_x,
                                        SCREEN_WIDTH - basket_width
                                    )
                                )

                                gesture_status = "Telapak - kontrol tangan"
                                catch_enabled = False

                            elif tracker.is_fist(landmarks):

                                gesture_status = "Kepalan - menangkap"
                                catch_enabled = True

                            else:
                                gesture_status = "Gesture tidak dikenali"
                                catch_enabled = False

                    else:
                        gesture_status = "Tangan tidak terdeteksi"

                    cv2.imshow("Fruity Catch - Webcam", frame)

                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        cv2.destroyWindow("Fruity Catch - Webcam")

                else:
                    gesture_status = "Kamera gagal membaca gambar"

            except Exception as error:
                print(f"Kesalahan kamera: {error}")
                gesture_status = "Kamera bermasalah"
                use_keyboard = True

        if use_keyboard:
            gesture_status = "Mode keyboard"
            catch_enabled = True

            if keys[pygame.K_LEFT]:
                basket_x -= basket_speed

            if keys[pygame.K_RIGHT]:
                basket_x += basket_speed

            basket_x = max(
                0,
                min(basket_x, SCREEN_WIDTH - basket_width)
            )

        if not game_over:
            fruit_y += fruit_speed

            basket_rect = pygame.Rect(
                basket_x,
                basket_y,
                basket_width,
                basket_height
            )

            fruit_rect = pygame.Rect(
                fruit_x - fruit_radius,
                fruit_y - fruit_radius,
                fruit_radius * 2,
                fruit_radius * 2
            )

            if catch_enabled and basket_rect.colliderect(fruit_rect):
                score += 10
                reset_fruit()

            elif fruit_y - fruit_radius > SCREEN_HEIGHT:
                reset_fruit()

            seconds_passed = (
                pygame.time.get_ticks() - start_ticks
            ) // 1000

            time_left = max(
                0,
                GAME_DURATION - seconds_passed
            )

            if time_left <= 0:
                game_over = True

        screen.fill(LIGHT_BLUE)

        pygame.draw.rect(
            screen,
            GREEN,
            (0, SCREEN_HEIGHT - 20, SCREEN_WIDTH, 20)
        )

        if not game_over:

            pygame.draw.rect(
                screen,
                BROWN,
                (basket_x, basket_y, basket_width, basket_height),
                border_radius=6
            )

            pygame.draw.circle(
                screen,
                RED,
                (fruit_x, int(fruit_y)),
                fruit_radius
            )

            draw_text(
                f"Skor: {score}",
                font_medium,
                BLACK,
                20,
                20
            )

            draw_text(
                f"Waktu: {time_left}s",
                font_medium,
                BLACK,
                SCREEN_WIDTH - 170,
                20
            )

            draw_text(
                f"Kontrol: {gesture_status}",
                font_small,
                BLUE,
                20,
                60
            )

            if use_keyboard:
                draw_text(
                    "Panah kiri/kanan: gerak",
                    font_small,
                    BLACK,
                    20,
                    85
                )
            else:
                draw_text(
                    "Telapak: gerak | Kepalan: tangkap",
                    font_small,
                    BLACK,
                    20,
                    85
                )

        else:

            over_text = font_large.render(
                "WAKTU HABIS!",
                True,
                RED
            )

            final_score_text = font_medium.render(
                f"Skor Akhir Anda: {score}",
                True,
                BLACK
            )

            restart_text = font_small.render(
                "Tekan R untuk bermain lagi",
                True,
                BLUE
            )

            screen.blit(
                over_text,
                over_text.get_rect(
                    center=(
                        SCREEN_WIDTH // 2,
                        SCREEN_HEIGHT // 2 - 60
                    )
                )
            )

            screen.blit(
                final_score_text,
                final_score_text.get_rect(
                    center=(
                        SCREEN_WIDTH // 2,
                        SCREEN_HEIGHT // 2
                    )
                )
            )

            screen.blit(
                restart_text,
                restart_text.get_rect(
                    center=(
                        SCREEN_WIDTH // 2,
                        SCREEN_HEIGHT // 2 + 50
                    )
                )
            )

        pygame.display.flip()
        clock.tick(FPS)

finally:
    if tracker is not None:
        tracker.close()

    if camera is not None:
        camera.release()

    cv2.destroyAllWindows()
    pygame.quit()

sys.exit()
