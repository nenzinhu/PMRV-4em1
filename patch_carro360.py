#!/usr/bin/env python3
# patch_carro360.py — aplica todas as alterações para o módulo carro360
import os, re

BASE = r'c:\Users\Nei\Downloads\Compressed\PMRV-4em1-main'
HTML = os.path.join(BASE, 'index.html')

# ── Lê base64 das imagens do carro ──────────────────────────────
def rb64(key):
    with open(os.path.join(BASE, f'b64_carro_{key}.txt'), 'r') as f:
        return f.read().strip()

B64 = {k: rb64(k) for k in ['frente','tras','direita','esquerda']}

with open(HTML, 'r', encoding='utf-8') as f:
    html = f.read()

orig_len = len(html)
print(f'Arquivo original: {orig_len} chars')

# ════════════════════════════════════════════════════════════════
# 1. INSERIR dan-step-carro360 após o fechamento do dan-step-moto360
# ════════════════════════════════════════════════════════════════
CARRO360_HTML = f"""
    <div id="dan-step-carro360" style="display:none;">
      <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap;">
        <button class="btn" onclick="danVoltarStep1()">← Trocar veículo</button>
        <button class="btn btn-danger" onclick="v360cLimpar()">🗑 Limpar tudo</button>
      </div>

      <div class="card">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-bottom:14px;">
          <div>
            <h2 class="card-title">🚗 Danos Aparentes — Carro</h2>
            <p class="card-sub">Toque nos círculos para registrar os danos.</p>
          </div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-bottom:14px;">
          <button class="dan-tab active" id="v360c-tab-frente"   onclick="v360cSwitchTab(this,'frente')">
            <img class="dan-tab-thumb" src="" id="dan-thumbc-frente" alt="Frente">
            ⬆️ Frente
          </button>
          <button class="dan-tab" id="v360c-tab-tras" onclick="v360cSwitchTab(this,'tras')">
            <img class="dan-tab-thumb" src="" id="dan-thumbc-tras" alt="Traseira">
            ⬇️ Traseira
          </button>
          <button class="dan-tab" id="v360c-tab-direita" onclick="v360cSwitchTab(this,'direita')">
            <img class="dan-tab-thumb" src="" id="dan-thumbc-direita" alt="Direita">
            ▶️ Direita
          </button>
          <button class="dan-tab" id="v360c-tab-esquerda" onclick="v360cSwitchTab(this,'esquerda')">
            <img class="dan-tab-thumb" src="" id="dan-thumbc-esquerda" alt="Esquerda">
            ◀️ Esquerda
          </button>
        </div>

        <div class="v360-wrap">
          <div class="v360-canvas" id="v360c-canvas">
            <div class="v360-hint" id="v360c-hint">👆 Toque na foto para posicionar o marcador</div>
            <img src="data:image/png;base64,{B64['frente']}" id="v360c-img-frente" class="moto-img active" alt="Carro frente">
            <img src="data:image/png;base64,{B64['tras']}" id="v360c-img-tras" class="moto-img" alt="Carro traseira">
            <img src="data:image/png;base64,{B64['direita']}" id="v360c-img-direita" class="moto-img" alt="Carro direita">
            <img src="data:image/png;base64,{B64['esquerda']}" id="v360c-img-esquerda" class="moto-img" alt="Carro esquerda">
          </div>
          <div class="v360-legend">
              <div class="v360-legend-header">🚗 Peças — soltar em: <span id="v360c-leg-vista">FRENTE</span></div>
              <div style="padding:4px 12px 5px;font-size:11px;color:var(--muted);border-bottom:1px solid var(--border);background:rgba(245,158,11,.06);">↔ Arraste ◯ para a foto · Clique no ◯ na foto para classificar</div>
              <div class="v360-legend-scroll" id="v360c-legend-list"></div>
          </div>
        </div>
      </div>

      <div class="card" style="margin-top:12px;">
        <div style="font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--label);margin-bottom:10px;">Danos registrados</div>
        <div id="v360c-summary-tags">
          <div style="font-size:13px;color:var(--label);text-align:center;padding:18px;border:1px dashed var(--border);border-radius:10px;">Nenhum dano registrado ainda.<br>Adicione marcadores na foto.</div>
        </div>
        <div style="height:1px;background:var(--border);margin:14px 0;"></div>
        <button class="btn btn-success btn-full" style="margin-bottom:8px;" onclick="danSalvarVeiculo()">💾 Salvar este veículo</button>
        <button class="btn btn-primary btn-full btn-lg" onclick="danGerarTexto()">⚡ Gerar Relatório</button>
        <div id="v360c-result-area" style="display:none;margin-top:14px;">
          <div class="result-text" id="v360c-result-text"></div>
          <div class="result-actions">
            <button class="btn btn-success" onclick="v360cCopiar(this)">📋 Copiar</button>
            <button class="btn btn-whats" onclick="v360cWhatsApp()">📲 WhatsApp</button>
          </div>
        </div>
      </div>

      <!-- Fotos dos danos — Carro 360 -->
      <div class="card" style="margin-top:12px;">
        <div style="font-size:11px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;color:var(--label);margin-bottom:10px;">📷 Fotos dos Danos</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:4px;">
          <label class="foto-label" style="flex-direction:column;padding:12px 6px;font-size:12px;">
            <span style="font-size:20px;margin-bottom:3px;">📷</span>Tirar Foto
            <input type="file" accept="image/*" capture="environment" multiple style="display:none;" onchange="danFotoMiniatura(this,'dan-foto-grid-carro360','dan-foto-actions-carro360')">
          </label>
          <label class="foto-label" style="flex-direction:column;padding:12px 6px;font-size:12px;">
            <span style="font-size:20px;margin-bottom:3px;">🖼️</span>Anexar Imagem
            <input type="file" accept="image/*" multiple style="display:none;" onchange="danFotoMiniatura(this,'dan-foto-grid-carro360','dan-foto-actions-carro360')">
          </label>
        </div>
        <div class="foto-grid" id="dan-foto-grid-carro360"></div>
        <div id="dan-foto-actions-carro360" style="display:none;gap:6px;flex-wrap:wrap;margin-top:8px;">
          <button type="button" class="btn btn-sm btn-whats" onclick="danFotoCompartilhar('dan-foto-grid-carro360')">📲 Compartilhar Fotos</button>
          <button type="button" class="btn btn-sm btn-danger" onclick="danFotoLimpar('dan-foto-grid-carro360','dan-foto-actions-carro360')">🗑 Remover Todas</button>
        </div>
      </div>
    </div>
"""

