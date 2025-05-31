import os
import sys
import time
import random
import requests
from colorama import Fore, init
from dotenv import load_dotenv

# Inisialisasi Colorama untuk pewarnaan konsol
init(autoreset=True)

def load_env_vars():
    """
    Muat variabel dari .env:
      - CHANNEL_IDS  (misal: "ID1,ID2,ID3")
      - WAKTU_HAPUS   (angka, dalam detik)
      - TOKEN         (user token Discord)
    Jika ada yang kosong atau invalid, skrip akan exit.
    """
    load_dotenv()  # Search dan load file .env di current working directory

    raw_channel_ids = os.getenv("CHANNEL_IDS", "").strip()
    waktu_hapus_str = os.getenv("WAKTU_HAPUS", "").strip()
    token = os.getenv("TOKEN", "").strip()

    if not raw_channel_ids:
        print(Fore.RED + "ERROR: Variabel CHANNEL_IDS di .env belum diisi.")
        sys.exit(1)

    # Split channel IDs berdasarkan koma, lalu strip whitespace
    channel_ids = [cid.strip() for cid in raw_channel_ids.split(",") if cid.strip()]
    if not channel_ids:
        print(Fore.RED + "ERROR: Format CHANNEL_IDS di .env tidak valid. Contoh: CHANNEL_IDS=123,456,789")
        sys.exit(1)

    if not waktu_hapus_str:
        print(Fore.RED + "ERROR: Variabel WAKTU_HAPUS di .env belum diisi.")
        sys.exit(1)
    try:
        waktu_hapus = int(waktu_hapus_str)
    except ValueError:
        print(Fore.RED + "ERROR: WAKTU_HAPUS harus berupa angka (integer).")
        sys.exit(1)

    if not token:
        print(Fore.RED + "ERROR: Variabel TOKEN di .env belum diisi.")
        sys.exit(1)

    return channel_ids, waktu_hapus, token

