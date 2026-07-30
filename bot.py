from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import requests
import urllib.parse
import time
import os
import gzip
import zlib
import re
import random

# ===== EN GÜÇLÜ 10 USER-AGENT =====
SUPER_USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0',
    'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1',
    'Mozilla/5.0 (Linux; Android 14; SM-S911B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
]

# ===== EN GÜÇLÜ HEADERS =====
def get_super_headers():
    return {
        'User-Agent': random.choice(SUPER_USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Google Chrome";v="120", "Not_A Brand";v="8", "Chromium";v="120"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://www.google.com/',
        'Dnt': '1',
        'Connection': 'keep-alive'
    }

# ===== CLOUDFLARE BYPASS =====
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

# ===== GZIP / DEFLATE / BR ÇÖZÜCÜ =====
def decode_content(content, encoding):
    try:
        if encoding == 'gzip':
            return gzip.decompress(content)
        elif encoding == 'deflate':
            try:
                return zlib.decompress(content)
            except:
                return zlib.decompress(content, -zlib.MAX_WBITS)
        elif encoding == 'br':
            try:
                import brotli
                return brotli.decompress(content)
            except:
                return content
        else:
            return content
    except:
        return content

# ===== REKLAM TEMİZLEME =====
def remove_ads_from_response(data):
    # Temizlenecek reklam anahtarları
    ads_to_remove = [
        "developer", "version", "api_sahibi", "api_surum", 
        "not", "ApiTelegramKanalı", "ApiSahibi", "ApiTelegramKanal",
        "ApiSahip", "TelegramKanal", "Sahibi", "@KarmaYxc",
        "t.me/yxcpanel", "yxcpanel"
    ]
    
    if isinstance(data, dict):
        # Reklam anahtarlarını sil
        for key in ads_to_remove:
            if key in data:
                del data[key]
        
        # İç içe geçmiş verileri temizle
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = remove_ads_from_response(value)
            elif isinstance(value, list):
                data[key] = [remove_ads_from_response(item) if isinstance(item, (dict, list)) else item for item in value]
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                data[i] = remove_ads_from_response(item)
    return data

# ===== SÜPER GÜÇLÜ API İSTEK =====
def make_api_request(url, params=None):
    if params is None:
        params = {}
    
    # Önce cloudscraper dene
    if CLOUDSCRAPER_AVAILABLE:
        try:
            print("⚡ Cloudscraper ile bypass...")
            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'desktop': True,
                    'mobile': False
                },
                delay=1
            )
            
            headers = get_super_headers()
            scraper.headers.update(headers)
            
            # Challenge çöz
            scraper.get('https://punisherservices.alwaysdata.net', timeout=15)
            time.sleep(1)
            
            # API isteği
            response = scraper.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                content = response.content
                encoding = response.headers.get('Content-Encoding', '').lower()
                
                if encoding and encoding != 'identity':
                    decoded_content = decode_content(content, encoding)
                else:
                    decoded_content = content
                
                try:
                    text = decoded_content.decode('utf-8')
                except:
                    try:
                        text = decoded_content.decode('latin-1')
                    except:
                        text = str(decoded_content)
                
                clean_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
                
                if 'Just a moment' not in clean_text:
                    try:
                        json.loads(clean_text)
                        print("✅ Cloudscraper başarılı!")
                        return {
                            'success': True,
                            'status_code': response.status_code,
                            'text': clean_text,
                            'headers': dict(response.headers)
                        }
                    except:
                        pass
        except Exception as e:
            print(f"⚠️ Cloudscraper hatası: {e}")
    
    # Normal requests + Güçlü Session
    print("⚡ Session ile bypass...")
    session = requests.Session()
    headers = get_super_headers()
    session.headers.update(headers)
    
    # Cookie'ler
    session.cookies.set('__cf_bm', str(int(time.time())), domain='punisherservices.alwaysdata.net')
    session.cookies.set('cf_clearance', 'true', domain='punisherservices.alwaysdata.net')
    
    try:
        session.get('https://punisherservices.alwaysdata.net', timeout=10)
        time.sleep(1)
    except:
        pass
    
    response = session.get(url, params=params, timeout=30)
    
    content = response.content
    encoding = response.headers.get('Content-Encoding', '').lower()
    
    if encoding and encoding != 'identity':
        decoded_content = decode_content(content, encoding)
    else:
        decoded_content = content
    
    try:
        text = decoded_content.decode('utf-8')
    except:
        try:
            text = decoded_content.decode('latin-1')
        except:
            text = str(decoded_content)
    
    clean_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return {
        'success': True,
        'status_code': response.status_code,
        'text': clean_text,
        'headers': dict(response.headers)
    }