OLD1 = """          <button type="button" class="btn btn-sm btn-danger" onclick="danFotoLimpar('dan-foto-grid-moto','dan-foto-actions-moto')">🗑 Remover Todas</button>
        </div>
      </div>
    </div>

  </section>"""

NEW1 = """          <button type="button" class="btn btn-sm btn-danger" onclick="danFotoLimpar('dan-foto-grid-moto','dan-foto-actions-moto')">🗑 Remover Todas</button>
        </div>
      </div>
    </div>
""" + CARRO360_HTML + """
  </section>"""

assert OLD1 in html, 'ERRO: marcador 1 não encontrado'
html = html.replace(OLD1, NEW1, 1)
print('✅ 1. dan-step-carro360 inserido')

# ════════════════════════════════════════════════════════════════
# 2. DOMContentLoaded — adicionar mapa de thumbnails do carro
# ════════════════════════════════════════════════════════════════
OLD2 = """  const map = {
    'dan-thumb-frente':   'v360-img-frente',
    'dan-thumb-tras':     'v360-img-tras',
    'dan-thumb-direita':  'v360-img-direita',
    'dan-thumb-esquerda': 'v360-img-esquerda'
  };
  Object.keys(map).forEach(function(thumbId){
    const src = document.getElementById(map[thumbId]);
    const thumb = document.getElementById(thumbId);
    if (src && thumb) thumb.src = src.src;
  });"""

NEW2 = """  const map = {
    'dan-thumb-frente':   'v360-img-frente',
    'dan-thumb-tras':     'v360-img-tras',
    'dan-thumb-direita':  'v360-img-direita',
    'dan-thumb-esquerda': 'v360-img-esquerda'
  };
  Object.keys(map).forEach(function(thumbId){
    const src = document.getElementById(map[thumbId]);
    const thumb = document.getElementById(thumbId);
    if (src && thumb) thumb.src = src.src;
  });
  const mapC = {
    'dan-thumbc-frente':   'v360c-img-frente',
    'dan-thumbc-tras':     'v360c-img-tras',
    'dan-thumbc-direita':  'v360c-img-direita',
    'dan-thumbc-esquerda': 'v360c-img-esquerda'
  };
  Object.keys(mapC).forEach(function(thumbId){
    const src = document.getElementById(mapC[thumbId]);
    const thumb = document.getElementById(thumbId);
    if (src && thumb) thumb.src = src.src;
  });"""

assert OLD2 in html, 'ERRO: marcador 2 não encontrado'
html = html.replace(OLD2, NEW2, 1)
print('✅ 2. DOMContentLoaded thumbnails carro')

