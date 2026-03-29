/* ---------------------------------------------------------------
   INICIANDO O SERVIÇO - Lógica Otimizada (Baseada em React)
--------------------------------------------------------------- */
const POLICIAIS_EFETIVO = [
  'Sub Ten JORGE LUIZ', 'Sub Ten OSORIO',
  '2º Sgt BARDT', '2º Sgt CAVALLAZZI', '3º Sgt DOUGLAS', '3º Sgt FIGUEIREDO', '3º Sgt FRANCISCO', '3º Sgt FRANCINE', '3º Sgt LEONARDO', '3º Sgt MARTINS', '3º Sgt WALTER',
  'Cb ADEMIR', 'Cb ANDRADE', 'Cb CABRAL', 'Cb DIEGO', 'Cb FABIANA', 'Cb JEFERSON', 'Cb JULIANA', 'Cb MATHEUS', 'Cb RODRIGUES', 'Cb SANTOS', 'Cb SCARABELOT', 'Cb SILVA', 'Cb THIAGO'
];

// Estado da Tela
let ass_isMesa = false;
let ass_currentVtr = '';
let ass_currentEscala = '';
let ass_selectedPols = [];
let ass_lotes = []; // {id, numero, tipo, policiais:[], horario, isMesa}

// Inicialização ao carregar a tela
function ass_init() {
  ass_renderPols();
  ass_renderLotes();
  ass_updateUI();
  // Reset de escala ao iniciar
  ass_currentEscala = '';
  document.getElementById('ass_escala_wrap').classList.add('hidden');
}

// Alternar entre Mesa e Viatura
function ass_setMode(isMesa) {
  ass_isMesa = isMesa;
  if (isMesa) {
    ass_currentVtr = 'MESA';
    ass_currentEscala = '';
    document.getElementById('ass_escala_wrap').classList.add('hidden');
  } else {
    ass_currentVtr = '';
  }
  
  // Atualiza visual dos botões de modo
  document.getElementById('btn-mode-mesa').className = isMesa ? 'btn btn-primary flex-1' : 'btn flex-1';
  document.getElementById('btn-mode-vtr').className = !isMesa ? 'btn btn-primary flex-1' : 'btn flex-1';
  
  // Esconde/Mostra seleção de viatura
  document.getElementById('ass_vtr_selection').classList.toggle('hidden', isMesa);
  document.getElementById('ass_confirm_btn').textContent = isMesa ? '➕ Adicionar Mesa' : '➕ Adicionar Viatura';
  
  ass_updateUI();
}

// Selecionar Viatura da Grid
function ass_selectVtr(vtr) {
  ass_currentVtr = vtr;
  document.getElementById('ass_vtr_manual_wrap').classList.add('hidden');
  
  // Mostra seleção de escala após escolher VTR
  document.getElementById('ass_escala_wrap').classList.remove('hidden');
  
  ass_updateUI();
}

function ass_toggleVtrManual() {
  const wrap = document.getElementById('ass_vtr_manual_wrap');
  wrap.classList.toggle('hidden');
  if (!wrap.classList.contains('hidden')) {
    ass_currentVtr = '__manual__';
    document.getElementById('ass_vtr_input_manual').focus();
    document.getElementById('ass_escala_wrap').classList.remove('hidden');
  }
  ass_updateUI();
}

// Selecionar Escala
function ass_selectEscala(escala) {
  ass_currentEscala = escala;
  document.getElementById('ass_escala_manual_wrap').classList.add('hidden');
  
  // Se for Ordinária, já sugere o horário de 24h
  if (escala === 'Ordinária') {
    document.getElementById('ass_horario_select').value = '07h às 07h';
    ass_onHorarioChange();
  }
  
  ass_updateUI();
}

function ass_toggleEscalaManual() {
  const wrap = document.getElementById('ass_escala_manual_wrap');
  wrap.classList.toggle('hidden');
  if (!wrap.classList.contains('hidden')) {
    ass_currentEscala = '__manual__';
    document.getElementById('ass_escala_input_manual').focus();
  }
  ass_updateUI();
}

