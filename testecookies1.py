import threading
import time
import zipfile
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import tkinter as tk
from tkinter import scrolledtext
from threading import Thread, active_count

class TesteAnunciosECookiesNVCOIN:
    def __init__(self):
        self.janela = tk.Tk()
        self.janela.title("Teste de Anúncios e Cookies")
        self.threads_em_execucao = 0

        # fila de proxies (interface daqui pra baixo) . lembrar de limitar as threads 
        self.frame_proxies = tk.Frame(self.janela)
        self.frame_proxies.pack(side=tk.LEFT, padx=10, pady=10)

        # label de proxies
        self.label_proxy = tk.Label(self.frame_proxies, text="Proxy")
        self.label_proxy.grid(row=0, column=0, padx=5, pady=5)
        self.label_usuario_proxy = tk.Label(self.frame_proxies, text="Usuário")
        self.label_usuario_proxy.grid(row=0, column=1, padx=5, pady=5)
        self.label_senha_proxy = tk.Label(self.frame_proxies, text="Senha")
        self.label_senha_proxy.grid(row=0, column=2, padx=5, pady=5)

        # caixa de texto para proxies
        self.texto_proxy = scrolledtext.ScrolledText(self.frame_proxies, width=15, height=10)
        self.texto_proxy.grid(row=1, column=0, padx=5, pady=5)
        self.texto_usuario_proxy = scrolledtext.ScrolledText(self.frame_proxies, width=15, height=10)
        self.texto_usuario_proxy.grid(row=1, column=1, padx=5, pady=5)
        self.texto_senha_proxy = scrolledtext.ScrolledText(self.frame_proxies, width=15, height=10)
        self.texto_senha_proxy.grid(row=1, column=2, padx=5, pady=5)

        # botao para adicionar proxy
        self.botao_adicionar_proxy = tk.Button(self.frame_proxies, text="Adicionar Proxy", command=self.adicionar_proxy)
        self.botao_adicionar_proxy.grid(row=2, column=0, columnspan=3, padx=5, pady=5)

        # frame para URL
        self.frame_url = tk.Frame(self.janela)
        self.frame_url.pack(side=tk.LEFT, padx=10, pady=10)

        # label de threads em execução
        self.label_threads_em_execucao = tk.Label(self.frame_url, text="Threads em execução: 0", fg="cyan")
        self.label_threads_em_execucao.grid(row=0, column=0, padx=5, pady=5)

        # label do URL
        self.label_url = tk.Label(self.frame_url, text="URL")
        self.label_url.grid(row=1, column=0, padx=5, pady=5)

        # caixa de texto para URL
        self.entrada_url = tk.Entry(self.frame_url, width=30)
        self.entrada_url.grid(row=2, column=0, padx=5, pady=5)

        # selecionar threads
        self.label_threads = tk.Label(self.frame_url, text="Selecionar Thread")
        self.label_threads.grid(row=3, column=0, padx=5, pady=5)

        # opçoes de threads
        self.var_threads = tk.StringVar(self.janela)
        self.var_threads.set("1")
        self.opcao_threads = tk.OptionMenu(self.frame_url, self.var_threads, *list(range(1, 101)))
        self.opcao_threads.grid(row=4, column=0, padx=5, pady=5)

        # botão Iniciar
        self.botao_iniciar = tk.Button(self.janela, text="Iniciar", command=self.iniciar_teste)
        self.botao_iniciar.pack(side=tk.LEFT, padx=10, pady=10)

        # frame para o status das threads
        self.frame_status = tk.Frame(self.janela)
        self.frame_status.pack(side=tk.LEFT, padx=10, pady=10)

        # label para o status das threads
        self.label_status = tk.Label(self.frame_status, text="Status das Threads")
        self.label_status.grid(row=0, column=0, padx=5, pady=5)

        # caixa de texto de status
        self.texto_status = scrolledtext.ScrolledText(self.frame_status, width=30, height=10)
        self.texto_status.grid(row=1, column=0, padx=5, pady=5)

        self.janela.mainloop()
        # Daqui pra cima é a interface nao apague nada 
    # função pra adicionar proxy
    def adicionar_proxy(self):
        proxy = self.texto_proxy.get("1.0", tk.END).strip()
        usuario = self.texto_usuario_proxy.get("1.0", tk.END).strip()
        senha = self.texto_senha_proxy.get("1.0", tk.END).strip()
        if proxy and usuario and senha:
            self.texto_proxy.insert(tk.END, proxy + "\n")
            self.texto_usuario_proxy.insert(tk.END, usuario + "\n")
            self.texto_senha_proxy.insert(tk.END, senha + "\n")

    # função para iniciar o teste
    def iniciar_teste(self):
        url = self.entrada_url.get()
        numero_threads = int(self.var_threads.get())
        proxies = self.texto_proxy.get("1.0", tk.END).strip().split("\n")
        usuarios = self.texto_usuario_proxy.get("1.0", tk.END).strip().split("\n")
        senhas = self.texto_senha_proxy.get("1.0", tk.END).strip().split("\n")

        # iniciar threads
        for i in range(len(proxies)):
            thread = Thread(target=self.testar_anuncios_e_cookies, args=(url, proxies[i], usuarios[i], senhas[i], numero_threads, i + 1))
            thread.start()

        # atualizar threads em execuçao
        self.atualizar_threads_em_execucao()

    # teste de anuncios e cookies
    def testar_anuncios_e_cookies(self, url, proxy, usuario, senha, numero_threads, id_thread):
        print(f"Thread {id_thread}: Iniciando teste de anuncios e cookies")
        print(f"Thread {id_thread}: URL: {url}, Proxy: {proxy}, Usuário: {usuario}, Thread selecionada: {numero_threads}")

        # cria a extensão do proxy
        self.criar_extensao_proxy(proxy, usuario, senha, f"proxy_auth_plugin_{id_thread}.zip")

        time.sleep(1)

        # Webdriver
        opcoes_chrome = Options()
        opcoes_chrome.add_argument("--headless")
        opcoes_chrome.add_argument("--disable-gpu")
        opcoes_chrome.add_argument("--disable-dev-shm-usage")
        opcoes_chrome.add_argument("--no-sandbox")
        opcoes_chrome.add_argument(f"--load-extension=proxy_auth_plugin_{id_thread}")

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opcoes_chrome)

        try:
            driver.get(url)
            print(f"Thread {id_thread}: Webdriver iniciado com proxy {proxy}")

            # testar anuncios e cookies
            if self.verificar_anuncios(driver):
                print(f"Thread {id_thread}: Anúncio detectado com sucesso.")
            else:
                print(f"Thread {id_thread}: Anúncio não detectado.")

            if self.verificar_cookies(driver):
                print(f"Thread {id_thread}: Cookies capturados com sucesso.")
            else:
                print(f"Thread {id_thread}: Nenhum cookie detectado.")

        except Exception as e:
            print(f"Thread {id_thread}: Ocorreu um erro - {e}")
        finally:
            driver.quit()
            self.atualizar_threads_em_execucao()

    # funçao para criar a extensao do proxy (super importante nao apague isso se nao quiser problemas)
    def criar_extensao_proxy(self, proxy, usuario, senha, nome_arquivo):
        manifest_json = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": "Chrome Proxy",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            }
        }

        background_js = """
        var config = {
            mode: "fixed_servers",
            rules: {
                singleProxy: {
                    scheme: "http",
                    host: "%s",
                    port: parseInt(%s)
                },
                bypassList: ["localhost"]
            }
        };
        chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
        function callbackFn(details) {
            return {
                authCredentials: {
                    username: "%s",
                    password: "%s"
                }
            };
        }
        chrome.webRequest.onAuthRequired.addListener(
            callbackFn,
            {urls: ["<all_urls>"]},
            ['blocking']
        );
        """ % (proxy.split(':')[0], proxy.split(':')[1], usuario, senha)

        with zipfile.ZipFile(nome_arquivo, 'w') as zipf:
            zipf.writestr("manifest.json", json.dumps(manifest_json))
            zipf.writestr("background.js", background_js)

    # funçao para verificar anuncios
    def verificar_anuncios(self, driver):
        try:
            # verificar anúncios
            anuncios = driver.find_elements(By.XPATH, "//div[contains(@class, 'ad')]")
            return len(anuncios) > 0
        except Exception as e:
            print(f"Erro ao verificar anúncios: {e}")
            return False

    # função para verificar se cookies estão funcionando
    def verificar_cookies(self, driver):
        try:
            cookies = driver.get_cookies()
            return len(cookies) > 0
        except Exception as e:
            print(f"Erro ao verificar cookies: {e}")
            return False

    # função para atualizar o número de threads em execução
    def atualizar_threads_em_execucao(self):
        self.threads_em_execucao = active_count() - 1
        self.label_threads_em_execucao.config(text=f"Threads em execução: {self.threads_em_execucao}")

if __name__ == "__main__":
    TesteAnunciosECookiesNVCOIN()
