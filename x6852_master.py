import os, sys, time, zipfile, threading, re, shutil

# ── Colors ─────────────────────────────────────────────────────────────────────
RST  = '\033[0m';  BOLD = '\033[1m'
RED  = '\033[1;31m'; GRN  = '\033[1;32m'; YLW  = '\033[1;33m'
CYN  = '\033[1;36m'; WHT  = '\033[1;37m'
DGRN = '\033[0;32m'; DCYN = '\033[0;36m'; DWHT = '\033[0;37m'

# ── INFINIX logo — 7 letters, 47 cols ─────────────────────────────────────────
LOGO = [
    r"  ██╗███╗   ██╗███████╗██╗███╗   ██╗██╗██╗  ██╗",
    r"  ██║████╗  ██║██╔════╝██║████╗  ██║██║╚██╗██╔╝",
    r"  ██║██╔██╗ ██║█████╗  ██║██╔██╗ ██║██║ ╚███╔╝ ",
    r"  ██║██║╚██╗██║██╔══╝  ██║██║╚██╗██║██║ ██╔██╗ ",
    r"  ██║██║ ╚████║██║     ██║██║ ╚████║██║██╔╝ ██╗",
    r"  ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝",
]

# ── Helpers ────────────────────────────────────────────────────────────────────
def clr():   os.system("clear")
def fb(cmd): os.system(f"fastboot {cmd}")
def w(t=.6): time.sleep(t)
def strip(s): return re.sub(r'\033\[[0-9;]*m', '', s)

def cols():
    return shutil.get_terminal_size((52, 24)).columns

def W():
    """Box content width — adapts to terminal, capped 40–60."""
    return max(40, min(cols() - 4, 60))

# ── Box drawing ────────────────────────────────────────────────────────────────
def _top():   print(f"{CYN}╔{'═' * W()}╗{RST}")
def _bot():   print(f"{CYN}╚{'═' * W()}╝{RST}")
def _div():   print(f"{CYN}╠{'═' * W()}╣{RST}")
def _sdiv():  print(f"{CYN}╟{'─' * W()}╢{RST}")
def _empty(): print(f"{CYN}║{' ' * W()}║{RST}")

def _cbox(text, color=""):
    clean = strip(text)
    pad   = max(0, W() - len(clean))
    l, r  = pad // 2, pad - pad // 2
    print(f"{CYN}║{' ' * l}{color}{text}{RST}{' ' * r}{CYN}║{RST}")

def _row(text, color=DWHT):
    clean = strip(text)
    pad   = W() - len(clean) - 2
    print(f"{CYN}║{RST} {color}{text}{RST}{' ' * max(0, pad)} {CYN}║{RST}")

def _kv(label, value, lc=DWHT, vc=YLW):
    pad = W() - len(label) - len(value) - 4
    print(f"{CYN}║{RST}  {lc}{label}{RST}  {vc}{value}{RST}"
          f"{' ' * max(0, pad)}{CYN}║{RST}")

