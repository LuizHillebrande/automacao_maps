# 🗺️ Automação de Pesquisa de Nicho no Google Maps

Automação completa para coletar dados de estabelecimentos do Google Maps (nome, telefone e endereço) com base em nichos de mercado e cidades selecionadas.

## 🚀 Funcionalidades

- ✅ Interface gráfica moderna e intuitiva
- ✅ Seleção de múltiplos nichos de mercado
- ✅ Integração com API do IBGE para estados e cidades
- ✅ Coleta automática de dados (nome, endereço, telefone)
- ✅ Exportação para Excel (.xlsx) ou CSV
- ✅ Pausas aleatórias para evitar bloqueios
- ✅ Barra de progresso em tempo real

## 📋 Requisitos

- Python 3.9+
- Chrome/Chromium instalado
- ChromeDriver (gerenciado automaticamente pelo Selenium 4+)

## 🔧 Instalação

1. Clone ou baixe este repositório

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Certifique-se de ter o Chrome instalado. O Selenium 4+ gerenciará o ChromeDriver automaticamente.

## 🎯 Como Usar

1. Execute o aplicativo:
```bash
python main.py
```

2. Na interface gráfica:
   - **Adicione nichos**: Digite um nicho (ex: "auto peças") e clique em "Adicionar"
   - **Selecione estado**: Escolha um estado no dropdown
   - **Selecione cidades**: Escolha cidades e clique em "Adicionar Cidade"
   - **Inicie a busca**: Clique em "▶️ Iniciar Busca"
   - **Aguarde a coleta**: O processo pode demorar dependendo da quantidade de dados
   - **Exporte os resultados**: Clique em "📥 Exportar Resultados" quando concluído

## 📊 Estrutura do Projeto

```
automacao_maps/
│
├── main.py                 # Ponto de entrada da aplicação
├── interface.py            # Interface gráfica (CustomTkinter)
├── scraper.py              # Automação do Google Maps (Selenium)
├── ibge_api.py             # API do IBGE para estados e cidades
├── requirements.txt        # Dependências do projeto
├── README.md              # Este arquivo
└── output/                # Pasta para arquivos exportados
    └── resultados.xlsx    # Resultados gerados
```

## 📦 Dependências

- `selenium`: Automação do navegador
- `customtkinter`: Interface gráfica moderna
- `pandas`: Manipulação de dados
- `openpyxl`: Exportação para Excel
- `requests`: Requisições HTTP para API do IBGE

## ⚙️ Funcionamento Técnico

### Automação do Google Maps

1. Abre o Google Maps em `https://www.google.com/maps`
2. Para cada combinação de nicho + cidade:
   - Limpa o campo de busca
   - Digita: `{nicho} em {cidade}`
   - Pressiona Enter
   - Aguarda o carregamento dos resultados
   - Localiza todos os elementos `<a class="hfpxzc">`
   - Para cada resultado:
     - Clica no elemento
     - Aguarda o painel lateral carregar
     - Extrai nome, endereço e telefone
     - Salva os dados

### Extração de Dados

- **Nome**: Busca em múltiplos seletores CSS para maior compatibilidade
- **Endereço**: Identifica padrões de endereço (ruas, avenidas, CEPs, etc.)
- **Telefone**: Identifica padrões de telefone brasileiro

### Proteções Anti-Bloqueio

- Pausas aleatórias entre ações (2-5 segundos)
- Scroll suave para elementos
- User-agent customizado
- Desabilita flags de automação do Chrome

## 📝 Formato de Exportação

Os dados são exportados em formato Excel/CSV com as seguintes colunas:

| Nicho | Cidade | Nome da Empresa | Endereço | Telefone |
|-------|--------|-----------------|----------|----------|
| Auto Peças | Cambé | Moto Peças Cambé | R. Belo Horizonte, 727 - Centro, Cambé - PR | (43) 3254-5910 |

## ⚠️ Observações Importantes

1. **Taxa de Requisições**: O Google Maps pode bloquear buscas em massa. O script inclui pausas aleatórias, mas use com moderação.

2. **Estrutura HTML**: O Google Maps pode alterar sua estrutura HTML. Se o scraper parar de funcionar, pode ser necessário atualizar os seletores CSS.

3. **Dados Faltantes**: Alguns estabelecimentos podem não ter telefone ou endereço completo. Nesses casos, será registrado como "Não informado".

4. **ChromeDriver**: O Selenium 4+ gerencia o ChromeDriver automaticamente. Se houver problemas, verifique se o Chrome está instalado e atualizado.

## 🐛 Solução de Problemas

### Erro ao inicializar o driver
- Verifique se o Chrome está instalado
- Atualize o Chrome para a versão mais recente
- Tente reinstalar o Selenium: `pip install --upgrade selenium`

### Nenhum resultado encontrado
- Verifique se o termo de busca está correto
- Alguns nichos podem não ter resultados em certas cidades
- O Google Maps pode ter alterado a estrutura HTML

### Timeout ao buscar elementos
- Aumente o `wait_time` no construtor do `GoogleMapsScraper`
- Verifique sua conexão com a internet
- O Google Maps pode estar bloqueando a automação

## 📄 Licença

Este projeto é fornecido como está, para uso educacional e de pesquisa.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Se encontrar problemas ou tiver ideias, sinta-se à vontade para contribuir.


