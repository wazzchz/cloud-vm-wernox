import sys
import os
import subprocess
import time
from supabase import create_client, Client

SUPABASE_URL = "https://ubcuaqrzqarzrxiptpjf.supabase.co"
SUPABASE_KEY = "Sb_publishable_Dc3ZdwlRvxufsV2RHV1dcw_b9sD8UWh"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

if len(sys.argv) < 3:
    print("❌ Erro fatal: Argumentos insuficientes (ID Discord e ID Sessão necessários).")
    sys.exit(1)

discord_id = sys.argv[1]
id_sessao = sys.argv[2]

print(f"🔍 Buscando credenciais para a Sessão: {id_sessao} (Usuário: {discord_id})")

try:
    response = supabase.table("chaves_anydesk").select("senha").eq("id_sessao", id_sessao).execute()
    
    if not response.data:
        print(f"❌ Nenhuma sessão {id_sessao} encontrada no banco.")
        sys.exit(1)
        
    senha_recuperada = response.data[0]["senha"]
    print("✅ Senha recuperada com sucesso!")
  
    subprocess.run(f'powershell -Command "Set-LocalUser -Name \'runneradmin\' -Password (ConvertTo-SecureString -AsPlainText \'{senha_recuperada}\' -Force)"', shell=True)
    anydesk_path = r"C:\ProgramData\chocolatey\lib\anydesk.portable\tools\AnyDesk.exe"
    subprocess.run(f'echo {senha_recuperada} | "{anydesk_path}" --set-password _full_access', shell=True)
    subprocess.run(f'"{anydesk_path}" --start', shell=True)
  
    id_anydesk = ""
    tentativas = 0
    while (not id_anydesk or id_anydesk == "0") and tentativas < 12:
        time.sleep(5)
        resultado = subprocess.run(f'"{anydesk_path}" --get-id', capture_output=True, text=True, shell=True)
        id_anydesk = resultado.stdout.strip()
        tentativas += 1

    if not id_anydesk or id_anydesk == "0":
        print("❌ Falha ao gerar ID do AnyDesk.")
        sys.exit(1)

    print(f"🎯 AnyDesk ID: {id_anydesk}")

    supabase.table("chaves_anydesk").update({"anydesk_id": id_anydesk}).eq("id_sessao", id_sessao).execute()
    print(f"✨ Máquina {id_sessao} sincronizada com sucesso!")

except Exception as e:
    print(f"💥 Erro: {e}")
    sys.exit(1)
