const API_URL = "http://127.0.0.1:8000/recommend";

const defaultScenario = {
  hero: "Anti-Mage",
  role: "carry",
  minute: 14,
  level: 10,
  gold: 1800,
  items: ["Power Treads", "Ring of Health", "Claymore"],
  hp_percent: 70,
  game_state: "enemy_pressure_mid",
  team_status: "supports_dead"
};

const scenarioInput = document.querySelector("#scenario-input");
const recommendButton = document.querySelector("#recommend-button");
const resultPanel = document.querySelector("#result-panel");
const errorPanel = document.querySelector("#error-panel");
const errorMessage = document.querySelector("#error-message");

const resultFields = {
  action: document.querySelector("#result-action"),
  reason: document.querySelector("#result-reason"),
  risk: document.querySelector("#result-risk"),
  priority: document.querySelector("#result-priority"),
  time_window: document.querySelector("#result-time-window"),
  source: document.querySelector("#result-source")
};

scenarioInput.value = JSON.stringify(defaultScenario, null, 2);

recommendButton.addEventListener("click", async () => {
  clearMessages();
  recommendButton.disabled = true;
  recommendButton.textContent = "Loading...";

  try {
    const payload = parseScenario();
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });

    const data = await readJsonResponse(response);

    if (!response.ok) {
      throw new Error(formatBackendError(data, response.status));
    }

    showRecommendation(data);
  } catch (error) {
    showError(error.message);
  } finally {
    recommendButton.disabled = false;
    recommendButton.textContent = "Get Recommendation";
  }
});

function parseScenario() {
  try {
    return JSON.parse(scenarioInput.value);
  } catch (error) {
    throw new Error(`Invalid JSON: ${error.message}`);
  }
}

async function readJsonResponse(response) {
  const text = await response.text();

  if (!text) {
    return {};
  }

  try {
    return JSON.parse(text);
  } catch {
    throw new Error(`Backend returned non-JSON response with status ${response.status}.`);
  }
}

function showRecommendation(data) {
  for (const field of Object.keys(resultFields)) {
    resultFields[field].textContent = data[field] ?? "";
  }

  resultPanel.classList.remove("hidden");
}

function showError(message) {
  errorMessage.textContent = message;
  errorPanel.classList.remove("hidden");
}

function clearMessages() {
  resultPanel.classList.add("hidden");
  errorPanel.classList.add("hidden");
  errorMessage.textContent = "";
}

function formatBackendError(data, status) {
  if (Array.isArray(data.detail)) {
    return data.detail
      .map((item) => {
        const location = Array.isArray(item.loc) ? item.loc.join(".") : "request";
        return `${location}: ${item.msg}`;
      })
      .join("\n");
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  return `Request failed with status ${status}.`;
}
