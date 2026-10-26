# Hand Catcher
### Implementasi Pengolahan Citra Video untuk Kontrol Game Menggunakan Deteksi Warna

## Deskripsi Proyek

Hand Catcher merupakan game 2D sederhana yang menggunakan webcam sebagai perangkat input untuk mengendalikan keranjang dalam permainan. Sistem memanfaatkan pengolahan citra video menggunakan OpenCV untuk mendeteksi warna target yang dipilih melalui proses kalibrasi.

Citra dari webcam diproses untuk memisahkan warna target dari latar belakang menggunakan segmentasi warna. Hasil segmentasi berupa mask digunakan untuk memperoleh posisi objek yang terdeteksi. Koordinat tersebut kemudian digunakan untuk menggerakkan keranjang ke kiri dan kanan guna menangkap buah yang jatuh.

Proyek ini dikembangkan untuk memenuhi tugas mata kuliah Pengolahan Citra Video.

## Tujuan

1. Mengimplementasikan akuisisi video menggunakan webcam.
2. Menerapkan deteksi dan segmentasi warna pada citra video.
3. Menggunakan proses kalibrasi untuk menentukan warna target.
4. Melacak posisi target berdasarkan hasil pengolahan citra.
5. Mengintegrasikan hasil pengolahan citra video sebagai input pengendali game.

## Fitur

- Kontrol keranjang menggunakan posisi warna target yang terdeteksi kamera.
- Kalibrasi warna melalui pemilihan titik pada tampilan kamera.
- Segmentasi warna untuk menghasilkan mask.
- Tampilan kamera dan hasil mask secara langsung.
- Kontrol keyboard sebagai alternatif ketika target tidak terdeteksi.
- Buah jatuh dengan posisi bervariasi.
- Collision detection untuk mendeteksi buah yang tertangkap.
- Sistem skor, nyawa, dan timer permainan.
- Countdown sebelum permainan dimulai.
- Tampilan hasil akhir permainan.

## Teknologi yang Digunakan

- **Python** — bahasa pemrograman utama.
- **OpenCV** — akuisisi kamera dan pengolahan citra.
- **NumPy** — operasi array citra.
- **Pygame** — pengelolaan game, tampilan, dan input keyboard.

## Metode Pengolahan Citra Video

### 1. Akuisisi Video

Webcam digunakan untuk mengambil video secara langsung. Setiap frame yang diperoleh menjadi masukan bagi proses pengolahan citra.

### 2. Kalibrasi Warna

Pengguna memilih titik pada tampilan kamera sebagai sampel warna target. Sampel tersebut digunakan sebagai acuan untuk menentukan rentang warna yang akan dideteksi.

### 3. Konversi dan Segmentasi Warna

Citra diproses menggunakan OpenCV. Jika implementasi menggunakan ruang warna HSV, citra BGR dikonversi ke HSV sebelum dilakukan segmentasi berdasarkan rentang warna target.

Segmentasi menghasilkan mask yang membedakan piksel sesuai warna target dari piksel lainnya.

### 4. Pelacakan Posisi Target

Posisi target diperoleh dari hasil deteksi pada citra. Koordinat tersebut digunakan sebagai acuan pergerakan keranjang pada area permainan.

### 5. Integrasi dengan Game

Program game menggunakan hasil pelacakan untuk memperbarui posisi keranjang. Game juga menangani pergerakan buah, collision detection, skor, nyawa, dan timer.

## Alur Kerja Sistem

1. Webcam mengambil frame video.
2. Frame diproses oleh modul pelacakan warna.
3. Pengguna melakukan kalibrasi dengan memilih warna target.
4. Sistem melakukan segmentasi warna dan menghasilkan mask.
5. Posisi target ditentukan dari hasil deteksi.
6. Koordinat target digunakan untuk menggerakkan keranjang.
7. Game memperbarui posisi buah dan memeriksa tabrakan.
8. Skor, nyawa, dan timer diperbarui selama permainan berlangsung.

## Struktur Proyek

```text
hand-catcher/
├── game.py
├── hand_tracking.py
├── test_webcam.py
├── requirements.txt
├── README.md
├── .gitignore
└── assets/
    ├── background.png
    ├── keranjang.png
    ├── manggis.png
    ├── mangga.png
    ├── apel.png
    ├── pir.png
    ├── jeruk.png
    └── anggur.png
```

## Instalasi

Pastikan Python telah terpasang di komputer.

Clone repositori:

```bash
git clone https://github.com/Shavna/hand-catcher.git
cd hand-catcher
```

Buat virtual environment:

```bash
python -m venv .venv
```

Aktifkan virtual environment di Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

Jika dependensi belum tercantum lengkap dalam `requirements.txt`, pastikan paket yang diperlukan oleh implementasi tersedia, yaitu OpenCV, NumPy, dan Pygame.

## Menjalankan Program

Untuk menjalankan game:

```bash
python game.py
```

Untuk menguji kamera dan pelacakan target:

```bash
python test_webcam.py
```

Pastikan webcam terhubung dan dapat diakses oleh program. Jika target tidak terdeteksi, kontrol keyboard dapat digunakan sebagai alternatif.

## Pengujian

Pengujian dilakukan untuk mengevaluasi kinerja pengolahan citra dan integrasinya dengan game.

Aspek yang dapat diuji meliputi:

1. **Akuisisi video:** memastikan webcam dapat menghasilkan frame.
2. **Kalibrasi warna:** memastikan warna yang dipilih dapat dijadikan target.
3. **Segmentasi mask:** mengamati kemampuan mask memisahkan target dari latar belakang.
4. **Pelacakan posisi:** mengamati respons koordinat terhadap pergerakan target.
5. **Pengaruh pencahayaan:** menguji kestabilan deteksi pada kondisi pencahayaan berbeda.
6. **Integrasi game:** memastikan keranjang merespons posisi target dan mekanisme permainan berjalan sesuai rancangan.

Hasil pengujian dicatat berdasarkan percobaan yang benar-benar dilakukan.

## Dokumentasi

Dokumentasi dapat dilengkapi dengan:

- Tampilan utama game.
- Tampilan webcam saat kalibrasi.
- Hasil segmentasi mask.
- Contoh perubahan posisi target dan respons keranjang.
- Tabel hasil pengujian pada kondisi pencahayaan berbeda.

## Pengembang

- **Nama:** Sintya Shavna Tamawulan
- **NRP:** 5024241047
- **Program Studi:** Teknik Komputer
- **Mata Kuliah:** Pengolahan Citra Video
- **Dosen Pengampu:** Artha Kusuma

## Status Proyek

Implementasi prototipe game dan pengolahan citra video. Pengujian dan evaluasi dilakukan untuk menilai kinerja deteksi warna serta pelacakan posisi target.
