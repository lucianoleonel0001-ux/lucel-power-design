from http.server import HTTPServer, BaseHTTPRequestHandler
import json, os, urllib.parse

PORT = int(os.environ.get('PORT', 3000))

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args): pass

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.serve_file('index.html', 'text/html')
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/gerar':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            html = gerar_slides(body)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({'html': html}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def serve_file(self, filename, content_type):
        try:
            with open(filename, 'rb') as f:
                content = f.read()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_response(404)
            self.end_headers()


MARCAS = {
    "Stripe":     {"bg":"#0a2540","accent":"#635bff","text":"#ffffff","muted":"#89b4fa","card":"#0d2d4f"},
    "Apple":      {"bg":"#000000","accent":"#f5f5f7","text":"#f5f5f7","muted":"#86868b","card":"#1a1a1a"},
    "Linear":     {"bg":"#0f0f13","accent":"#5e6ad2","text":"#f2f2f2","muted":"#8a8a9b","card":"#1a1a20"},
    "Notion":     {"bg":"#ffffff","accent":"#000000","text":"#1a1a1a","muted":"#6b7280","card":"#f7f7f5"},
    "Vercel":     {"bg":"#000000","accent":"#ffffff","text":"#ffffff","muted":"#888888","card":"#111111"},
    "Spotify":    {"bg":"#121212","accent":"#1db954","text":"#ffffff","muted":"#b3b3b3","card":"#1e1e1e"},
    "Tesla":      {"bg":"#cc0000","accent":"#ffffff","text":"#ffffff","muted":"#ffcccc","card":"#aa0000"},
    "Airbnb":     {"bg":"#ffffff","accent":"#ff5a5f","text":"#1a1a1a","muted":"#717171","card":"#f7f7f7"},
    "Anthropic":  {"bg":"#0f0f0f","accent":"#d4a96a","text":"#f5f0e8","muted":"#a0998a","card":"#1a1a18"},
    "OpenAI":     {"bg":"#ffffff","accent":"#10a37f","text":"#202123","muted":"#6e6e80","card":"#f7f7f8"},
    "GitHub":     {"bg":"#0d1117","accent":"#58a6ff","text":"#c9d1d9","muted":"#8b949e","card":"#161b22"},
    "Figma":      {"bg":"#1e1e1e","accent":"#a259ff","text":"#ffffff","muted":"#b3b3b3","card":"#2c2c2c"},
    "Notion":     {"bg":"#ffffff","accent":"#000000","text":"#37352f","muted":"#6b7280","card":"#f7f7f5"},
    "Slack":      {"bg":"#4a154b","accent":"#ecb22e","text":"#ffffff","muted":"#e8d5e8","card":"#3f0e40"},
    "Uber":       {"bg":"#000000","accent":"#276ef1","text":"#ffffff","muted":"#8d8d8d","card":"#1a1a1a"},
    "Airbnb":     {"bg":"#ffffff","accent":"#ff5a5f","text":"#1a1a1a","muted":"#717171","card":"#f7f7f7"},
    "Netflix":    {"bg":"#141414","accent":"#e50914","text":"#ffffff","muted":"#808080","card":"#1f1f1f"},
    "Nike":       {"bg":"#111111","accent":"#ffffff","text":"#ffffff","muted":"#999999","card":"#222222"},
    "BMW":        {"bg":"#1c69d4","accent":"#ffffff","text":"#ffffff","muted":"#b3c9ee","card":"#1558b0"},
    "Ferrari":    {"bg":"#cc0000","accent":"#f5c518","text":"#ffffff","muted":"#ffaaaa","card":"#aa0000"},
    "Shopify":    {"bg":"#ffffff","accent":"#008060","text":"#202223","muted":"#6d7175","card":"#f6f6f7"},
    "Coinbase":   {"bg":"#0052ff","accent":"#ffffff","text":"#ffffff","muted":"#ccd9ff","card":"#0040cc"},
    "Binance":    {"bg":"#181a20","accent":"#f0b90b","text":"#eaecef","muted":"#848e9c","card":"#1e2026"},
    "Revolut":    {"bg":"#191c1f","accent":"#7b61ff","text":"#ffffff","muted":"#8c9196","card":"#23272b"},
    "Wise":       {"bg":"#9fe870","accent":"#163300","text":"#163300","muted":"#2b5900","card":"#b5f285"},
    "Wired":      {"bg":"#ffffff","accent":"#ff0000","text":"#000000","muted":"#555555","card":"#f5f5f5"},
    "IBM":        {"bg":"#000000","accent":"#0f62fe","text":"#ffffff","muted":"#8d8d8d","card":"#161616"},
    "NVIDIA":     {"bg":"#1a1a1a","accent":"#76b900","text":"#ffffff","muted":"#aaaaaa","card":"#252525"},
    "SpaceX":     {"bg":"#000000","accent":"#005288","text":"#ffffff","muted":"#888888","card":"#0a0a0a"},
    "Mastercard": {"bg":"#ffffff","accent":"#eb001b","text":"#231f20","muted":"#666666","card":"#f5f5f5"},
    "Intercom":   {"bg":"#ffffff","accent":"#1f8ded","text":"#1a1a1a","muted":"#6b7280","card":"#f5f9ff"},
    "Notion":     {"bg":"#ffffff","accent":"#000000","text":"#1a1a1a","muted":"#9b9a97","card":"#f7f7f5"},
    "Miro":       {"bg":"#fff700","accent":"#050038","text":"#050038","muted":"#555500","card":"#ffff33"},
    "Zapier":     {"bg":"#ffffff","accent":"#ff4a00","text":"#1a1a1a","muted":"#716f75","card":"#fff5f2"},
    "Supabase":   {"bg":"#1c1c1c","accent":"#3ecf8e","text":"#ededed","muted":"#9e9e9e","card":"#2a2a2a"},
    "Framer":     {"bg":"#0c0c0c","accent":"#0075ff","text":"#ffffff","muted":"#888888","card":"#1a1a1a"},
    "Webflow":    {"bg":"#146ef5","accent":"#ffffff","text":"#ffffff","muted":"#c0d8fe","card":"#0f5ed4"},
    "Raycast":    {"bg":"#1a1523","accent":"#ff6363","text":"#ffffff","muted":"#9b8fa6","card":"#231d2e"},
    "Cursor":     {"bg":"#000000","accent":"#9b59b6","text":"#ffffff","muted":"#888888","card":"#0f0f0f"},
    "Starbucks":  {"bg":"#00704a","accent":"#cba258","text":"#ffffff","muted":"#d4edda","card":"#005a3c"},
    "BMW M":      {"bg":"#000000","accent":"#e52222","text":"#ffffff","muted":"#888888","card":"#111111"},
    "Bugatti":    {"bg":"#1a1a8c","accent":"#c8a951","text":"#ffffff","muted":"#aaaacc","card":"#12127a"},
    "Lamborghini":{"bg":"#1a1a1a","accent":"#ffd700","text":"#ffffff","muted":"#aaaaaa","card":"#252525"},
    "PlayStation":{"bg":"#003087","accent":"#00439c","text":"#ffffff","muted":"#aabbdd","card":"#002060"},
    "Sony":       {"bg":"#000000","accent":"#0070d1","text":"#ffffff","muted":"#888888","card":"#111111"},
    "Renault":    {"bg":"#efdf00","accent":"#000000","text":"#000000","muted":"#333300","card":"#fff200"},
}


