"""
Parser de arquivos de atividades do Garmin (.fit, .tcx, .gpx)
Converte arquivos exportados manualmente do Garmin Connect para formato estruturado
"""
import io
from datetime import datetime, timezone
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from fitparse import FitFile
    HAS_FITPARSE = True
except ImportError:
    HAS_FITPARSE = False
    logger.warning("fitparse not installed - .FIT files not supported")

try:
    import gpxpy
    import gpxpy.gpx
    HAS_GPXPY = True
except ImportError:
    HAS_GPXPY = False
    logger.warning("gpxpy not installed - .GPX files not supported")

try:
    from lxml import etree
    HAS_LXML = True
except ImportError:
    HAS_LXML = False
    logger.warning("lxml not installed - .TCX files not supported")


class ActivityParser:
    """Parser unificado para arquivos de atividades"""
    
    @staticmethod
    def parse_file(file_content: bytes, filename: str) -> Dict:
        """
        Parse arquivo de atividade baseado na extensão
        
        Args:
            file_content: Conteúdo do arquivo em bytes
            filename: Nome do arquivo (usado para detectar tipo)
            
        Returns:
            Dict com dados da atividade no formato:
            {
                'type': 'run',
                'start_time': datetime,
                'duration_seconds': float,
                'distance_meters': float,
                'calories': int (opcional),
                'avg_heart_rate': int (opcional),
                'gps_data': [{'lat': float, 'lng': float, 'timestamp': datetime}, ...] (opcional)
            }
        """
        filename_lower = filename.lower()
        
        if filename_lower.endswith('.fit'):
            return ActivityParser._parse_fit(file_content)
        elif filename_lower.endswith('.gpx'):
            return ActivityParser._parse_gpx(file_content)
        elif filename_lower.endswith('.tcx'):
            return ActivityParser._parse_tcx(file_content)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {filename}")
    
    @staticmethod
    def _parse_fit(file_content: bytes) -> Dict:
        """Parse arquivo .FIT"""
        if not HAS_FITPARSE:
            raise ImportError("fitparse não instalado. Instale com: pip install fitparse")
        
        fitfile = FitFile(io.BytesIO(file_content))
        
        activity_data = {
            'type': 'run',
            'start_time': None,
            'duration_seconds': 0,
            'distance_meters': 0,
            'calories': None,
            'avg_heart_rate': None,
            'gps_data': []
        }
        
        # Processa mensagens do arquivo FIT
        for record in fitfile.get_messages('record'):
            record_data = {}
            for data in record:
                record_data[data.name] = data.value
            
            # GPS data
            if 'position_lat' in record_data and 'position_long' in record_data:
                # FIT usa semicircles, precisa converter para graus
                lat = record_data['position_lat'] * (180 / 2**31)
                lng = record_data['position_long'] * (180 / 2**31)
                
                timestamp = record_data.get('timestamp')
                if timestamp:
                    activity_data['gps_data'].append({
                        'lat': lat,
                        'lng': lng,
                        'timestamp': timestamp
                    })
        
        # Dados da sessão (resumo)
        for session in fitfile.get_messages('session'):
            for data in session:
                if data.name == 'start_time':
                    activity_data['start_time'] = data.value
                elif data.name == 'total_distance':
                    activity_data['distance_meters'] = data.value
                elif data.name == 'total_timer_time':
                    activity_data['duration_seconds'] = data.value
                elif data.name == 'total_calories':
                    activity_data['calories'] = int(data.value)
                elif data.name == 'avg_heart_rate':
                    activity_data['avg_heart_rate'] = int(data.value)
                elif data.name == 'sport':
                    # Mapeia tipo de esporte
                    sport_map = {
                        'running': 'run',
                        'cycling': 'cycle',
                        'walking': 'walk'
                    }
                    activity_data['type'] = sport_map.get(str(data.value).lower(), 'run')
        
        if not activity_data['start_time']:
            raise ValueError("Arquivo FIT não contém data/hora de início")
        
        return activity_data
    
    @staticmethod
    def _parse_gpx(file_content: bytes) -> Dict:
        """Parse arquivo .GPX"""
        if not HAS_GPXPY:
            raise ImportError("gpxpy não instalado. Instale com: pip install gpxpy")
        
        gpx = gpxpy.parse(io.BytesIO(file_content))
        
        activity_data = {
            'type': 'run',
            'start_time': None,
            'duration_seconds': 0,
            'distance_meters': 0,
            'calories': None,
            'avg_heart_rate': None,
            'gps_data': []
        }
        
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    activity_data['gps_data'].append({
                        'lat': point.latitude,
                        'lng': point.longitude,
                        'timestamp': point.time
                    })
        
        if activity_data['gps_data']:
            activity_data['start_time'] = activity_data['gps_data'][0]['timestamp']
            
            # Calcula distância e duração
            activity_data['distance_meters'] = gpx.length_2d()
            
            start = activity_data['gps_data'][0]['timestamp']
            end = activity_data['gps_data'][-1]['timestamp']
            activity_data['duration_seconds'] = (end - start).total_seconds()
        
        if not activity_data['start_time']:
            raise ValueError("Arquivo GPX não contém pontos com timestamp")
        
        return activity_data
    
    @staticmethod
    def _parse_tcx(file_content: bytes) -> Dict:
        """Parse arquivo .TCX (Training Center XML)"""
        if not HAS_LXML:
            raise ImportError("lxml não instalado. Instale com: pip install lxml")
        
        root = etree.fromstring(file_content)
        
        # Namespace do TCX
        ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
        
        activity_data = {
            'type': 'run',
            'start_time': None,
            'duration_seconds': 0,
            'distance_meters': 0,
            'calories': None,
            'avg_heart_rate': None,
            'gps_data': []
        }
        
        # Primeira atividade
        activity = root.find('.//tcx:Activity', ns)
        if activity is None:
            raise ValueError("Arquivo TCX não contém atividades")
        
        # Tipo de esporte
        sport = activity.get('Sport', 'Running')
        sport_map = {
            'Running': 'run',
            'Biking': 'cycle',
            'Walking': 'walk'
        }
        activity_data['type'] = sport_map.get(sport, 'run')
        
        # ID (geralmente é o timestamp de início)
        id_elem = activity.find('tcx:Id', ns)
        if id_elem is not None and id_elem.text:
            activity_data['start_time'] = datetime.fromisoformat(id_elem.text.replace('Z', '+00:00'))
        
        # Lap data (pode ter múltiplos laps)
        total_distance = 0
        total_time = 0
        total_calories = 0
        heart_rates = []
        
        for lap in activity.findall('.//tcx:Lap', ns):
            # Distância
            distance_elem = lap.find('tcx:DistanceMeters', ns)
            if distance_elem is not None:
                total_distance += float(distance_elem.text)
            
            # Tempo
            time_elem = lap.find('tcx:TotalTimeSeconds', ns)
            if time_elem is not None:
                total_time += float(time_elem.text)
            
            # Calorias
            calories_elem = lap.find('tcx:Calories', ns)
            if calories_elem is not None:
                total_calories += int(calories_elem.text)
            
            # Pontos do track
            for trackpoint in lap.findall('.//tcx:Trackpoint', ns):
                timestamp_elem = trackpoint.find('tcx:Time', ns)
                position = trackpoint.find('tcx:Position', ns)
                
                if timestamp_elem is not None and position is not None:
                    lat_elem = position.find('tcx:LatitudeDegrees', ns)
                    lng_elem = position.find('tcx:LongitudeDegrees', ns)
                    
                    if lat_elem is not None and lng_elem is not None:
                        timestamp = datetime.fromisoformat(timestamp_elem.text.replace('Z', '+00:00'))
                        activity_data['gps_data'].append({
                            'lat': float(lat_elem.text),
                            'lng': float(lng_elem.text),
                            'timestamp': timestamp
                        })
                
                # Heart rate
                hr_elem = trackpoint.find('.//tcx:HeartRateBpm/tcx:Value', ns)
                if hr_elem is not None:
                    heart_rates.append(int(hr_elem.text))
        
        activity_data['distance_meters'] = total_distance
        activity_data['duration_seconds'] = total_time
        activity_data['calories'] = total_calories if total_calories > 0 else None
        
        if heart_rates:
            activity_data['avg_heart_rate'] = int(sum(heart_rates) / len(heart_rates))
        
        if not activity_data['start_time']:
            raise ValueError("Arquivo TCX não contém timestamp de início")
        
        return activity_data


def validate_activity(activity: Dict) -> bool:
    """
    Valida se a atividade tem dados mínimos necessários
    
    Args:
        activity: Dict com dados da atividade
        
    Returns:
        True se válida, False caso contrário
    """
    required_fields = ['start_time', 'duration_seconds', 'distance_meters']
    
    for field in required_fields:
        if field not in activity or activity[field] is None:
            logger.error(f"Atividade inválida: campo '{field}' ausente")
            return False
    
    # Validações básicas
    if activity['duration_seconds'] <= 0:
        logger.error("Atividade inválida: duração <= 0")
        return False
    
    if activity['distance_meters'] <= 0:
        logger.error("Atividade inválida: distância <= 0")
        return False
    
    return True
