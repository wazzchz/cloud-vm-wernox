import sys
import os
import subprocess
import time
import requests

SUPABASE_URL = "https://ubcuaqrzqarzrxiptpjf.supabase.co"
SUPABASE_KEY = "sb_secret_DQDU_q_Gx9lq1WnvTuHd8A_d4lpnvf8"

if len(sys.argv) < 3:
    print("Erro: Parametros ausentes.")
    sys.exit(1)

discord_id = sys.argv[1]
id_sessao = sys.argv[2]

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal"
}

try:
    print("Iniciando instalacao local do AnyDesk...")
    anydesk_path = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    if not os.path.exists(anydesk_path):
        anydesk_path = r"C:\Program Files (x86)\AnyDesk\AnyDesk.exe"

    subprocess.run(f'"{anydesk_path}" --start', shell=True)
    time.sleep(5)

    print("Definindo senha de acesso no AnyDesk...")
    subprocess.run(f'echo SenhaVirtual123 | "{anydesk_path}" --set-password _full_access', shell=True)

    id_anydesk = ""
    tentativas = 0
    while (not id_anydesk or id_anydesk == "0") and tentativas < 12:
        time.sleep(5)
        resultado = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True)
        id_anydesk = "".join(filter(str.isdigit, resultado.stdout.strip()))
        tentativas += 1

    if not id_anydesk:
        id_anydesk = "ERRO_ID"

    print(f"AnyDesk ID obtido com sucesso: {id_anydesk}")
    url_update = f"{SUPABASE_URL}/rest/v1/chaves_anydesk?id_sessao=eq.{id_sessao}"
    payload = {"anydesk_id": id_anydesk}
    
    update_response = requests.patch(url_update, headers=headers, json=payload)
    print(f"Status da atualizacao no banco: {update_response.status_code}")

except Exception as e:
    print(f"Erro na rotina operacional: {e}")
    
