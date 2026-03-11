const fs = require('fs');
const pdf = require('pdf-parse');

const fileName = 'Agente_IA_Selecao_Curriculos.docx (1).pdf';

if (fs.existsSync(fileName)) {
    let dataBuffer = fs.readFileSync(fileName);
    pdf(dataBuffer).then(function (data) {
        console.log("--- PDF CONTENT START ---");
        console.log(data.text);
        console.log("--- PDF CONTENT END ---");
    }).catch(function (error) {
        console.log("ERROR parsing PDF:", error);
    });
} else {
    console.log("File not found:", fileName);
}
