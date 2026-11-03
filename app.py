from flask import Flask, render_template_string
import psutil
import requests
import socket
import platform

app = Flask(__name__)

# ========================================================
# NOME DA EQUIPE (Altere para testar o CI/CD!)
EQUIPE = "Equipe Zetta"
# ========================================================

def obter_conselho_devops():
    try:
        # Consome uma API externa de conselhos (Slip Advice API)
        resposta = requests.get("https://api.adviceslip.com/advice", timeout=2)
        return resposta.json()['slip']['advice']
    except:
        return "Automatize tudo."

TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Painel de Infra · {{ equipe }}</title>
<style>
  :root {
    --bg: #f5f5f7;
    --card: #ffffff;
    --text: #1d1d1f;
    --muted: #6e6e73;
    --line: rgba(0, 0, 0, 0.08);
    --accent: #0071e3;
    --track: #e8e8ed;
    --nav: rgba(245, 245, 247, 0.72);
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #000000;
      --card: #1c1c1e;
      --text: #f5f5f7;
      --muted: #98989d;
      --line: rgba(255, 255, 255, 0.1);
      --accent: #2997ff;
      --track: #3a3a3c;
      --nav: rgba(0, 0, 0, 0.72);
    }
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter",
                 "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    -webkit-font-smoothing: antialiased;
    line-height: 1.47;
  }

  nav {
    position: sticky;
    top: 0;
    z-index: 10;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 max(22px, calc((100% - 980px) / 2));
    background: var(--nav);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid var(--line);
    font-size: 13px;
  }
  nav .brand { font-weight: 600; letter-spacing: -0.01em; }
  nav .status { color: var(--muted); display: flex; align-items: center; gap: 8px; }
  nav .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #30d158;
    box-shadow: 0 0 0 3px rgba(48, 209, 88, 0.2);
  }

  main { max-width: 980px; margin: 0 auto; padding: 0 22px 80px; }

  header { text-align: center; padding: 88px 0 64px; }
  header .eyebrow {
    font-size: 17px;
    font-weight: 600;
    color: var(--accent);
    margin-bottom: 8px;
  }
  header h1 {
    font-size: clamp(40px, 7vw, 72px);
    font-weight: 700;
    letter-spacing: -0.035em;
    line-height: 1.05;
  }
  header p {
    margin-top: 16px;
    font-size: clamp(17px, 2.2vw, 21px);
    color: var(--muted);
    letter-spacing: -0.01em;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
  }
  .card {
    background: var(--card);
    border-radius: 24px;
    padding: 32px;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }
  .label {
    font-size: 14px;
    font-weight: 600;
    color: var(--muted);
    letter-spacing: 0.01em;
  }
  .value {
    font-size: clamp(48px, 7vw, 80px);
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1;
  }
  .value small {
    font-size: 0.4em;
    font-weight: 600;
    color: var(--muted);
    margin-left: 4px;
    letter-spacing: -0.01em;
  }
  .bar {
    height: 6px;
    background: var(--track);
    border-radius: 999px;
    overflow: hidden;
    margin-top: 24px;
  }
  .bar span {
    display: block;
    height: 100%;
    background: var(--accent);
    border-radius: inherit;
    transition: width 0.8s cubic-bezier(0.22, 1, 0.36, 1);
  }

  .mono {
    font-family: "SF Mono", ui-monospace, Menlo, Consolas, monospace;
    font-size: clamp(18px, 2.4vw, 26px);
    font-weight: 500;
    letter-spacing: -0.02em;
    word-break: break-all;
  }

  .quote {
    grid-column: 1 / -1;
    text-align: center;
    padding: 72px 32px;
    min-height: 0;
    align-items: center;
    gap: 20px;
  }
  .quote blockquote {
    font-size: clamp(24px, 4vw, 40px);
    font-weight: 600;
    letter-spacing: -0.03em;
    line-height: 1.2;
    max-width: 720px;
  }

  footer {
    margin-top: 48px;
    text-align: center;
    font-size: 12px;
    color: var(--muted);
  }

  @media (max-width: 700px) {
    .grid { grid-template-columns: 1fr; }
    header { padding: 56px 0 40px; }
    .card { padding: 26px; min-height: 180px; }
  }
</style>
</head>
<body>
  <nav>
    <span class="brand">{{ equipe }}</span>
    <span class="status"><span class="dot"></span>Operacional</span>
  </nav>

  <main>
    <header>
      <div class="eyebrow">{{ equipe }}</div>
      <h1>Painel de Infra.</h1>
      <p>Telemetria do servidor, em tempo real.</p>
    </header>

    <section class="grid">
      <div class="card">
        <div class="label">Uso de CPU</div>
        <div>
          <div class="value">{{ cpu }}<small>%</small></div>
          <div class="bar"><span style="width: {{ cpu }}%"></span></div>
        </div>
      </div>

      <div class="card">
        <div class="label">Uso de RAM</div>
        <div>
          <div class="value">{{ ram }}<small>%</small></div>
          <div class="bar"><span style="width: {{ ram }}%"></span></div>
        </div>
      </div>

      <div class="card">
        <div class="label">Hostname do container</div>
        <div class="mono">{{ hostname }}</div>
      </div>

      <div class="card">
        <div class="label">Arquitetura</div>
        <div class="mono">{{ arch }}</div>
      </div>

      <div class="card quote">
        <div class="label">Conselho DevOps do dia</div>
        <blockquote>“{{ conselho }}”</blockquote>
      </div>
    </section>

    <footer>Atualize a página para novas métricas.</footer>
  </main>
</body>
</html>
"""

@app.route('/')
def home():
    memoria = psutil.virtual_memory()
    cpu_percent = psutil.cpu_percent(interval=0.1)

    return render_template_string(
        TEMPLATE,
        equipe=EQUIPE,
        hostname=socket.gethostname(),
        arch=platform.machine(),
        cpu=cpu_percent,
        ram=memoria.percent,
        conselho=obter_conselho_devops(),
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
