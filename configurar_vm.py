import sys
import os
import subprocess
import time
import requests
import re

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
    choco_anydesk = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    target_dir = r"C:\Program Files (x86)\AnyDesk"
    system_anydesk = os.path.join(target_dir, "AnyDesk.exe")

    print("[CHOQUE DE REDE] Matando processos antigos...")
    subprocess.run("taskkill /f /im anydesk.exe", shell=True, capture_output=True)
    subprocess.run("net stop AnyDesk", shell=True, capture_output=True)

    print("[CHOQUE DE REDE] Forcando sincronizacao de horario (Correcao SSL)...")
    subprocess.run("net start w32time", shell=True, capture_output=True)
    subprocess.run("w32tm /resync /force", shell=True, capture_output=True)

    print("[CHOQUE DE REDE] Substituindo DNS da Microsoft por Google/Cloudflare...")
    ps_dns = 'powershell -Command "Get-NetAdapter | Where-Object {$_.Status -eq \'Up\'} | Set-DnsClientServerAddress -ServerAddresses (\'8.8.8.8\',\'1.1.1.1\')"'
    subprocess.run(ps_dns, shell=True, capture_output=True)
    subprocess.run("ipconfig /flushdns", shell=True, capture_output=True)

    print("[CHOQUE DE REDE] Acordando rota externa...")
    subprocess.run("ping -n 2 anydesk.com", shell=True, capture_output=True)

    if os.path.exists(choco_anydesk) and not os.path.exists(system_anydesk):
        print("[STEP 2] Instalando servico oficial...")
        try:
            cmd_install = f'"{choco_anydesk}" --install "{target_dir}" --start-with-win --silent'
            subprocess.run(cmd_install, shell=True, capture_output=True, timeout=25)
        except Exception:
            pass
        time.sleep(4)

    anydesk_path = system_anydesk if os.path.exists(system_anydesk) else choco_anydesk

    config_dirs = [
        r"C:\ProgramData\AnyDesk",
        os.path.expandvars(r"%APPDATA%\AnyDesk"),
        r"C:\Windows\SysWOW64\config\systemprofile\AppData\Roaming\AnyDesk",
        r"C:\Windows\System32\config\systemprofile\AppData\Roaming\AnyDesk"
    ]

    print("[STEP 3] Injetando travas de bypass e Proxy Zero...")
    for config_dir in config_dirs:
        if not os.path.exists(config_dir):
            try: os.makedirs(config_dir)
            except: pass

        for filename in ["system.conf", "service.conf", "connection.conf"]:
            config_path = os.path.join(config_dir, filename)
            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    f.write("ad.security.interactive_connections=2\n")
                    f.write("ad.security.allow_unattended_access=1\n")
                    f.write("ad.security.allow_unattended_access.anywhere=1\n")
                    f.write("ad.security.allow_unattended_access.password_only=1\n")
                    f.write("ad.ro_session_features.terminal_server=0\n")
                    f.write("ad.features.terminal_server=0\n")
                    f.write("ad.net.proxy.mode=0\n")  # <--- MATA O PROXY FANTASMA DA AZURE
                    f.write("ad.features.incoming.audio=1\n")
                    f.write("ad.features.incoming.clip=1\n")
                    f.write("ad.features.incoming.control=1\n")
                    f.write("ad.features.incoming.file=1\n")
            except Exception:
                pass

    print("[STEP 4] Aplicando senha master...")
    try:
        bat_cmd = f'echo {senha_real} | "{anydesk_path}" --set-password'
        subprocess.run(bat_cmd, shell=True, capture_output=True, timeout=10)
    except Exception:
        pass
    time.sleep(2)

    print("[STEP 5] Inicializando AnyDesk...")
    subprocess.run("net start AnyDesk", shell=True, capture_output=True)
    subprocess.Popen(f'start "" "{anydesk_path}" --start', shell=True)
    time.sleep(6)

    print("[STEP 6] Capturando ID de 9 digitos...")
    id_anydesk = ""
    tentativas = 0

    while (not id_anydesk or id_anydesk == "0") and tentativas < 25:
        time.sleep(4)
        tentativas += 1
        
        try:
            res = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True, timeout=5)
            saida = res.stdout.strip() if res.stdout else ""
            num = "".join(filter(str.isdigit, saida))
            if num and int(num) > 10000:
                id_anydesk = num
                break
        except Exception:
            pass

        if not id_anydesk or id_anydesk == "0":
            for c_dir in config_dirs:
                sys_conf = os.path.join(c_dir, "system.conf")
                if os.path.exists(sys_conf):
                    try:
                        with open(sys_conf, "r", encoding="utf-8", errors="ignore") as f:
                            match = re.search(r'ad\.anydesk_id=(\d+)', f.read())
                            if match:
                                num_f = match.group(1)
                                if int(num_f) > 10000:
                                    id_anydesk = num_f
                                    break
                    except Exception:
                        pass
            if id_anydesk and int(id_anydesk) > 10000:
                break

    if not id_anydesk or id_anydesk == "0":
        id_anydesk = "FALHA_CRITICA_REDE_AZURE"

    print(f"[SUCCESS] Enviando ID [{id_anydesk}] para o Supabase...")
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    requests.patch(url_update, headers=headers, json=payload)

    try:
        subprocess.Popen('start "" /MAX "C:\\Users\\Public\\Desktop\\VMQuickConfig"', shell=True)
    except Exception:
        pass

    print("[DONE] Script concluido!")

except Exception as e:
    print(f"[FATAL ERROR]: {str(e)}")
    sys.exit(1)
    
