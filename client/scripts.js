const GPTResearcher = {
  ws: null,
  startResearch: function () {
      // Connect to WebSocket
      this.ws = new WebSocket("ws://localhost:8000/ws");

      this.ws.addEventListener('open', () => {
          console.log("WebSocket connection opened.");

          // Collect the form data
          let task = document.getElementById("task").value;
          let agent = document.querySelector('input[name="agent"]:checked').value;
          let report_type = document.querySelector('select[name="report_type"]').value;
          let webToggle = document.getElementById("webToggle").checked;
          let kbToggle = document.getElementById("kbToggle").checked;

          let formData = {
              task: task,
              agent: agent,
              report_type: report_type,
              webToggle: webToggle,
              kbToggle: kbToggle
          };

          // Send the form data to start the research
          this.ws.send("start" + JSON.stringify(formData));
      });

      this.ws.addEventListener('message', (event) => {
          let response = JSON.parse(event.data);
          if (response.type === "logs") {
              let outputDiv = document.getElementById("output");
              let newLog = document.createElement("p");
              newLog.textContent = response.output;
              outputDiv.appendChild(newLog);

              // Highlight PDF access
              if (response.output.includes("Accessing uploaded PDF:")) {
                  newLog.style.color = "green";
                  newLog.style.fontWeight = "bold";
              }
          } else if (response.type === "report") {
              let reportContainer = document.getElementById("reportContainer");
              reportContainer.innerHTML = markdownToHtml(response.output);
              document.getElementById("status").innerText = "Research complete!";
          }
      });
  },
  copyToClipboard: function () {
      let reportContainer = document.getElementById("reportContainer");
      let text = reportContainer.innerText;
      let textArea = document.createElement("textarea");
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      alert("Report copied to clipboard.");
  }
};

function markdownToHtml(markdown) {
  let converter = new showdown.Converter();
  return converter.makeHtml(markdown);
}
