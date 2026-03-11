import os
from dotenv import load_dotenv

# Explicitly load from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from services.db_service import supabase

def create_admin_user(email: str, password: str):
    print(f"Tentando criar admin user para o email: {email}")
    try:
        # Tenta criar usuário via Auth Service
        response = supabase.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True
        })
        print(f"Usuário admin criado com sucesso!")
        print(f"User ID: {response.user.id}")
        return True
    except Exception as e:
        print(f"Erro ao criar usuário admin: {e}")
        return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Criar Admin User para o painel.")
    parser.add_argument("--email", required=True, help="E-mail do novo admin")
    parser.add_argument("--password", required=True, help="Senha do novo admin")
    args = parser.parse_args()
    
    create_admin_user(args.email, args.password)
