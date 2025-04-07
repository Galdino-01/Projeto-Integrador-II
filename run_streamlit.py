import os
import subprocess
import sys
from pathlib import Path

def main():
    # Caminho para o certificado SSL
    cert_path = os.environ.get("SSL_CERT_PATH", "/etc/ssl/certs/your_certificate.crt")
    key_path = os.environ.get("SSL_KEY_PATH", "/etc/ssl/private/your_private_key.key")
    
    # Verificar se os certificados existem
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print(f"Aviso: Certificados SSL não encontrados em {cert_path} e {key_path}")
        print("O Streamlit será iniciado sem HTTPS.")
        print("Para usar HTTPS, defina as variáveis de ambiente SSL_CERT_PATH e SSL_KEY_PATH.")
        print("Exemplo: export SSL_CERT_PATH=/caminho/para/seu/certificado.crt")
        print("         export SSL_KEY_PATH=/caminho/para/sua/chave.key")
        
        # Iniciar Streamlit sem HTTPS
        subprocess.run(["streamlit", "run", "dashboard/1_📄_Homepage.py"])
    else:
        # Iniciar Streamlit com HTTPS
        print(f"Iniciando Streamlit com HTTPS usando certificado em {cert_path}")
        subprocess.run([
            "streamlit", "run", "dashboard/1_📄_Homepage.py",
            "--server.address", "0.0.0.0",
            "--server.port", "5173",
            "--server.sslCertFile", cert_path,
            "--server.sslKeyFile", key_path
        ])

if __name__ == "__main__":
    main()