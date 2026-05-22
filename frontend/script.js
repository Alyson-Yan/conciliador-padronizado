const form = document.getElementById("form-conciliacao");
const botao = document.getElementById("botao-conciliar");
const statusBox = document.getElementById("status");

const selectInstituicao = document.getElementById("instituicao");
const inputErp = document.getElementById("arquivo_erp");
const inputInstituicao = document.getElementById("arquivo_instituicao");

const formatosPorInstituicao = {
    cielo: [".xlsx"],
    santander: [".xlsx"],
    credishop: [".csv"],
    pagbank: [".csv"]
};

function mostrarStatus(mensagem, tipo) {
    statusBox.textContent = mensagem;
    statusBox.className = `status ${tipo}`;
}

function obterExtensao(nomeArquivo) {
    const partes = nomeArquivo.toLowerCase().split(".");
    return partes.length > 1 ? `.${partes.pop()}` : "";
}

function atualizarAceiteArquivoInstituicao() {
    const instituicao = selectInstituicao.value;
    const formatos = formatosPorInstituicao[instituicao] || [];

    inputInstituicao.accept = formatos.join(",");
    inputInstituicao.value = "";

    if (!instituicao) {
        mostrarStatus("Selecione uma instituição para saber o formato aceito.", "info");
        return;
    }

    mostrarStatus(
        `Formato aceito para ${instituicao}: ${formatos.join(", ")}`,
        "info"
    );
}

function validarArquivos(instituicao, arquivoErp, arquivoInstituicao) {
    const extensaoErp = obterExtensao(arquivoErp.name);
    const extensaoInstituicao = obterExtensao(arquivoInstituicao.name);

    if (extensaoErp !== ".csv") {
        return "O arquivo ERP deve ser sempre .csv.";
    }

    const formatosAceitos = formatosPorInstituicao[instituicao];

    if (!formatosAceitos) {
        return "Instituição inválida.";
    }

    if (!formatosAceitos.includes(extensaoInstituicao)) {
        return `Arquivo inválido para ${instituicao}. Formatos aceitos: ${formatosAceitos.join(", ")}.`;
    }

    return null;
}

selectInstituicao.addEventListener("change", atualizarAceiteArquivoInstituicao);

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const instituicao = selectInstituicao.value;
    const arquivoErp = inputErp.files[0];
    const arquivoInstituicao = inputInstituicao.files[0];

    if (!instituicao || !arquivoErp || !arquivoInstituicao) {
        mostrarStatus("Preencha todos os campos antes de conciliar.", "erro");
        return;
    }

    const erroValidacao = validarArquivos(
        instituicao,
        arquivoErp,
        arquivoInstituicao
    );

    if (erroValidacao) {
        mostrarStatus(erroValidacao, "erro");
        return;
    }

    const formData = new FormData();
    formData.append("instituicao", instituicao);
    formData.append("arquivo_erp", arquivoErp);
    formData.append("arquivo_instituicao", arquivoInstituicao);

    botao.disabled = true;
    botao.textContent = "Conciliando...";
    mostrarStatus("Processando arquivos. Aguarde...", "info");

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

        mostrarStatus("Conciliação concluída. O download foi iniciado.", "sucesso");
    } catch (erro) {
        console.error(erro);
        mostrarStatus("Erro ao executar conciliação. Veja o terminal da API.", "erro");
    } finally {
        botao.disabled = false;
        botao.textContent = "Conciliar";
    }
});