# ── Header ─────────────────────────────────────────────────────────────────────
def print_header(subtitle="MAIN MENU"):
    clr()
    c = cols()

    # Logo — printed above the box, centered to terminal width
    for line in LOGO:
        pad = max(0, (c - len(line)) // 2)
        print(f"{' ' * pad}{CYN}{line}{RST}")

    # Sub-title line beneath logo
    sub = "NOTE 40 5G  ·  X6852  ·  FLASH TOOL"
    pad = max(0, (c - len(sub)) // 2)
    print(f"\n{' ' * pad}{BOLD}{DWHT}{sub}{RST}\n")

    # Info box
    _top()
    _cbox(subtitle, f"{BOLD}{YLW}")
    _sdiv()
    _empty()
    _kv("Developer :", "@shelby",                    lc=DWHT, vc=f"{BOLD}{GRN}")
    _kv("Device    :", "Infinix Note 40 5G (X6852)", lc=DWHT, vc=CYN)
    _kv("Platform  :", "MediaTek  |  Android",       lc=DWHT, vc=DCYN)
    _empty()
    _bot()
    print()

# ── Spinner ────────────────────────────────────────────────────────────────────
class Spinner:
    def __init__(self, msg="Processing..."):
        self.msg     = msg
        self.running = False
        self.thread  = None

    def _task(self):
        frames = ['⣾','⣽','⣻','⢿','⡿','⣟','⣯','⣷']
        i = 0
        while self.running:
            sys.stdout.write(f"\r  {YLW}{frames[i]}{RST}  {DWHT}{self.msg}{RST}  ")
            sys.stdout.flush()
            time.sleep(0.08)
            i = (i + 1) % len(frames)

    def start(self):
        self.running = True
        self.thread  = threading.Thread(target=self._task, daemon=True)
        self.thread.start()

    def stop(self, ok=True):
        self.running = False
        if self.thread: self.thread.join()
        sys.stdout.write("\r\033[K"); sys.stdout.flush()
        icon = f"{GRN}✔{RST}" if ok else f"{RED}✘{RST}"
        print(f"  {icon}  {DWHT}{self.msg}{RST}")

# ── Logging shortcuts ──────────────────────────────────────────────────────────
def info(m):        print(f"\n  {CYN}[·]{RST}  {DWHT}{m}{RST}")
def ok(m):          print(f"  {GRN}[✔]{RST}  {DGRN}{m}{RST}")
def warn(m):        print(f"  {YLW}[!]{RST}  {YLW}{m}{RST}")
def err(m):         print(f"  {RED}[✘]{RST}  {RED}{m}{RST}")
def step(n, t, m):  print(f"\n  {CYN}[{n}/{t}]{RST}  {WHT}{m}{RST}")
def prompt(m):      return input(f"\n  {YLW}▶{RST}  {DWHT}{m}{RST}  ").strip()
def press_enter():  input(f"\n  {DCYN}Press {YLW}Enter{RST}{DCYN} to continue...{RST}")

def confirm(m):
    return prompt(f"{m}  [{GRN}y{DWHT}/{RED}n{DWHT}]:").lower() == 'y'

# ── Flashing engine ────────────────────────────────────────────────────────────
SLOT_ALL = [
    'dtbo','gz','lk','logo','md1img','pi_img',
    'scp','spmfw','sspm','tee','vbmeta',
    'vbmeta_system','vbmeta_vendor','mcupm','dpm',
]

def scan_firmware(target_dir):
    img_map = {}
    for root, _, files in os.walk(target_dir):
        for f in files:
            lf = f.lower()
            if lf.endswith(('.img', '.bin')):
                img_map[os.path.splitext(lf)[0]] = os.path.join(root, f)
                img_map[lf]                       = os.path.join(root, f)
    return img_map

def flash_part(part, path, slot=True):
    flag = "--slot=all " if slot else ""
    sys.stdout.write(f"    {DWHT}» {CYN}{part:<20}{RST}  ")
    sys.stdout.flush()
    ret = os.system(f"fastboot {flag}flash {part} '{path}' > /dev/null 2>&1")
    print(f"  {GRN}✔  done{RST}" if ret == 0 else f"  {RED}✘  failed{RST}")

def start_flashing_process(target_dir):
    print_header("FLASHING FIRMWARE")

    sp = Spinner("Scanning firmware directory...")
    sp.start()
    img_map = scan_firmware(target_dir)
    sp.stop(ok=True)

    found = len([k for k in img_map if not k.endswith(('.img','.bin'))])
    ok(f"Found {found} partition image(s)")
    print()

    if not confirm("Authorize flashing?  All data will be wiped"):
        warn("Flashing cancelled."); press_enter(); return

    step(1, 4, "Setting active slot → a")
    fb("set_active a")

    step(2, 4, "Flashing boot partitions")
    for p in ['boot', 'vendor_boot']:
        if p in img_map: flash_part(p, img_map[p])

    step(3, 4, "Flashing super partition  (may take a few minutes)")
    if 'super' in img_map:
        sp2 = Spinner("Writing super.img …")
        sp2.start()
        os.system(f"fastboot flash super '{img_map['super']}' > /dev/null 2>&1")
        sp2.stop(ok=True)
    else:
        warn("super.img not found — skipping")

    step(4, 4, "Flashing remaining partitions")
    preloader = next((img_map[k] for k in img_map if 'preloader' in k), None)
    if preloader: flash_part('preloader', preloader)
    for p in SLOT_ALL:
        if p in img_map: flash_part(p, img_map[p])
    if 'userdata' in img_map:
        flash_part('userdata', img_map['userdata'], slot=False)

    info("Erasing userdata and cache...")
    fb("erase userdata")
    ok("Userdata erased")

    # Done banner
    print()
    _top()
    _cbox("🎉  FLASH COMPLETED SUCCESSFULLY  🎉", f"{BOLD}{GRN}")
    _sdiv()
    _kv("Developer :", "@shelby",                    lc=DWHT, vc=f"{BOLD}{GRN}")
    _kv("Device    :", "Infinix Note 40 5G (X6852)", lc=DWHT, vc=CYN)
    _bot()

    info("Rebooting device...")
    w(1); fb("reboot"); press_enter()

# ── ROM scanner ────────────────────────────────────────────────────────────────
KEYWORDS = ['infinix', 'x6852', 'note40', 'note 40', 'xos', 'stock']

def flash_stock_rom_combined():
    print_header("FLASH STOCK ROM")

    sp = Spinner("Scanning internal storage...")
    sp.start()

    zips = []
    for root, _, files in os.walk("/sdcard/"):
        if any(x in root for x in ["Android", ".cache"]): continue
        for f in files:
            lf = f.lower()
            if lf.endswith(".zip") and any(k in lf for k in KEYWORDS):
                zips.append(os.path.join(root, f))

    folders = {}
    for root, _, files in os.walk("/sdcard/"):
        if any(x in root for x in ["Android", ".cache", "DCIM", "Pictures"]): continue
        cnt = sum(1 for f in files if f.lower().endswith(('.img','.bin')))
        if cnt: folders[root] = cnt

    sp.stop(ok=True)

    item_map = {}
    idx = 1

    print(f"\n  {BOLD}{CYN}── FIRMWARE ZIP FILES {'─'*26}{RST}")
    if zips:
        for z in zips:
            print(f"  {YLW}[{idx:2d}]{RST}  {WHT}{os.path.basename(z)}{RST}")
            item_map[idx] = ('zip', z); idx += 1
    else:
        warn("No matching ZIP files found on /sdcard/")

    print(f"\n  {BOLD}{CYN}── EXTRACTED FOLDERS {'─'*27}{RST}")
    if folders:
        for fpath, cnt in folders.items():
            print(f"  {YLW}[{idx:2d}]{RST}  {WHT}{os.path.basename(fpath)}{RST}"
                  f"  {DGRN}({cnt} images){RST}")
            item_map[idx] = ('folder', fpath); idx += 1
    else:
        warn("No extracted firmware folders found")

    if not item_map:
        err("Nothing to flash. Copy firmware to /sdcard/ first.")
        press_enter(); return

    print()
    try:
        sel = int(prompt(f"Select entry to flash  [1–{idx-1}]:"))
    except ValueError:
        err("Invalid input."); press_enter(); return

    if sel not in item_map:
        err("Selection out of range."); press_enter(); return

    itype, ipath = item_map[sel]

    if itype == 'zip':
        out_path = "/sdcard/INFINIX_X6852"
        os.makedirs(out_path, exist_ok=True)
        sp3 = Spinner("Extracting firmware package...")
        sp3.start()
        try:
            with zipfile.ZipFile(ipath, 'r') as z:
                z.extractall(out_path)
            sp3.stop(ok=True)
            sub = os.listdir(out_path); actual = out_path
            if len(sub) == 1:
                maybe = os.path.join(out_path, sub[0])
                if os.path.isdir(maybe):
                    if any(f.lower().endswith(('.img','.bin'))
                           for r,_,fs in os.walk(maybe) for f in fs):
                        actual = maybe
            w(0.4); start_flashing_process(actual)
        except Exception as e:
            sp3.stop(ok=False)
            err(f"Extraction failed: {e}"); press_enter()
    else:
        start_flashing_process(ipath)

# ── Device check ───────────────────────────────────────────────────────────────
def device_check_menu():
    print_header("FASTBOOT DEVICE CHECK")
    info("Querying connected fastboot devices...")
    print(f"\n  {CYN}{'─' * (W()-2)}{RST}")
    fb("devices")
    print(f"  {CYN}{'─' * (W()-2)}{RST}")
    press_enter()

# ── Reboot menu ────────────────────────────────────────────────────────────────
REBOOT_OPTS = {
    '1': ("System",       "reboot"),
    '2': ("Fastboot",     "reboot-bootloader"),
    '3': ("Recovery",     "reboot recovery"),
    '4': ("EDL / BROM",   "reboot edl"),
}

def reboot_menu():
    while True:
        print_header("REBOOT OPTIONS")
        for k, (label, _) in REBOOT_OPTS.items():
            print(f"  {CYN}[{k}]{RST}  Reboot to {WHT}{label}{RST}")
        print(f"  {CYN}[5]{RST}  {DWHT}Back{RST}\n")
        ch = prompt("Select option:")
        if ch in REBOOT_OPTS:
            _, cmd = REBOOT_OPTS[ch]
            info(f"Rebooting to {REBOOT_OPTS[ch][0]}...")
            fb(cmd); break
        elif ch == '5':
            break
        else:
            warn("Invalid option."); w(0.4)

# ── Bootloader unlock ──────────────────────────────────────────────────────────
def unlock_bootloader():
    print_header("UNLOCK BOOTLOADER")
    _top()
    _cbox("⚠  WARNING — DATA WILL BE ERASED  ⚠", f"{BOLD}{RED}")
    _sdiv()
    _row(" 1.  Settings › About Phone › Build Number  ×7")
    _row(" 2.  Settings › System › Developer Options")
    _row(" 3.  Enable  OEM Unlocking  +  USB Debugging")
    _row(" 4.  Boot device into Fastboot mode")
    _row(" 5.  Connect via USB to this machine")
    _empty()
    _bot()

    if not confirm("Proceed with bootloader unlock?"):
        warn("Unlock cancelled."); press_enter(); return

    info("Sending unlock commands...")
    fb("flashing unlock")
    fb("oem unlock")
    ok("Done. Confirm on device screen if prompted.")
    press_enter()

# ── Main ───────────────────────────────────────────────────────────────────────
MENU = {
    '1': ("Unlock Bootloader",    unlock_bootloader),
    '2': ("Fastboot Device Check",device_check_menu),
    '3': ("Flash Stock ROM",      flash_stock_rom_combined),
    '4': ("Reboot Options",       reboot_menu),
}

def main():
    while True:
        print_header("MAIN MENU")
        for k, (label, _) in MENU.items():
            print(f"  {CYN}[{k}]{RST}  {WHT}{label}{RST}")
        print(f"  {CYN}[5]{RST}  {DWHT}Exit{RST}\n")

        ch = prompt("Select option:")
        if ch in MENU:
            MENU[ch][1]()
        elif ch == '5':
            clr()
            print(f"\n  {GRN}@shelby{RST}  {DWHT}— Infinix Note 40 5G Tool{RST}\n")
            sys.exit(0)
        else:
            warn("Invalid option."); w(0.4)

if __name__ == "__main__":
    main()
