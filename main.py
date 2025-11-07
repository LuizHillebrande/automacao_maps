"""
Arquivo principal da aplicação de automação de pesquisa no Google Maps.
"""
import customtkinter as ctk
from interface import GoogleMapsScraperGUI


def main():
    """Função principal da aplicação."""
    root = ctk.CTk()
    app = GoogleMapsScraperGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()


