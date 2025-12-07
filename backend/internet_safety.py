# Internet Safety - Download + VirusTotal
# Автоматическая проверка файлов через VirusTotal API

import requests, hashlib, time, os, logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class VirusTotalScanner:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.virustotal.com/api/v3"
        self.headers = {"x-apikey": self.api_key}
        
    def get_file_hash(self, file_path: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def check_hash(self, file_hash: str) -> Dict:
        try:
            response = requests.get(f"{self.base_url}/files/{file_hash}", headers=self.headers)
            if response.status_code == 200:
                return response.json()
            return {'error': 'not_found' if response.status_code == 404 else 'api_error'}
        except Exception as e:
            logger.error(f"VT check error: {e}")
            return {'error': str(e)}
    
    def upload_file(self, file_path: str) -> Dict:
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = requests.post(f"{self.base_url}/files", headers=self.headers, files=files)
            if response.status_code == 200:
                return {'analysis_id': response.json()['data']['id']}
            return {'error': 'upload_failed'}
        except Exception as e:
            return {'error': str(e)}
    
    def get_analysis_results(self, analysis_id: str, max_wait: int = 60) -> Dict:
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{self.base_url}/analyses/{analysis_id}", headers=self.headers)
                if response.status_code == 200:
                    data = response.json()
                    if data['data']['attributes']['status'] == 'completed':
                        return data
                time.sleep(5)
            except Exception as e:
                return {'error': str(e)}
        return {'error': 'timeout'}
    
    def is_file_safe(self, scan_results: Dict, threshold: int = 5) -> bool:
        if 'error' in scan_results:
            return False
        try:
            stats = scan_results['data']['attributes']['stats']
            total = stats.get('malicious', 0) + stats.get('suspicious', 0)
            logger.info(f"✅ VT: {stats.get('malicious')} malicious, {stats.get('suspicious')} suspicious")
            return total < threshold
        except:
            return False

class SafeDownloader:
    def __init__(self, vt_api_key: str, download_dir: str = "downloads"):
        self.vt_scanner = VirusTotalScanner(vt_api_key)
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        
    def download_file(self, url: str, filename: Optional[str] = None) -> Dict:
        if filename is None:
            filename = url.split('/')[-1]
        file_path = self.download_dir / filename
        
        try:
            logger.info(f"📥 Загрузка: {url}")
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            logger.info(f"✅ Скачан: {file_path}")
            
            # VirusTotal проверка
            file_hash = self.vt_scanner.get_file_hash(str(file_path))
            logger.info(f"🔐 SHA256: {file_hash}")
            
            scan_results = self.vt_scanner.check_hash(file_hash)
            
            if scan_results.get('error') == 'not_found':
                logger.info("📤 Загружаю на VT...")
                upload_result = self.vt_scanner.upload_file(str(file_path))
                if 'error' in upload_result:
                    os.remove(file_path)
                    return {'status': 'error', 'message': 'VT upload failed'}
                scan_results = self.vt_scanner.get_analysis_results(upload_result['analysis_id'])
            
            if self.vt_scanner.is_file_safe(scan_results):
                logger.info(f"✅ Файл безопасен: {filename}")
                return {'status': 'success', 'file_path': str(file_path), 'sha256': file_hash}
            else:
                logger.warning(f"⚠️ Опасный файл! Удаляю: {filename}")
                os.remove(file_path)
                return {'status': 'unsafe', 'message': 'File flagged by VirusTotal'}
        except Exception as e:
            if file_path.exists():
                os.remove(file_path)
            return {'status': 'error', 'message': str(e)}

class InternetAccessControl:
    def __init__(self, vt_api_key: str):
        self.downloader = SafeDownloader(vt_api_key)
        self.allowed_domains = []  # Whitelist
        self.blocked_domains = []  # Blacklist
    
    def is_url_allowed(self, url: str) -> bool:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if self.blocked_domains and domain in self.blocked_domains:
            return False
        if self.allowed_domains and domain not in self.allowed_domains:
            return False
        return True
    
    def safe_download(self, url: str) -> Dict:
        if not self.is_url_allowed(url):
            return {'status': 'error', 'message': 'URL not allowed'}
        return self.downloader.download_file(url)
