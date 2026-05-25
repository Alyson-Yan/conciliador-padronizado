const form = document.getElementById("form-conciliacao");
const botao = document.getElementById("botao-conciliar");
const statusBox = document.getElementById("status");

const selectInstituicao = document.getElementById("instituicao");
const inputErp = document.getElementById("arquivo_erp");
const inputInstituicao = document.getElementById("arquivo_instituicao");

const institutionCards = document.querySelectorAll(".institution-btn");

const selectedName = document.getElementById("selected-name");
const selectedFormat = document.getElementById("selected-format");

const erpArea = document.getElementById("arquivo_erp").closest(".field");
const instituicaoArea = document.getElementById("arquivo_instituicao").closest(".field");

const instituicoes = {
    cielo: {
        nome: "Cielo",
        formato: ".xlsx",
        cor: "#2563eb",
        corSuave: "rgba(37, 99, 235, 0.16)",
        fundoPrimario: "rgba(37, 99, 235, 0.18)",
        fundoSecundario: "rgba(37, 99, 235, 0.08)"
    },
    santander: {
        nome: "Santander",
        formato: ".xlsx",
        cor: "#dc2626",
        corSuave: "rgba(220, 38, 38, 0.16)",
        fundoPrimario: "rgba(220, 38, 38, 0.18)",
        fundoSecundario: "rgba(220, 38, 38, 0.08)"
    },
    pagbank: {
        nome: "PagBank",
        formato: ".csv",
        cor: "#16a34a",
        corSuave: "rgba(22, 163, 74, 0.16)",
        fundoPrimario: "rgba(22, 163, 74, 0.18)",
        fundoSecundario: "rgba(22, 163, 74, 0.08)"
    },
    credishop: {
        nome: "CredShop",
        formato: ".csv",
        cor: "#f59e0b",
        corSuave: "rgba(245, 158, 11, 0.18)",
        fundoPrimario: "rgba(245, 158, 11, 0.20)",
        fundoSecundario: "rgba(245, 158, 11, 0.08)"
    }
};

function mostrarStatus(mensagem, tipo) {
    statusBox.textContent = mensagem;
    statusBox.className = `status ${tipo}`;
}

function limparStatus() {
    statusBox.textContent = "";
    statusBox.className = "status";
}

function obterExtensao(nomeArquivo) {
    const partes = nomeArquivo.toLowerCase().split(".");
    return partes.length > 1 ? `.${partes.pop()}` : "";
}

function obterArquivo(input) {
    return input.files && input.files.length > 0 ? input.files[0] : null;
}

function atualizarTemaInstituicao(dados) {
    document.documentElement.style.setProperty("--accent", dados.cor);
    document.documentElement.style.setProperty("--accent-soft", dados.corSuave);
    document.documentElement.style.setProperty("--page-glow", dados.fundoPrimario);
    document.documentElement.style.setProperty("--page-glow-secondary", dados.fundoSecundario);
}

function selecionarInstituicao(instituicao) {
    const dados = instituicoes[instituicao];

    atualizarTemaInstituicao(dados);

    selectInstituicao.value = instituicao;

    institutionCards.forEach((card) => {
        card.classList.toggle(
            "active",
            card.dataset.instituicao === instituicao
        );
    });

    selectedName.textContent = dados.nome;
    selectedFormat.textContent = "Agora envie os arquivos para continuar.";

    inputInstituicao.accept = dados.formato;
    inputInstituicao.value = "";
    instituicaoArea.classList.remove("valid", "invalid");

    limparStatus();
    atualizarBotao();
}

function validarArquivos() {
    const instituicao = selectInstituicao.value;
    const dados = instituicoes[instituicao];

    const arquivoErp = obterArquivo(inputErp);
    const arquivoInstituicao = obterArquivo(inputInstituicao);

    if (!dados) {
        return "Selecione uma instituição.";
    }

    if (!arquivoErp) {
        return "Selecione o arquivo ERP.";
    }

    if (obterExtensao(arquivoErp.name) !== ".csv") {
        return "O arquivo ERP deve ser um arquivo CSV.";
    }

    if (!arquivoInstituicao) {
        return "Selecione o arquivo da instituição.";
    }

    if (obterExtensao(arquivoInstituicao.name) !== dados.formato) {
        return `Arquivo inválido para ${dados.nome}.`;
    }

    return null;
}

