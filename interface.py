"""
Módulo de interface gráfica do usuário usando CustomTkinter.
"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from typing import List, Dict
import threading
import os
import time
import json
from datetime import datetime

from ibge_api import IBGEAPI
from scraper import GoogleMapsScraper


class GoogleMapsScraperGUI:
    """Interface gráfica para o scraper do Google Maps."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🗺️ Automação de Pesquisa - Google Maps")
        self.root.geometry("900x700")
        
        # Configuração do CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Variáveis
        self.estados = []
        self.municipios = []
        self.nichos = []
        self.scraper = None
        self.is_running = False
        self.all_results = []
        self.current_save_file = None  # Arquivo de salvamento da sessão atual
        
        # Garante que a pasta output existe
        self._ensure_output_dir()
        
        self._create_widgets()
        self._load_estados()
        self._load_nichos_auto()  # Tenta carregar nichos salvos automaticamente
    
    def _create_widgets(self):
        """Cria os widgets da interface."""
        
        # Frame principal
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Título
        title = ctk.CTkLabel(
            main_frame,
            text="🗺️ Automação de Pesquisa de Nicho no Google Maps",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(10, 20))
        
        # Frame de nichos
        nichos_frame = ctk.CTkFrame(main_frame)
        nichos_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(nichos_frame, text="📋 Nichos de Mercado:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        nichos_input_frame = ctk.CTkFrame(nichos_frame)
        nichos_input_frame.pack(fill="x", padx=10, pady=5)
        
        self.nicho_entry = ctk.CTkEntry(nichos_input_frame, placeholder_text="Ex: auto peças, salão de beleza...")
        self.nicho_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.add_nicho_btn = ctk.CTkButton(nichos_input_frame, text="Adicionar", command=self._add_nicho, width=100)
        self.add_nicho_btn.pack(side="left")
        
        self.nichos_listbox = tk.Listbox(nichos_frame, height=4, bg="#2b2b2b", fg="white", selectbackground="#1f6aa5")
        self.nichos_listbox.pack(fill="x", padx=10, pady=(0, 10))
        
        nichos_buttons_frame = ctk.CTkFrame(nichos_frame)
        nichos_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        remove_nicho_btn = ctk.CTkButton(nichos_buttons_frame, text="Remover Selecionado", command=self._remove_nicho)
        remove_nicho_btn.pack(side="left", padx=(0, 5))
        
        save_nichos_btn = ctk.CTkButton(nichos_buttons_frame, text="💾 Salvar Nichos", command=self._save_nichos, fg_color="#17a2b8", hover_color="#138496")
        save_nichos_btn.pack(side="left", padx=5)
        
        load_nichos_btn = ctk.CTkButton(nichos_buttons_frame, text="📂 Carregar Nichos", command=self._load_nichos, fg_color="#17a2b8", hover_color="#138496")
        load_nichos_btn.pack(side="left", padx=5)
        
        # Frame de localização
        location_frame = ctk.CTkFrame(main_frame)
        location_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(location_frame, text="📍 Localização:", font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(10, 5))
        
        # Estado
        estado_frame = ctk.CTkFrame(location_frame)
        estado_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(estado_frame, text="Estado:").pack(side="left", padx=5)
        self.estado_combo = ctk.CTkComboBox(estado_frame, values=[], command=self._on_estado_selected, width=200)
        self.estado_combo.pack(side="left", padx=5)
        
        # Cidade
        cidade_frame = ctk.CTkFrame(location_frame)
        cidade_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(cidade_frame, text="Cidade:").pack(side="left", padx=5)
        self.cidade_combo = ctk.CTkComboBox(cidade_frame, values=[], width=200)
        self.cidade_combo.pack(side="left", padx=5)
        
        self.add_cidade_btn = ctk.CTkButton(cidade_frame, text="Adicionar Cidade", command=self._add_cidade)
        self.add_cidade_btn.pack(side="left", padx=5)
        
        self.select_all_cidades_btn = ctk.CTkButton(cidade_frame, text="Selecionar Todas", command=self._select_all_cidades, fg_color="#28a745", hover_color="#218838")
        self.select_all_cidades_btn.pack(side="left", padx=5)
        
        self.select_all_brasil_btn = ctk.CTkButton(cidade_frame, text="Selecionar Todo Brasil", command=self._select_all_brasil, fg_color="#ff6b35", hover_color="#e55a2b")
        self.select_all_brasil_btn.pack(side="left", padx=5)
        
        # Lista de cidades selecionadas
        ctk.CTkLabel(location_frame, text="Cidades Selecionadas:", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(10, 5))
        
        self.cidades_listbox = tk.Listbox(location_frame, height=8, bg="#2b2b2b", fg="white", selectbackground="#1f6aa5")
        self.cidades_listbox.pack(fill="x", padx=10, pady=(0, 10))
        
        cidades_buttons_frame = ctk.CTkFrame(location_frame)
        cidades_buttons_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        remove_cidade_btn = ctk.CTkButton(cidades_buttons_frame, text="Remover Selecionada", command=self._remove_cidade)
        remove_cidade_btn.pack(side="left", padx=(0, 5))
        
        remove_all_cidades_btn = ctk.CTkButton(cidades_buttons_frame, text="Remover Todas", command=self._remove_all_cidades, fg_color="#dc3545", hover_color="#c82333")
        remove_all_cidades_btn.pack(side="left", padx=5)
        
        # Frame de controle
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", padx=10, pady=5)
        
        self.start_btn = ctk.CTkButton(
            control_frame,
            text="▶️ Iniciar Busca",
            command=self._start_scraping,
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        )
        self.start_btn.pack(side="left", padx=10, pady=10)
        
        self.stop_btn = ctk.CTkButton(
            control_frame,
            text="⏹️ Parar",
            command=self._stop_scraping,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#dc3545",
            hover_color="#c82333",
            state="disabled"
        )
        self.stop_btn.pack(side="left", padx=10, pady=10)
        
        self.export_btn = ctk.CTkButton(
            control_frame,
            text="📥 Exportar Resultados",
            command=self._export_results,
            font=ctk.CTkFont(size=14),
            height=40,
            state="disabled"
        )
        self.export_btn.pack(side="left", padx=10, pady=10)
        
        # Barra de progresso
        self.progress = ctk.CTkProgressBar(main_frame)
        self.progress.pack(fill="x", padx=10, pady=5)
        self.progress.set(0)
        
        # Status
        self.status_label = ctk.CTkLabel(main_frame, text="⏳ Pronto para iniciar", font=ctk.CTkFont(size=12))
        self.status_label.pack(pady=10)
    
    def _load_estados(self):
        """Carrega os estados do IBGE."""
        self.status_label.configure(text="⏳ Carregando estados...")
        self.root.update()
        
        self.estados = IBGEAPI.get_estados()
        estado_values = [f"{estado['sigla']} - {estado['nome']}" for estado in self.estados]
        self.estado_combo.configure(values=estado_values)
        
        if estado_values:
            self.estado_combo.set(estado_values[0])
            self._on_estado_selected(estado_values[0])
        
        self.status_label.configure(text="✅ Estados carregados")
    
    def _on_estado_selected(self, value):
        """Callback quando um estado é selecionado."""
        if not value:
            return
        
        sigla = value.split(" - ")[0]
        self.status_label.configure(text=f"⏳ Carregando municípios de {sigla}...")
        self.root.update()
        
        self.municipios = IBGEAPI.get_municipios_por_estado(sigla)
        cidade_values = [municipio['nome'] for municipio in self.municipios]
        self.cidade_combo.configure(values=cidade_values)
        
        if cidade_values:
            self.cidade_combo.set(cidade_values[0])
        
        self.status_label.configure(text=f"✅ {len(cidade_values)} municípios carregados")
    
    def _add_nicho(self):
        """Adiciona um nicho à lista."""
        nicho = self.nicho_entry.get().strip()
        if nicho and nicho not in self.nichos:
            self.nichos.append(nicho)
            self.nichos_listbox.insert(tk.END, nicho)
            self.nicho_entry.delete(0, tk.END)
            # Salva automaticamente após adicionar
            self._save_nichos_auto()
    
    def _remove_nicho(self):
        """Remove o nicho selecionado."""
        selection = self.nichos_listbox.curselection()
        if selection:
            idx = selection[0]
            self.nichos_listbox.delete(idx)
            self.nichos.pop(idx)
            # Salva automaticamente após remover
            self._save_nichos_auto()
    
    def _save_nichos(self):
        """Salva os nichos em um arquivo JSON."""
        if not self.nichos:
            messagebox.showwarning("Aviso", "Não há nichos para salvar!")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="nichos.json"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.nichos, f, ensure_ascii=False, indent=2)
            
            messagebox.showinfo("Sucesso", f"Nichos salvos com sucesso!\n{len(self.nichos)} nicho(s) salvos em:\n{file_path}")
            self.status_label.configure(text=f"✅ Nichos salvos: {file_path}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar nichos: {e}")
    
    def _save_nichos_auto(self):
        """Salva automaticamente os nichos no arquivo padrão."""
        try:
            # Garante que a pasta output existe
            self._ensure_output_dir()
            
            file_path = os.path.join("output", "nichos.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.nichos, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # Não mostra erro para salvamento automático
            pass
    
    def _load_nichos(self):
        """Carrega nichos de um arquivo JSON."""
        file_path = filedialog.askopenfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            initialfile="nichos.json"
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                nichos_carregados = json.load(f)
            
            if not isinstance(nichos_carregados, list):
                messagebox.showerror("Erro", "Formato de arquivo inválido! O arquivo deve conter uma lista de nichos.")
                return
            
            # Limpa a lista atual
            self.nichos_listbox.delete(0, tk.END)
            self.nichos = []
            
            # Adiciona os nichos carregados
            for nicho in nichos_carregados:
                if nicho and nicho.strip() and nicho not in self.nichos:
                    self.nichos.append(nicho.strip())
                    self.nichos_listbox.insert(tk.END, nicho.strip())
            
            messagebox.showinfo("Sucesso", f"{len(self.nichos)} nicho(s) carregado(s) com sucesso!")
            self.status_label.configure(text=f"✅ {len(self.nichos)} nichos carregados")
            
            # Salva automaticamente após carregar
            self._save_nichos_auto()
            
        except FileNotFoundError:
            messagebox.showerror("Erro", "Arquivo não encontrado!")
        except json.JSONDecodeError:
            messagebox.showerror("Erro", "Erro ao ler o arquivo JSON! Verifique se o arquivo está no formato correto.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar nichos: {e}")
    
    def _load_nichos_auto(self):
        """Carrega automaticamente os nichos do arquivo padrão, se existir."""
        try:
            file_path = os.path.join("output", "nichos.json")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    nichos_carregados = json.load(f)
                
                if isinstance(nichos_carregados, list):
                    for nicho in nichos_carregados:
                        if nicho and nicho.strip() and nicho not in self.nichos:
                            self.nichos.append(nicho.strip())
                            self.nichos_listbox.insert(tk.END, nicho.strip())
        except Exception:
            # Ignora erros no carregamento automático
            pass
    
    def _ensure_output_dir(self):
        """Garante que a pasta output existe."""
        output_dir = os.path.abspath("output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def _add_cidade(self):
        """Adiciona uma cidade à lista."""
        cidade = self.cidade_combo.get().strip()
        if cidade and cidade not in self.cidades_listbox.get(0, tk.END):
            self.cidades_listbox.insert(tk.END, cidade)
    
    def _remove_cidade(self):
        """Remove a cidade selecionada."""
        selection = self.cidades_listbox.curselection()
        if selection:
            self.cidades_listbox.delete(selection[0])
        else:
            messagebox.showwarning("Aviso", "Selecione uma cidade para remover!")
    
    def _remove_all_cidades(self):
        """Remove todas as cidades selecionadas."""
        total = self.cidades_listbox.size()
        if total == 0:
            messagebox.showinfo("Info", "Não há cidades para remover.")
            return
        
        resposta = messagebox.askyesno(
            "Confirmar Remoção",
            f"Deseja remover todas as {total} cidade(s) selecionada(s)?",
            icon="question"
        )
        
        if resposta:
            self.cidades_listbox.delete(0, tk.END)
            self.status_label.configure(text="✅ Todas as cidades foram removidas")
    
    def _select_all_cidades(self):
        """Seleciona todas as cidades do estado atual."""
        if not self.municipios:
            messagebox.showwarning("Aviso", "Nenhuma cidade disponível! Selecione um estado primeiro.")
            return
        
        # Limpa a lista atual
        self.cidades_listbox.delete(0, tk.END)
        
        # Adiciona todas as cidades
        for municipio in self.municipios:
            cidade = municipio['nome']
            if cidade not in self.cidades_listbox.get(0, tk.END):
                self.cidades_listbox.insert(tk.END, cidade)
        
        self.status_label.configure(text=f"✅ {len(self.municipios)} cidades selecionadas")
    
    def _select_all_brasil(self):
        """Seleciona todas as cidades do Brasil."""
        # Confirmação antes de carregar todas as cidades (são muitas!)
        resposta = messagebox.askyesno(
            "Confirmar Seleção",
            "Isso irá selecionar TODAS as cidades do Brasil (~5.500+ cidades).\n\n"
            "Isso pode demorar alguns segundos para carregar.\n\n"
            "Deseja continuar?",
            icon="question"
        )
        
        if not resposta:
            return
        
        # Atualiza status
        self.status_label.configure(text="⏳ Carregando todas as cidades do Brasil...")
        self.root.update()
        
        # Desabilita botões durante o carregamento
        self.select_all_brasil_btn.configure(state="disabled")
        self.select_all_cidades_btn.configure(state="disabled")
        self.add_cidade_btn.configure(state="disabled")
        
        try:
            # Busca todas as cidades do Brasil
            todas_cidades = IBGEAPI.get_todas_cidades_brasil()
            
            if not todas_cidades:
                messagebox.showerror("Erro", "Não foi possível carregar as cidades do Brasil. Verifique sua conexão com a internet.")
                self.status_label.configure(text="❌ Erro ao carregar cidades")
                return
            
            # Limpa a lista atual
            self.cidades_listbox.delete(0, tk.END)
            
            # Atualiza status durante a inserção
            self.status_label.configure(text=f"⏳ Adicionando {len(todas_cidades)} cidades...")
            self.root.update()
            
            # Adiciona todas as cidades
            for municipio in todas_cidades:
                cidade = municipio['nome']
                self.cidades_listbox.insert(tk.END, cidade)
                # Atualiza a cada 100 cidades para não travar a interface
                if self.cidades_listbox.size() % 100 == 0:
                    self.root.update()
            
            self.status_label.configure(text=f"✅ {len(todas_cidades)} cidades do Brasil selecionadas")
            messagebox.showinfo(
                "Sucesso",
                f"Todas as cidades do Brasil foram selecionadas!\n\n"
                f"Total: {len(todas_cidades)} cidades"
            )
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar todas as cidades: {e}")
            self.status_label.configure(text="❌ Erro ao carregar cidades")
        finally:
            # Reabilita botões
            self.select_all_brasil_btn.configure(state="normal")
            self.select_all_cidades_btn.configure(state="normal")
            self.add_cidade_btn.configure(state="normal")
    
    def _validate_inputs(self) -> bool:
        """Valida se os inputs estão preenchidos."""
        if not self.nichos:
            messagebox.showwarning("Aviso", "Adicione pelo menos um nicho de mercado!")
            return False
        
        if not self.cidades_listbox.get(0, tk.END):
            messagebox.showwarning("Aviso", "Adicione pelo menos uma cidade!")
            return False
        
        return True
    
    def _start_scraping(self):
        """Inicia o processo de scraping em uma thread separada."""
        if not self._validate_inputs():
            return
        
        self.is_running = True
        self.all_results = []
        self.current_save_file = None  # Reseta o arquivo de salvamento
        
        # Garante que a pasta output existe
        self._ensure_output_dir()
        
        # Cria o arquivo de salvamento único para esta sessão
        output_dir = os.path.abspath("output")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.current_save_file = os.path.join(output_dir, f"resultados_{timestamp}.xlsx")
        
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.export_btn.configure(state="disabled")
        
        # Inicia em thread separada
        thread = threading.Thread(target=self._scraping_worker, daemon=True)
        thread.start()
    
    def _scraping_worker(self):
        """Worker que executa o scraping em thread separada."""
        try:
            nichos = self.nichos.copy()
            cidades = list(self.cidades_listbox.get(0, tk.END))
            
            total = len(nichos) * len(cidades)
            current = 0
            
            for nicho in nichos:
                if not self.is_running:
                    break
                
                for cidade in cidades:
                    if not self.is_running:
                        break
                    
                    # Abre o navegador para esta busca
                    self.scraper = GoogleMapsScraper(headless=False)
                    self.scraper.open_maps()
                    
                    self.root.after(0, lambda n=nicho, c=cidade: 
                        self.status_label.configure(text=f"🔍 Buscando: {n} em {c}"))
                    
                    try:
                        results = self.scraper.scrape_nicho_cidade(nicho, cidade)
                        self.all_results.extend(results)
                    except Exception as e:
                        print(f"Erro ao buscar {nicho} em {cidade}: {e}")
                    
                    # Fecha o navegador após cada busca
                    if self.scraper:
                        self.scraper.close()
                        self.scraper = None
                    
                    # Salva após cada cidade processada
                    self._auto_save_results()
                    
                    current += 1
                    progress = current / total if total > 0 else 0
                    self.root.after(0, lambda p=progress: self.progress.set(p))
                    
                    # Pequena pausa entre buscas para não sobrecarregar
                    time.sleep(2)
            
            if self.is_running:
                # Salva uma última vez ao final (caso tenha algo pendente)
                self._auto_save_results()
                
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"✅ Coleta concluída! {len(self.all_results)} resultados encontrados. Arquivo salvo: {self.current_save_file}"
                ))
                self.root.after(0, lambda: self.export_btn.configure(state="normal"))
            else:
                # Se foi parado, salva o que tem
                self._auto_save_results()
                self.root.after(0, lambda: self.status_label.configure(
                    text=f"⏸️ Processo interrompido. {len(self.all_results)} resultados salvos em: {self.current_save_file}"
                ))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro durante o scraping: {e}"))
            self.root.after(0, lambda: self.status_label.configure(text="❌ Erro durante a coleta"))
        finally:
            # Garante que o navegador está fechado
            if self.scraper:
                try:
                    self.scraper.close()
                except:
                    pass
                self.scraper = None
            
            self.is_running = False
            self.root.after(0, lambda: self.start_btn.configure(state="normal"))
            self.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
    
    def _stop_scraping(self):
        """Para o processo de scraping."""
        self.is_running = False
        
        if self.scraper:
            try:
                self.scraper.close()
            except:
                pass
            self.scraper = None
        
        self.root.after(0, lambda: self.status_label.configure(text="⏸️ Processo interrompido pelo usuário"))
    
    def _auto_save_results(self):
        """Salva automaticamente os resultados na pasta output/ (incremental)."""
        if not self.all_results:
            return  # Não salva se não houver resultados
        
        try:
            import pandas as pd
            
            # Usa o arquivo da sessão atual
            if not self.current_save_file:
                # Garante que a pasta output existe
                self._ensure_output_dir()
                
                # Cria arquivo se não existir
                output_dir = os.path.abspath("output")
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                self.current_save_file = os.path.join(output_dir, f"resultados_{timestamp}.xlsx")
            
            df = pd.DataFrame(self.all_results)
            
            # Verifica se todas as colunas existem
            columns_order = ['nicho', 'cidade', 'nome', 'endereco', 'telefone', 'avaliacao', 'num_avaliacoes']
            missing_cols = [col for col in columns_order if col not in df.columns]
            if missing_cols:
                # Adiciona colunas faltantes com valores vazios
                for col in missing_cols:
                    df[col] = 'Não informado'
            
            # Reordena colunas
            df = df[columns_order]
            
            # Renomeia colunas
            df.columns = ['Nicho', 'Cidade', 'Nome da Empresa', 'Endereço', 'Telefone', 'Avaliação', 'Nº de Avaliações']
            
            # Salva no arquivo da sessão (sobrescreve com todos os dados acumulados)
            df.to_excel(self.current_save_file, index=False, engine='openpyxl')
            print(f"💾 Arquivo atualizado: {self.current_save_file} ({len(df)} registros)")
            
        except Exception as e:
            import traceback
            print(f"❌ Erro ao salvar automaticamente: {e}")
            traceback.print_exc()
    
    def _export_results(self):
        """Exporta os resultados para Excel ou CSV (com opção de escolher local)."""
        if not self.all_results:
            messagebox.showwarning("Aviso", "Nenhum resultado para exportar!")
            return
        
        # Garante que a pasta output existe
        self._ensure_output_dir()
        
        # Define o diretório inicial como a pasta output/
        initial_dir = os.path.abspath("output")
        
        # Gera nome padrão com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_filename = f"resultados_{timestamp}.xlsx"
        
        # Pergunta o formato e local
        file_path = filedialog.asksaveasfilename(
            initialdir=initial_dir,
            initialfile=default_filename,
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("CSV files", "*.csv")]
        )
        
        if not file_path:
            return
        
        try:
            import pandas as pd
            
            df = pd.DataFrame(self.all_results)
            
            # Reordena colunas
            columns_order = ['nicho', 'cidade', 'nome', 'endereco', 'telefone', 'avaliacao', 'num_avaliacoes']
            missing_cols = [col for col in columns_order if col not in df.columns]
            if missing_cols:
                # Adiciona colunas faltantes com valores vazios
                for col in missing_cols:
                    df[col] = 'Não informado'
            
            df = df[columns_order]
            
            # Renomeia colunas
            df.columns = ['Nicho', 'Cidade', 'Nome da Empresa', 'Endereço', 'Telefone', 'Avaliação', 'Nº de Avaliações']
            
            if file_path.endswith('.xlsx'):
                df.to_excel(file_path, index=False, engine='openpyxl')
            else:
                df.to_csv(file_path, index=False, encoding='utf-8-sig')
            
            messagebox.showinfo("Sucesso", f"Resultados exportados com sucesso!\n{len(self.all_results)} registros salvos em:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar resultados: {e}")

