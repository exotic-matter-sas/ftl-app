import pdfjsLib from 'pdfjs-dist/webpack'

// pdfjsLib.disableWorker = true;
window.URL = window.URL || window.webkitURL;

export default {
  methods: {
    createThumb: function (file) {
      return new Promise((resolve, reject) => {
        let objectURL = window.URL.createObjectURL(file);

        pdfjsLib.getDocument(objectURL).then(function (pdf) {
          pdf.getPage(1).then(function (page) {
            const canvas = document.createElement("canvas");
            const context = canvas.getContext('2d');

            let viewport = page.getViewport(0.5);

            canvas.height = viewport.height;
            canvas.width = viewport.width;

            page.render({
              canvasContext: context,
              viewport: viewport
            }).then(function () {
              resolve(canvas.toDataURL());
            });
          }).catch(function () {
            reject("pdf thumb error: could not open page 1 of document " + filePath + ". Not a pdf ?");
          });
        }).catch(function () {
          reject("pdf thumb error: could not find or open document " + filePath + ". Not a pdf ?");
        });
      });
    }
  }
}
