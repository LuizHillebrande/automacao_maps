"""
Módulo para interagir com a API do IBGE e obter estados e municípios.
"""
import requests
from typing import List, Dict, Optional


class IBGEAPI:
    """Classe para buscar dados de estados e municípios da API do IBGE."""
    
    BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
    
    @staticmethod
    def get_estados() -> List[Dict[str, str]]:
        """
        Retorna lista de todos os estados brasileiros.
        
        Returns:
            Lista de dicionários com 'id', 'sigla' e 'nome' do estado.
        """
        try:
            url = f"{IBGEAPI.BASE_URL}/estados"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            estados = response.json()
            # Ordena por nome
            estados_ordenados = sorted(estados, key=lambda x: x['nome'])
            
            return [
                {
                    'id': estado['id'],
                    'sigla': estado['sigla'],
                    'nome': estado['nome']
                }
                for estado in estados_ordenados
            ]
        except requests.RequestException as e:
            print(f"Erro ao buscar estados: {e}")
            return []
    
    @staticmethod
    def get_municipios_por_estado(uf: str) -> List[Dict[str, str]]:
        """
        Retorna lista de municípios de um estado específico.
        
        Args:
            uf: Sigla do estado (ex: 'PR', 'SP')
            
        Returns:
            Lista de dicionários com 'id' e 'nome' do município.
        """
        try:
            url = f"{IBGEAPI.BASE_URL}/estados/{uf}/municipios"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            municipios = response.json()
            # Ordena por nome
            municipios_ordenados = sorted(municipios, key=lambda x: x['nome'])
            
            return [
                {
                    'id': municipio['id'],
                    'nome': municipio['nome']
                }
                for municipio in municipios_ordenados
            ]
        except requests.RequestException as e:
            print(f"Erro ao buscar municípios do estado {uf}: {e}")
            return []
    
    @staticmethod
    def get_todas_cidades_brasil() -> List[Dict[str, str]]:
        """
        Retorna lista de todos os municípios do Brasil.
        
        Returns:
            Lista de dicionários com 'id' e 'nome' do município.
        """
        try:
            url = f"{IBGEAPI.BASE_URL}/municipios"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            municipios = response.json()
            # Ordena por nome
            municipios_ordenados = sorted(municipios, key=lambda x: x['nome'])
            
            return [
                {
                    'id': municipio['id'],
                    'nome': municipio['nome']
                }
                for municipio in municipios_ordenados
            ]
        except requests.RequestException as e:
            print(f"Erro ao buscar todos os municípios do Brasil: {e}")
            return []

