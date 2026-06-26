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
    # 1. Encontra o executavel do AnyDesk instalado
    anydesk_path = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files\AnyDesk\AnyDesk.exe"

    print("[BAT LOGIC] Matando processos para liberar escrita de arquivos...")
    subprocess.run("taskkill /f /im anydesk.exe", shell=True, capture_output=True)
    subprocess.run("net stop AnyDesk", shell=True, capture_output=True)
    time.sleep(2)

    # 2. Copia fiel dos comandos .bat de preparacao de ambiente
    print("[BAT LOGIC] Limpando e recriando diretorios de seguranca do Windows...")
    config_dirs = [
        r"C:\ProgramData\AnyDesk",
        os.path.expandvars(r"%APPDATA%\AnyDesk"),
        r"C:\Windows\SysWOW64\config\systemprofile\AppData\Roaming\AnyDesk",
        r"C:\Windows\System32\config\systemprofile\AppData\Roaming\AnyDesk"
    ]

    for config_dir in config_dirs:
        if not os.path.exists(config_dir):
            try: os.makedirs(config_dir)
            except: pass

        # Criando a estrutura base limpa via CMD em lote
        for filename in ["system.conf", "service.conf", "connection.conf"]:
            config_path = os.path.join(config_dir, filename)
            # Adiciona os parametros crueis diretamente no arquivo usando escrita sequencial limpa
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

    # 3. A Lógica de Ouro do .bat para Gravação Estável da Senha:
    # Executa a passagem de senha e força o AnyDesk a gerar o token interno dele dentro do CMD nativo
    print("[BAT LOGIC] Injetando senha via CMD nativo em background...")
    bat_cmd = f'echo {senha_real} | "{anydesk_path}" --set-password'
    subprocess.run(bat_cmd, shell=True, capture_output=True)
    time.sleep(2)

    # 4. Inicializa o AnyDesk forcando o modo servico e interface simultaneamente
    print("[BAT LOGIC] Subindo o AnyDesk de forma definitiva...")
    subprocess.run("net start AnyDesk", shell=True, capture_output=True)
    subprocess.run(f'start "" "{anydesk_path}" --start', shell=True)
    time.sleep(5)

    # 5. Captura o ID gerado e sincroniza no Supabase
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
    
    print(f"[SUCCESS] ID Capturado: {id_anydesk}. Enviando para o Supabase...")
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    requests.patch(url_update, headers=headers, json=payload)

    try:
        os.system('start "" /MAX "C:\\Users\\Public\\Desktop\\VMQuickConfig"')
    except Exception:
        pass

except Exception as e:
    print(f"Erro na execucao da rotina: {str(e)}")
        