# ===== HTTP HANDLER =====
class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        params = urllib.parse.parse_qs(parsed.query)
        params = {k: v[0] if v else '' for k, v in params.items()}
        
        # Ana sayfa
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
            return
        
        # API proxy
        if path.startswith('/api/'):
            api_path = path.replace('/api/', '')
            base_url = 'https://punisherservices.alwaysdata.net/apiservices'
            full_url = f"{base_url}/{api_path}"
            
            print(f"\n{'='*50}")
            print(f"⚡ API: {full_url}")
            print(f"📝 Params: {params}")
            print(f"{'='*50}\n")
            
            start_time = time.time()
            result = make_api_request(full_url, params)
            elapsed = time.time() - start_time
            
            print(f"⏱️ Süre: {elapsed:.2f}s")
            
            if result.get('success'):
                try:
                    data = json.loads(result['text'])
                    cleaned_data = remove_ads_from_response(data)
                    
                    response_data = {
                        'success': True,
                        'status_code': result['status_code'],
                        'data': cleaned_data,
                        'response_time': f"{elapsed:.2f}s",
                        'api_sahibi': '@rinexdestek',
                        'api_surum': '8.0',
                        'not': 'BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR'
                    }
                except json.JSONDecodeError:
                    response_data = {
                        'success': True,
                        'status_code': result['status_code'],
                        'raw': result['text'][:2000] + ('...' if len(result['text']) > 2000 else ''),
                        'response_time': f"{elapsed:.2f}s",
                        'api_sahibi': '@rinexdestek',
                        'api_surum': '8.0',
                        'not': 'BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR'
                    }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response_data, ensure_ascii=False, indent=2).encode('utf-8'))
            else:
                error_data = {
                    'success': False,
                    'error': result.get('error', 'Bilinmeyen hata'),
                    'response_time': f"{elapsed:.2f}s",
                    'api_sahibi': '@rinexdestek',
                    'api_surum': '8.0',
                    'not': 'BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR'
                }
                
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(error_data, ensure_ascii=False, indent=2).encode('utf-8'))
            return
        
        self.send_response(404)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps({'error': 'Not Found'}).encode('utf-8'))
    
    def log_message(self, format, *args):
        print(f"{time.strftime('%H:%M:%S')} - {format % args}")

