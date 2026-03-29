/**
 * Módulo: Patrulhamento de Trânsito SC
 * Desenvolvido para registro rápido de infrações durante o patrulhamento.
 */

let PAT_VEICULOS = [];

/**
 * Formata a placa para o padrão (ABC1234 ou ABC1D23)
 */
function pat_formatarPlaca(el) {
    let val = el.value.toUpperCase().replace(/[^A-Z0-9]/g, '');
    if (val.length > 7) val = val.substring(0, 7);
    el.value = val;
}

/**
 * Obtém a localização via GPS para o patrulhamento
 */
function pat_obterGPS() {
    if (typeof gps_obterLocalizacao !== 'function') {
        alert("Módulo de GPS não encontrado.");
        return;
    }

    // Temporariamente sobrescrever o callback do GPS para preencher o campo correto
    const originalGPS = navigator.geolocation.getCurrentPosition;
    
    // Mostra feedback no botão de GPS da tela de patrulhamento
    const localInput = document.getElementById('pat_local');
    localInput.value = "Localizando...";

    navigator.geolocation.getCurrentPosition(
        (pos) => {
            const { latitude, longitude } = pos.coords;
            const res = gps_identificarRodoviaKM(latitude, longitude);
            if (res) {
                localInput.value = `${res.rodovia}, KM ${res.km.toFixed(1)}`;
            } else {
                localInput.value = "Rodovia não identificada";
                alert("Você não está em uma das rodovias mapeadas (SC-401, 405, 406, 407, 281).");
            }
        },
        (err) => {
            localInput.value = "";
            alert("Erro ao obter GPS: " + err.message);
        },
        { enableHighAccuracy: true, timeout: 10000 }
    );
}

/**
 * Controla a exibição do campo manual
 */
function pat_onInfracaoChange() {
    const select = document.getElementById('pat_infracao_select');
    const boxManual = document.getElementById('pat_box_manual');
    if (select.value === 'MANUAL') {
        boxManual.classList.remove('hidden');
    } else {
        boxManual.classList.add('hidden');
    }
}

/**
 * Salva o veículo na lista temporária
 */
function pat_salvarVeiculo() {
    const placa = document.getElementById('pat_placa').value;
    const local = document.getElementById('pat_local').value;
    const infracaoSelect = document.getElementById('pat_infracao_select').value;
    const infracaoManual = document.getElementById('pat_infracao_manual').value;

    if (!placa || placa.length < 7) {
        alert("Informe uma placa válida.");
        return;
    }

    if (!local) {
        alert("Obtenha a localização via GPS primeiro.");
        return;
    }

    let infracaoData = {};
    if (infracaoSelect === 'MANUAL') {
        if (!infracaoManual) {
            alert("Descreva a infração manual.");
            return;
        }
        infracaoData = { nome: infracaoManual, codigo: "---", gravidade: "---", artigo: "---" };
    } else if (infracaoSelect) {
        const partes = infracaoSelect.split('|');
        infracaoData = { nome: partes[0], codigo: partes[1], gravidade: partes[2], artigo: partes[3] };
    } else {
        alert("Selecione uma infração.");
        return;
    }

    const agora = new Date();
    const veiculo = {
        placa,
        local,
        data: agora.toLocaleDateString('pt-BR'),
        hora: agora.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }),
        infracao: infracaoData
    };

    PAT_VEICULOS.push(veiculo);
    pat_renderizarLista();
    pat_limparFormulario();
    
    // Mostrar feedback
    document.getElementById('pat_lista_card').classList.remove('hidden');
}

/**
 * Renderiza a lista de veículos salvos na tela
 */
function pat_renderizarLista() {
    const container = document.getElementById('pat_lista_container');
    container.innerHTML = "";

    PAT_VEICULOS.forEach((v, index) => {
        const item = document.createElement('div');
        item.className = "lote-item";
        item.style.borderLeft = "4px solid var(--primary)";
        item.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:start;">
                <div>
                    <strong>🚗 ${v.placa}</strong> - ${v.hora}<br>
                    <small>📍 ${v.local}</small><br>
                    <small>📑 ${v.infracao.nome}</small>
                </div>
                <button class="btn btn-sm btn-danger" onclick="pat_removerVeiculo(${index})">✕</button>
            </div>
        `;
        container.appendChild(item);
    });
}

/**
 * Remove um veículo da lista
 */
function pat_removerVeiculo(index) {
    PAT_VEICULOS.splice(index, 1);
    pat_renderizarLista();
    if (PAT_VEICULOS.length === 0) {
        document.getElementById('pat_lista_card').classList.add('hidden');
        document.getElementById('pat_result_area').classList.add('hidden');
    }
}

/**
 * Limpa o formulário após salvar
 */
function pat_limparFormulario() {
    document.getElementById('pat_placa').value = "";
    document.getElementById('pat_infracao_select').value = "";
    document.getElementById('pat_infracao_manual').value = "";
    document.getElementById('pat_box_manual').classList.add('hidden');
}

/**
 * Limpa toda a lista de patrulhamento
 */
function pat_limparTudo() {
    if (confirm("Deseja limpar todos os veículos registrados?")) {
        PAT_VEICULOS = [];
        pat_renderizarLista();
        document.getElementById('pat_lista_card').classList.add('hidden');
        document.getElementById('pat_result_area').classList.add('hidden');
    }
}

/**
 * Gera o texto final do relatório
 */
function pat_gerarRelatorio() {
    if (PAT_VEICULOS.length === 0) return;

    let txt = `🚨 *RELATÓRIO DE PATRULHAMENTO - PMRv SC*\n`;
    txt += `📅 Data: ${PAT_VEICULOS[0].data}\n`;
    txt += `━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n`;

    PAT_VEICULOS.forEach((v, i) => {
        txt += `*VEÍCULO ${i + 1}*\n`;
        txt += `Placa: ${v.placa}\n`;
        txt += `Hora: ${v.hora}\n`;
        txt += `Local: ${v.local}\n`;
        txt += `Infração: ${v.infracao.nome}\n`;
        txt += `Enquadramento: ${v.infracao.codigo}\n`;
        txt += `Gravidade: ${v.infracao.gravidade}\n`;
        txt += `Amparo Legal: ${v.infracao.artigo}\n`;
        txt += `──────────────────────────\n\n`;
    });

    txt += `_Gerado via PMRv Operacional_`;

    document.getElementById('pat_result_text').innerText = txt;
    document.getElementById('pat_result_area').classList.remove('hidden');
    
    // Scroll para o resultado
    document.getElementById('pat_result_area').scrollIntoView({ behavior: 'smooth' });
}

/**
 * Compartilha via WhatsApp
 */
function pat_whatsapp() {
    const txt = document.getElementById('pat_result_text').innerText;
    const url = "https://api.whatsapp.com/send?text=" + encodeURIComponent(txt);
    window.open(url, '_blank');
}

/**
 * Download em formato TXT
 */
function pat_downloadTXT() {
    const txt = document.getElementById('pat_result_text').innerText;
    const blob = new Blob([txt], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Patrulhamento_PMRv_${new Date().toLocaleDateString('pt-BR').replace(/\//g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}