# ════════════════════════════════════════════════════════════════
# 3. danEscolherVeiculo — mostrar carro360 em vez de diagrama SVG
# ════════════════════════════════════════════════════════════════
OLD3 = """  if (v === 'moto') {
    document.getElementById('dan-step-moto360').style.display = 'block';
    document.getElementById('dan-step-diagram').style.display = 'none';
    v360db = v360makeDb();
    v360tab = 'frente';
    v360mode = 'moto';
    v360render();
  } else {
    document.getElementById('dan-step-diagram').style.display = 'block';
    document.getElementById('dan-step-moto360').style.display = 'none';
    document.getElementById('dan-veh-badge').textContent  = '🚗';
    document.getElementById('dan-diag-title').textContent = 'Mapeie os danos — Carro';
    danAtualizarTabs();
    danRenderDiagrama();
  }"""

# Tenta com v360mode se já estiver lá, senão sem
if OLD3 not in html:
    OLD3 = """  if (v === 'moto') {
    document.getElementById('dan-step-moto360').style.display = 'block';
    document.getElementById('dan-step-diagram').style.display = 'none';
    v360db = v360makeDb();
    v360tab = 'frente';
    v360render();
  } else {
    document.getElementById('dan-step-diagram').style.display = 'block';
    document.getElementById('dan-step-moto360').style.display = 'none';
    document.getElementById('dan-veh-badge').textContent  = '🚗';
    document.getElementById('dan-diag-title').textContent = 'Mapeie os danos — Carro';
    danAtualizarTabs();
    danRenderDiagrama();
  }"""

assert OLD3 in html, 'ERRO: marcador 3 não encontrado'

NEW3 = """  if (v === 'moto') {
    document.getElementById('dan-step-moto360').style.display = 'block';
    document.getElementById('dan-step-diagram').style.display = 'none';
    document.getElementById('dan-step-carro360').style.display = 'none';
    v360db = v360makeDb();
    v360tab = 'frente';
    v360mode = 'moto';
    v360render();
  } else {
    document.getElementById('dan-step-carro360').style.display = 'block';
    document.getElementById('dan-step-diagram').style.display = 'none';
    document.getElementById('dan-step-moto360').style.display = 'none';
    v360cdb = v360cMakeDb();
    v360ctab = 'frente';
    v360mode = 'carro';
    v360cRender();
  }"""

html = html.replace(OLD3, NEW3, 1)
print('✅ 3. danEscolherVeiculo atualizado')

# ════════════════════════════════════════════════════════════════
# 4. danVoltarStep1 — também esconder carro360
# ════════════════════════════════════════════════════════════════
OLD4 = """function danVoltarStep1() {
  document.getElementById('dan-step-diagram').style.display = 'none';
  document.getElementById('dan-step-moto360').style.display = 'none';
  document.getElementById('dan-step-vehicle').style.display = 'block';
  document.getElementById('dan-result-area').style.display  = 'none';
}"""

NEW4 = """function danVoltarStep1() {
  document.getElementById('dan-step-diagram').style.display = 'none';
  document.getElementById('dan-step-moto360').style.display = 'none';
  document.getElementById('dan-step-carro360').style.display = 'none';
  document.getElementById('dan-step-vehicle').style.display = 'block';
  document.getElementById('dan-result-area').style.display  = 'none';
}"""

assert OLD4 in html, 'ERRO: marcador 4 não encontrado'
html = html.replace(OLD4, NEW4, 1)
print('✅ 4. danVoltarStep1 atualizado')

# ════════════════════════════════════════════════════════════════
# 5. go('danos') — reset do carro360 também
# ════════════════════════════════════════════════════════════════
OLD5 = """    document.getElementById('dan-step-vehicle').style.display = 'block';
    document.getElementById('dan-step-diagram').style.display = 'none';
    document.getElementById('dan-step-moto360').style.display = 'none';
    danVeiculo = null; danDanos = {};
    danVeiculosSalvos = [];
    v360db = v360makeDb();
    document.getElementById('dan-btn-carro').classList.remove('active');
    document.getElementById('dan-btn-moto').classList.remove('active');
    document.getElementById('dan-salvos-area').style.display = 'none';
    danFotoLimpar('dan-foto-grid-carro','dan-foto-actions-carro');
    danFotoLimpar('dan-foto-grid-moto','dan-foto-actions-moto');"""

NEW5 = """    document.getElementById('dan-step-vehicle').style.display = 'block';
    document.getElementById('dan-step-diagram').style.display = 'none';
    document.getElementById('dan-step-moto360').style.display = 'none';
    document.getElementById('dan-step-carro360').style.display = 'none';
    danVeiculo = null; danDanos = {};
    danVeiculosSalvos = [];
    v360db = v360makeDb();
    v360cdb = null;
    document.getElementById('dan-btn-carro').classList.remove('active');
    document.getElementById('dan-btn-moto').classList.remove('active');
    document.getElementById('dan-salvos-area').style.display = 'none';
    danFotoLimpar('dan-foto-grid-carro','dan-foto-actions-carro');
    danFotoLimpar('dan-foto-grid-moto','dan-foto-actions-moto');
    danFotoLimpar('dan-foto-grid-carro360','dan-foto-actions-carro360');"""

