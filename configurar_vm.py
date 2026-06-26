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
    # 1. Busca e define o executavel definitivo
    choco_anydesk = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    target_dir = r"C:\Program Files (x86)\AnyDesk"
    system_anydesk = os.path.join(target_dir, "AnyDesk.exe")

    print("[STEP 1] Matando processos antigos...")
    subprocess.run("taskkill /f /im anydesk.exe", shell=True, capture_output=True)
    subprocess.run("net stop AnyDesk", shell=True, capture_output=True)
    time.sleep(2)

    # 2. Re-instalação limpa como Serviço do Sistema (SYSTEM)
    if os.path.exists(choco_anydesk) and not os.path.exists(system_anydesk):
        print("[STEP 2] Instalando AnyDesk como servico nativo...")
        try:
            cmd_install = f'"{choco_anydesk}" --install "{target_dir}" --start-with-win --silent'
            subprocess.run(cmd_install, shell=True, capture_output=True, timeout=15)
        except subprocess.TimeoutExpired:
            print("[WARN] Timeout no comando de instalacao, prosseguindo...")
        time.sleep(3)

    anydesk_path = system_anydesk if os.path.exists(system_anydesk) else choco_anydesk

    # 3. Força as flags em todos os perfis de ambiente possíveis
    config_dirs = [
        r"C:\ProgramData\AnyDesk",
        os.path.expandvars(r"%APPDATA%\AnyDesk"),
        r"C:\Windows\SysWOW64\config\systemprofile\AppData\Roaming\AnyDesk",
        r"C:\Windows\System32\config\systemprofile\AppData\Roaming\AnyDesk"
    ]

    print("[STEP 3] Gravando tabelas de permissao irrestrita...")
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
                    f.write("ad.features.incoming.audio=1\n")
                    f.write("ad.features.incoming.clip=1\n")
                    f.write("ad.features.incoming.control=1\n")
                    f.write("ad.features.incoming.file=1\n")
            except Exception:
                pass

    # 4. Injeta a senha usando pipe com TIMEOUT para não travar a esteira do GitHub
    print("[STEP 4] Aplicando senha master...")
    try:
        bat_cmd = f'echo {senha_real} | "{anydesk_path}" --set-password'
        subprocess.run(bat_cmd, shell=True, capture_output=True, timeout=10)
    except subprocess.TimeoutExpired:
        print("[WARN] AnyDesk segurou o pipe da senha. Forcando liberacao da thread...")
    time.sleep(2)

    # 5. Inicia o serviço do sistema e abre a interface gráfica desvinculada
    print("[STEP 5] Subindo servicos...")
    subprocess.run("net start AnyDesk", shell=True, capture_output=True)
    subprocess.Popen(f'start "" "{anydesk_path}" --start', shell=True)
    time.sleep(4)

    # 6. Captura resiliente de ID (Até 30 tentativas = 150 segundos de tolerância)
    print("[STEP 6] Aguardando alocacao de ID na rede AnyDesk...")
    id_anydesk = ""
    tentativas = 0
    while (not id_anydesk or id_anydesk == "0") and tentativas < 30:
        time.sleep(5)
        try:
            res = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True, timeout=5)
            saida = res.stdout.strip() if res.stdout else ""
            id_anydesk = "".join(filter(str.isdigit, saida))
        except Exception:
            pass
        tentativas += 1

    if not id_anydesk or id_anydesk == "0":
        id_anydesk = "FALHA_REDE_ID"

    print(f"[SUCCESS] Sincronizando ID [{id_anydesk}] no banco de dados...")
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    requests.patch(url_update, headers=headers, json=payload)

    # 7. Abre o painel auxiliar sem bloquear a finalização do Python
    try:
        subprocess.Popen('start "" /MAX "C:\\Users\\Public\\Desktop\\VMQuickConfig"', shell=True)
    except Exception:
        pass

    print("[DONE] Configuração dinâmica finalizada com êxito!")

except Exception as e:
    print(f"[FATAL ERROR] Falha na rotina: {str(e)}")
    sys.exit(1)
    
