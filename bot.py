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
import html

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
    ads_to_remove = [
        "developer", "version", "api_sahibi", "api_surum", 
        "not", "ApiTelegramKanalı", "ApiSahibi", "ApiTelegramKanal",
        "ApiSahip", "TelegramKanal", "Sahibi", "@KarmaYxc",
        "t.me/yxcpanel", "yxcpanel"
    ]
    
    if isinstance(data, dict):
        for key in ads_to_remove:
            if key in data:
                del data[key]
        
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
            
            scraper.get('https://punisherservices.alwaysdata.net', timeout=15)
            time.sleep(1)
            
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
    
    print("⚡ Session ile bypass...")
    session = requests.Session()
    headers = get_super_headers()
    session.headers.update(headers)
    
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
        
        # Ana sayfa (Login sayfası)
        if path == '/' or path == '':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(LOGIN_PAGE.encode('utf-8'))
            return
        
        # Ana API sayfası (giriş sonrası)
        if path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(DASHBOARD_PAGE.encode('utf-8'))
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
                        'premium_destek': '@sinopya',
                        'api_surum': '29.1',
                        'kanal': '@relaxapiservisi'
                    }
                except json.JSONDecodeError:
                    response_data = {
                        'success': True,
                        'status_code': result['status_code'],
                        'raw': result['text'][:2000] + ('...' if len(result['text']) > 2000 else ''),
                        'response_time': f"{elapsed:.2f}s",
                        'PREMİUM_DESTEK': '@sinopya',
                        'api_surum': '29.1',
                        'KANAL': '@relaxapiservisi'
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

# ===== LOGIN PAGE =====
LOGIN_PAGE = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SİNOPYA SERVİCE - Giriş</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            overflow: hidden;
            position: relative;
            background: #0a0a0a;
        }
        .bg-gif {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyNHJzYnF6YzZrYnVueGxpenhjb21scnBqdzJ4eG9tNDF4ZzVhNHVtcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1aTUTJOn3aavLVC6G1/giphy.gif') center/cover;
            filter: blur(8px) brightness(0.4);
            z-index: 0;
        }
        .login-container {
            position: relative;
            z-index: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }
        .login-box {
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(20px);
            border-radius: 30px;
            padding: 50px 40px;
            max-width: 420px;
            width: 100%;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 30px 60px rgba(0,0,0,0.8);
            animation: slideUp 0.8s ease;
        }
        @keyframes slideUp {
            from { opacity: 0; transform: translateY(40px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .logo {
            text-align: center;
            margin-bottom: 35px;
        }
        .logo h1 {
            font-size: 2.2em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .logo p {
            color: rgba(255,255,255,0.5);
            margin-top: 8px;
            font-size: 14px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        .input-group label {
            display: block;
            color: rgba(255,255,255,0.7);
            font-size: 13px;
            font-weight: 600;
            margin-bottom: 8px;
            letter-spacing: 1px;
        }
        .input-group input {
            width: 100%;
            padding: 16px 20px;
            border: 2px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            background: rgba(255,255,255,0.05);
            color: #fff;
            font-size: 16px;
            transition: all 0.3s;
            outline: none;
        }
        .input-group input:focus {
            border-color: #667eea;
            background: rgba(255,255,255,0.08);
            box-shadow: 0 0 30px rgba(102, 126, 234, 0.1);
        }
        .input-group input::placeholder {
            color: rgba(255,255,255,0.3);
        }
        .btn-login {
            width: 100%;
            padding: 16px;
            border: none;
            border-radius: 16px;
            font-size: 18px;
            font-weight: 700;
            cursor: pointer;
            transition: all 0.3s;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-top: 10px;
            letter-spacing: 1px;
        }
        .btn-login:hover {
            transform: scale(1.02);
            box-shadow: 0 10px 30px -8px rgba(102, 126, 234, 0.5);
        }
        .btn-login:active {
            transform: scale(0.98);
        }
        .footer-text {
            text-align: center;
            margin-top: 25px;
            color: rgba(255,255,255,0.3);
            font-size: 12px;
        }
        .footer-text span {
            color: #667eea;
        }
        .warning {
            text-align: center;
            margin-top: 15px;
            color: rgba(255,107,107,0.7);
            font-size: 13px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="bg-gif"></div>
    <div class="login-container">
        <div class="login-box">
            <div class="logo">
                <h1>🔍 SİNOPYA</h1>
                <p>API Servisine Hoş Geldiniz</p>
            </div>
            <div class="input-group">
                <label>👤 TELEGRAM KULLANICI ADI</label>
                <input type="text" id="usernameInput" placeholder="@kullaniciadi" value="@sinopya">
            </div>
            <button class="btn-login" onclick="login()">🚀 GİRİŞ YAP</button>
            <div class="footer-text">
                <span>🔒</span> Güvenli Bağlantı
            </div>
            <div class="warning">
                ⚠️ BU APİLER BEDAVADIR
            </div>
        </div>
    </div>

    <script>
        function login() {
            const username = document.getElementById('usernameInput').value.trim();
            if (!username) {
                alert('❌ Lütfen Telegram kullanıcı adınızı girin!');
                return;
            }
            localStorage.setItem('telegram_username', username);
            window.location.href = '/dashboard';
        }

        document.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                login();
            }
        });
    </script>
</body>
</html>'''

# ===== DASHBOARD PAGE =====
DASHBOARD_PAGE = '''<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SİNOPYA SERVİCE - API</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            min-height: 100vh;
            background: #0a0a0a;
            color: #fff;
            overflow-x: hidden;
        }
        .bg-gif {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: url('https://media2.giphy.com/media/v1.Y2lkPTZjMDliOTUyNHJzYnF6YzZrYnVueGxpenhjb21scnBqdzJ4eG9tNDF4ZzVhNHVtcCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/1aTUTJOn3aavLVC6G1/giphy.gif') center/cover;
            filter: blur(6px) brightness(0.3);
            z-index: 0;
        }
        .container {
            position: relative;
            z-index: 1;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 30px 40px;
            margin-bottom: 30px;
            border: 1px solid rgba(255,255,255,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 15px;
        }
        .header h1 {
            font-size: 2em;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .user-info span {
            color: rgba(255,255,255,0.7);
        }
        .user-info .name {
            color: #667eea;
            font-weight: bold;
        }
        .btn-logout {
            padding: 10px 24px;
            border: 2px solid rgba(255,107,107,0.3);
            border-radius: 12px;
            background: transparent;
            color: #ff6b6b;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.3s;
        }
        .btn-logout:hover {
            background: rgba(255,107,107,0.1);
            border-color: #ff6b6b;
        }
        .badge-container {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 10px 0;
        }
        .badge {
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 13px;
            font-weight: 600;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.1);
        }
        .badge.owner { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border: none; }
        .badge.version { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); border: none; }
        .badge.free { background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border: none; color: #000; }
        .badge.fast { background: linear-gradient(135deg, #fccb90 0%, #d57eeb 100%); border: none; color: #000; }
        .badge.ua { background: linear-gradient(135deg, #a18cd1 0%, #fbc2eb 100%); border: none; color: #000; }
        .warning-box {
            margin-top: 15px;
            padding: 15px 25px;
            background: rgba(255, 107, 107, 0.12);
            border: 2px solid rgba(255,107,107,0.3);
            border-radius: 12px;
            text-align: center;
            font-weight: bold;
            animation: pulse 2s infinite;
            font-size: 14px;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
        }
        .system-start {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.95);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 9999;
            animation: fadeOut 0.8s ease forwards 3.5s;
            pointer-events: none;
        }
        @keyframes fadeOut {
            0% { opacity: 1; }
            100% { opacity: 0; visibility: hidden; }
        }
        .system-start h1 {
            font-size: 4em;
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            text-shadow: 0 0 60px rgba(67, 233, 123, 0.3);
            letter-spacing: 5px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: rgba(255,255,255,0.04);
            backdrop-filter: blur(20px);
            border-radius: 18px;
            padding: 22px 25px;
            border: 1px solid rgba(255,255,255,0.06);
            transition: all 0.3s ease;
        }
        .card:hover {
            transform: translateY(-3px);
            border-color: rgba(102, 126, 234, 0.3);
            background: rgba(255,255,255,0.06);
        }
        .card h3 {
            font-size: 1.1em;
            color: #667eea;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .card .endpoint {
            background: rgba(0,0,0,0.4);
            padding: 10px 14px;
            border-radius: 10px;
            font-family: 'Courier New', monospace;
            font-size: 12px;
            margin: 8px 0;
            word-break: break-all;
            color: #4facfe;
            border: 1px solid rgba(255,255,255,0.05);
        }
        .card .params {
            color: rgba(255,255,255,0.6);
            font-size: 12px;
            margin: 6px 0;
            padding: 6px 10px;
            background: rgba(255,255,255,0.03);
            border-radius: 6px;
        }
        .card .params strong {
            color: #fccb90;
        }
        .footer {
            text-align: center;
            padding: 30px 20px;
            border-top: 1px solid rgba(255,255,255,0.05);
            margin-top: 20px;
        }
        .footer p {
            color: rgba(255,255,255,0.4);
            font-size: 13px;
        }
        .footer .highlight {
            color: #ff6b6b;
            font-weight: bold;
        }
        @media (max-width: 768px) {
            .header h1 { font-size: 1.5em; }
            .header { padding: 20px; flex-direction: column; text-align: center; }
            .grid { grid-template-columns: 1fr; }
            .system-start h1 { font-size: 2.5em; }
        }
    </style>
</head>
<body>
    <div class="system-start">
        <h1>⚡ SYSTEM BAŞLATİLDİ</h1>
    </div>

    <div class="bg-gif"></div>
    
    <div class="container">
        <div class="header">
            <div>
                <h1>🔍 SİNOPYA API</h1>
                <div class="badge-container">
                    <span class="badge owner">👤 @sinopya</span>
                    <span class="badge version">📦 v29.1</span>
                    <span class="badge free">🔓 VİP @sinopya</span>
                    <span class="badge ua">🤖 Süper Bot</span>
                    <span class="badge fast">⚡ HIZLI</span>
                </div>
            </div>
            <div class="user-info">
                <span>👤 <span class="name" id="usernameDisplay">@kullanici</span></span>
                <button class="btn-logout" onclick="logout()">🚪 Çıkış</button>
            </div>
        </div>

        <div class="warning-box">📞 APİ KANALI @relaxapiservisi 📞</div>

        <div class="grid" id="apiGrid"></div>

        <div class="footer">
            <p>🔗 SİNOPYA API Servisi v29.1 | <span class="highlight">⚠️ BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR</span></p>
        </div>
    </div>

    <script>
        // YouTube müzik
        const musicPlayer = document.createElement('div');
        musicPlayer.innerHTML = `
            <iframe 
                width="0" 
                height="0" 
                src="https://www.youtube.com/embed/qR36gJ0uR8M?autoplay=1&loop=1&playlist=qR36gJ0uR8M&controls=0&showinfo=0&rel=0&iv_load_policy=3&modestbranding=1" 
                frameborder="0" 
                allow="autoplay; encrypted-media" 
                style="display:none;"
                id="musicIframe"
            ></iframe>
        `;
        document.body.appendChild(musicPlayer);

        // Kullanıcı adını göster
        const username = localStorage.getItem('telegram_username') || '@misafir';
        document.getElementById('usernameDisplay').textContent = username;

        // API listesi
        const apis = [
            { name: 'TC Sorgulama', endpoint: '/api/tc.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'TC Pro Sorgulama', endpoint: '/api/tcpro.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Ad-Soyad Sorgulama', endpoint: '/api/adsoyad.php?ad={AD}&soyad={SOYAD}', params: 'ad, soyad', example: 'roket, atar' },
            { name: 'Ad-Soyad Pro', endpoint: '/api/adsoyadpro.php?ad={AD}&soyad={SOYAD}', params: 'ad, soyad', example: 'roket, atar' },
            { name: 'Aile Sorgulama', endpoint: '/api/aile.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Aile Pro', endpoint: '/api/ailepro.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Çocuk Sorgulama', endpoint: '/api/cocuk.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Eş Sorgulama', endpoint: '/api/es.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Kardeş Sorgulama', endpoint: '/api/kardes.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Doğum Yeri', endpoint: '/api/dogumtililce.php?dogumt={TARIH}&il={IL}&ilce={ILCE}', params: 'dogumt, il, ilce', example: '17.03.1998, istanbul, buyukcekmece' },
            { name: 'Soyad-Doğum Tarihi', endpoint: '/api/soyaddogumt.php?dogumt={TARIH}&soyad={SOYAD}', params: 'dogumt, soyad', example: '17.03.1998, deniz' },
            { name: 'Adres Sorgulama', endpoint: '/api/adres.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Sülale Sorgulama', endpoint: '/api/sulale.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'Sülale Pro', endpoint: '/api/sulalepro.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'İşyeri Sorgulama', endpoint: '/api/isyeri.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11144576054' },
            { name: 'Tapu Sorgulama', endpoint: '/api/tapu.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '27727166918' },
            { name: 'IBAN Sorgulama', endpoint: '/api/iban.php?iban={IBAN}', params: 'iban', example: 'TR280006256953335759003718' },
            { name: 'GSM Operator', endpoint: '/api/gncloperator.php?numara={NUMARA}', params: 'numara', example: '5315312472' },
            { name: 'TC ile GSM', endpoint: '/api/tcgsm.php?tc={TC}', params: 'tc (TC Kimlik No)', example: '11111111110' },
            { name: 'GSM ile TC', endpoint: '/api/gsmtc.php?gsm={GSM}', params: 'gsm', example: '5415722525' }
        ];

        // API kartlarını oluştur
        const grid = document.getElementById('apiGrid');
        apis.forEach(api => {
            const card = document.createElement('div');
            card.className = 'card';
            
            const iconMap = {
                'TC': '🔍', 'Ad-Soyad': '👤', 'Aile': '👨‍👩‍👧‍👦', 'Çocuk': '👶', 
                'Eş': '💑', 'Kardeş': '👫', 'Doğum': '📅', 'Adres': '🏠',
                'Sülale': '👨‍👩‍👧‍👦', 'İşyeri': '🏢', 'Tapu': '🏠', 'IBAN': '🏦',
                'GSM': '📱', 'Operator': '📱', 'Pro': '⭐'
            };
            
            let icon = '🔗';
            for (const [key, val] of Object.entries(iconMap)) {
                if (api.name.includes(key)) { icon = val; break; }
            }
            
            card.innerHTML = `
                <h3>${icon} ${api.name}</h3>
                <div class="endpoint">${api.endpoint}</div>
                <div class="params">📌 Parametreler: <strong>${api.params}</strong></div>
                <div class="params" style="color: rgba(255,255,255,0.4); font-size: 11px;">Örnek: ${api.example}</div>
            `;
            grid.appendChild(card);
        });

        function logout() {
            if (confirm('Çıkış yapmak istediğinize emin misiniz?')) {
                localStorage.removeItem('telegram_username');
                window.location.href = '/';
            }
        }
    </script>
</body>
</html>'''

# ===== MAIN =====
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    server = HTTPServer(('0.0.0.0', port), APIHandler)
    
    print("=" * 70)
    print("🚀 SİNOPYA API Servisi v29.1 - SÜPER GÜÇLÜ")
    print("👤 API Sahibi: @sinopya")
    print("🛡️ 10x En Güçlü User-Agent")
    print("🤖 Cloudflare Bypass Aktif")
    print("📦 20 API Eklendi")
    print("🎵 YouTube Müzik: https://youtu.be/qR36gJ0uR8M")
    print("🖼️ Arka Plan GIF: Giphy link")
    print("⚠️ BU APİLER BEDAVADIR, PARAYLA SATILMASI SUÇTUR")
    print("=" * 70)
    print(f"🌐 Sunucu: http://0.0.0.0:{port}")
    print(f"🔑 Giriş: http://0.0.0.0:{port}/")
    print(f"📊 Dashboard: http://0.0.0.0:{port}/dashboard")
    print("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n⏹️ Sunucu durduruluyor...")
        server.shutdown()
