const steps = [
    "Uploading Image",
    "Analyzing Prescription...",
    "Extracting Medicine Names...",
    "Reading Dosages...",
    "Detecting Frequency & Duration...",
    "Preparing Result..."
];

let index = 0;

function updateState() {
    const step = document.getElementById("steptext");
    step.innerText = steps[index];
    index++;

    if (index < steps.length) {
        setTimeout(updateState, 1500);
    } else {
        window.location.href = RESULT_URL;

    }
}

updateState();
