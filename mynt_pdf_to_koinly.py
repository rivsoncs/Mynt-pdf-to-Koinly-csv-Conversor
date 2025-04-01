import pdfplumber
import csv
import re
import unicodedata
from datetime import datetime

def normalize_str(s: str) -> str:
    """
    Remove acentos e caracteres especiais, retornando texto ASCII básico, 
    tudo em minúsculo, para facilitar comparação.
    """
    if not isinstance(s, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c)).lower()

def parse_date(date_str: str) -> str:
    """
    Converte data no formato 'DD/MM/YYYY' para 'YYYY-MM-DD HH:MM UTC'.
    """
    try:
        dt = datetime.strptime(date_str.strip(), "%d/%m/%Y")
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except ValueError as e:
        print(f"Erro ao converter data '{date_str}': {str(e)}")
        return "Invalid Date"

def parse_value_brl(brl_str: str) -> str:
    """
    Recebe algo como 'R$ 30.000,00' e retorna '30000.00'.
    """
    if not isinstance(brl_str, str):
        return "0.00"
        
    # Remove 'R$', espaços e caracteres estranhos
    temp = brl_str.replace("R$", "").strip()
    
    # Remove todos os pontos (separadores de milhar)
    temp = temp.replace(".", "")
    
    # Substitui vírgula por ponto
    temp = temp.replace(",", ".")
    
    # Remove qualquer outro caractere que não seja dígito ou ponto
    temp = re.sub(r"[^\d\.]", "", temp)
    
    if not temp:
        return "0.00"
        
    # Garante que temos duas casas decimais
    if "." not in temp:
        temp += ".00"
    elif len(temp.split(".")[-1]) == 1:
        temp += "0"
        
    return temp

def parse_value_crypto(crypto_str: str) -> str:
    """
    Recebe algo como '1,714000' e retorna '1.714000'.
    """
    if not isinstance(crypto_str, str):
        return ""
        
    temp = str(crypto_str).strip()
    temp = re.sub(r"[^0-9,\.-]+", "", temp)
    if not temp:
        return ""
    # Substitui vírgulas por ponto
    temp = temp.replace(",", ".")
    return temp

def process_line(line_text: str) -> tuple:
    """
    Processa uma linha do texto e retorna uma tupla com os dados extraídos.
    """
    # Remove espaços extras e caracteres indesejados
    line = ' '.join(line_text.split())
    
    print(f"\nTentando processar linha: {line}")  # Debug
    
    # Primeiro tenta o padrão de depósito
    deposit_pattern = r'(Depósito|Deposito)\s+(\d{2}/\d{2}/\d{4})\s+(\w+)\s+([\d,]+)\s+R\$\s*([\d\.,]+)\s+R\$\s*([\d\.,]+)\s+R\$\s*([\d\.,]+)'
    deposit_match = re.search(deposit_pattern, line)
    if deposit_match:
        print("Padrão de depósito encontrado")  # Debug
        return deposit_match.groups()
    
    # Se não for depósito, tenta processar como venda
    if line.startswith('Vend'):
        print("Linha de venda encontrada, processando manualmente")  # Debug
        parts = line.split()
        try:
            # Extrai as partes relevantes
            data = parts[1]  # DD/MM/YYYY
            ativo = parts[2]  # ETH
            quantidade = parts[3]  # X,XXXXXX
            
            # Procura os valores em R$ na linha
            valores_reais = []
            for i, part in enumerate(parts):
                if part == 'R$' and i + 1 < len(parts):
                    valores_reais.append(parts[i + 1])
            
            if len(valores_reais) >= 3:
                preco_medio = valores_reais[0]
                corretagem = valores_reais[1]
                valor_total = valores_reais[2]
                
                print(f"Venda processada manualmente:")  # Debug
                print(f"Data: {data}")
                print(f"Ativo: {ativo}")
                print(f"Quantidade: {quantidade}")
                print(f"Preço Médio: {preco_medio}")
                print(f"Corretagem: {corretagem}")
                print(f"Valor Total: {valor_total}")
                
                return ("Venda", data, ativo, quantidade, preco_medio, corretagem, valor_total)
        except Exception as e:
            print(f"Erro ao processar venda manualmente: {str(e)}")
    
    print(f"Nenhum padrão encontrado para a linha")  # Debug
    print(f"Tentativa de venda falhou para: {line}")  # Debug adicional
    return None

