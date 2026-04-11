function showPage(page) {
	document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
	document.getElementById(page).classList.add("active");
}

/* --------------------
   NOTIFICATIONS
-------------------- */
const notifications = [
	"Your MRI analysis result is ready.",
	"You have a dose at 8:00 PM.",
	"Doctor updated your medication plan.",
];

const notificationList = document.getElementById("notificationList");

notifications.forEach(text => {
	const div = document.createElement("div");
	div.className = "notification-item";
	div.innerText = text;
	notificationList.appendChild(div);
});

/* --------------------
   MEDICATION PLAN
-------------------- */
function markTaken(btn) {
	btn.classList.add("taken");
	btn.innerText = "Taken ✓";
}

function addMedication() {
	const name = document.getElementById("medName").value;
	const dose = document.getElementById("medDose").value;
	const inst = document.getElementById("medInstructions").value;

	if (!name || !dose || !inst) return alert("Please fill all fields.");

	const container = document.querySelector("#medication .card:first-of-type");

	const newItem = document.createElement("div");
	newItem.className = "med-item";
	newItem.innerHTML = `
		<div>
			<h3>${name}</h3>
			<p>${dose} — ${inst}</p>
		</div>
		<button class="take-btn" onclick="markTaken(this)">Take</button>
	`;

	container.appendChild(newItem);

	document.getElementById("medName").value = "";
	document.getElementById("medDose").value = "";
	document.getElementById("medInstructions").value = "";
}

