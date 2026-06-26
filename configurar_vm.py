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
    # 1. Localiza o executável correto do AnyDesk
    anydesk_path = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files\AnyDesk\AnyDesk.exe"

    print("🛑 [1/5] Finalizando instâncias ativas do AnyDesk...")
    # Para o serviço e mata qualquer janela órfã que bloqueie os arquivos .conf
    subprocess.run(["powershell", "-Command", "Stop-Service -Name AnyDesk -Force"], capture_output=True)
    subprocess.run(["taskkill", "/f", "/im", "anydesk.exe"], capture_output=True)
    time.sleep(3)

    # 2. Injeta as diretrizes de Bypass de Aceitação Remota nos arquivos de configuração
    config_dirs = [r"C:\ProgramData\AnyDesk", os.path.expandvars(r"%APPDATA%\AnyDesk")]
    
    config_override = {
        "ad.security.interactive_connections": "2",  # 2 = NUNCA exibir janela de aceitação (Permitir direto)
        "ad.security.allow_unattended_access": "1",   # 1 = Habilitar acesso não supervisionado
        "ad.security.allow_unattended_access.anywhere": "1",
        "ad.security.allow_unattended_access.password_only": "1",
        "ad.features.incoming.audio": "1",
        "ad.features.incoming.clip": "1",
        "ad.features.incoming.control": "1",
        "ad.features.incoming.file": "1"
    }

    print("📝 [2/5] Escrevendo parâmetros de acesso irrestrito...")
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

    print("🔐 [3/5] Definindo senha de acesso em background...")
    # Define a senha via CLI nativa (Funciona melhor com o serviço desativado neste ponto do script)
    cmd_senha = f'echo {senha_real}| "{anydesk_path}" --set-password'
    subprocess.run(cmd_senha, shell=True, capture_output=True)
    time.sleep(2)

    print("🔄 [4/5] Reiniciando o serviço AnyDesk de forma limpa para aplicar as diretrizes...")
    # Força o recarregamento do serviço do Windows para ler o system.conf alterado antes da conexão externa
    subprocess.run(["powershell", "-Command", "Start-Service -Name AnyDesk"], capture_output=True)
    subprocess.Popen(f'start "" "{anydesk_path}" --start', shell=True)
    time.sleep(5)

    id_anydesk = ""
    tentativas = 0
    
    # 3. Captura o ID estável gerado pela VM
    print("🔍 [5/5] Aguardando geração do ID AnyDesk...")
    while (not id_anydesk or id_anydesk == "0") and tentativas < 15:
        time.sleep(4)
        resultado = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True)
        saida_limpa = resultado.stdout.strip() if resultado.stdout else ""
        id_anydesk = "".join(filter(str.isdigit, saida_limpa))
        tentativas += 1

    if not id_anydesk:
        id_anydesk = "ERRO_ID"
    
    print(f"📡 ID Gerado: {id_anydesk}. Atualizando banco de dados Supabase...")
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    requests.patch(url_update, headers=headers, json=payload)

    # Inicializa a interface principal do Windows Quick Config se disponível
    try:
        os.system('start "" /MAX "C:\\Users\\Public\\Desktop\\VMQuickConfig"')
    except Exception:
        pass

except Exception as e:
    print(f"❌ Ocorreu um erro crítico no processo de configuração: {e}")
    