def process_mynt_line(line_text: str) -> list:
    """
    Processa uma linha de texto do PDF da Mynt.
    """
    # Processa a linha
    result = process_line(line_text.strip())
    
    if not result:
        print(f"Linha não corresponde ao padrão: {line_text.strip()}")
        return None
        
    ordem, dia, ativo, quantidade, preco_medio, corretagem, valor_total = result
    
    print(f"\nProcessando linha:")
    print(f"Ordem: {ordem}")
    print(f"Dia: {dia}")
    print(f"Ativo: {ativo}")
    print(f"Quantidade: {quantidade}")
    print(f"Preço Médio: {preco_medio}")
    print(f"Corretagem: {corretagem}")
    print(f"Valor Total: {valor_total}")

    # Converter valores
    date = parse_date(dia)
    crypto_amount = parse_value_crypto(quantidade)
    corretagem_brl = parse_value_brl(corretagem)
    valor_total_brl = parse_value_brl(valor_total)
    operacao_norm = normalize_str(ordem)

    print(f"Valores convertidos:")
    print(f"Data: {date}")
    print(f"Crypto: {crypto_amount}")
    print(f"Corretagem: {corretagem_brl}")
    print(f"Valor Total: {valor_total_brl}")

    # Campos Koinly
    sent_amount = ""
    sent_currency = ""
    received_amount = ""
    received_currency = ""
    fee_amount = corretagem_brl if float(corretagem_brl or 0) > 0 else ""
    fee_currency = "BRL" if fee_amount else ""
    label = ""
    description = ordem  # texto original
    txhash = ""

    # Mapear operações
    if "vend" in operacao_norm or ordem == "Venda":
        sent_amount = crypto_amount
        sent_currency = ativo
        received_amount = valor_total_brl
        received_currency = "BRL"
        print("Operação identificada: Venda")

    elif "deposit" in operacao_norm or "depósito" in operacao_norm:
        received_amount = crypto_amount
        received_currency = ativo
        label = "deposit"
        print("Operação identificada: Depósito")

    # Monta linha Koinly
    result = [
        date,            # Date
        sent_amount,     # Sent Amount
        sent_currency,   # Sent Currency
        received_amount, # Received Amount
        received_currency, 
        fee_amount,      
        fee_currency,    
        "",  # Net Worth Amount
        "",  # Net Worth Currency
        label, 
        description, 
        txhash
    ]
    
    print("Linha Koinly gerada:")
    print(result)
    return result

def convert_pdf_to_koinly(pdf_path: str, output_csv_path: str):
    """
    Lê o PDF da Mynt e gera CSV no formato Koinly.
    """
    print(f"\nIniciando conversão do arquivo: {pdf_path}")
    
    # Abre o CSV de saída
    with open(output_csv_path, "w", encoding="utf-8", newline="") as outfile:
        writer = csv.writer(outfile)

        # Escreve cabeçalho do Koinly
        writer.writerow([
            "Date", "Sent Amount", "Sent Currency",
            "Received Amount", "Received Currency",
            "Fee Amount", "Fee Currency",
            "Net Worth Amount", "Net Worth Currency",
            "Label", "Description", "TxHash"
        ])

        # Lista para armazenar todas as transações
        transactions = []

        # Abre o PDF com pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)
            print(f"Total de páginas no PDF: {total_pages}")
            
            for page_num, page in enumerate(pdf.pages, 1):
                print(f"\nProcessando página {page_num}/{total_pages}")
                
                # Extrai o texto da página
                text = page.extract_text()
                
                # Processa cada linha do texto
                for line in text.split('\n'):
                    # Pula linhas que não são transações
                    if not any(op in line for op in ['Depósito', 'Deposito', 'Venda', 'Vend']):
                        continue
                        
                    # Processa a linha
                    koinly_row = process_mynt_line(line)
                    if koinly_row:
                        transactions.append(koinly_row)

        # Ordena as transações por data e escreve no CSV
        transactions.sort(key=lambda x: x[0])  # Ordena pela data (primeiro campo)
        for transaction in transactions:
            writer.writerow(transaction)

    print(f"\nConversão finalizada! Arquivo Koinly gerado em: {output_csv_path}")

if __name__ == "__main__":
    pdf_path = "mynt.pdf"
    output_csv = "extrato_mynt_koinly.csv"
    convert_pdf_to_koinly(pdf_path, output_csv) 