assert OLD5 in html, 'ERRO: marcador 5 não encontrado'
html = html.replace(OLD5, NEW5, 1)
print('✅ 5. go(danos) reset atualizado')

# ════════════════════════════════════════════════════════════════
# 6. danSalvarVeiculo — tratar carro com v360cdb
# ════════════════════════════════════════════════════════════════
OLD6 = """  } else {
    if (!Object.keys(danDanos).length) { alert('Registre ao menos um dano antes de salvar.'); return; }
    danVeiculosSalvos.push({ tipo: danVeiculo, danos: Object.assign({}, danDanos) });
  }"""

NEW6 = """  } else if (danVeiculo === 'carro') {
    let hasInspC = false;
    ['frente','tras','direita','esquerda'].forEach(t => {
      if (v360cdb) v360cdb[t].forEach(i => { if (i.dano !== null) hasInspC = true; });
    });
    if (!hasInspC) { alert('Registre ao menos um dano antes de salvar.'); return; }
    danVeiculosSalvos.push({ tipo: 'carro', v360cdb: JSON.parse(JSON.stringify(v360cdb)) });
  } else {
    if (!Object.keys(danDanos).length) { alert('Registre ao menos um dano antes de salvar.'); return; }
    danVeiculosSalvos.push({ tipo: danVeiculo, danos: Object.assign({}, danDanos) });
  }"""

assert OLD6 in html, 'ERRO: marcador 6 não encontrado'
html = html.replace(OLD6, NEW6, 1)
print('✅ 6. danSalvarVeiculo atualizado')

# ════════════════════════════════════════════════════════════════
# 7. danRenderSalvos — contar danos do carro v360cdb
# ════════════════════════════════════════════════════════════════
OLD7 = """    if (v.tipo === 'moto') {
      ['frente','tras','direita','esquerda'].forEach(t => { v.v360db[t].forEach(i => { if (i.dano !== null) count++; }); });
    } else {
      count = Object.keys(v.danos).length;
    }"""

NEW7 = """    if (v.tipo === 'moto') {
      ['frente','tras','direita','esquerda'].forEach(t => { v.v360db[t].forEach(i => { if (i.dano !== null) count++; }); });
    } else if (v.tipo === 'carro' && v.v360cdb) {
      ['frente','tras','direita','esquerda'].forEach(t => { v.v360cdb[t].forEach(i => { if (i.dano !== null) count++; }); });
    } else {
      count = Object.keys(v.danos || {}).length;
    }"""

assert OLD7 in html, 'ERRO: marcador 7 não encontrado'
html = html.replace(OLD7, NEW7, 1)
print('✅ 7. danRenderSalvos atualizado')

# ════════════════════════════════════════════════════════════════
# 8. danGerarTextoTodos — tratar carro com v360cdb
# ════════════════════════════════════════════════════════════════
OLD8 = """    if (v.tipo === 'moto') {
      const V360_NAMES_L = { frente: 'Frente', tras: 'Traseira', direita: 'Lado Direito', esquerda: 'Lado Esquerdo' };
      ['frente','tras','direita','esquerda'].forEach(function(t) {
        const its = v.v360db[t].filter(function(i) { return i.dano !== null; });
        if (!its.length) return;
        txt += '\\n\\n' + V360_NAMES_L[t] + ':';
        its.sort(function(a,b) { return a.num - b.num; }).forEach(function(i) {
          txt += '\\n• ' + i.nome + ': ' + i.dano;
        });
      });
    } else {
      const cfg_map = DAN_DIAGRAMAS[v.tipo];
      const porVista = { frontal: [], traseira: [], esquerda: [], direita: [] };
      Object.keys(v.danos).forEach(function(id) {
        const mapa = { F: 'frontal', T: 'traseira', E: 'esquerda', D: 'direita' };
        const vis = mapa[id.charAt(0)];
        if (vis) porVista[vis].push(id);
      });
      Object.entries(porVista).forEach(function([vista, pontos]) {
        if (!pontos.length) return;
        const cfg = cfg_map[vista];
        txt += '\\n\\n' + DAN_VISTA_LABELS[vista] + ':';
        pontos.forEach(function(id) {
          const ponto = cfg.pontos.find(function(p) { return p.id === id; });
          if (!ponto) return;
          const tipo = v.danos[id];
          const num = cfg.pontos.indexOf(ponto) + 1;
          txt += '\\n• ' + ponto.label + ': ' + tipo;
        });
      });
    }"""

