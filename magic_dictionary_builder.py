#!/usr/bin/env python3
"""
Dictionary Builder for Bug Bounty & Pentesting
Generates custom wordlists from GAU and URLFinder results
"""

import subprocess
import argparse
import sys
from urllib.parse import urlparse
import os
from pathlib import Path

class DictionaryBuilder:
    def __init__(self):
        # Extensiones a filtrar (no incluir en el diccionario)
        self.filtered_extensions = {
            'js', 'gif', 'jpg', 'jpeg', 'png', 'css', 'ttf', 'woff', 'woff2', 
            'svg', 'pdf', 'ico', 'webp', 'mp4', 'mp3', 'avi', 'mov', 'zip', 
            'rar', 'tar', 'gz', 'bz2', 'exe', 'dmg', 'iso', 'doc', 'docx', 
            'xls', 'xlsx', 'ppt', 'pptx'
        }
        
    def run_gau(self, domain):
        """Ejecuta GAU con subdominios"""
        print(f"[+] Ejecutando GAU para {domain}...")
        try:
            cmd = ['gau', '--subs', domain]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                urls = result.stdout.strip().split('\n')
                print(f"[+] GAU encontró {len(urls)} URLs")
                return [url for url in urls if url.strip()]
            else:
                print(f"[-] Error ejecutando GAU: {result.stderr}")
                return []
        except subprocess.TimeoutExpired:
            print("[-] Timeout ejecutando GAU")
            return []
        except FileNotFoundError:
            print("[-] GAU no encontrado. Instalar con: go install github.com/lc/gau/v2/cmd/gau@latest")
            return []
    
    def run_urlfinder(self, domain):
        """Ejecuta URLFinder (asumiendo que es de ProjectDiscovery - httpx o similar)"""
        print(f"[+] Ejecutando URLFinder para {domain}...")
        try:
            # Nota: Ajustar comando según la herramienta específica
            # Aquí asumo subfinder + httpx como alternativa común
            cmd1 = ['subfinder', '-d', domain, '-silent']
            cmd2 = ['httpx', '-silent']
            
            # Obtener subdominios
            result1 = subprocess.run(cmd1, capture_output=True, text=True, timeout=180)
            if result1.returncode != 0:
                print("[-] Error con subfinder, intentando solo con el dominio principal")
                subdomains = [domain]
            else:
                subdomains = result1.stdout.strip().split('\n')
                subdomains = [sub for sub in subdomains if sub.strip()]
            
            # Verificar URLs activas
            urls = []
            for subdomain in subdomains:
                if subdomain.strip():
                    urls.extend([f"http://{subdomain}", f"https://{subdomain}"])
            
            if urls:
                result2 = subprocess.run(cmd2, input='\n'.join(urls), 
                                       capture_output=True, text=True, timeout=300)
                if result2.returncode == 0:
                    active_urls = result2.stdout.strip().split('\n')
                    print(f"[+] URLFinder encontró {len(active_urls)} URLs activas")
                    return [url for url in active_urls if url.strip()]
            
            return []
            
        except subprocess.TimeoutExpired:
            print("[-] Timeout ejecutando URLFinder")
            return []
        except FileNotFoundError:
            print("[-] Herramientas no encontradas. Instalar subfinder y httpx")
            return []
    
    def extract_paths(self, urls):
        """Extrae directorios y archivos de las URLs"""
        paths = set()
        
        for url in urls:
            if not url or not url.startswith(('http://', 'https://')):
                continue
                
            try:
                parsed = urlparse(url)
                path = parsed.path
                
                if not path or path == '/':
                    continue
                
                # Dividir el path en partes
                path_parts = [part for part in path.split('/') if part]
                
                for part in path_parts:
                    if not part:
                        continue
                    
                    # Si es un archivo, verificar extensión
                    if '.' in part:
                        extension = part.split('.')[-1].lower()
                        if extension not in self.filtered_extensions:
                            paths.add(part)
                    else:
                        # Es un directorio
                        paths.add(part)
                
                # También agregar rutas parciales (directorios padre)
                current_path = ""
                for part in path_parts[:-1]:  # Excluir el último si es archivo
                    if part:
                        paths.add(part)
                        
            except Exception as e:
                print(f"[-] Error parseando URL {url}: {e}")
                continue
        
        return paths
    
    def save_dictionary(self, words, output_file):
        """Guarda el diccionario ordenado y único"""
        try:
            unique_words = sorted(set(words))
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for word in unique_words:
                    f.write(f"{word}\n")
            
            print(f"[+] Diccionario guardado en {output_file}")
            print(f"[+] Total de palabras únicas: {len(unique_words)}")
            
            return True
        except Exception as e:
            print(f"[-] Error guardando archivo: {e}")
            return False
    
    def build_dictionary(self, domain, output_file):
        """Proceso principal para construir el diccionario"""
        print(f"[+] Iniciando construcción de diccionario para {domain}")
        
        # Ejecutar herramientas
        gau_urls = self.run_gau(domain)
        urlfinder_urls = self.run_urlfinder(domain)
        
        # Combinar resultados
        all_urls = list(set(gau_urls + urlfinder_urls))
        print(f"[+] Total de URLs únicas encontradas: {len(all_urls)}")
        
        if not all_urls:
            print("[-] No se encontraron URLs. Verificar conectividad y herramientas.")
            return False
        
        # Extraer paths
        paths = self.extract_paths(all_urls)
        print(f"[+] Paths extraídos: {len(paths)}")
        
        # Guardar diccionario
        return self.save_dictionary(paths, output_file)

def main():
    parser = argparse.ArgumentParser(
        description="Generador de diccionarios personalizados para Bug Bounty y Pentesting",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=        """
Ejemplos:
  python3 dictionary_builder.py -i example.com -o wordlist.txt
  python3 dictionary_builder.py --input target.com --output custom_dict.txt

Requisitos:
  - gau: go install github.com/lc/gau/v2/cmd/gau@latest
  - urlfinder: go install -v github.com/projectdiscovery/urlfinder/cmd/urlfinder@latest
        """
    )
    
    parser.add_argument('-i', '--input', required=True,
                       help='Dominio objetivo (ej: example.com)')
    parser.add_argument('-o', '--output', required=True,
                       help='Archivo de salida para el diccionario')
    
    args = parser.parse_args()
    
    # Validar dominio
    domain = args.input.strip()
    if not domain:
        print("[-] Dominio no válido")
        sys.exit(1)
    
    # Crear instancia y construir diccionario
    builder = DictionaryBuilder()
    success = builder.build_dictionary(domain, args.output)
    
    if success:
        print(f"[+] ¡Diccionario creado exitosamente!")
        sys.exit(0)
    else:
        print("[-] Error creando el diccionario")
        sys.exit(1)

if __name__ == "__main__":
    main()
