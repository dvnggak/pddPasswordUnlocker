import pikepdf
import multiprocessing as mp
from multiprocessing import Value, Lock
import time
import sys
import ctypes

def try_password(args):
    pdf_path, password, found_flag = args
    # Kalau proses lain udah nemu, langsung stop cek
    if found_flag.value:
        return None
    try:
        with pikepdf.open(pdf_path, password=password):
            found_flag.value = 1
            return password
    except pikepdf._core.PasswordError:
        return None
    except Exception:
        return None

def chunk_generator(start, end):
    """Generate password candidates sebagai string 6 digit dengan leading zero"""
    for i in range(start, end):
        yield f"{i:06d}"

def worker(args):
    pdf_path, pw_range, found_flag = args
    start, end = pw_range
    for i in range(start, end):
        if found_flag.value:
            return None
        pw = f"{i:06d}"
        try:
            with pikepdf.open(pdf_path, password=pw):
                found_flag.value = 1
                return pw
        except pikepdf._core.PasswordError:
            continue
        except Exception:
            continue
    return None

def brute_force_pdf(pdf_path, num_workers=None):
    if num_workers is None:
        num_workers = mp.cpu_count()

    print(f"[*] Target file : {pdf_path}")
    print(f"[*] Total kombinasi: 1,000,000 (000000-999999)")
    print(f"[*] Jumlah worker  : {num_workers}")
    print(f"[*] Mulai brute force...\n")

    total = 1_000_000
    chunk_size = total // num_workers
    ranges = []
    for i in range(num_workers):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < num_workers - 1 else total
        ranges.append((start, end))

    manager = mp.Manager()
    found_flag = manager.Value(ctypes.c_int, 0)

    start_time = time.time()

    tasks = [(pdf_path, r, found_flag) for r in ranges]

    result = None
    with mp.Pool(processes=num_workers) as pool:
        for res in pool.imap_unordered(worker, tasks):
            if res is not None:
                result = res
                pool.terminate()
                break

    elapsed = time.time() - start_time

    if result:
        print(f"\n[+] PASSWORD DITEMUKAN: {result}")
        print(f"[+] Waktu proses: {elapsed:.2f} detik")
        return result
    else:
        print(f"\n[-] Password tidak ditemukan dalam 000000-999999")
        print(f"[-] Waktu proses: {elapsed:.2f} detik")
        return None

if __name__ == "__main__":
    PDF_PATH = r"D:\dev\decriptPDF-bruteForce\Devangga Kertawijaya.pdf"

    if len(sys.argv) > 1:
        PDF_PATH = sys.argv[1]

    password = brute_force_pdf(PDF_PATH)

    if password:
        print(f"\n=== HASIL ===")
        print(f"Password PDF: {password}")
    else:
        print(f"\n=== GAGAL ===")
        print(f"Coba cek lagi apakah password memang 6 digit angka.")