NEW8 = """    if (v.tipo === 'moto') {
      const V360_NAMES_L = { frente: 'Frente', tras: 'Traseira', direita: 'Lado Direito', esquerda: 'Lado Esquerdo' };
      ['frente','tras','direita','esquerda'].forEach(function(t) {
        const its = v.v360db[t].filter(function(i) { return i.dano !== null; });
        if (!its.length) return;
        txt += '\\n\\n' + V360_NAMES_L[t] + ':';
        its.sort(function(a,b) { return a.num - b.num; }).forEach(function(i) {
          txt += '\\n• ' + i.nome + ': ' + i.dano;
        });
      });
    } else if (v.tipo === 'carro' && v.v360cdb) {
      const V360C_NAMES_L = { frente: 'Frente', tras: 'Traseira', direita: 'Lado Direito', esquerda: 'Lado Esquerdo' };
      ['frente','tras','direita','esquerda'].forEach(function(t) {
        const its = v.v360cdb[t].filter(function(i) { return i.dano !== null; });
        if (!its.length) return;
        txt += '\\n\\n' + V360C_NAMES_L[t] + ':';
        its.forEach(function(i) {
          txt += '\\n• ' + i.nome + ': ' + i.dano;
        });
      });
    } else {
      const cfg_map = DAN_DIAGRAMAS[v.tipo];
      const porVista = { frontal: [], traseira: [], esquerda: [], direita: [] };
      Object.keys(v.danos).forEach(function(id) {
        const mapa = { F: 'frontal', T: 'traseira', E: 'esquerda', D: 'direita' };
        const vis = mapa[id.charAt(0)];
        if (vis) porVista[vis].push(id);
      });
      Object.entries(porVista).forEach(function([vista, pontos]) {
        if (!pontos.length) return;
        const cfg = cfg_map[vista];
        txt += '\\n\\n' + DAN_VISTA_LABELS[vista] + ':';
        pontos.forEach(function(id) {
          const ponto = cfg.pontos.find(function(p) { return p.id === id; });
          if (!ponto) return;
          const tipo = v.danos[id];
          const num = cfg.pontos.indexOf(ponto) + 1;
          txt += '\\n• ' + ponto.label + ': ' + tipo;
        });
      });
    }"""

assert OLD8 in html, 'ERRO: marcador 8 não encontrado'
html = html.replace(OLD8, NEW8, 1)
print('✅ 8. danGerarTextoTodos atualizado')

# ════════════════════════════════════════════════════════════════
# 9. danGerarTexto — adicionar case carro v360c
# ════════════════════════════════════════════════════════════════
OLD9 = """function danGerarTexto() {
  /* ── MOTO via v360 ── */
  if (danVeiculo === 'moto') {"""

NEW9 = """function danGerarTexto() {
  /* ── CARRO via v360c ── */
  if (danVeiculo === 'carro' && v360cdb) {
    const tabs = ['frente','tras','direita','esquerda'];
    let hasInsp = false;
    tabs.forEach(t => { v360cdb[t].forEach(i => { if (i.dano !== null) hasInsp = true; }); });
    if (!hasInsp) { alert('Inspecione ao menos uma peça antes de gerar o relatório.'); return; }
    const data = new Date().toLocaleDateString('pt-BR');
    const avarias = tabs.reduce((s,t) => s + v360cdb[t].filter(i=>i.dano!==null).length, 0);
    const V360C_NAMES_G = { frente:'FRENTE', tras:'TRASEIRA', direita:'LADO DIREITO', esquerda:'LADO ESQUERDO' };
    let txt = `*VISTORIA DE CARRO*\\nData: ${data}`;
    txt += `\\nAvarias registradas: ${avarias}`;
    txt += `\\n---------------------------`;
    tabs.forEach(t => {
      const its = v360cdb[t].filter(i => i.dano !== null);
      if (!its.length) return;
      txt += `\\n\\n${V360C_NAMES_G[t]}:`;
      its.forEach(i => {
        txt += `\\n• ${i.num} - ${i.nome}: ⚠️ ${i.dano}`;
      });
    });
    txt += '\\n\\nObs.: relato baseado em condições visíveis no local, sem caráter pericial.';
    document.getElementById('v360c-result-text').textContent = txt;
    const ra = document.getElementById('v360c-result-area');
    ra.style.display = 'block';
    ra.scrollIntoView({ behavior:'smooth', block:'nearest' });
    return;
  }

  /* ── MOTO via v360 ── */
  if (danVeiculo === 'moto') {"""

assert OLD9 in html, 'ERRO: marcador 9 não encontrado'
html = html.replace(OLD9, NEW9, 1)
print('✅ 9. danGerarTexto atualizado')

