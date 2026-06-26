import sys
import os
import subprocess
import time
import requests

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

    subprocess.run(["powershell", "-Command", "Stop-Service -Name AnyDesk -Force"], capture_output=True)
    subprocess.run(["taskkill", "/f", "/im", "anydesk.exe"], capture_output=True)
    time.sleep(2)

    config_dir = r"C:\ProgramData\AnyDesk"
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
        
    config_path = os.path.join(config_dir, "system.conf")
    
    config_lines = [
        "ad.security.interactive_connections=2\n",
        "ad.security.allow_unattended_access=1\n"
    ]
    
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        new_lines = []
        for line in lines:
            if not line.startswith("ad.security.interactive_connections") and not line.startswith("ad.security.allow_unattended_access"):
                new_lines.append(line)
        new_lines.extend(config_lines)
        
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
    else:
        with open(config_path, "w", encoding="utf-8") as f:
            f.writelines(config_lines)

    cmd_senha = f'echo {senha_real}| "{anydesk_path}" --set-password'
    subprocess.run(cmd_senha, shell=True, capture_output=True)

    subprocess.run(["powershell", "-Command", "Start-Service -Name AnyDesk"], capture_output=True)
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

except Exception:
    pass
    
