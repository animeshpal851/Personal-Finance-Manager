/**
 * library-viz.js
 * Singly Linked List visualization with real-time animation.
 *
 * Entry points:
 *   renderLinkedList(nodes)          – draw the full list
 *   animateTraversal(steps, onDone)  – step-by-step traversal highlight
 *   animateDelete(bookId, form)      – fetch traversal steps then delete
 */

"use strict";

// ── Configuration ─────────────────────────────────────────────────────────────
const STEP_DELAY_MS = 500;   // ms between traversal steps
const COLORS = {
  normal:   "var(--bg-card)",
  visiting: "rgba(255,184,0,0.25)",
  found:    "rgba(79,195,247,0.30)",
  deleting: "rgba(255,79,106,0.35)",
  border: {
    normal:   "var(--border)",
    visiting: "var(--warning)",
    found:    "var(--info)",
    deleting: "var(--danger)",
  },
};

// ── DOM helpers ───────────────────────────────────────────────────────────────
const container = () => document.getElementById("llViz");
const statusBar  = () => document.getElementById("animStatus");
const statusMsg  = () => document.getElementById("animMsg");

function setStatus(msg, visible = true) {
  statusBar().style.display = visible ? "flex" : "none";
  if (msg) statusMsg().textContent = msg;
}

// ── Build node HTML ───────────────────────────────────────────────────────────
function buildNode(node, isHead) {
  const wrapper = document.createElement("div");
  wrapper.className = "ll-node-wrap";
  wrapper.dataset.nodeId = node.book_id;

  let headLabel = "";
  if (isHead) {
    headLabel = `<div class="ll-head-label">HEAD</div>`;
  }

  wrapper.innerHTML = `
    ${headLabel}
    <div class="ll-node" id="node-${CSS.escape(node.book_id)}">
      <div class="ll-node-id">${escHtml(node.book_id)}</div>
      <div class="ll-node-title">${escHtml(node.title)}</div>
      <div class="ll-node-author">${escHtml(node.author)}</div>
      ${node.genre ? `<div class="ll-node-genre">${escHtml(node.genre)}</div>` : ""}
      <div class="ll-node-ptr">next →</div>
    </div>
    ${node.has_next
      ? `<div class="ll-arrow"><span class="ll-arrow-line"></span><span class="ll-arrow-head">▶</span></div>`
      : `<div class="ll-null"><span class="ll-null-label">NULL</span></div>`
    }
  `;
  return wrapper;
}

// ── Render the full linked list ───────────────────────────────────────────────
function renderLinkedList(data) {
  const c = container();
  c.innerHTML = "";

  if (!data || !data.nodes || data.nodes.length === 0) {
    c.innerHTML = `
      <div class="ll-empty">
        <i class="fas fa-unlink"></i>
        <span>Linked list is empty — add a book to create the first node.</span>
      </div>`;
    return;
  }

  data.nodes.forEach((node, idx) => {
    c.appendChild(buildNode(node, idx === 0));
  });

  // Update stat counter
  const stat = document.getElementById("stat-total");
  if (stat) stat.textContent = data.total;
}

// ── Highlight a single node ───────────────────────────────────────────────────
function highlightNode(bookId, state) {
  const el = document.getElementById(`node-${CSS.escape(bookId)}`);
  if (!el) return;
  el.style.background     = COLORS[state]          || COLORS.normal;
  el.style.borderColor    = COLORS.border[state]   || COLORS.border.normal;
  el.style.boxShadow      = state !== "normal"
    ? `0 0 16px ${COLORS.border[state]}`
    : "none";
}

function resetAllHighlights() {
  document.querySelectorAll(".ll-node").forEach(el => {
    el.style.background  = "";
    el.style.borderColor = "";
    el.style.boxShadow   = "";
  });
}

// ── Animate traversal (search / delete preview) ───────────────────────────────
function animateTraversal(steps, onDone) {
  if (!steps || steps.length === 0) {
    if (onDone) onDone();
    return;
  }

  setStatus("Traversing linked list…");
  resetAllHighlights();

  let i = 0;
  function doStep() {
    if (i >= steps.length) {
      setStatus("", false);
      if (onDone) onDone();
      return;
    }
    const step = steps[i++];
    const state = step.action === "found" ? "found"
                : step.action === "visit" ? "visiting"
                : step.action;

    setStatus(`Step ${i}/${steps.length}: Node ${step.node_id} — ${step.action}`);
    highlightNode(step.node_id, state);

    // Scroll the node into view inside the scroll container
    const el = document.getElementById(`node-${CSS.escape(step.node_id)}`);
    if (el) el.scrollIntoView({ behavior: "smooth", inline: "center", block: "nearest" });

    setTimeout(doStep, STEP_DELAY_MS);
  }
  doStep();
}

// ── Animate delete: show traversal then let form submit ───────────────────────
function animateDelete(bookId, form) {
  // Prevent immediate form submit
  const steps = [];

  // Collect traversal steps by walking visible nodes (stop after target found)
  const wraps = document.querySelectorAll(".ll-node-wrap");
  for (let idx = 0; idx < wraps.length; idx++) {
    const wrap = wraps[idx];
    const id = wrap.dataset.nodeId;
    steps.push({
      node_id: id,
      action: id === bookId ? "found" : "visit",
      position: idx,
    });
    if (id === bookId) break; // stop after finding the target
  }

  setStatus(`Deleting node ${bookId}…`);
  resetAllHighlights();

  let i = 0;
  function doStep() {
    if (i >= steps.length) {
      // Mark target as deleting for a moment, then submit
      highlightNode(bookId, "deleting");
      setStatus(`Removing node ${bookId} from list…`);
      setTimeout(() => form.submit(), 700);
      return;
    }
    const step = steps[i++];
    const state = step.action === "found" ? "found" : "visiting";
    setStatus(`Traversing — visiting node ${step.node_id}`);
    highlightNode(step.node_id, state);
    setTimeout(doStep, STEP_DELAY_MS);
  }
  doStep();
  return false; // block default form submit
}

// ── Animate search results ────────────────────────────────────────────────────
function animateSearch(steps) {
  if (!steps || steps.length === 0) return;
  setStatus("Replaying search traversal…");
  animateTraversal(steps, () => setStatus("", false));
}

// ── Edit row: fill update form ────────────────────────────────────────────────
function attachEditHandlers() {
  document.querySelectorAll(".btn-edit-row").forEach(btn => {
    btn.addEventListener("click", () => {
      const id     = btn.dataset.id;
      const title  = btn.dataset.title;
      const author = btn.dataset.author;
      const genre  = btn.dataset.genre || "";

      document.getElementById("updateId").value     = id;
      document.getElementById("updateTitle").value  = title;
      document.getElementById("updateAuthor").value = author;
      document.getElementById("updateGenre").value  = genre;

      // Update form action
      document.getElementById("updateBookForm").action =
        `/library/update/${encodeURIComponent(id)}`;

      // Scroll to update form
      document.getElementById("updateBookForm").scrollIntoView({ behavior: "smooth" });
    });
  });
}

// ── Initialise ────────────────────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
  // Render the linked list
  renderLinkedList(VIZ_DATA);

  // If this was a search page, replay traversal animation
  if (SEARCH_Q && SEARCH_STEPS && SEARCH_STEPS.length > 0) {
    setTimeout(() => animateSearch(SEARCH_STEPS), 600);
  }

  attachEditHandlers();
});

// ── Utility ───────────────────────────────────────────────────────────────────
function escHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}