function atualizarEstadoUploads() {
    const instituicao = selectInstituicao.value;
    const dados = instituicoes[instituicao];

    const arquivoErp = obterArquivo(inputErp);
    const arquivoInstituicao = obterArquivo(inputInstituicao);

    erpArea.classList.remove("valid", "invalid");
    instituicaoArea.classList.remove("valid", "invalid");

    if (arquivoErp) {
        erpArea.classList.add(
            obterExtensao(arquivoErp.name) === ".csv" ? "valid" : "invalid"
        );
    }

    if (arquivoInstituicao && dados) {
        instituicaoArea.classList.add(
            obterExtensao(arquivoInstituicao.name) === dados.formato ? "valid" : "invalid"
        );
    }

    atualizarBotao();
}

function atualizarBotao() {
    const erro = validarArquivos();
    botao.disabled = Boolean(erro);
}

institutionCards.forEach((card) => {
    card.addEventListener("click", () => {
        selecionarInstituicao(card.dataset.instituicao);
    });
});

inputErp.addEventListener("change", () => {
    atualizarEstadoUploads();

    const arquivo = obterArquivo(inputErp);

    if (arquivo && obterExtensao(arquivo.name) !== ".csv") {
        mostrarStatus("O arquivo ERP deve ser um arquivo CSV.", "erro");
    } else {
        limparStatus();
    }
});

inputInstituicao.addEventListener("change", () => {
    atualizarEstadoUploads();

    const erro = validarArquivos();

    if (erro) {
        mostrarStatus(erro, "erro");
    } else {
        mostrarStatus("Arquivos válidos. Clique para conciliar.", "sucesso");
    }
});

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const erroValidacao = validarArquivos();

    if (erroValidacao) {
        mostrarStatus(erroValidacao, "erro");
        return;
    }

    const instituicao = selectInstituicao.value;
    const arquivoErp = obterArquivo(inputErp);
    const arquivoInstituicao = obterArquivo(inputInstituicao);

    const formData = new FormData();
    formData.append("instituicao", instituicao);
    formData.append("arquivo_erp", arquivoErp);
    formData.append("arquivo_instituicao", arquivoInstituicao);

    botao.disabled = true;
    botao.textContent = "Conciliando...";
    mostrarStatus("Processando arquivos, aguarde...", "info");

    try {
        const resposta = await fetch("/conciliacao/executar", {
            method: "POST",
            body: formData
        });

        if (!resposta.ok) {
            const textoErro = await resposta.text();
            throw new Error(textoErro);
        }

        const blob = await resposta.blob();

        const contentDisposition = resposta.headers.get("content-disposition");
        let nomeArquivo = "relatorio_conciliacao.xlsx";

        if (contentDisposition && contentDisposition.includes("filename=")) {
            nomeArquivo = contentDisposition
                .split("filename=")[1]
                .replaceAll('"', "")
                .trim();
        }

        const url = window.URL.createObjectURL(blob);

        const linkDownload = document.createElement("a");
        linkDownload.href = url;
        linkDownload.download = nomeArquivo;
        document.body.appendChild(linkDownload);
        linkDownload.click();

        linkDownload.remove();
        window.URL.revokeObjectURL(url);

        mostrarStatus("Conciliação concluída. Download iniciado.", "sucesso");
    } catch (erro) {
        console.error(erro);
        mostrarStatus("Erro ao executar a conciliação.", "erro");
    } finally {
        botao.disabled = false;
        botao.textContent = "Conciliar e baixar relatório";
        atualizarBotao();
    }
});

atualizarBotao();