# ===== HTML PAGE =====
HTML_PAGE = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>rinex API Servisi v8.0</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            min-height: 100vh;
            padding: 20px;
            color: #fff;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        .header {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 40px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .header h1 {
            font-size: 3em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .badge-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 15px 0;
        }
        .badge {
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 14px;
            font-weight: 600;
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .badge.owner { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border: none; }
        .badge.version { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border: none; }
        .badge.free { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border: none; color: #000; }
        .badge.bot { background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); border: none; color: #000; }
        .badge.ua { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); border: none; color: #000; }
        .badge.fast { background: linear-gradient(135deg, #fccb90 0%, #d57eeb 100%); border: none; color: #000; }
        .warning-box {
            margin-top: 20px;
            padding: 20px;
            background: rgba(255, 107, 107, 0.15);
            border: 2px solid #ff6b6b;
            border-radius: 12px;
            text-align: center;
            font-weight: bold;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-5px);
            border-color: rgba(102, 126, 234, 0.5);
        }
        .card h3 { font-size: 1.2em; color: #667eea; margin-bottom: 10px; }
        .endpoint {
            background: rgba(0,0,0,0.3);
            padding: 10px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            margin: 10px 0;
            word-break: break-all;
            color: #4facfe;
        }
        .params {
            color: rgba(255,255,255,0.7);
            font-size: 13px;
            margin: 8px 0;
            padding: 8px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
        }
        .input-group {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 15px 0;
        }
        .input-group input {
            padding: 12px 16px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 14px;
            transition: all 0.3s;
        }
        .input-group input:focus {
            border-color: #667eea;
            outline: none;
            background: rgba(255,255,255,0.08);
        }
        .input-group input::placeholder { color: rgba(255,255,255,0.4); }
        .btn {
            padding: 14px;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .btn:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 20px -8px rgba(102, 126, 234, 0.4);
        }
        .response {
            background: rgba(0,0,0,0.4);
            border-radius: 12px;
            padding: 16px;
            margin-top: 15px;
            max-height: 400px;
            overflow: auto;
            font-family: 'Courier New', monospace;
            font-size: 13px;
            white-space: pre-wrap;
            word-wrap: break-word;
            border: 1px solid rgba(255,255,255,0.05);
            color: #a8d8ea;
            display: none;
        }
        .response.active { display: block; }
        .response.success { border-left: 4px solid #43e97b; }
        .response.error { border-left: 4px solid #ff6b6b; }
        .loading {
            display: none;
            text-align: center;
            padding: 15px;
            color: #667eea;
            font-weight: bold;
        }
        .loading.active { display: block; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(102, 126, 234, 0.3);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: spin 0.8s ease-in-out infinite;
            margin-right: 10px;
            vertical-align: middle;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
        .footer {
            text-align: center;
            padding: 40px 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
            margin-top: 30px;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 2em; }
            .grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 rinex API Servisi v8.0</h1>
            <div class="badge-container">
                <span class="badge owner">👤 @rinexdestek</span>
                <span class="badge version">📦 Sürüm 8.0</span>
                <span class="badge free">🔓 BEDAVA</span>
                <span class="badge bot">🤖 Süper Bot</span>
                <span class="badge ua">👾 10x User-Agent</span>
                <span class="badge fast">⚡ HIZLI</span>
            </div>
            <div class="warning-box">⚠️ BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR ⚠️</div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🔍 TC Sorgulama</h3>
                <div class="endpoint">GET /api/tc.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="tcInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('tc')">🔍 Sorgula</button>
                <div id="tcLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="tcResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>🔍 TC Pro Sorgulama</h3>
                <div class="endpoint">GET /api/tcpro.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="tcproInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('tcpro')">🔍 Sorgula</button>
                <div id="tcproLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="tcproResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👤 Ad-Soyad Sorgulama</h3>
                <div class="endpoint">GET /api/adsoyad.php?ad={AD}&soyad={SOYAD}</div>
                <div class="params">📌 Parametreler: <strong>ad, soyad</strong></div>
                <div class="input-group">
                    <input type="text" id="adiInput" placeholder="Ad" value="roket">
                    <input type="text" id="soyadiInput" placeholder="Soyad" value="atar">
                </div>
                <button class="btn" onclick="callAPI('adsoyad')">🔍 Sorgula</button>
                <div id="adsoyadLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="adsoyadResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👤 Ad-Soyad Pro Sorgulama</h3>
                <div class="endpoint">GET /api/adsoyadpro.php?ad={AD}&soyad={SOYAD}</div>
                <div class="params">📌 Parametreler: <strong>ad, soyad</strong></div>
                <div class="input-group">
                    <input type="text" id="adiProInput" placeholder="Ad" value="roket">
                    <input type="text" id="soyadiProInput" placeholder="Soyad" value="atar">
                </div>
                <button class="btn" onclick="callAPI('adsoyadpro')">🔍 Sorgula</button>
                <div id="adsoyadproLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="adsoyadproResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👨‍👩‍👧‍👦 Aile Sorgulama</h3>
                <div class="endpoint">GET /api/aile.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="aileInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('aile')">🔍 Sorgula</button>
                <div id="aileLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="aileResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👨‍👩‍👧‍👦 Aile Pro Sorgulama</h3>
                <div class="endpoint">GET /api/ailepro.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="aileproInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('ailepro')">🔍 Sorgula</button>
                <div id="aileproLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="aileproResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👶 Çocuk Sorgulama</h3>
                <div class="endpoint">GET /api/cocuk.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="cocukInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('cocuk')">🔍 Sorgula</button>
                <div id="cocukLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="cocukResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>💑 Eş Sorgulama</h3>
                <div class="endpoint">GET /api/es.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="esInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('es')">🔍 Sorgula</button>
                <div id="esLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="esResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👫 Kardeş Sorgulama</h3>
                <div class="endpoint">GET /api/kardes.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="kardesInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('kardes')">🔍 Sorgula</button>
                <div id="kardesLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="kardesResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>📅 Doğum Yeri Sorgulama</h3>
                <div class="endpoint">GET /api/dogumtililce.php?dogumt={TARIH}&il={IL}&ilce={ILCE}</div>
                <div class="params">📌 Parametreler: <strong>dogumt, il, ilce</strong></div>
                <div class="input-group">
                    <input type="text" id="dogumtInput" placeholder="Doğum Tarihi (17.03.1998)" value="17.03.1998">
                    <input type="text" id="ilInput" placeholder="İl" value="istanbul">
                    <input type="text" id="ilceInput" placeholder="İlçe" value="buyukcekmece">
                </div>
                <button class="btn" onclick="callAPI('dogumtililce')">🔍 Sorgula</button>
                <div id="dogumtililceLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="dogumtililceResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>📅 Soyad-Doğum Tarihi Sorgulama</h3>
                <div class="endpoint">GET /api/soyaddogumt.php?dogumt={TARIH}&soyad={SOYAD}</div>
                <div class="params">📌 Parametreler: <strong>dogumt, soyad</strong></div>
                <div class="input-group">
                    <input type="text" id="dogumtSoyadInput" placeholder="Doğum Tarihi (17.03.1998)" value="17.03.1998">
                    <input type="text" id="soyadDogumtInput" placeholder="Soyad" value="deniz">
                </div>
                <button class="btn" onclick="callAPI('soyaddogumt')">🔍 Sorgula</button>
                <div id="soyaddogumtLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="soyaddogumtResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>🏠 Adres Sorgulama</h3>
                <div class="endpoint">GET /api/adres.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="adresInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('adres')">🔍 Sorgula</button>
                <div id="adresLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="adresResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👨‍👩‍👧‍👦 Sülale Sorgulama</h3>
                <div class="endpoint">GET /api/sulale.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="sulaleInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('sulale')">🔍 Sorgula</button>
                <div id="sulaleLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="sulaleResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>👨‍👩‍👧‍👦 Sülale Pro Sorgulama</h3>
                <div class="endpoint">GET /api/sulalepro.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="sulaleproInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('sulalepro')">🔍 Sorgula</button>
                <div id="sulaleproLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="sulaleproResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>🏢 İşyeri Sorgulama</h3>
                <div class="endpoint">GET /api/isyeri.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="isyeriInput" placeholder="TC Kimlik No girin" value="11144576054">
                </div>
                <button class="btn" onclick="callAPI('isyeri')">🔍 Sorgula</button>
                <div id="isyeriLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="isyeriResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>🏠 Tapu Sorgulama</h3>
                <div class="endpoint">GET /api/tapu.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="tapuInput" placeholder="TC Kimlik No girin" value="27727166918">
                </div>
                <button class="btn" onclick="callAPI('tapu')">🔍 Sorgula</button>
                <div id="tapuLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="tapuResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>🏦 IBAN Sorgulama</h3>
                <div class="endpoint">GET /api/iban.php?iban={IBAN}</div>
                <div class="params">📌 Parametre: <strong>iban</strong></div>
                <div class="input-group">
                    <input type="text" id="ibanInput" placeholder="IBAN girin" value="TR280006256953335759003718">
                </div>
                <button class="btn" onclick="callAPI('iban')">🔍 Sorgula</button>
                <div id="ibanLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="ibanResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>📱 GSM Operator Sorgulama</h3>
                <div class="endpoint">GET /api/gncloperator.php?numara={NUMARA}</div>
                <div class="params">📌 Parametre: <strong>numara</strong></div>
                <div class="input-group">
                    <input type="text" id="gsmOperatorInput" placeholder="GSM Numarası" value="5315312472">
                </div>
                <button class="btn" onclick="callAPI('gncloperator')">🔍 Sorgula</button>
                <div id="gncloperatorLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="gncloperatorResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>📱 TC ile GSM Sorgulama</h3>
                <div class="endpoint">GET /api/tcgsm.php?tc={TC}</div>
                <div class="params">📌 Parametre: <strong>tc</strong> (TC Kimlik No)</div>
                <div class="input-group">
                    <input type="text" id="tcgsmInput" placeholder="TC Kimlik No girin" value="11111111110">
                </div>
                <button class="btn" onclick="callAPI('tcgsm')">🔍 Sorgula</button>
                <div id="tcgsmLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="tcgsmResponse" class="response"></div>
            </div>
            
            <div class="card">
                <h3>📱 GSM ile TC Sorgulama</h3>
                <div class="endpoint">GET /api/gsmtc.php?gsm={GSM}</div>
                <div class="params">📌 Parametre: <strong>gsm</strong></div>
                <div class="input-group">
                    <input type="text" id="gsmtcInput" placeholder="GSM Numarası" value="5415722525">
                </div>
                <button class="btn" onclick="callAPI('gsmtc')">🔍 Sorgula</button>
                <div id="gsmtcLoading" class="loading"><span class="spinner"></span> Yükleniyor...</div>
                <div id="gsmtcResponse" class="response"></div>
            </div>
        </div>
        
        <div class="footer">
            <p style="font-size: 1.2em; font-weight: bold;">🔗 rinex API Servisi v8.0</p>
            <p>👤 API Sahibi: @rinexdestek</p>
            <p style="color: #ff6b6b; font-weight: bold; margin-top: 10px;">⚠️ BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR</p>
        </div>
    </div>
    
    <script>
        function callAPI(type) {
            let url = '', responseId = '', loadingId = '';
            
            switch(type) {
                case 'tc':
                    const tc = document.getElementById('tcInput').value.trim();
                    if (!tc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/tc.php?tc=${tc}`;
                    responseId = 'tcResponse';
                    loadingId = 'tcLoading';
                    break;
                case 'tcpro':
                    const tcpro = document.getElementById('tcproInput').value.trim();
                    if (!tcpro) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/tcpro.php?tc=${tcpro}`;
                    responseId = 'tcproResponse';
                    loadingId = 'tcproLoading';
                    break;
                case 'adsoyad':
                    const adi = document.getElementById('adiInput').value.trim();
                    const soyadi = document.getElementById('soyadiInput').value.trim();
                    if (!adi && !soyadi) { alert('❌ Lütfen Ad veya Soyad girin!'); return; }
                    url = `/api/adsoyad.php?ad=${encodeURIComponent(adi)}&soyad=${encodeURIComponent(soyadi)}`;
                    responseId = 'adsoyadResponse';
                    loadingId = 'adsoyadLoading';
                    break;
                case 'adsoyadpro':
                    const adiPro = document.getElementById('adiProInput').value.trim();
                    const soyadiPro = document.getElementById('soyadiProInput').value.trim();
                    if (!adiPro && !soyadiPro) { alert('❌ Lütfen Ad veya Soyad girin!'); return; }
                    url = `/api/adsoyadpro.php?ad=${encodeURIComponent(adiPro)}&soyad=${encodeURIComponent(soyadiPro)}`;
                    responseId = 'adsoyadproResponse';
                    loadingId = 'adsoyadproLoading';
                    break;
                case 'aile':
                    const aileTc = document.getElementById('aileInput').value.trim();
                    if (!aileTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/aile.php?tc=${aileTc}`;
                    responseId = 'aileResponse';
                    loadingId = 'aileLoading';
                    break;
                case 'ailepro':
                    const aileproTc = document.getElementById('aileproInput').value.trim();
                    if (!aileproTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/ailepro.php?tc=${aileproTc}`;
                    responseId = 'aileproResponse';
                    loadingId = 'aileproLoading';
                    break;
                case 'cocuk':
                    const cocukTc = document.getElementById('cocukInput').value.trim();
                    if (!cocukTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/cocuk.php?tc=${cocukTc}`;
                    responseId = 'cocukResponse';
                    loadingId = 'cocukLoading';
                    break;
                case 'es':
                    const esTc = document.getElementById('esInput').value.trim();
                    if (!esTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/es.php?tc=${esTc}`;
                    responseId = 'esResponse';
                    loadingId = 'esLoading';
                    break;
                case 'kardes':
                    const kardesTc = document.getElementById('kardesInput').value.trim();
                    if (!kardesTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/kardes.php?tc=${kardesTc}`;
                    responseId = 'kardesResponse';
                    loadingId = 'kardesLoading';
                    break;
                case 'dogumtililce':
                    const dogumt = document.getElementById('dogumtInput').value.trim();
                    const il = document.getElementById('ilInput').value.trim();
                    const ilce = document.getElementById('ilceInput').value.trim();
                    if (!dogumt || !il || !ilce) { alert('❌ Tüm alanları doldurun!'); return; }
                    url = `/api/dogumtililce.php?dogumt=${encodeURIComponent(dogumt)}&il=${encodeURIComponent(il)}&ilce=${encodeURIComponent(ilce)}`;
                    responseId = 'dogumtililceResponse';
                    loadingId = 'dogumtililceLoading';
                    break;
                case 'soyaddogumt':
                    const dogumtSoyad = document.getElementById('dogumtSoyadInput').value.trim();
                    const soyadDogumt = document.getElementById('soyadDogumtInput').value.trim();
                    if (!dogumtSoyad || !soyadDogumt) { alert('❌ Tüm alanları doldurun!'); return; }
                    url = `/api/soyaddogumt.php?dogumt=${encodeURIComponent(dogumtSoyad)}&soyad=${encodeURIComponent(soyadDogumt)}`;
                    responseId = 'soyaddogumtResponse';
                    loadingId = 'soyaddogumtLoading';
                    break;
                case 'adres':
                    const adresTc = document.getElementById('adresInput').value.trim();
                    if (!adresTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/adres.php?tc=${adresTc}`;
                    responseId = 'adresResponse';
                    loadingId = 'adresLoading';
                    break;
                case 'sulale':
                    const sulaleTc = document.getElementById('sulaleInput').value.trim();
                    if (!sulaleTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/sulale.php?tc=${sulaleTc}`;
                    responseId = 'sulaleResponse';
                    loadingId = 'sulaleLoading';
                    break;
                case 'sulalepro':
                    const sulaleproTc = document.getElementById('sulaleproInput').value.trim();
                    if (!sulaleproTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/sulalepro.php?tc=${sulaleproTc}`;
                    responseId = 'sulaleproResponse';
                    loadingId = 'sulaleproLoading';
                    break;
                case 'isyeri':
                    const isyeriTc = document.getElementById('isyeriInput').value.trim();
                    if (!isyeriTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/isyeri.php?tc=${isyeriTc}`;
                    responseId = 'isyeriResponse';
                    loadingId = 'isyeriLoading';
                    break;
                case 'tapu':
                    const tapuTc = document.getElementById('tapuInput').value.trim();
                    if (!tapuTc) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/tapu.php?tc=${tapuTc}`;
                    responseId = 'tapuResponse';
                    loadingId = 'tapuLoading';
                    break;
                case 'iban':
                    const iban = document.getElementById('ibanInput').value.trim();
                    if (!iban) { alert('❌ Lütfen IBAN girin!'); return; }
                    url = `/api/iban.php?iban=${encodeURIComponent(iban)}`;
                    responseId = 'ibanResponse';
                    loadingId = 'ibanLoading';
                    break;
                case 'gncloperator':
                    const numara = document.getElementById('gsmOperatorInput').value.trim();
                    if (!numara) { alert('❌ Lütfen GSM Numarası girin!'); return; }
                    url = `/api/gncloperator.php?numara=${numara}`;
                    responseId = 'gncloperatorResponse';
                    loadingId = 'gncloperatorLoading';
                    break;
                case 'tcgsm':
                    const tcgsm = document.getElementById('tcgsmInput').value.trim();
                    if (!tcgsm) { alert('❌ Lütfen TC Kimlik No girin!'); return; }
                    url = `/api/tcgsm.php?tc=${tcgsm}`;
                    responseId = 'tcgsmResponse';
                    loadingId = 'tcgsmLoading';
                    break;
                case 'gsmtc':
                    const gsmtc = document.getElementById('gsmtcInput').value.trim();
                    if (!gsmtc) { alert('❌ Lütfen GSM Numarası girin!'); return; }
                    url = `/api/gsmtc.php?gsm=${gsmtc}`;
                    responseId = 'gsmtcResponse';
                    loadingId = 'gsmtcLoading';
                    break;
            }
            
            const loadingEl = document.getElementById(loadingId);
            const responseEl = document.getElementById(responseId);
            loadingEl.classList.add('active');
            responseEl.classList.remove('active', 'success', 'error');
            responseEl.textContent = '';
            
            fetch(url)
                .then(response => response.json())
                .then(data => {
                    loadingEl.classList.remove('active');
                    responseEl.classList.add('active');
                    responseEl.textContent = JSON.stringify(data, null, 2);
                    responseEl.className = 'response active success';
                })
                .catch(error => {
                    loadingEl.classList.remove('active');
                    responseEl.classList.add('active');
                    responseEl.className = 'response active error';
                    responseEl.textContent = '❌ Hata: ' + error.message;
                });
        }
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const active = document.activeElement;
                const id = active.id;
                if (id === 'tcInput') callAPI('tc');
                else if (id === 'tcproInput') callAPI('tcpro');
                else if (id === 'adiInput' || id === 'soyadiInput') callAPI('adsoyad');
                else if (id === 'adiProInput' || id === 'soyadiProInput') callAPI('adsoyadpro');
                else if (id === 'aileInput') callAPI('aile');
                else if (id === 'aileproInput') callAPI('ailepro');
                else if (id === 'cocukInput') callAPI('cocuk');
                else if (id === 'esInput') callAPI('es');
                else if (id === 'kardesInput') callAPI('kardes');
                else if (id === 'dogumtInput' || id === 'ilInput' || id === 'ilceInput') callAPI('dogumtililce');
                else if (id === 'dogumtSoyadInput' || id === 'soyadDogumtInput') callAPI('soyaddogumt');
                else if (id === 'adresInput') callAPI('adres');
                else if (id === 'sulaleInput') callAPI('sulale');
                else if (id === 'sulaleproInput') callAPI('sulalepro');
                else if (id === 'isyeriInput') callAPI('isyeri');
                else if (id === 'tapuInput') callAPI('tapu');
                else if (id === 'ibanInput') callAPI('iban');
                else if (id === 'gsmOperatorInput') callAPI('gncloperator');
                else if (id === 'tcgsmInput') callAPI('tcgsm');
                else if (id === 'gsmtcInput') callAPI('gsmtc');
            }
        });
    </script>
</body>
</html>'''

# ===== MAIN =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    
    print("=" * 70)
    print("🚀 rinex API Servisi v8.0 - SÜPER GÜÇLÜ")
    print("👤 API Sahibi: @rinexdestek")
    print("🛡️ 10x En Güçlü User-Agent")
    print("🤖 Cloudflare Bypass Aktif")
    print("📦 20 API Eklendi:")
    print("   - /api/tc.php")
    print("   - /api/tcpro.php")
    print("   - /api/adsoyad.php")
    print("   - /api/adsoyadpro.php")
    print("   - /api/aile.php")
    print("   - /api/ailepro.php")
    print("   - /api/cocuk.php")
    print("   - /api/es.php")
    print("   - /api/kardes.php")
    print("   - /api/dogumtililce.php")
    print("   - /api/soyaddogumt.php")
    print("   - /api/adres.php")
    print("   - /api/sulale.php")
    print("   - /api/sulalepro.php")
    print("   - /api/isyeri.php")
    print("   - /api/tapu.php")
    print("   - /api/iban.php")
    print("   - /api/gncloperator.php")
    print("   - /api/tcgsm.php")
    print("   - /api/gsmtc.php")
    print("⚠️ BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR")
    print("=" * 70)
    print(f"🌐 Sunucu: http://0.0.0.0:{port}")
    print("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Sunucu durduruluyor...")
        server.shutdown()