# ════════════════════════════════════════════════════════════════
# 10. relFull_gerarTexto — tratar carro com v360cdb
# ════════════════════════════════════════════════════════════════
OLD10 = """      } else {
        const cfg_map = DAN_DIAGRAMAS[v.tipo];
        const porVista = { frontal: [], traseira: [], esquerda: [], direita: [] };
        Object.keys(v.danos).forEach(function(id) {
          const mapa = { F: 'frontal', T: 'traseira', E: 'esquerda', D: 'direita' };
          const vis = mapa[id.charAt(0)];
          if (vis) porVista[vis].push(id);
        });
        Object.entries(porVista).forEach(function([vista, pontos]) {
          if (!pontos.length) return;
          const cfg = cfg_map[vista];
          txt += '\\n' + DAN_VISTA_LABELS[vista] + ':\\n';
          pontos.forEach(function(id) {
            const ponto = cfg.pontos.find(function(p) { return p.id === id; });
            if (!ponto) return;
            const tipo = v.danos[id];
            const num = cfg.pontos.indexOf(ponto) + 1;
            txt += '• ' + ponto.label + ': ' + tipo + '\\n';
          });
        });
      }"""

NEW10 = """      } else if (v.tipo === 'carro' && v.v360cdb) {
        const V360C_NAMES_RL = { frente: 'Frente', tras: 'Traseira', direita: 'Lado Direito', esquerda: 'Lado Esquerdo' };
        ['frente','tras','direita','esquerda'].forEach(function(t) {
          const its = v.v360cdb[t].filter(function(i) { return i.dano !== null; });
          if (!its.length) return;
          txt += '\\n' + V360C_NAMES_RL[t] + ':\\n';
          its.forEach(function(i) {
            txt += '• ' + i.nome + ': ' + i.dano + '\\n';
          });
        });
      } else {
        const cfg_map = DAN_DIAGRAMAS[v.tipo];
        const porVista = { frontal: [], traseira: [], esquerda: [], direita: [] };
        Object.keys(v.danos).forEach(function(id) {
          const mapa = { F: 'frontal', T: 'traseira', E: 'esquerda', D: 'direita' };
          const vis = mapa[id.charAt(0)];
          if (vis) porVista[vis].push(id);
        });
        Object.entries(porVista).forEach(function([vista, pontos]) {
          if (!pontos.length) return;
          const cfg = cfg_map[vista];
          txt += '\\n' + DAN_VISTA_LABELS[vista] + ':\\n';
          pontos.forEach(function(id) {
            const ponto = cfg.pontos.find(function(p) { return p.id === id; });
            if (!ponto) return;
            const tipo = v.danos[id];
            const num = cfg.pontos.indexOf(ponto) + 1;
            txt += '• ' + ponto.label + ': ' + tipo + '\\n';
          });
        });
      }"""

assert OLD10 in html, 'ERRO: marcador 10 não encontrado'
html = html.replace(OLD10, NEW10, 1)
print('✅ 10. relFull_gerarTexto atualizado')

# ════════════════════════════════════════════════════════════════
# 11. v360saveModal — usar v360mode
# ════════════════════════════════════════════════════════════════
OLD11 = """function v360saveModal(dano){
  if(v360editId !== null){
    const item = v360db[v360tab].find(i=>i.id===v360editId);
    if(item) item.dano = dano;
  }
  v360closeModal(); v360render();
}"""

NEW11 = """function v360saveModal(dano){
  if(v360editId !== null){
    const db = v360mode === 'carro' ? v360cdb[v360ctab] : v360db[v360tab];
    const item = db.find(i=>i.id===v360editId);
    if(item) item.dano = dano;
  }
  v360closeModal();
  if(v360mode === 'carro') v360cRender(); else v360render();
}"""

assert OLD11 in html, 'ERRO: marcador 11 não encontrado'
html = html.replace(OLD11, NEW11, 1)
print('✅ 11. v360saveModal atualizado')

# ════════════════════════════════════════════════════════════════
# 12. v360clearDano — usar v360mode
# ════════════════════════════════════════════════════════════════
OLD12 = """function v360clearDano(){
  if(v360editId !== null){
    const item = v360db[v360tab].find(i=>i.id===v360editId);
    if(item) item.dano = null;
  }
  v360closeModal(); v360render();
}"""

NEW12 = """function v360clearDano(){
  if(v360editId !== null){
    const db = v360mode === 'carro' ? v360cdb[v360ctab] : v360db[v360tab];
    const item = db.find(i=>i.id===v360editId);
    if(item) item.dano = null;
  }
  v360closeModal();
  if(v360mode === 'carro') v360cRender(); else v360render();
}"""

assert OLD12 in html, 'ERRO: marcador 12 não encontrado'
html = html.replace(OLD12, NEW12, 1)
print('✅ 12. v360clearDano atualizado')