// Renderizar Grid de Policiais
function ass_renderPols() {
  const grid = document.getElementById('ass_pol_grid');
  grid.innerHTML = '';
  POLICIAIS_EFETIVO.forEach(p => {
    const btn = document.createElement('button');
    const active = ass_selectedPols.includes(p);
    btn.className = `pol-chip ${active ? 'active' : ''}`;
    btn.textContent = p;
    btn.onclick = () => ass_togglePol(p);
    grid.appendChild(btn);
  });
}

function ass_togglePol(p) {
  const idx = ass_selectedPols.indexOf(p);
  if (idx > -1) ass_selectedPols.splice(idx, 1);
  else ass_selectedPols.push(p);
  ass_renderPols();
}

function ass_toggleManualPol() {
  document.getElementById('ass_manual_pol_wrap').classList.toggle('hidden');
}

function ass_addPolManual() {
  const grad = document.getElementById('ass_grad_manual').value;
  const nome = document.getElementById('ass_nome_manual').value.trim().toUpperCase();
  if (!nome) return;
  const completo = grad + ' ' + nome;
  if (!ass_selectedPols.includes(completo)) {
    ass_selectedPols.push(completo);
    ass_renderPols();
  }
  document.getElementById('ass_nome_manual').value = '';
}

function ass_onHorarioChange() {
  const select = document.getElementById('ass_horario_select');
  const wrap = document.getElementById('ass_horario_manual_wrap');
  wrap.classList.toggle('hidden', select.value !== '__manual__');
  if (select.value === '__manual__') {
    document.getElementById('ass_horario_input_manual').focus();
  }
}

// Gerenciamento de Lotes
function ass_addLote() {
  if (ass_selectedPols.length === 0) {
    alert('Selecione ao menos um policial.');
    return;
  }
  
  let vtrFinal = ass_currentVtr;
  if (vtrFinal === '__manual__') {
    vtrFinal = document.getElementById('ass_vtr_input_manual').value.trim();
    if (!vtrFinal) { alert('Informe o número da viatura.'); return; }
  }
  
  if (!ass_isMesa && !vtrFinal) {
    alert('Selecione uma viatura.');
    return;
  }

  let escalaFinal = ass_currentEscala;
  if (escalaFinal === '__manual__') {
    escalaFinal = document.getElementById('ass_escala_input_manual').value.trim();
    if (!escalaFinal) { alert('Informe o nome do evento.'); return; }
  }
  
  if (!ass_isMesa && !escalaFinal) {
    alert('Selecione o tipo de escala.');
    return;
  }

  let horarioFinal = document.getElementById('ass_horario_select').value;
  if (horarioFinal === '__manual__') {
    horarioFinal = document.getElementById('ass_horario_input_manual').value.trim();
    if (!horarioFinal) { alert('Informe o horário manual.'); return; }
  }
  
  const newLote = {
    id: Date.now().toString(),
    numero: ass_isMesa ? 'MESA' : vtrFinal,
    tipo: ass_isMesa ? '' : escalaFinal,
    policiais: [...ass_selectedPols],
    horario: horarioFinal,
    isMesa: ass_isMesa
  };

  ass_lotes.push(newLote);
  ass_resetCurrent(); // Limpa campos para o próximo
  ass_renderLotes();
}

