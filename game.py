import pygame
import random
import sys

# Inisialisasi Pygame
pygame.init()

# ==========================================
# KONFIGURASI LAYAR & WARNA (Langkah 3.2)
# ==========================================
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game Tangkap Buah")

# Definisi Warna (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED   = (230, 57, 70)
BLUE  = (69, 123, 157)
BROWN = (107, 68, 35)

# Clock untuk mengatur Frame Rate
clock = pygame.time.Clock()
FPS = 60

# Fonts untuk Teks
font_large = pygame.font.SysFont("Arial", 48, bold=True)
font_medium = pygame.font.SysFont("Arial", 28)

# ==========================================
# OBJEK KERANJANG (Langkah 3.3)
# ==========================================
basket_width = 100
basket_height = 20
basket_x = (SCREEN_WIDTH - basket_width) // 2
basket_y = SCREEN_HEIGHT - 40
basket_speed = 8

# ==========================================
# OBJEK BUAH (Langkah 3.4)
# ==========================================
fruit_radius = 15
fruit_x = random.randint(fruit_radius, SCREEN_WIDTH - fruit_radius)
fruit_y = 0
fruit_speed = 6

# Fungsi untuk mereset posisi buah ke atas
def reset_fruit():
    global fruit_x, fruit_y
    fruit_x = random.randint(fruit_radius, SCREEN_WIDTH - fruit_radius)
    fruit_y = 0

# ==========================================
# SKOR DAN TIMER (Langkah 3.5 & 3.6)
# ==========================================
score = 0
GAME_DURATION = 30  # Durasi permainan dalam detik
start_ticks = pygame.time.get_ticks()  # Catat waktu mulai

game_over = False

# ==========================================
# MAIN GAME LOOP
# ==========================================
running = True
while running:
    # 1. Handling Events (Tutup Jendela)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # ----------------------------------
        # KONTROL KEYBOARD (Langkah 3.3)
        # ----------------------------------
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and basket_x > 0:
            basket_x -= basket_speed
        if keys[pygame.K_RIGHT] and basket_x < SCREEN_WIDTH - basket_width:
            basket_x += basket_speed

        # ----------------------------------
        # PERGERAKAN BUAH (Langkah 3.4)
        # ----------------------------------
        fruit_y += fruit_speed

        # Jika buah jatuh melewati batas bawah layar, munculkan lagi dari atas
        if fruit_y > SCREEN_HEIGHT + fruit_radius:
            reset_fruit()

        # ----------------------------------
        # COLLISION DETECTION (Langkah 3.5)
        # ----------------------------------
        # Keranjang sebagai Rectangle
        basket_rect = pygame.Rect(basket_x, basket_y, basket_width, basket_height)
        # Buah (Bounding Box Lingkaran)
        fruit_rect = pygame.Rect(
            fruit_x - fruit_radius,
            fruit_y - fruit_radius,
            fruit_radius * 2,
            fruit_radius * 2
        )

        # Cek Tabrakan
        if basket_rect.colliderect(fruit_rect):
            score += 10
            reset_fruit()

        # ----------------------------------
        # HITUNG TIMER (Langkah 3.6)
        # ----------------------------------
        seconds_passed = (pygame.time.get_ticks() - start_ticks) // 1000
        time_left = max(0, GAME_DURATION - seconds_passed)

        if time_left <= 0:
            game_over = True

    # --------------------------------------
    # RENDERING / MENGGAMBAR KE LAYAR
    # --------------------------------------
    screen.fill(WHITE)

    if not game_over:
        # Gambar Keranjang (Persegi Panjang)
        pygame.draw.rect(screen, BROWN, (basket_x, basket_y, basket_width, basket_height))

        # Gambar Buah (Lingkaran)
        pygame.draw.circle(screen, RED, (fruit_x, fruit_y), fruit_radius)

        # Tampilkan Skor
        score_surface = font_medium.render(f"Skor: {score}", True, BLACK)
        screen.blit(score_surface, (20, 20))

        # Tampilkan Timer
        timer_surface = font_medium.render(f"Waktu: {time_left}s", True, BLACK)
        screen.blit(timer_surface, (SCREEN_WIDTH - 150, 20))

    else:
        # Tampilan Game Over / Hasil Akhir
        over_text = font_large.render("WAKTU HABIS!", True, RED)
        final_score_text = font_medium.render(f"Skor Akhir Anda: {score}", True, BLACK)
        
        # Posisikan teks di tengah layar
        over_rect = over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        
        screen.blit(over_text, over_rect)
        screen.blit(final_score_text, score_rect)

    # Perbarui Tampilan Layar
    pygame.display.flip()
    
    # Batasi Frame Rate
    clock.tick(FPS)

# Keluar dari Pygame
pygame.quit()
sys.exit()