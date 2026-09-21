from flask import Flask, render_template_string, request, Response
import yt_dlp
from fpdf import FPDF
import io
import requests

app = Flask(__name__)

# Configuración del Bot de Telegram (Para alertas Premium)
TELEGRAM_BOT_TOKEN = "TU_TOKEN_DE_TELEGRAM_AQUI"
TELEGRAM_CHAT_ID = "TU_CHAT_ID_AQUI"

USUARIOS_SaaS = {
    "cliente_express": {"plan": "Express"},
    "cliente_premium": {"plan": "Premium"}
}

# CAMBIA AQUÍ: "cliente_express" para probar el de $20 o "cliente_premium" para el de $35
USUARIO_ACTUAL = "cliente_premium"

def enviar_alerta_telegram(mensaje):
    if TELEGRAM_BOT_TOKEN == "TU_TOKEN_DE_TELEGRAM_AQUI": return
    url = f"https://telegram.org{TELEGRAM_BOT_TOKEN}/sendMessage"
    try: requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": mensaje}, timeout=5)
    except: pass

def espiar_nichos_completo(keyword, tipo_plan):
    ydl_opts = {'extract_flat': True, 'quiet': True}
    limite = 3 if tipo_plan == "Express" else 10
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            search_results = ydl.extract_info(f"ytsearch{limite}:channel {keyword}", download=False)
            items = search_results.get('entries', [])
            canales = []
            for item in items:
                texto_desc = str(item.get('description', '')).lower()
                if tipo_plan == "Premium":
                    if "premiere" in texto_desc: editor = "🎬 Adobe Premiere Pro"
                    elif "davinci" in texto_desc: editor = "🎬 DaVinci Resolve"
                    elif "capcut" in texto_desc: editor = "🎬 CapCut Pro"
                    else: editor = "🎬 CapCut / Celular"
                else:
                    editor = "🔒 Bloqueado (Plan Premium)"
                
                subs_conteo = item.get('channel_follower_count')
                subs_texto = f"{subs_conteo:,} suscriptores" if subs_conteo else "Audiencia Activa"
                
                palabra = keyword.lower()
                rpm_estimado = 12.50 if "finanzas" in palabra or "dinero" in palabra else 3.50
                ganancia_base = 2400 if "finanzas" in palabra or "dinero" in palabra else 500

                canales.append({
                    "nombre": item.get('title', 'Canal'),
                    "link": item.get('url', 'https://youtube.com'),
                    "subs": subs_texto,
                    "rpm": f"${rpm_estimado:.2f} USD",
                    "ganancia": f"${ganancia_base:,} USD/mes",
                    "editor": editor
                })
            return canales
        except: return []

HTML_COMPLETO = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaaS YouTube Spier</title>
    <script src="https://tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 p-4 font-sans">
    <div class="max-w-xl mx-auto">
        <div class="text-center mb-6">
            <h1 class="text-2xl font-extrabold text-red-500">YouTube Niche Spier 🕵️‍♂️</h1>
            <span class="bg-orange-500 text-slate-950 text-[10px] font-bold px-3 py-1 rounded-full uppercase">Cuenta: {{ plan }}</span>
        </div>
        <form method="POST" class="bg-slate-800 p-4 rounded-xl border border-slate-700 mb-6 flex flex-col gap-2">
            <input type="text" name="nicho" value="{{ busqueda }}" placeholder="Escribe un tema (ej: finanzas)..." class="bg-slate-950 p-3 rounded-lg text-white border border-slate-700 text-sm">
            <button type="submit" class="bg-red-600 font-bold py-3 rounded-lg text-sm">Analizar Nicho</button>
        </form>
        {% if resultados %}
            <div class="flex justify-between items-center mb-4 text-xs">
                <span class="text-slate-400">Canales Detectados:</span>
                {% if plan == 'Premium' %}
                    <a href="/descargar_pdf?nicho={{ busqueda }}" target="_blank" class="bg-emerald-600 px-3 py-1.5 rounded font-bold">📄 PDF</a>
                {% endif %}
            </div>
            <div class="space-y-4">
                {% for canal in resultados %}
                    <div class="bg-slate-800 p-4 rounded-xl border border-slate-700">
                        <div class="flex justify-between items-center mb-1">
                            <strong class="text-white text-sm truncate max-w-[150px]">{{ canal.nombre }}</strong>
                            <a href="{{ canal.link }}" target="_blank" class="text-red-400 text-xs font-bold">Ver ➡️</a>
                        </div>
                        <p class="text-orange-400 text-[11px] font-bold">📊 Volumen: {{ canal.subs }}</p>
                        <p class="text-slate-400 text-[11px] mb-3">🎬 Editor: {{ canal.editor }}</p>
                        <div class="grid grid-cols-2 gap-2 bg-slate-950 p-2 rounded-lg text-center text-[11px]">
                            <div><span class="text-slate-500 block text-[9px]">RPM</span><strong class="text-emerald-400">{{ canal.rpm }}</strong></div>
                            <div><span class="text-slate-500 block text-[9px]">GANANCIA</span><strong class="text-white">{{ canal.ganancia }}</strong></div>
                        </div>
                    </div>
                {% endfor %}
            </div>
        {% endif %}
        <div class="border-t border-slate-800 mt-8 pt-4">
            <h2 class="text-center font-bold text-sm mb-4 text-slate-400">Planes de Suscripción</h2>
            <div class="space-y-3 text-xs">
                <div class="bg-slate-800 p-4 rounded-xl border border-slate-700 text-center">
                    <strong>Plan Express: $20 USD / 15 días</strong>
                    <p class="text-[10px] text-slate-500 mt-1">Top 3 canales básicos. Bloquea editores, PDFs y Telegram.</p>
                </div>
                <div class="bg-slate-800 p-4 rounded-xl border-2 border-red-500 text-center bg-slate-900">
                    <strong class="text-orange-400">Plan Premium Total: $35 USD / 30 días 🤖</strong>
                    <p class="text-[10px] text-slate-400 mt-1">Top 10 completo, suscriptores, detector de editores, reportes en PDF y alertas directas a Telegram.</p>
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    resultados = None
    busqueda = ""
    datos_usuario = USUARIOS_SaaS[USUARIO_ACTUAL]
    if request.method == "POST":
        busqueda = request.form.get("nicho")
        if busqueda: resultados = espiar_nichos_completo(busqueda, datos_usuario["plan"])
    return render_template_string(HTML_COMPLETO, resultados=resultados, busqueda=busqueda, plan=datos_usuario["plan"])

@app.route("/descargar_pdf")
def descargar_pdf():
    nicho = request.args.get("nicho", "General")
    datos_usuario = USUARIOS_SaaS[USUARIO_ACTUAL]
    if datos_usuario["plan"] != "Premium": return "🔒 Requiere Plan Premium.", 403
    lista_canales = espiar_nichos_completo(nicho, "Premium")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"REPORTE: {nicho.upper()}", ln=True, align="C")
    for idx, canal in enumerate(lista_canales, 1):
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 8, f"{idx}. {canal['nombre']} ({canal['subs']})", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 5, f"   Editor: {canal['editor']} | RPM: {canal['rpm']} | Est: {canal['ganancia']}", ln=True)
    output_pdf = io.BytesIO()
    pdf.output(output_pdf)
    output_pdf.seek(0)
    return Response(output_pdf.getvalue(), mimetype="application/pdf", headers={"Content-Disposition": f"attachment;filename=Reporte.pdf"})

if __name__ == "__main__":
    app.run()