function goHome() { window.location.href = 'dashboard.html'; }

// --- Occupancy dynamique ---
let currentOccupancy = 0;
const maxPartial = 20;
const availabilityElem = document.getElementById('availability');
const occupancyElem = document.getElementById('occupancy');
const inBadge = document.getElementById('inBadge');
const inRoomBtn = document.getElementById('inRoomBtn');

function updateOccupancyDisplay() {
  occupancyElem.textContent = currentOccupancy + " people";

  // Priority to Schedule
  if (window.currentScheduleClass) {
    availabilityElem.textContent = "🔴 Occupied (" + window.currentScheduleClass + ")";
    availabilityElem.className = "occupied";
    return;
  }

  if (currentOccupancy === 0) {
    availabilityElem.textContent = "🟢 Free";
    availabilityElem.className = "free";
  } else if (currentOccupancy <= maxPartial) {
    availabilityElem.textContent = "🟠 Partial";
    availabilityElem.className = "partial";
  } else {
    availabilityElem.textContent = "🔴 Occupied";
    availabilityElem.className = "occupied";
  }
}

// --- Toast function ---
function showToast(message, color = "#2ecc71") {
  const toast = document.getElementById("toast");
  toast.textContent = message;
  toast.style.backgroundColor = color;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 5000);
}

// --- Reward function ---
function addRewardPoints(points) {
  let score = parseInt(localStorage.getItem("userScore")) || 0;
  score += points;
  localStorage.setItem("userScore", score);
  return score;
}

function showBadge(score) {
  let badgesSeen = JSON.parse(localStorage.getItem("badgesSeen")) || [];

  if (score >= 10 && !badgesSeen.includes("🥉 Contributor")) {
    showToast("Badge unlocked: 🥉 Contributor!");
    badgesSeen.push("🥉 Contributor");
  }
  if (score >= 50 && !badgesSeen.includes("🥈 Active Helper")) {
    showToast("Badge unlocked: 🥈 Active Helper!");
    badgesSeen.push("🥈 Active Helper");
  }
  if (score >= 100 && !badgesSeen.includes("🥇 Super User")) {
    showToast("Badge unlocked: 🥇 Super User!");
    badgesSeen.push("🥇 Super User");
  }
  if (score >= 200 && !badgesSeen.includes("🏆 Campus Hero")) {
    showToast("Badge unlocked: 🏆 Campus Hero!");
    badgesSeen.push("🏆 Campus Hero");
  }

  localStorage.setItem("badgesSeen", JSON.stringify(badgesSeen));
}

// --- Boutons "I am in / I left" ---
function enterRoom() {
  currentOccupancy++;
  updateOccupancyDisplay();
  inBadge.style.display = "inline";
  inRoomBtn.textContent = "✅ In the room";
  inRoomBtn.disabled = true;
  inRoomBtn.classList.add("in-room-active");

  // Ajouter 10 points au score global
  let score = addRewardPoints(10);

  // Afficher notification toast
  showToast(`🎉+10 points! Total score: ${score}`);

  // Vérifier badge
  showBadge(score);
}

function leaveRoom() {
  if (currentOccupancy > 0) currentOccupancy--;
  updateOccupancyDisplay();
  inBadge.style.display = "none";
  inRoomBtn.textContent = "I am in this room";
  inRoomBtn.disabled = false;
  inRoomBtn.classList.remove("in-room-active");
}

// --- Make a change ---
function makeChange() {
  if (!inRoomBtn.disabled) {
    showToast("⚠️ You must be IN the room to change occupancy", "#e74c3c");
    return;
  }
  // Affiche la modal
  document.getElementById("occupancyModal").style.display = "flex";
  document.getElementById("newOccupancyInput").value = currentOccupancy; // valeur par défaut
  document.getElementById("newOccupancyInput").focus();
}

function closeOccupancyModal() {
  document.getElementById("occupancyModal").style.display = "none";
}

// Valider le nouveau nombre
function submitOccupancyChange() {
  const input = document.getElementById("newOccupancyInput");
  let newOccupancy = parseInt(input.value);
  if (!isNaN(newOccupancy) && newOccupancy >= 1) {
    currentOccupancy = newOccupancy;
    updateOccupancyDisplay();
    showToast(`✅ Occupancy updated to ${newOccupancy} people`);
    closeOccupancyModal();
  } else {
    showToast("❌ Please enter a valid number >= 1", "#e74c3c");
  }
}


// Initial display
updateOccupancyDisplay();

// --- Exposed logic for dynamic rooms ---
window.setCurrentRoomId = function (id) {
  // Current logic doesn't use ID much except logic, can add here if needed
  console.log("Room context set to:", id);
};

// --- Expose functions to global scope for HTML onclick attributes ---
window.goHome = goHome;
window.enterRoom = enterRoom;
window.leaveRoom = leaveRoom;
window.makeChange = makeChange;
window.submitOccupancyChange = submitOccupancyChange;
window.closeOccupancyModal = closeOccupancyModal;

window.setCurrentOccupancy = function (val) {
  currentOccupancy = val;
  updateOccupancyDisplay();
};

// --- Sensors.js update for other values ---
// Removed fixed interval here to avoid conflict with room.html logic
// function updateSensorsDisplay() { ... }