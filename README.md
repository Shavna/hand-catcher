# Hand Catcher
### Implementasi Hand Tracking Berbasis Pengolahan Citra Video sebagai Pengendali Game

## Deskripsi Proyek

Hand Catcher merupakan game 2D sederhana yang menggunakan gerakan tangan sebagai pengendali permainan. Sistem memanfaatkan webcam untuk menangkap video tangan pemain, kemudian melakukan deteksi tangan untuk memperoleh koordinat posisi tangan secara real-time.

Koordinat tersebut digunakan untuk menggerakkan keranjang ke kiri dan kanan guna menangkap buah yang jatuh.

Proyek ini dikembangkan untuk memenuhi tugas mata kuliah Pengolahan Citra Video.

## Tujuan

1. Mengimplementasikan akuisisi video menggunakan webcam.
2. Menerapkan deteksi dan pelacakan posisi tangan.
3. Menggunakan hasil pengolahan video sebagai input pengendali game.
4. Mengembangkan game sederhana dengan sistem skor dan batas waktu.

## Fitur

- Kontrol keranjang menggunakan gerakan tangan.
- Deteksi tangan melalui webcam.
- Buah jatuh dengan posisi yang bervariasi.
- Sistem collision detection.
- Sistem skor.
- Timer permainan selama 30 detik.
- Tampilan skor akhir.

## Teknologi yang Digunakan

- Python
- OpenCV
- MediaPipe
- Pygame

## Cara Kerja Sistem

1. Webcam menangkap video pemain.
2. OpenCV membaca frame video.
3. MediaPipe mendeteksi tangan dan landmark-nya.
4. Koordinat tangan dipetakan ke posisi keranjang.
5. Game memperbarui posisi buah dan keranjang.
6. Collision detection menentukan apakah buah tertangkap.
7. Skor diperbarui hingga waktu permainan habis.

## Struktur Proyek

```text
hand-catcher/
├── main.py
├── hand_tracking.py
├── game.py
├── config.py
├── requirements.txt
├── README.md
├── .gitignore
├── assets/
│   ├── images/
│   └── sounds/
├── docs/
│   ├── flowchart.png
│   └── pengujian.md
└── screenshots/
    ├── gameplay.png
    └── hand_tracking.png
```

## Instalasi

Pastikan Python telah terpasang di komputer.

```bash
git clone https://github.com/USERNAME/hand-catcher.git
cd hand-catcher
python -m venv .venv
```

Aktifkan virtual environment di Windows:

```powershell
.venv\Scripts\Activate.ps1
```

Instal dependensi:

```bash
pip install -r requirements.txt
```

## Menjalankan Program

```bash
python main.py
```

Pastikan webcam terhubung dan izin akses kamera telah diberikan.

## Dokumentasi

Tambahkan screenshot gameplay, hasil deteksi tangan, dan flowchart sistem.

## Pengujian

Pengujian mencakup deteksi tangan, respons gerakan keranjang, collision detection, skor, timer, dan kondisi pencahayaan.

Hasil pengujian akan dicantumkan setelah implementasi selesai.

## Pengembang

- Nama: [Sintya Shavna Tamawulan]
- NRP: [5024241047]
- Program Studi: [Teknik Komputer]
- Mata Kuliah: Pengolahan Citra Video
- Dosen Pengampu: [Artha Kusuma]

## Status Proyek

Dalam tahap pengembangan.
