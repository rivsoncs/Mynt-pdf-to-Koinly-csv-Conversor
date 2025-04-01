# Mynt PDF to Koinly CSV Converter

Este script Python converte extratos em PDF da corretora Mynt para o formato CSV compatível com a plataforma Koinly, facilitando o controle e declaração de impostos sobre operações com criptomoedas.

## Funcionalidades

- Extrai automaticamente depósitos e vendas de criptomoedas do extrato da Mynt
- Converte datas para o formato UTC exigido pelo Koinly
- Processa valores em BRL e criptomoedas corretamente
- Inclui taxas de corretagem nas operações
- Gera arquivo CSV pronto para importação no Koinly
- Ordena as transações por data

## Requisitos

- Python 3.6 ou superior
- Biblioteca `pdfplumber` para extração de texto do PDF

## Instalação

1. Clone este repositório:
```bash
git clone https://github.com/rivsoncs/Mynt-pdf-to-Koinly-csv-Conversor.git
cd Mynt-pdf-to-Koinly-csv-Conversor
```

2. Instale as dependências:
```bash
pip install pdfplumber
```

## Uso

1. Coloque seu extrato da Mynt (em formato PDF) no mesmo diretório do script
2. Renomeie o arquivo para `mynt.pdf` ou ajuste o nome do arquivo no código
3. Execute o script:
```bash
python mynt_pdf_to_koinly.py
```

O script irá gerar um arquivo `extrato_mynt_koinly.csv` que pode ser importado diretamente no Koinly.

## Formato do CSV Gerado

O arquivo CSV gerado segue o formato padrão do Koinly com as seguintes colunas:
- Date (UTC)
- Sent Amount
- Sent Currency
- Received Amount
- Received Currency
- Fee Amount
- Fee Currency
- Net Worth Amount
- Net Worth Currency
- Label
- Description
- TxHash

## Tipos de Operações Suportadas

### Depósitos
- Identificados automaticamente
- Registrados como "deposit" no Koinly
- Valor recebido em cripto

### Vendas
- Valor enviado em cripto
- Valor recebido em BRL
- Taxa de corretagem incluída

## Limitações

- O script foi desenvolvido e testado com extratos da Mynt contendo operações de ETH
- Atualmente suporta apenas depósitos e vendas
- O arquivo PDF deve estar no formato padrão da Mynt

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Enviar pull requests

## Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## Disclaimer

Este é um projeto não oficial e não tem nenhuma afiliação com a Mynt ou o Koinly. Use por sua conta e risco e sempre verifique se as transações foram importadas corretamente no Koinly.
