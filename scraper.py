"""
Módulo para automação de coleta de dados do Google Maps usando Selenium.
"""
import time
import random
import re
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException


class GoogleMapsScraper:
    """Classe para automatizar a coleta de dados do Google Maps."""
    
    def __init__(self, headless: bool = False, wait_time: int = 10):
        """
        Inicializa o scraper.
        
        Args:
            headless: Se True, executa o navegador em modo headless
            wait_time: Tempo máximo de espera para elementos (segundos)
        """
        self.wait_time = wait_time
        self.driver = None
        self.headless = headless
        
    def _init_driver(self):
        """Inicializa o driver do Selenium."""
        options = webdriver.ChromeOptions()
        if self.headless:
            options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.maximize_window()
            self.wait = WebDriverWait(self.driver, self.wait_time)
        except Exception as e:
            raise Exception(f"Erro ao inicializar o driver: {e}")
    
    def open_maps(self):
        """Abre o Google Maps."""
        if not self.driver:
            self._init_driver()
        
        self.driver.get("https://www.google.com/maps")
        time.sleep(random.uniform(2, 4))
    
    def search(self, query: str) -> bool:
        """
        Realiza uma busca no Google Maps.
        
        Args:
            query: Termo de busca (ex: "auto peças em Cambé")
            
        Returns:
            True se a busca foi realizada com sucesso
        """
        try:
            # Tenta múltiplos seletores para encontrar o campo de busca
            # O Google Maps muda frequentemente os seletores
            search_selectors = [
                (By.ID, "UGojuc"),  # Novo ID atualizado
                (By.NAME, "q"),  # Atributo name
                (By.ID, "searchboxinput"),  # ID antigo (fallback)
                (By.CSS_SELECTOR, "input[role='combobox'][name='q']"),  # Seletor CSS mais específico
                (By.CSS_SELECTOR, "input.UGojuc"),  # Por classe
                (By.CSS_SELECTOR, "input[autocomplete='off'][name='q']"),  # Por atributos
            ]
            
            search_box = None
            for by, selector in search_selectors:
                try:
                    search_box = self.wait.until(
                        EC.presence_of_element_located((by, selector))
                    )
                    print(f"✓ Campo de busca encontrado usando: {by} = {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not search_box:
                print("❌ Não foi possível encontrar o campo de busca")
                return False
            
            # Limpa o campo
            search_box.clear()
            time.sleep(random.uniform(0.5, 1))
            
            # Foca no campo (garante que está ativo)
            search_box.click()
            time.sleep(random.uniform(0.3, 0.5))
            
            # Digita a query
            search_box.send_keys(query)
            time.sleep(random.uniform(0.5, 1))
            
            # Pressiona Enter
            search_box.send_keys(Keys.RETURN)
            
            # Aguarda o carregamento dos resultados
            time.sleep(random.uniform(3, 5))
            
            return True
            
        except TimeoutException:
            print(f"Timeout ao buscar: {query}")
            return False
        except Exception as e:
            print(f"Erro ao realizar busca '{query}': {e}")
            return False
    
    def get_results_links(self) -> List:
        """
        Obtém todos os links de resultados da pesquisa.
        
        Returns:
            Lista de elementos <a> com classe 'hfpxzc'
        """
        try:
            # Aguarda um pouco para os resultados carregarem
            time.sleep(random.uniform(2, 3))
            
            # Procura pelos elementos de resultado
            results = self.driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            
            return results
            
        except Exception as e:
            print(f"Erro ao obter links de resultados: {e}")
            return []
    
    def extract_business_data(self) -> Optional[Dict[str, str]]:
        """
        Extrai dados do negócio da página de detalhes.
        
        Returns:
            Dicionário com nome, endereço, telefone, avaliação e número de avaliações, ou None se houver erro
        """
        try:
            data = {
                'nome': 'Não informado',
                'endereco': 'Não informado',
                'telefone': 'Não informado',
                'avaliacao': 'Não informado',
                'num_avaliacoes': 'Não informado'
            }
            
            # Aguarda o painel lateral carregar
            time.sleep(random.uniform(2, 3))
            
            # Extrai o nome - várias estratégias
            nome_selectors = [
                "h1.DUwDvf.lfPIob",
                "h1[data-attrid='title']",
                "h1.DUwDvf",
                "h1.qrShPb",
                "h1.x3AX1-LfntMc-header-title-title"
            ]
            
            for selector in nome_selectors:
                try:
                    nome_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    nome_text = nome_element.text.strip()
                    if nome_text:
                        data['nome'] = nome_text
                        break
                except:
                    continue
            
            # Extrai endereço e telefone
            # Estratégia 1: Buscar por classes específicas
            info_selectors = [
                "div.Io6YTe.fontBodyMedium.kR99db.fdkmkc",
                "div.Io6YTe.fontBodyMedium",
                "button[data-item-id='address']",
                "div[data-item-id='address']"
            ]
            
            info_texts = []
            for selector in info_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        text = element.text.strip()
                        if text and text not in info_texts:
                            info_texts.append(text)
                except:
                    continue
            
            # Processa os textos coletados
            for text in info_texts:
                # Verifica se é telefone (padrões: (XX) XXXX-XXXX, (XX) XXXXX-XXXX, etc.)
                phone_pattern = r'\(?\d{2}\)?\s?\d{4,5}[-.\s]?\d{4}'
                if re.search(phone_pattern, text) and len(text) <= 20:
                    if data['telefone'] == 'Não informado':
                        data['telefone'] = text
                # Verifica se é endereço (contém palavras comuns ou padrões de endereço)
                elif any(word in text.lower() for word in [
                    'rua', 'av', 'avenida', 'estrada', 'rodovia', 'praça', 
                    'bairro', 'centro', 'distrito', 'vila', 'jardim',
                    '- pr', '- sp', '- mg', '- rj', '- sc', '- rs', '- ba',
                    '- go', '- pe', '- ce', '- df', '- es', '- mt', '- ms',
                    '- pa', '- pb', '- al', '- se', '- to', '- pi', '- ma',
                    '- rn', '- ap', '- ac', '- rr', '- ro', '- am'
                ]) or re.search(r'\d{5}-?\d{3}', text):  # CEP
                    if data['endereco'] == 'Não informado':
                        data['endereco'] = text
            
            # Extrai avaliação e número de avaliações
            # Busca pelo div com classe F7nice que contém as avaliações
            rating_selectors = [
                "div.F7nice span[aria-hidden='true']",
                "div.F7nice span[aria-hidden=\"true\"]",
                "div[class*='F7nice'] span[aria-hidden='true']",
                "span[aria-hidden='true']"
            ]
            
            for selector in rating_selectors:
                try:
                    rating_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in rating_elements:
                        rating_text = element.text.strip()
                        # Verifica se é um número válido (formato: 4,8 ou 4.8)
                        if rating_text and re.match(r'^\d+[,.]?\d*$', rating_text):
                            # Normaliza para usar vírgula
                            rating_text = rating_text.replace('.', ',')
                            if data['avaliacao'] == 'Não informado':
                                data['avaliacao'] = rating_text
                                break
                    if data['avaliacao'] != 'Não informado':
                        break
                except:
                    continue
            
            # Extrai número de avaliações
            num_reviews_selectors = [
                "span[aria-label*='avaliações']",
                "span[aria-label*='avaliação']",
                "div.F7nice span[aria-label*='avaliações']",
                "div.F7nice span[aria-label*='avaliação']"
            ]
            
            for selector in num_reviews_selectors:
                try:
                    review_elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in review_elements:
                        aria_label = element.get_attribute('aria-label')
                        if aria_label:
                            # Extrai o número de avaliações do aria-label (ex: "57 avaliações")
                            match = re.search(r'(\d+)', aria_label)
                            if match:
                                if data['num_avaliacoes'] == 'Não informado':
                                    data['num_avaliacoes'] = match.group(1)
                                    break
                    if data['num_avaliacoes'] != 'Não informado':
                        break
                except:
                    continue
            
            # Se não encontrou pelo aria-label, tenta extrair do texto dentro do span
            if data['num_avaliacoes'] == 'Não informado':
                try:
                    # Busca por padrão (57) dentro de spans
                    all_spans = self.driver.find_elements(By.CSS_SELECTOR, "div.F7nice span")
                    for span in all_spans:
                        text = span.text.strip()
                        # Procura por padrão (número) entre parênteses
                        match = re.search(r'\((\d+)\)', text)
                        if match:
                            if data['num_avaliacoes'] == 'Não informado':
                                data['num_avaliacoes'] = match.group(1)
                                break
                except:
                    pass
            
            return data
            
        except Exception as e:
            print(f"Erro ao extrair dados do negócio: {e}")
            return None
    
    def scrape_nicho_cidade(self, nicho: str, cidade: str) -> List[Dict[str, str]]:
        """
        Realiza scraping de um nicho em uma cidade específica.
        
        Args:
            nicho: Nicho de mercado (ex: "auto peças")
            cidade: Nome da cidade (ex: "Cambé")
            
        Returns:
            Lista de dicionários com os dados coletados
        """
        results_data = []
        query = f"{nicho} em {cidade}"
        
        print(f"🔍 Buscando: {query}")
        
        # Realiza a busca
        if not self.search(query):
            return results_data
        
        # Obtém todos os links de resultados
        results_links = self.get_results_links()
        
        if not results_links:
            print(f"⚠️ Nenhum resultado encontrado para: {query}")
            return results_data
        
        print(f"📊 Encontrados {len(results_links)} resultados")
        
        # Itera sobre cada resultado
        for idx, link in enumerate(results_links, 1):
            try:
                print(f"  [{idx}/{len(results_links)}] Processando resultado...")
                
                # Scroll para o elemento ficar visível
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", link)
                time.sleep(random.uniform(1, 2))
                
                # Clica no resultado
                try:
                    link.click()
                except ElementClickInterceptedException:
                    # Tenta com JavaScript
                    self.driver.execute_script("arguments[0].click();", link)
                
                time.sleep(random.uniform(2, 3))
                
                # Extrai os dados
                business_data = self.extract_business_data()
                
                if business_data:
                    business_data['nicho'] = nicho
                    business_data['cidade'] = cidade
                    results_data.append(business_data)
                    print(f"    ✓ {business_data['nome']}")
                
                # Pausa aleatória entre requisições
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(f"    ✗ Erro ao processar resultado {idx}: {e}")
                continue
        
        return results_data
    
    def close(self):
        """Fecha o navegador."""
        if self.driver:
            self.driver.quit()
            self.driver = None