# ════════════════════════════════════════════════════════════════
# 13. v360openEdit — set v360mode = 'moto'
# ════════════════════════════════════════════════════════════════
OLD13 = """function v360openEdit(id){
  const item = v360db[v360tab].find(i=>i.id===id); if(!item) return;
  v360editId = id;"""

NEW13 = """function v360openEdit(id){
  v360mode = 'moto';
  const item = v360db[v360tab].find(i=>i.id===id); if(!item) return;
  v360editId = id;"""

assert OLD13 in html, 'ERRO: marcador 13 não encontrado'
html = html.replace(OLD13, NEW13, 1)
print('✅ 13. v360openEdit atualizado')

# ════════════════════════════════════════════════════════════════
# 14. Adicionar variáveis e funções v360c após v360WhatsApp
# ════════════════════════════════════════════════════════════════
V360C_JS = """
/* ═══════════════════════════════════════════════════════════════
   CARRO 360 — variáveis, db e funções
═══════════════════════════════════════════════════════════════ */
const V360C_TABS  = ['frente','tras','direita','esquerda'];
const V360C_NAMES = {frente:'FRENTE',tras:'TRASEIRA',direita:'DIREITA',esquerda:'ESQUERDA'};

let v360cdb  = null;
let v360ctab = 'frente';
let v360mode = 'moto'; // 'moto' | 'carro'

function v360cMakeDb(){
  const cp = DAN_DIAGRAMAS.carro;
  const mk = (p, g) => ({id:'c_'+p.id, num:p.id, nome:p.label, grupo:g, dano:null, x:p.px, y:p.py});
  return {
    frente:   cp.frontal.pontos.map(p => mk(p,'FRONTAL')),
    tras:     cp.traseira.pontos.map(p => mk(p,'TRASEIRO')),
    direita:  cp.direita.pontos.map(p => mk(p,'DIREITA')),
    esquerda: cp.esquerda.pontos.map(p => mk(p,'ESQUERDA')),
  };
}

function v360cSwitchTab(el, t){
  v360ctab = t;
  document.querySelectorAll('#dan-step-carro360 .dan-tab').forEach(b=>b.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('#dan-step-carro360 .moto-img').forEach(i=>i.classList.remove('active'));
  document.getElementById('v360c-img-'+t).classList.add('active');
  document.getElementById('v360c-leg-vista').innerText = V360C_NAMES[t];
  v360cRender();
}

function v360cOpenEdit(id){
  if(!v360cdb) return;
  const item = v360cdb[v360ctab].find(i=>i.id===id); if(!item) return;
  v360mode = 'carro';
  v360editId = id;
  document.getElementById('v360-m-title').innerText = item.num+' — '+item.nome;
  document.getElementById('v360-m-sub').innerText   = item.grupo ? 'Grupo: '+item.grupo+'. Selecione a avaria.' : 'Selecione o tipo de avaria.';
  document.querySelectorAll('.v360-dbtn').forEach(b=>{
    b.classList.toggle('sel', b.dataset.val === item.dano);
  });
  const btnPend = document.getElementById('v360-btn-pend');
  if(btnPend) btnPend.style.display = item.dano !== null ? '' : 'none';
  document.getElementById('v360-overlay').classList.add('show');
}

function v360cRender(){
  document.querySelectorAll('#v360c-canvas .v360-pin').forEach(p=>p.remove());
  if(!v360cdb) return;
  v360cdb[v360ctab].forEach(item=>{
    const cor = v360corDano(item.dano);
    const ehAvaria = item.dano !== null;
    const pin = document.createElement('div');
    pin.className = 'v360-pin' + (ehAvaria?' avaria':'');
    pin.style.background = cor;
    pin.style.left = item.x+'%';
    pin.style.top  = item.y+'%';
    pin.innerText  = item.num;
    pin.title      = item.num+' — '+item.nome+': '+(item.dano||'Pendente');
    pin.onclick    = () => v360cOpenEdit(item.id);
    document.getElementById('v360c-canvas').appendChild(pin);
  });
  v360cRenderPalette();
  v360cUpdateSummary();
}

function v360cRenderPalette(){
  const list = document.getElementById('v360c-legend-list');
  if(!list || !v360cdb) return;
  const groups = {}, groupOrder = [];
  V360C_TABS.forEach(tab => {
    v360cdb[tab].forEach(item => {
      if(!groups[item.grupo]){ groups[item.grupo]=[]; groupOrder.push(item.grupo); }
      groups[item.grupo].push({tab, item});
    });
  });
  let html = '';
  groupOrder.forEach(gname => {
    html += `<div class="v360-pal-group"><div class="v360-pal-ghdr">${gname}</div>`;
    groups[gname].forEach(({tab, item}) => {
      const cor = v360corDano(item.dano);
      const statusLabel = item.dano || 'Pendente';
      html += `<div class="v360-pal-item" onclick="v360cSwitchTab(document.getElementById('v360c-tab-${tab}'),'${tab}');setTimeout(()=>v360cOpenEdit('${item.id}'),80);" title="${item.nome}">
        <div class="v360-pal-chip" style="background:${cor};color:#fff;">${item.num}</div>
        <div class="v360-pal-name">${item.nome}</div>
        <div class="v360-pal-badge" style="background:${cor};color:#fff;">${statusLabel}</div>
      </div>`;
    });
    html += `</div>`;
  });
  list.innerHTML = html;
}

function v360cUpdateSummary(){
  const container = document.getElementById('v360c-summary-tags');
  if(!container || !v360cdb) return;
  const total   = V360C_TABS.reduce((s,t)=>s+v360cdb[t].length, 0);
  const insp    = V360C_TABS.reduce((s,t)=>s+v360cdb[t].filter(i=>i.dano!==null).length, 0);
  const avarias = insp;
  const pct = total ? Math.round(insp/total*100) : 0;
  let html = `<div style="margin-bottom:10px;">
    <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:4px;">
      <span>📋 Posicionadas: <b style="color:var(--text)">${total}</b> &nbsp;·&nbsp; Inspecionadas: <b style="color:var(--text)">${insp}</b></span>
      <span>🚨 Avarias: <b style="color:${avarias?'#ef4444':'#22c55e'}">${avarias}</b></span>
    </div>
    <div style="height:6px;background:var(--border);border-radius:4px;overflow:hidden;">
      <div style="height:100%;width:${pct}%;background:${avarias?'#e67e22':'#22c55e'};border-radius:4px;transition:width .3s"></div>
    </div>
  </div>`;
  const avTags = [];
  V360C_TABS.forEach(t => {
    v360cdb[t].filter(i=>i.dano!==null).forEach(item => {
      const cor   = v360corDano(item.dano);
      const emoji = item.dano==='Quebrado'?'🔴':item.dano==='Trincado'?'🟠':item.dano==='Riscado'?'🟡':'🟣';
      avTags.push(`<span class="dan-tag" style="background:${cor};color:#fff;cursor:pointer;" onclick="v360cSwitchTab(document.getElementById('v360c-tab-${t}'),'${t}');setTimeout(()=>v360cOpenEdit('${item.id}'),80);" title="Clique para editar">${emoji} ${item.num}. ${item.nome} — ${item.dano}</span>`);
    });
  });
  if(avTags.length){
    html += `<div style="font-size:11px;font-weight:700;color:var(--label);text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px;">⚠️ Avarias detectadas</div><div>${avTags.join('')}</div>`;
  } else if(insp > 0){
    html += `<div style="font-size:13px;color:#22c55e;text-align:center;padding:8px 0;">✅ Nenhuma avaria registrada.</div>`;
  } else {
    html += `<div style="font-size:13px;color:var(--label);text-align:center;padding:8px 0;">Clique nos círculos na foto para classificar o dano.</div>`;
  }
  container.innerHTML = html;
}

function v360cLimpar(){
  if(confirm('Resetar toda a vistoria do carro? As classificações serão apagadas.')){
    v360cdb = v360cMakeDb();
    v360cSwitchTab(document.getElementById('v360c-tab-frente'),'frente');
    v360cRender();
  }
}

function v360cCopiar(btn){
  navigator.clipboard.writeText(document.getElementById('v360c-result-text').textContent).then(()=>{
    const old = btn.innerHTML; btn.innerHTML = '✅ Copiado!';
    setTimeout(()=> btn.innerHTML = old, 2000);
  });
}

function v360cWhatsApp(){
  window.open('https://wa.me/?text=' + encodeURIComponent(document.getElementById('v360c-result-text').textContent), '_blank');
}
"""

OLD14 = """function v360WhatsApp(){
  window.open('https://wa.me/?text=' + encodeURIComponent(document.getElementById('v360-result-text').textContent), '_blank');
}

/* ---------------------------------------------------------------
   RELATÓRIO COMPLETO (Envolvidos + Danos)"""

NEW14 = """function v360WhatsApp(){
  window.open('https://wa.me/?text=' + encodeURIComponent(document.getElementById('v360-result-text').textContent), '_blank');
}
""" + V360C_JS + """
/* ---------------------------------------------------------------
   RELATÓRIO COMPLETO (Envolvidos + Danos)"""

assert OLD14 in html, 'ERRO: marcador 14 não encontrado'
html = html.replace(OLD14, NEW14, 1)
print('✅ 14. Funções v360c adicionadas')

# ════════════════════════════════════════════════════════════════
# Salvar
# ════════════════════════════════════════════════════════════════
with open(HTML, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'\n✅ Arquivo salvo: {len(html)} chars (antes: {orig_len}, diff: +{len(html)-orig_len})')