def gerar_slides(data):
    tema = data.get('tema', 'Apresentação')
    marca_nome = data.get('marca', 'Stripe')
    pontos = data.get('pontos', [])
    
    s = MARCAS.get(marca_nome, MARCAS['Stripe'])
    
    if not pontos:
        pontos = ['Visão geral', 'Como funciona', 'Benefícios', 'Resultados', 'Próximos passos']

    slides = []

    # Slide 1 — Título
    slides.append(f"""
    <div class="slide active" data-index="0">
      <div class="slide-inner" style="justify-content:center;align-items:flex-start;padding:80px 100px;">
        <div style="max-width:800px;">
          <div class="label">{marca_nome} Style — Lucel Digital</div>
          <h1 style="font-size:68px;font-weight:800;line-height:1.05;margin:20px 0 28px;letter-spacing:-2px;">{tema}</h1>
          <div style="width:64px;height:4px;background:{s['accent']};margin-bottom:28px;border-radius:2px;"></div>
          <p style="font-size:22px;color:{s['muted']};max-width:520px;line-height:1.6;">Apresentação gerada com Lucel Power Design</p>
        </div>
      </div>
    </div>""")

    # Slides de conteúdo
    for i, ponto in enumerate(pontos):
        num = str(i + 1).zfill(2)
        total = str(len(pontos)).zfill(2)
        slides.append(f"""
    <div class="slide" data-index="{i+1}">
      <div class="slide-inner" style="justify-content:center;align-items:flex-start;padding:80px 100px;">
        <div style="max-width:900px;width:100%;">
          <div class="label">{num} / {total}</div>
          <h2 style="font-size:56px;font-weight:700;line-height:1.1;margin:20px 0 48px;letter-spacing:-1.5px;">{ponto}</h2>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;">
            <div class="card">
              <div class="card-icon">→</div>
              <div class="card-label">Ponto chave</div>
            </div>
            <div class="card">
              <div class="card-icon">◆</div>
              <div class="card-label">Detalhe</div>
            </div>
            <div class="card">
              <div class="card-icon">✓</div>
              <div class="card-label">Resultado</div>
            </div>
          </div>
        </div>
      </div>
    </div>""")

    # Slide final — CTA
    slides.append(f"""
    <div class="slide" data-index="{len(pontos)+1}">
      <div class="slide-inner" style="justify-content:center;align-items:center;text-align:center;padding:80px;">
        <div>
          <div style="font-size:88px;margin-bottom:28px;line-height:1;">→</div>
          <h2 style="font-size:56px;font-weight:700;margin-bottom:16px;letter-spacing:-1.5px;">Vamos começar?</h2>
          <p style="font-size:20px;color:{s['muted']};margin-bottom:48px;">{tema}</p>
          <a href="https://wa.me/5511939435370" target="_blank" class="cta-btn">Falar com a Lucel Digital →</a>
        </div>
      </div>
    </div>""")

    total_slides = len(slides)
    slides_html = '\n'.join(slides)

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width">
<title>{tema} — Lucel Power Design</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: {s['bg']}; color: {s['text']}; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'Segoe UI', sans-serif; overflow: hidden; height: 100vh; }}
  .deck {{ width: 100vw; height: 100vh; position: relative; }}
  .slide {{ width: 100%; height: 100%; position: absolute; top: 0; left: 0; opacity: 0; pointer-events: none; transition: opacity .5s ease; }}
  .slide.active {{ opacity: 1; pointer-events: all; }}
  .slide-inner {{ width: 100%; height: 100%; display: flex; flex-direction: column; }}
  .label {{ font-size: 12px; letter-spacing: 3px; text-transform: uppercase; color: {s['accent']}; font-weight: 600; }}
  .card {{ padding: 20px 24px; background: {s['card']}; border: 1px solid {s['accent']}22; border-radius: 10px; }}
  .card-icon {{ font-size: 24px; color: {s['accent']}; margin-bottom: 10px; }}
  .card-label {{ font-size: 14px; color: {s['muted']}; }}
  .cta-btn {{ display: inline-block; padding: 18px 44px; background: {s['accent']}; color: {s['bg']}; border-radius: 8px; font-size: 17px; font-weight: 600; text-decoration: none; transition: opacity .2s; }}
  .cta-btn:hover {{ opacity: 0.85; }}
  .nav {{ position: fixed; bottom: 32px; right: 40px; display: flex; gap: 12px; align-items: center; z-index: 100; }}
  .nav-btn {{ width: 46px; height: 46px; border-radius: 50%; border: 1px solid {s['text']}33; background: {s['card']}; color: {s['text']}; font-size: 18px; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all .2s; }}
  .nav-btn:hover {{ background: {s['accent']}; color: {s['bg']}; border-color: {s['accent']}; }}
  .counter {{ font-size: 13px; color: {s['muted']}; }}
  .progress {{ position: fixed; top: 0; left: 0; height: 2px; background: {s['accent']}; transition: width .5s ease; z-index: 100; }}
  .brand-tag {{ position: fixed; top: 24px; left: 40px; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; color: {s['muted']}; }}
