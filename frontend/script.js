const form = document.getElementById("form-conciliacao");
const botao = document.getElementById("botao-conciliar");
const statusBox = document.getElementById("status");

function mostrarStatus(mensagem, tipo) {
    statusBox.textContent = mensagem;
    statusBox.className = `status ${tipo}`;
}

form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const instituicao = document.getElementById("instituicao").value;
    const arquivoErp = document.getElementById("arquivo_erp").files[0];
    const arquivoInstituicao = document.getElementById("arquivo_instituicao").files[0];

    if (!instituicao || !arquivoErp || !arquivoInstituicao) {
        mostrarStatus("Preencha todos os campos antes de conciliar.", "erro");
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
        const resposta = await fetch("http://127.0.0.1:8000/conciliacao/executar", {
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