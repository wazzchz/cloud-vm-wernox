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
    # Localiza o executavel correto
    anydesk_path = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files\AnyDesk\AnyDesk.exe"

    print("[1/4] Encerrando todas as instancias e servicos do AnyDesk...")
    subprocess.run(["powershell", "-Command", "Stop-Service -Name AnyDesk -Force"], capture_output=True)
    subprocess.run(["taskkill", "/f", "/im", "anydesk.exe"], capture_output=True)
    time.sleep(2)

    # MAIOR COBERTURA: Mapeia todos os diretorios possiveis de configuracao do Windows
    config_dirs = [
        r"C:\ProgramData\AnyDesk",
        os.path.expandvars(r"%APPDATA%\AnyDesk"),
        r"C:\Windows\SysWOW64\config\systemprofile\AppData\Roaming\AnyDesk",
        r"C:\Windows\System32\config\systemprofile\AppData\Roaming\AnyDesk"
    ]
    
    # Travas completas de Acesso Nao Supervisionado e bypass de sessao Terminal RDP
    config_override = {
        "ad.security.interactive_connections": "2",  # 2 = PERMITIR CONEXAO DIRETA
        "ad.security.allow_unattended_access": "1",   # 1 = Ativa acesso por senha
        "ad.security.allow_unattended_access.anywhere": "1",
        "ad.security.allow_unattended_access.password_only": "1",
        "ad.features.incoming.audio": "1",
        "ad.features.incoming.clip": "1",
        "ad.features.incoming.control": "1",
        "ad.features.incoming.file": "1",
        "ad.ro_session_features.terminal_server": "0", # Desativa menu de escolha de tela
        "ad.features.terminal_server": "0"             # Conecta direto no Console principal
    }

    print("[2/4] Aplicando diretrizes de bypass nos arquivos .conf encontrados...")
    for config_dir in config_dirs:
        if not os.path.exists(config_dir):
            try:
                os.makedirs(config_dir)
            except:
                pass
        
        # Garante a modificacao no system.conf, service.conf e connection.conf simultaneamente
        for filename in ["system.conf", "service.conf", "connection.conf"]:
            config_path = os.path.join(config_dir, filename)
            lines = []
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8", errors="ignore") as f:
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

            try:
                with open(config_path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
            except:
                pass

    print("[3/4] Forcando injecao da senha master...")
    cmd_senha = f'echo {senha_real}| "{anydesk_path}" --set-password'
    subprocess.run(cmd_senha, shell=True, capture_output=True)
    time.sleep(1)

    print("[4/4] Inicializando o AnyDesk com os novos parametros...")
    subprocess.run(["powershell", "-Command", "Start-Service -Name AnyDesk"], capture_output=True)
    subprocess.Popen(f'start "" "{anydesk_path}" --start', shell=True)
    time.sleep(5)

    id_anydesk = ""
    tentativas = 0
    
    print("Capturando ID de conexao remota...")
    while (not id_anydesk or id_anydesk == "0") and tentativas < 12:
        time.sleep(5)
        resultado = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True)
        saida_limpa = resultado.stdout.strip() if resultado.stdout else ""
        id_anydesk = "".join(filter(str.isdigit, saida_limpa))
        tentativas += 1

    if not id_anydesk:
        id_anydesk = "ERRO_ID"
    
    print(f"ID obtido com sucesso: {id_anydesk}. Sincronizando com Supabase...")
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    requests.patch(url_update, headers=headers, json=payload)

    try:
        os.system('start "" /MAX "C:\\Users\\Public\\Desktop\\VMQuickConfig"')
    except Exception:
        pass

except Exception as e:
    print(f"Erro operacional interno: {str(e)}")
    