</style>
</head>
<body>
<div class="progress" id="prog" style="width:{round(1/total_slides*100)}%"></div>
<div class="brand-tag">Lucel Power Design × {marca_nome}</div>
<div class="deck">{slides_html}</div>
<div class="nav">
  <button class="nav-btn" onclick="ir(-1)">←</button>
  <span class="counter" id="counter">1 / {total_slides}</span>
  <button class="nav-btn" onclick="ir(1)">→</button>
</div>
<script>
  let cur = 0;
  const slides = document.querySelectorAll('.slide');
  const total = {total_slides};
  function ir(d) {{
    slides[cur].classList.remove('active');
    cur = (cur + d + total) % total;
    slides[cur].classList.add('active');
    document.getElementById('counter').textContent = (cur+1) + ' / ' + total;
    document.getElementById('prog').style.width = ((cur+1)/total*100) + '%';
  }}
  document.addEventListener('keydown', e => {{
    if (e.key === 'ArrowRight' || e.key === ' ') ir(1);
    if (e.key === 'ArrowLeft') ir(-1);
  }});
<\/script>
</body>
</html>"""


if __name__ == '__main__':
    print(f'Lucel Power Design rodando na porta {PORT}')
    HTTPServer(('0.0.0.0', PORT), Handler).serve_forever()
