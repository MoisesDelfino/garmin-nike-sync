"""
Nike Run Club API Client
Cliente não-oficial para Nike Run Club API (reverse engineered)
"""

import requests
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from loguru import logger
import json
import base64
import uuid


class NikeClient:
    """Cliente para interagir com Nike Run Club API"""
    
    # Endpoints da Nike API (reverse engineered)
    BASE_URL = "https://api.nike.com"
    AUTH_URL = "https://unite.nike.com"
    ACTIVITIES_URL = f"{BASE_URL}/sport/v3/me/activities"
    ACTIVITY_URL = f"{BASE_URL}/sport/v3/me/activity"
    
    def __init__(self, access_token: str):
        """
        Inicializa o cliente Nike
        
        Args:
            access_token: Token de acesso Nike (Bearer token)
        """
        self.access_token = access_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'User-Agent': 'Nike/5.44.0 (iPhone; iOS 15.0; Scale/3.00)',
            'Accept': 'application/json',
        })
    
    @staticmethod
    def authenticate(email: str, password: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Autentica no Nike.com e obtém access token automaticamente
        Usa múltiplos métodos de fallback para garantir sucesso
        
        Args:
            email: Email da conta Nike
            password: Senha da conta Nike
            
        Returns:
            Tupla (sucesso, access_token, mensagem_erro)
        """
        try:
            logger.info(f"Autenticando no Nike com email: {email}")
            
            session = requests.Session()
            
            # Método 1: Nike Unite API (mobile app)
            try:
                headers = {
                    'User-Agent': 'Nike/5.44.0 (iPhone; iOS 16.0; Scale/3.00)',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Accept-Language': 'en-US',
                }
                
                # Endpoint correto do Nike Unite
                auth_url = "https://unite.nike.com/login"
                
                payload = {
                    'client_id': 'HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH',
                    'ux_id': 'com.nike.sport.running.ios',
                    'grant_type': 'password',
                    'username': email,
                    'password': password,
                }
                
                response = session.post(auth_url, json=payload, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get('access_token')
                    if access_token:
                        logger.success("Nike authentication successful (Method 1)")
                        return True, access_token, None
            except Exception as e:
                logger.debug(f"Method 1 failed: {e}")
            
            # Método 2: OAuth2 Password Flow
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15',
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'Accept': 'application/json',
                }
                
                auth_url = "https://unite.nike.com/loginWithSetCookie"
                
                payload = {
                    'client_id': 'HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH',
                    'ux_id': 'com.nike.commerce.nikedotcom.web',
                    'grant_type': 'password',
                    'username': email,
                    'password': password,
                    'keepMeLoggedIn': 'true'
                }
                
                response = session.post(auth_url, data=payload, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get('access_token')
                    if access_token:
                        logger.success("Nike authentication successful (Method 2)")
                        return True, access_token, None
            except Exception as e:
                logger.debug(f"Method 2 failed: {e}")
            
            # Método 3: Login web + extract cookies
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Content-Type': 'application/json',
                    'Accept': 'application/json',
                }
                
                # CSRF token
                csrf_response = session.get('https://www.nike.com', headers=headers, timeout=10)
                
                auth_url = "https://unite.nike.com/login?appVersion=968&experienceVersion=1202&uxId=com.nike.commerce.nikedotcom.web&locale=en_US&backendEnvironment=identity&browser=Google%20Inc.&os=undefined&mobile=false&native=false&visit=1&visitor=undefined"
                
                payload = {
                    'username': email,
                    'password': password,
                    'keepMeLoggedIn': True,
                    'client_id': 'HlHa2Cje3ctlaOqnxvgZXNaAs7T9nAuH',
                    'ux_id': 'com.nike.commerce.nikedotcom.web',
                    'grant_type': 'password'
                }
                
                response = session.post(auth_url, json=payload, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    access_token = data.get('access_token')
                    
                    # Tenta também nos cookies
                    if not access_token:
                        for cookie in session.cookies:
                            if 'access_token' in cookie.name.lower() or 'bearer' in cookie.name.lower():
                                access_token = cookie.value
                                break
                    
                    if access_token:
                        logger.success("Nike authentication successful (Method 3)")
                        return True, access_token, None
            except Exception as e:
                logger.debug(f"Method 3 failed: {e}")
            
            # Se chegou aqui, todos os métodos falharam
            logger.error("All Nike authentication methods failed")
            return False, None, "Não foi possível autenticar. A API Nike pode estar temporariamente indisponível ou suas credenciais estão incorretas."
        
        except requests.exceptions.Timeout:
            logger.error("Timeout connecting to Nike")
            return False, None, "Timeout na conexão com Nike.com"
        
        except requests.exceptions.ConnectionError:
            logger.error("Connection error to Nike")
            return False, None, "Erro de conexão com Nike.com"
        
        except Exception as e:
            logger.error(f"Unexpected error in Nike authentication: {e}")
            return False, None, f"Erro inesperado: {str(e)}"
            logger.error(f"Erro inesperado na autenticação Nike: {e}")
            return False, None, f"Erro inesperado: {str(e)}"
        
    def test_connection(self) -> bool:
        """
        Testa a conexão e validade do token
        
        Returns:
            True se conectado com sucesso
        """
        try:
            logger.info("Testando conexão com Nike Run Club...")
            response = self.session.get(
                f"{self.ACTIVITIES_URL}",
                params={'limit': 1},
                timeout=15
            )
            
            # Verifica Content-Type
            content_type = response.headers.get('Content-Type', '')
            
            if 'html' in content_type.lower():
                logger.error("❌ Nike retornou HTML em vez de JSON - Token inválido ou expirado")
                logger.error(f"Status: {response.status_code}")
                logger.error("O token Nike precisa ser renovado pelo administrador")
                return False
            
            if response.status_code == 401:
                logger.error("❌ Token Nike não autorizado (401) - Token inválido ou expirado")
                return False
            
            if response.status_code == 403:
                logger.error("❌ Acesso negado pela Nike (403) - Token pode estar bloqueado")
                return False
            
            if response.status_code == 200:
                try:
                    # Tenta parsear JSON para garantir que é válido
                    data = response.json()
                    logger.success("✓ Conectado ao Nike Run Club com sucesso")
                    return True
                except ValueError as e:
                    logger.error(f"❌ Nike retornou resposta inválida: {e}")
                    logger.error(f"Content-Type: {content_type}")
                    logger.error("Token Nike pode estar corrompido ou expirado")
                    return False
            else:
                logger.error(f"❌ Falha na conexão: Status {response.status_code}")
                logger.debug(f"Response: {response.text[:200]}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ Timeout ao conectar com Nike API")
            return False
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com Nike: {type(e).__name__}: {e}")
            return False
    
    def get_activities(self, start_date: Optional[datetime] = None,
                       limit: int = 100) -> List[Dict]:
        """
        Busca atividades do Nike Run Club
        
        Args:
            start_date: Data inicial (padrão: últimas 100 atividades)
            limit: Número máximo de atividades
            
        Returns:
            Lista de atividades
        """
        try:
            logger.info(f"Buscando atividades do Nike Run Club (limit: {limit})")
            
            params = {
                'limit': limit,
                'offset': 0
            }
            
            response = self.session.get(self.ACTIVITIES_URL, params=params, timeout=15)
            
            # Verifica Content-Type
            content_type = response.headers.get('Content-Type', '')
            
            if 'html' in content_type.lower():
                logger.error("Nike retornou HTML - Token inválido ou expirado")
                raise Exception("Token Nike inválido. A API retornou HTML em vez de JSON. Token precisa ser renovado.")
            
            if response.status_code == 401:
                logger.error("Token Nike não autorizado (401)")
                raise Exception("Token Nike expirou ou é inválido. Entre em contato com o administrador.")
            
            if response.status_code == 403:
                logger.error("Acesso negado pela Nike (403)")
                raise Exception("Token Nike bloqueado. Entre em contato com o administrador.")
            
            if response.status_code != 200:
                logger.error(f"Erro ao buscar atividades Nike: {response.status_code}")
                raise Exception(f"Erro ao buscar atividades Nike: Status {response.status_code}")
            
            try:
                data = response.json()
            except ValueError as e:
                logger.error(f"Resposta não é JSON válido: {e}")
                logger.error(f"Content-Type: {content_type}")
                raise Exception("Nike retornou resposta inválida. Token pode estar corrompido.")
            
            activities = data.get('activities', [])
            
            # Parse atividades
            parsed_activities = []
            for activity in activities:
                parsed = self._parse_activity(activity)
                
                # Filtra por data se especificada
                if start_date:
                    activity_date = datetime.fromisoformat(
                        parsed['start_time'].replace('Z', '+00:00')
                    )
                    if activity_date < start_date:
                        continue
                
                parsed_activities.append(parsed)
            
            logger.info(f"Encontradas {len(parsed_activities)} atividades Nike")
            return parsed_activities
            
        except Exception as e:
            logger.error(f"Erro ao buscar atividades Nike: {e}")
            return []
    
    def create_activity(self, activity_data: Dict) -> Optional[str]:
        """
        Cria uma nova atividade no Nike Run Club
        
        Args:
            activity_data: Dados da atividade formatados para Nike API
            
        Returns:
            ID da atividade criada ou None em caso de erro
        """
        try:
            logger.info(f"Criando atividade no Nike: {activity_data.get('name', 'Sem nome')}")
            
            # Formata dados para Nike API
            nike_payload = self._format_for_nike(activity_data)
            
            response = self.session.post(
                f"{self.ACTIVITIES_URL}",
                json=[nike_payload]  # Envia como array
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                activity_id = result.get('id')
                logger.success(f"Atividade criada com sucesso: {activity_id}")
                return activity_id
            else:
                logger.error(f"Erro ao criar atividade: {response.status_code}")
                logger.error(f"Nike response: {response.text[:500]}")
                logger.error(f"Payload enviado: {nike_payload}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao criar atividade Nike: {e}")
            return None
    
    def _parse_activity(self, activity: Dict) -> Dict:
        """
        Parse atividade Nike para formato padronizado
        
        Args:
            activity: Dados brutos da Nike
            
        Returns:
            Atividade formatada
        """
        metrics = activity.get('summaries', [])
        
        # Extrai métricas principais
        distance = 0
        duration = 0
        calories = 0
        
        for metric in metrics:
            metric_type = metric.get('metric')
            value = metric.get('value', 0)
            
            if metric_type == 'distance':
                distance = value  # em metros
            elif metric_type == 'duration':
                duration = value  # em segundos
            elif metric_type == 'calories':
                calories = value
        
        return {
            'id': activity.get('id'),
            'name': activity.get('tags', {}).get('com.nike.name', 'Corrida'),
            'type': activity.get('type', 'run'),
            'start_time': activity.get('start_epoch_ms'),
            'end_time': activity.get('end_epoch_ms'),
            'distance': distance,
            'duration': duration,
            'calories': calories,
            'raw_data': activity
        }
    
    def _format_for_nike(self, garmin_activity: Dict) -> Dict:
        """
        Formata atividade do Garmin para formato Nike API
        
        Args:
            garmin_activity: Atividade do Garmin
            
        Returns:
            Payload formatado para Nike API
        """
        # Converte timestamp para epoch milliseconds
        start_time = datetime.fromisoformat(
            garmin_activity['start_time'].replace('Z', '+00:00')
        )
        start_epoch_ms = int(start_time.timestamp() * 1000)
        end_epoch_ms = start_epoch_ms + (garmin_activity['duration'] * 1000)
        
        # Mapeamento de tipo de atividade
        activity_type_map = {
            'running': 'run',
            'street_running': 'run',
            'track_running': 'run',
            'trail_running': 'run',
            'treadmill_running': 'run',
            'walking': 'walk'
        }
        
        nike_type = activity_type_map.get(garmin_activity['type'], 'run')
        
        # Gera ID único para a atividade
        activity_id = str(uuid.uuid4())
        
        # Monta payload Nike
        payload = {
            'id': activity_id,
            'type': nike_type,
            'start_epoch_ms': start_epoch_ms,
            'end_epoch_ms': end_epoch_ms,
            'app_id': 'garmin_sync',
            'metric_type': 'distance',
            'summaries': [
                {
                    'metric': 'distance',
                    'value': garmin_activity['distance'],
                    'unit': 'METER'
                },
                {
                    'metric': 'duration',
                    'value': garmin_activity['duration'],
                    'unit': 'SECOND'
                },
                {
                    'metric': 'calories',
                    'value': garmin_activity.get('calories', 0),
                    'unit': 'CALORIE'
                }
            ],
            'tags': {
                'com.nike.name': garmin_activity.get('name', 'Corrida')
            }
        }
        
        # Adiciona métricas extras se disponíveis
        if garmin_activity.get('average_speed'):
            payload['summaries'].append({
                'metric': 'speed',
                'value': garmin_activity['average_speed'],
                'unit': 'METER_PER_SECOND'
            })
        
        if garmin_activity.get('average_hr'):
            payload['summaries'].append({
                'metric': 'heart_rate',
                'value': garmin_activity['average_hr'],
                'unit': 'BPM'
            })
        
        if garmin_activity.get('elevation_gain'):
            payload['summaries'].append({
                'metric': 'ascent',
                'value': garmin_activity['elevation_gain'],
                'unit': 'METER'
            })
        
        return payload
    
    def find_duplicate(self, garmin_activity: Dict, 
                      time_tolerance_seconds: int = 300,
                      distance_tolerance_meters: int = 50) -> Optional[str]:
        """
        Busca por atividade duplicada no Nike baseada em data/hora e distância
        
        Args:
            garmin_activity: Atividade do Garmin para comparar
            time_tolerance_seconds: Tolerância de tempo (padrão: 5 minutos)
            distance_tolerance_meters: Tolerância de distância (padrão: 50m)
            
        Returns:
            ID da atividade Nike duplicada ou None
        """
        try:
            # Busca atividades Nike próximas da data
            nike_activities = self.get_activities(limit=50)
            
            garmin_time = datetime.fromisoformat(
                garmin_activity['start_time'].replace('Z', '+00:00')
            )
            garmin_distance = garmin_activity['distance']
            
            for nike_activity in nike_activities:
                # Compara tempo
                nike_time = datetime.fromtimestamp(
                    nike_activity['start_time'] / 1000
                )
                time_diff = abs((garmin_time - nike_time).total_seconds())
                
                if time_diff <= time_tolerance_seconds:
                    # Compara distância
                    distance_diff = abs(garmin_distance - nike_activity['distance'])
                    
                    if distance_diff <= distance_tolerance_meters:
                        logger.info(
                            f"Atividade duplicada encontrada: Nike ID {nike_activity['id']}"
                        )
                        return nike_activity['id']
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar duplicatas: {e}")
            return None