def load_file_lines(path):
    """
    Baca semua baris non-kosong dari file, hapus newline/spasi tepi.
    Jika file tidak ditemukan atau kosong, exit.
    """
    if not os.path.isfile(path):
        print(Fore.RED + f"ERROR: File '{path}' tidak ditemukan. Buat file 'pesan.txt' dulu.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        print(Fore.RED + f"ERROR: File '{path}' kosong atau hanya mengandung whitespace.")
        sys.exit(1)

    return lines

def send_message(token, channel_id, content):
    """
    Kirim satu pesan teks ke channel_id menggunakan user token.
    Jika terkena rate limit (HTTP 429), tunggu retry_after lalu retry.
    Return tuple (status_code, json_response_dict_or_empty_dict).
    """
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    payload = {"content": content}

    r = requests.post(url, headers=headers, json=payload)
    if r.status_code == 429:
        retry_after = r.json().get("retry_after", 1)
        print(Fore.MAGENTA + f"[RATE LIMIT SEND][{channel_id}] Tunggu {retry_after:.2f} detik sebelum retry.")
        time.sleep(retry_after)
        return send_message(token, channel_id, content)

    return r.status_code, (r.json() if "application/json" in r.headers.get("Content-Type", "") else {})

def get_last_message_id(token, channel_id):
    """
    Ambil ID pesan terbaru (limit=1) di channel tersebut.
    Jika rate limit, tunggu retry_after lalu retry.
    Return: message_id (string) atau None kalau gagal/empty.
    """
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
    headers = {"Authorization": token}

    r = requests.get(url, headers=headers)
    if r.status_code == 429:
        retry_after = r.json().get("retry_after", 1)
        print(Fore.MAGENTA + f"[RATE LIMIT GET][{channel_id}] Tunggu {retry_after:.2f} detik sebelum retry.")
        time.sleep(retry_after)
        return get_last_message_id(token, channel_id)

    if r.status_code != 200:
        print(Fore.RED + f"[{channel_id}] Gagal GET pesan terbaru (status {r.status_code}): {r.text}")
        return None

    msgs = r.json()
    if not msgs:
        return None
    return msgs[0].get("id")

def delete_message(token, channel_id, message_id):
    """
    Hapus pesan dengan message_id di channel tertentu.
    Jika rate limit, tunggu retry_after lalu retry.
    Return: status_code (204 jika berhasil).
    """
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}"
    headers = {"Authorization": token}

    r = requests.delete(url, headers=headers)
    if r.status_code == 429:
        retry_after = r.json().get("retry_after", 1)
        print(Fore.MAGENTA + f"[RATE LIMIT DELETE][{channel_id}] Tunggu {retry_after:.2f} detik sebelum retry.")
        time.sleep(retry_after)
        return delete_message(token, channel_id, message_id)

    return r.status_code

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    # ------------------ Load .env Vars ------------------
    channel_ids, waktu_hapus, token = load_env_vars()

    # ------------------ Tampilkan Banner ------------------
    print("   ____          ____       _                    ")
    print("  | __ )  __ _  |  _ \\ __ _| |_ ___ _ __   __ _  ")
    print("  |  _ \\ / _' | | |_) / _' | __/ _ \\ '_ \\ / _' | ")
    print("  | |_) | (_| | |  __/ (_| | ||  __/ | | | (_| | ")
    print("  |____/ \\__, | |_|   \\__,_|\\__\\___|_| |_|\\__, | ")
    print("         |___/                            |___/  \n")
    print("=================================================")
    author = "Bg.Pateng"
    print("Author : " + author)
    script_name = "Push Rank Discord (User Token Multi-Channel)"
    print("Script : " + script_name)
    telegram = "@bangpateng_group"
    print("Telegram: " + telegram)
    youtube = "Bang Pateng"
    print("YouTube : " + youtube)
    print("===========================================")
    print("PERINGATAN : TIDAK UNTUK DI PERJUAL-BELIKAN")
    print("===========================================\n")

    # Informasi jalannya skrip
    print(Fore.CYAN + f"[INFO] CHANNEL_IDS = {', '.join(channel_ids)}")
    print(Fore.CYAN + f"[INFO] WAKTU_HAPUS  = {waktu_hapus} detik")
    print(Fore.CYAN + "[INFO] Menggunakan User Token (dibaca dari .env).")
    print(Fore.CYAN + "[INFO] Setiap pengiriman, tunggu random 1–3 menit per channel.\n")

    # Countdown 3-2-1, lalu clear screen
    print("Mulai dalam:")
    for i in ("3", "2", "1"):
        print(i)
        time.sleep(1)
    clear_console()

    # ------------------ Load konten pesan ------------------
    words = load_file_lines("pesan.txt")
    print(Fore.CYAN + f"[INFO] Ditemukan {len(words)} baris di 'pesan.txt'.\n")

    iterasi = 0
    try:
        # Loop tak terbatas
        while True:
            for channel_id in channel_ids:
                iterasi += 1

                # --- Delay random 1–3 menit sebelum kirim setiap channel ---
                delay_send = random.randint(60, 180)  # detik
                menit_ke = delay_send // 60
                sisa_detik = delay_send % 60
                print(Fore.BLUE + f"[{iterasi}][Channel {channel_id}] Menunggu {menit_ke} menit {sisa_detik} detik sebelum kirim pesan.")
                time.sleep(delay_send)

                # --- Kirim pesan acak ke channel yang sedang diproses ---
                content = random.choice(words)
                status_send, resp_send = send_message(token, channel_id, content)
                if status_send in (200, 201):
                    print(Fore.WHITE + f"[{iterasi}][Channel {channel_id}] Sent message: {Fore.YELLOW}{content}")
                else:
                    print(Fore.RED + f"[{iterasi}][Channel {channel_id}] Gagal mengirim pesan (status {status_send}): {resp_send}")
                    # Jika bukan rate-limit, tunggu sedikit sebelum lanjut ke channel selanjutnya
                    fail_delay = random.randint(10, 20)
                    print(Fore.BLUE + f"[{iterasi}][Channel {channel_id}] Tunggu {fail_delay} detik sebelum lanjut ke channel berikutnya.\n")
                    time.sleep(fail_delay)
                    continue

                # --- Delay sebelum hapus: WAKTU_HAPUS + jitter 0.5–1.5 detik ---
                total_delay_hapus = waktu_hapus + random.uniform(0.5, 1.5)
                print(Fore.BLUE + f"[{iterasi}][Channel {channel_id}] Menunggu {total_delay_hapus:.2f} detik sebelum menghapus pesan.")
                time.sleep(total_delay_hapus)

                # --- Ambil ID pesan terakhir dan hapus ---
                last_id = get_last_message_id(token, channel_id)
                if not last_id:
                    print(Fore.RED + f"[{iterasi}][Channel {channel_id}] Tidak ada pesan untuk dihapus (channel kosong atau GET gagal).\n")
                else:
                    status_del = delete_message(token, channel_id, last_id)
                    if status_del == 204:
                        print(Fore.GREEN + f"[{iterasi}][Channel {channel_id}] Pesan dengan ID {last_id} berhasil dihapus\n")
                    else:
                        print(Fore.RED + f"[{iterasi}][Channel {channel_id}] Gagal menghapus pesan ID {last_id} (status {status_del})\n")

                # Setelah menyelesaikan satu channel, langsung lanjut ke channel berikutnya
                # (tidak ada delay tambahan karena delay pengiriman di awal setiap channel)

            # Setelah semua channel selesai, otomatis ulangi lagi dari channel pertama
            # Tanpa jeda ekstra di antara loop—karena setiap channel sudah di-handle dengan delay masing-masing.

    except KeyboardInterrupt:
        print(Fore.MAGENTA + "\n[SISTEM] Deteksi KeyboardInterrupt. Skrip dihentikan oleh user. Sampai jumpa!")
        sys.exit(0)

if __name__ == "__main__":
    main()
