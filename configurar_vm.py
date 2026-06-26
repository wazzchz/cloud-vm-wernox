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

    config_dirs = [r"C:\ProgramData\AnyDesk", os.path.expandvars(r"%APPDATA%\AnyDesk")]
    
    config_override = {
        "ad.security.interactive_connections": "2",
        "ad.security.allow_unattended_access": "1",
        "ad.security.allow_unattended_access.anywhere": "1",
        "ad.security.allow_unattended_access.password_only": "1",
        "ad.features.incoming.audio": "1",
        "ad.features.incoming.clip": "1",
        "ad.features.incoming.control": "1",
        "ad.features.incoming.file": "1"
    }

    for config_dir in config_dirs:
        if not os.path.exists(config_dir):
            os.makedirs(config_dir)
        
        for filename in ["system.conf", "service.conf"]:
            config_path = os.path.join(config_dir, filename)
            lines = []
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            new_lines = []
            keys_written = set()
            
            for line in lines:
                stripped = line.strip()
                if "=" in stripped:
                    k, v = stripped.split("=", 1)
                    k = k.strip()
                    if k in config_override:
                        new_lines.append(f"{k}={config_override[k]}\n")
                        keys_written.add(k)
                        continue
                new_lines.append(line)

            for k, v in config_override.items():
                if k not in keys_written:
                    new_lines.append(f"{k}={v}\n")

            with open(config_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

    cmd_senha = f'echo {senha_real}| "{anydesk_path}" --set-password'
    subprocess.run(cmd_senha, shell=True, capture_output=True)

    subprocess.run(["powershell", "-Command", "Start-Service -Name AnyDesk"], capture_output=True)
    subprocess.Popen(f'start "" "{anydesk_path}" --start', shell=True)
    time.sleep(5)

    id_anydesk = ""
    tentativas = 0
    
    while (not id_anydesk or id_anydesk == "0") and tentativas < 12:
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
    
