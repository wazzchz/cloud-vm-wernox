import sys
import os
import subprocess
import time
import requests

try:
    import pyautogui as pag
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui"], capture_output=True)
    import pyautogui as pag

SUPABASE_URL = "https://ubcuaqrzqarzrxiptpjf.supabase.co"
SUPABASE_KEY = "sb_secret_DQDU_q_Gx9lq1WnvTuHd8A_d4lpnvf8"

if len(sys.argv) < 4:
    sys.exit(1)

discord_id = sys.argv[1]
id_sessao = sys.argv[2]
senha_real = sys.argv[3]

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

try:
    anydesk_path = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files\AnyDesk\AnyDesk.exe"

    subprocess.Popen(f'start "" "{anydesk_path}" --start', shell=True)
    time.sleep(10)

    id_anydesk = ""
    tentativas = 0
    
    while (not id_anydesk or id_anydesk == "0") and tentativas < 10:
        time.sleep(5)
        resultado = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True)
        saida_limpa = resultado.stdout.strip() if resultado.stdout else ""
        id_anydesk = "".join(filter(str.isdigit, saida_limpa))
        tentativas += 1

    if not id_anydesk:
        id_anydesk = "ERRO_ID"
    
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    requests.patch(url_update, headers=headers, json=payload)

    try:
        os.system('start "" /MAX "C:\\Users\\Public\\Desktop\\VMQuickConfig"')
    except Exception:
        pass

    while True:
        try:
            pag.click(147, 489)
            time.sleep(1)
            pag.click(156, 552)
            time.sleep(1)
            pag.click(587, 14)
            time.sleep(1)
            pag.click(916, 17)
            time.sleep(1)
            pag.click(897, 64)
            time.sleep(5)
        except Exception:
            time.sleep(5)

except Exception:
    pass
    