function ass_resetCurrent() {
  ass_selectedPols = [];
  ass_currentVtr = '';
  ass_currentEscala = '';
  
  // Limpar inputs manuais
  document.getElementById('ass_vtr_input_manual').value = '';
  document.getElementById('ass_escala_input_manual').value = '';
  document.getElementById('ass_horario_input_manual').value = '';
  document.getElementById('ass_nome_manual').value = '';
  
  // Voltar selects para o padrão
  document.getElementById('ass_horario_select').value = '07h às 19h';
  
  // Esconder seções condicionais
  document.getElementById('ass_vtr_manual_wrap').classList.add('hidden');
  document.getElementById('ass_escala_manual_wrap').classList.add('hidden');
  document.getElementById('ass_horario_manual_wrap').classList.add('hidden');
  document.getElementById('ass_manual_pol_wrap').classList.add('hidden');
  
  if (!ass_isMesa) {
    document.getElementById('ass_escala_wrap').classList.add('hidden');
  } else {
    ass_currentVtr = 'MESA'; // Se estiver em modo mesa, mantém o valor interno
  }
  
  ass_renderPols();
  ass_updateUI();
  
  // Rolar para o topo da configuração
  document.querySelector('#screen-assumir .card').scrollIntoView({ behavior: 'smooth' });
}

function ass_clearAll() {
  if (confirm('Deseja limpar todo o relatório montado?')) {
    ass_lotes = [];
    ass_renderLotes();
    ass_resetCurrent();
  }
}

function ass_removeLote(id) {
  ass_lotes = ass_lotes.filter(l => l.id !== id);
  ass_renderLotes();
}

function ass_renderLotes() {
  const card = document.getElementById('ass_lotes_card');
  const container = document.getElementById('ass_lotes_container');
  
  if (ass_lotes.length === 0) {
    card.classList.add('hidden');
    return;
  }
  
  card.classList.remove('hidden');
  container.innerHTML = '';
  
  ass_lotes.forEach(l => {
    const div = document.createElement('div');
    div.className = 'lote-item';
    const infoVtr = l.isMesa ? '🪑 MESA P19' : `🚔 PM-${l.numero} — ${l.tipo}`;
    div.innerHTML = `
      <div style="flex:1">
        <div class="lote-title">
          ${infoVtr} 
          <span class="lote-horario">[${l.horario}]</span>
        </div>
        <div class="lote-pols">${l.policiais.join(' / ')}</div>
      </div>
      <button class="btn-remove" onclick="ass_removeLote('${l.id}')">✕</button>
    `;
    container.appendChild(div);
  });
}

// UI State Helpers
function ass_updateUI() {
  // Atualiza botões das viaturas
  document.querySelectorAll('#ass_vtr_grid .vtr-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent === ass_currentVtr);
  });
  
  // Atualiza botões de escala
  document.querySelectorAll('#ass_escala_grid .vtr-btn').forEach(btn => {
    btn.classList.toggle('active', btn.textContent === ass_currentEscala);
  });
}

// Geração de Texto Final
function ass_generateText() {
  const h = new Date().getHours();
  const saudacao = h >= 5 && h < 12 ? '☀️ Bom dia' : h >= 12 && h < 18 ? '🌤️ Boa tarde' : '🌙 Boa noite';
  let text = `${saudacao}! Guarnição iniciando serviço\n`;
  
  ass_lotes.forEach(l => {
    if (l.isMesa) {
      text += `🔹 Na Recepção do P19 (${l.horario})\n🔹 *Policiais:* ${l.policiais.join(' / ')}\n`;
    } else {
      text += `🔹 *Viatura* PM-${l.numero} — ${l.tipo}\n🔹 *Policiais:* ${l.policiais.join(' / ')}\n🔹 *Horário:* ${l.horario}\n`;
    }
  });
  
  text += `🔹 *Local:* P19\nBom serviço a todos! 👮‍♂️🚓`;
  return text;
}

function ass_copyText() {
  const text = ass_generateText();
  navigator.clipboard.writeText(text).then(() => alert('Texto copiado!'));
}

function ass_shareWhats() {
  const text = ass_generateText();
  window.open('https://wa.me/?text=' + encodeURIComponent(text), '_blank');
}

// Hook no core.js go()
const originalGo = window.go;
window.go = function(name) {
  if (originalGo) originalGo(name);
  if (name === 'assumir') ass_init();
};
