
from pathlib import Path
import csv
import json

ROOT = Path(__file__).resolve().parents[1]
TRACE_FILE = ROOT / "results" / "single_cycle_cycle_trace.csv"
OUTPUT_FILE = ROOT / "results" / "datapath_view.html"


def load_trace():
    if not TRACE_FILE.exists():
        raise FileNotFoundError(
            f"Trace file not found: {TRACE_FILE}\n"
            "Run the single-cycle simulator first."
        )

    with TRACE_FILE.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    if not rows:
        raise ValueError("The execution trace is empty.")

    required = {"PC", "Instruction", "NextPC"}
    missing = required - set(rows[0].keys())

    if missing:
        raise ValueError(
            "Missing CSV columns: " + ", ".join(sorted(missing))
        )

    return rows


HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Single-Cycle MIPS Datapath Viewer</title>
<style>
:root {
  --green: #16834a;
  --green-bg: #d9fbe5;
  --border: #d8deea;
  --text: #182230;
  --muted: #596579;
  --page: #f5f7fb;
}
* { box-sizing: border-box; }
body {
  font-family: system-ui, sans-serif;
  max-width: 1100px;
  margin: 24px auto;
  padding: 0 18px 36px;
  background: var(--page);
  color: var(--text);
}
.panel {
  background: white;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 18px;
  margin: 14px 0;
}
.toolbar {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}
button, select {
  font: inherit;
  padding: 9px 12px;
  border: 1px solid #9ba8ba;
  border-radius: 8px;
  background: white;
  color: var(--text);
}
button { cursor: pointer; }
button:disabled { opacity: .45; cursor: default; }
.small { color: var(--muted); font-size: .9rem; }
.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 10px;
}
.metric { background: #f5f7fb; padding: 12px; border-radius: 8px; }
.metric span { display: block; color: var(--muted); font-size: .85rem; }
.metric strong { display: block; margin-top: 5px; }
.diagram-scroll { overflow-x: auto; }
svg { width: 100%; min-width: 650px; height: auto; background: white; }
.node { fill: #f3f5f9; stroke: #8492a6; stroke-width: 2; }
.node.active { fill: var(--green-bg); stroke: var(--green); stroke-width: 3; }
.edge { stroke: #a5afbd; stroke-width: 2; fill: none; }
.edge.active { stroke: var(--green); stroke-width: 4; }
.node-label {
  font-size: 14px;
  text-anchor: middle;
  fill: var(--text);
  pointer-events: none;
}
pre {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  background: #f5f7fb;
  padding: 14px;
  border-radius: 8px;
}
footer { color: var(--muted); font-size: .85rem; }
</style>
</head>
<body>

<h1>Single-Cycle MIPS Datapath Viewer</h1>
<p class="small">
Green highlights show conceptual components associated with the selected
instruction. This is an educational architectural visualization, not
a gate-level timing simulation.
</p>

<section class="panel">
  <div class="toolbar">
    <label for="inst">Instruction:</label>
    <select id="inst"></select>
    <button id="prev" type="button">Previous</button>
    <button id="next" type="button">Next</button>
    <button id="first" type="button">First</button>
    <span id="status" class="small" aria-live="polite"></span>
  </div>
</section>

<section class="panel">
  <h2 id="heading">Datapath</h2>
  <p id="details"></p>
  <p id="signals"></p>

  <div class="metrics">
    <div class="metric"><span>Instruction</span><strong id="m-op">—</strong></div>
    <div class="metric"><span>PC</span><strong id="m-pc">—</strong></div>
    <div class="metric"><span>Next PC</span><strong id="m-next">—</strong></div>
    <div class="metric"><span>ALU control</span><strong id="m-alu">—</strong></div>
  </div>

  <div class="diagram-scroll">
  <svg viewBox="0 0 800 490" role="img"
       aria-label="Conceptual MIPS single-cycle datapath">
    <defs>
      <marker id="arrow" markerWidth="8" markerHeight="8"
              refX="6" refY="3" orient="auto">
        <path d="M0,0 L6,3 L0,6 Z" fill="#16834a"/>
      </marker>
    </defs>

    <g id="edges">
      <path id="e-fetch" class="edge" d="M140 60 H180"/>
      <path id="e-decode" class="edge" d="M310 60 H350"/>
      <path id="e-regalu" class="edge" d="M430 100 V145"/>
      <path id="e-immediate" class="edge" d="M310 170 H350"/>
      <path id="e-alumem" class="edge" d="M430 195 V240"/>
      <path id="e-memory" class="edge" d="M430 290 V330"/>
      <path id="e-loadwb" class="edge" d="M350 355 H310 V395"/>
      <path id="e-aluwb" class="edge" d="M510 170 H550 V395 H480"/>
      <path id="e-writeback" class="edge" d="M350 420 H245 V100"/>
      <path id="e-storedata" class="edge" d="M510 80 H580 V265 H510"/>
      <path id="e-branch" class="edge" d="M510 170 H620 V100"/>
      <path id="e-nextpc" class="edge" d="M700 100 V455 H80 V100"/>
    </g>

    <g id="n-pc">
      <rect class="node" x="20" y="25" width="120" height="75" rx="8"/>
      <text class="node-label" x="80" y="55">Program</text>
      <text class="node-label" x="80" y="75">Counter</text>
    </g>

    <g id="n-im">
      <rect class="node" x="180" y="25" width="130" height="75" rx="8"/>
      <text class="node-label" x="245" y="55">Instruction</text>
      <text class="node-label" x="245" y="75">Memory / Decode</text>
    </g>

    <g id="n-reg">
      <rect class="node" x="350" y="25" width="160" height="75" rx="8"/>
      <text class="node-label" x="430" y="55">Register File</text>
      <text class="node-label" x="430" y="75">Read operands</text>
    </g>

    <g id="n-immediate">
      <rect class="node" x="180" y="145" width="130" height="50" rx="8"/>
      <text class="node-label" x="245" y="165">Immediate</text>
      <text class="node-label" x="245" y="182">Operand</text>
    </g>

    <g id="n-alu">
      <rect class="node" x="350" y="145" width="160" height="50" rx="8"/>
      <text class="node-label" x="430" y="175">ALU</text>
    </g>

    <g id="n-mem">
      <rect class="node" x="350" y="240" width="160" height="50" rx="8"/>
      <text class="node-label" x="430" y="270">Data Memory</text>
    </g>

    <g id="n-wb">
      <rect class="node" x="350" y="330" width="160" height="50" rx="8"/>
      <text class="node-label" x="430" y="360">Write-back Mux</text>
    </g>

    <g id="n-control">
      <rect class="node" x="620" y="145" width="150" height="55" rx="8"/>
      <text class="node-label" x="695" y="168">Control Unit</text>
      <text class="node-label" x="695" y="186">Signals</text>
    </g>

    <g id="n-branch">
      <rect class="node" x="620" y="25" width="150" height="75" rx="8"/>
      <text class="node-label" x="695" y="55">Next-PC Logic</text>
      <text class="node-label" x="695" y="75">Branch / Jump</text>
    </g>

    <text x="20" y="480" font-size="12" fill="#596579">
      Simplified conceptual paths; not a physical hardware netlist.
    </text>
  </svg>
  </div>
</section>

<section class="panel">
  <h2>Control signals</h2>
  <pre id="control"></pre>
</section>

<section class="panel">
  <h2>Cycle trace</h2>
  <pre id="trace"></pre>
</section>

<footer>
The model and this visualization demonstrate architectural behavior.
They do not establish a custom single-cycle CPU implemented inside gem5.
</footer>

<script>
"use strict";

const rows = __TRACE_DATA__;
const select = document.getElementById("inst");

function get(row, ...keys) {
  for (const key of keys) {
    if (row[key] !== undefined && row[key] !== "") return row[key];
  }
  return "N/A";
}

function opOf(row) {
  return String(get(row, "Instruction", "instruction"))
    .trim().split(/\s+/)[0].toUpperCase();
}

function flag(row, key) {
  return ["1", "true", "yes"].includes(
    String(get(row, key)).toLowerCase()
  );
}

function node(id, on = true) {
  const element = document.querySelector("#n-" + id + " .node");
  if (element && on) element.classList.add("active");
}

function edge(id, on = true) {
  const element = document.getElementById("e-" + id);
  if (element && on) element.classList.add("active");
}

function show(index) {
  index = Math.max(0, Math.min(rows.length - 1, index));
  select.value = String(index);

  const r = rows[index];
  const op = opOf(r);
  const pc = get(r, "PC", "pc");
  const nextPC = get(r, "NextPC", "next_pc");
  const alu = get(r, "ALUOp", "ALUControl", "alu_control");

  document.getElementById("heading").textContent =
    `Cycle ${get(r, "Cycle", "cycle")} — ${get(r, "Instruction", "instruction")}`;

  document.getElementById("details").textContent =
    `PC = ${pc}; next PC = ${nextPC}; ALU control = ${alu}`;

  document.getElementById("signals").textContent =
    `RegWrite=${get(r, "RegWrite")}; MemRead=${get(r, "MemRead")}; ` +
    `MemWrite=${get(r, "MemWrite")}; Branch=${get(r, "Branch")}; ` +
    `Jump=${get(r, "Jump")}`;

  document.getElementById("m-op").textContent = op;
  document.getElementById("m-pc").textContent = pc;
  document.getElementById("m-next").textContent = nextPC;
  document.getElementById("m-alu").textContent = alu;
  document.getElementById("status").textContent =
    `${index + 1} of ${rows.length}`;

  const names = [
    "RegDst", "ALUSrc", "MemToReg", "RegWrite",
    "MemRead", "MemWrite", "Branch", "Jump", "ALUOp"
  ];

  document.getElementById("control").textContent =
    names.map(name => `${name.padEnd(10)} : ${get(r, name)}`).join("\n");

  document.getElementById("trace").textContent =
    JSON.stringify(r, null, 2);

  document.querySelectorAll(".node, .edge").forEach(el => {
    el.classList.remove("active");
  });

  // Every instruction begins with fetch and decode.
  node("pc");
  node("im");
  node("control");
  edge("fetch");
  edge("decode");

  const arithmetic = ["ADD", "SUB", "AND", "OR", "SLT"];
  const registerALU = [...arithmetic, "ADDI"];
  const aluInstructions = [...registerALU, "LW", "SW", "BEQ"];

  if (aluInstructions.includes(op)) {
    node("reg");
    node("alu");
    edge("regalu");
    edge("alumem", false);
  }

  if (["ADDI", "LW", "SW"].includes(op)) {
    node("immediate");
    edge("immediate");
  }

  if (op === "LW" || op === "SW") {
    node("mem");
    edge("memory");
  }

  if (op === "SW") {
    edge("storedata");
  }

  if (op === "LW") {
    node("wb");
    edge("loadwb");
    edge("writeback");
  }

  if (registerALU.includes(op)) {
    node("wb");
    edge("aluwb");
    edge("writeback");
  }

  if (op === "BEQ") {
    node("branch");
    edge("branch");
    edge("nextpc");
  }

  if (op === "J") {
    node("branch");
    edge("nextpc");
  }

  if (op !== "BEQ" && op !== "J") {
    edge("nextpc");
  }

  document.getElementById("prev").disabled = index === 0;
  document.getElementById("next").disabled = index === rows.length - 1;
  document.getElementById("first").disabled = index === 0;
}

rows.forEach((row, index) => {
  const option = document.createElement("option");
  option.value = String(index);
  option.textContent =
    `Cycle ${get(row, "Cycle", "cycle")}: ${get(row, "Instruction", "instruction")}`;
  select.appendChild(option);
});

select.addEventListener("change", () => show(Number(select.value)));
document.getElementById("prev").addEventListener(
  "click", () => show(Number(select.value) - 1)
);
document.getElementById("next").addEventListener(
  "click", () => show(Number(select.value) + 1)
);
document.getElementById("first").addEventListener("click", () => show(0));

show(0);
</script>
</body>
</html>
"""


def main():
    rows = load_trace()

    # Safely embed the trace as JSON in the HTML JavaScript.
    trace_json = json.dumps(rows, ensure_ascii=True).replace(
        "</", "<\\/"
    )

    page = HTML_TEMPLATE.replace("__TRACE_DATA__", trace_json)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(page, encoding="utf-8")

    print("Datapath viewer generated successfully.")
    print(f"Trace records: {len(rows)}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
