import sys
import os
import subprocess
import time
import requests

SUPABASE_URL = "https://ubcuaqrzqarzrxiptpjf.supabase.co"
SUPABASE_KEY = "sb_secret_DQDU_q_Gx9lq1WnvTuHd8A_d4lpnvf8"

if len(sys.argv) < 3:
    print("Erro: Parametros operacionais ausentes (ID Usuario e Sessao requeridos).")
    sys.exit(1)

discord_id = sys.argv[1]
id_sessao = sys.argv[2]

print(f"Sincronizando parametros para a sessao isolada: {id_sessao}")

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json"
}

try:
    url_select = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}&select=senha"
    response = requests.get(url_select, headers=headers)
    
    if response.status_code != 200 or not response.json():
        print(f"Erro: Registro {id_sessao} inexistente no banco. Status: {response.status_code}")
        sys.exit(1)
        
    dados_banco = response.json()
    senha_recuperada = dados_banco[0]["senha"]
    print("Chave/Senha validada e capturada com sucesso.")

    subprocess.run(f'powershell -Command "Set-LocalUser -Name \'runneradmin\' -Password (ConvertTo-SecureString -AsPlainText \'{senha_recuperada}\' -Force)"', shell=True)

    anydesk_path = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"

    subprocess.run(f'echo {senha_recuperada} | "{anydesk_path}" --set-password _full_access', shell=True)
    subprocess.run(f'"{anydesk_path}" --start', shell=True)

    id_anydesk = ""
    tentativas = 0
    while (not id_anydesk or id_anydesk == "0") and tentativas < 12:
        time.sleep(5)
        resultado = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True)
        id_anydesk = resultado.stdout.strip()
        id_anydesk = "".join(filter(str.isdigit, id_anydesk))
        tentativas += 1

    if not id_anydesk or id_anydesk == "0":
        print("Erro: Timeout na atribuicao do AnyDesk ID.")
        sys.exit(1)

    print(f"AnyDesk ID determinado com sucesso: {id_anydesk}")
    
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    
    update_response = requests.patch(url_update, headers=headers, json=payload)
    
    if update_response.status_code in [200, 201, 204]:
        print(f"Sucesso: Ciclo operacional da maquina {id_sessao} ativado com exito.")
    else:
        print(f"Erro ao salvar no banco: Status {update_response.status_code} - {update_response.text}")
        sys.exit(1)

except Exception as e:
    print(f"Falha na execucao da rotina interna da VM: {e}")
    sys.exit(1)
    
