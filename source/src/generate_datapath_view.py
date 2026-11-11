import csv
import json
from pathlib import Path

# Expected location: submission/source/src/generate_datapath_view.py
SOURCE_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = SOURCE_ROOT.parent
RESULTS = PROJECT_ROOT / "results"
TRACE_FILE = RESULTS / "single_cycle_cycle_trace.csv"
OUTPUT_FILE = RESULTS / "datapath_view.html"


def load_trace():
    if not TRACE_FILE.exists():
        raise FileNotFoundError(
            f"Trace not found: {TRACE_FILE}\n"
            "Run: python source/src/cycle_trace.py"
        )

    with TRACE_FILE.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        raise ValueError("The execution trace is empty.")

    required = {
        "Cycle", "PC", "PCPlus4", "Instruction", "NextPC", "PCSource",
        "RegDst", "ALUSrc", "MemToReg", "RegWrite", "MemRead",
        "MemWrite", "Branch", "Jump", "ALUControl", "ReadRegister1",
        "ReadRegister2", "ReadData1", "ReadData2", "ALUResult",
        "BranchTaken", "JumpAddress", "DestinationRegister",
        "RegisterWriteData", "WritebackSource",
        "RegDstInput0", "RegDstInput1", "RegDstSelected",
        "ALUSrcInput0", "ALUSrcInput1", "ALUSrcSelected",
        "MemToRegInput0", "MemToRegInput1", "MemToRegSelected",
        "PCMuxInput0", "PCMuxInput1", "PCMuxInput2",
        "PCMuxSelected", "MemoryReadData",
    }

    missing = required - set(rows[0])
    if missing:
        raise ValueError(
            "Trace CSV is missing columns: " + ", ".join(sorted(missing))
        )

    return rows


HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Single-Cycle MIPS Datapath Viewer</title>
<style>
:root{--page:#f3f6fb;--panel:#fff;--ink:#172235;--muted:#617087;--line:#aab6c7;--active:#087f5b;--active-bg:#d9fbe9;--border:#d7dfeb}
*{box-sizing:border-box}
body{margin:0;padding:24px;background:var(--page);color:var(--ink);font:15px/1.45 system-ui,Segoe UI,sans-serif}
main{max-width:1500px;margin:auto}
h1{margin:0 0 5px}
h2{margin:0 0 12px;font-size:1.15rem}
.muted{color:var(--muted)}
.panel{background:var(--panel);border:1px solid var(--border);border-radius:14px;padding:18px;margin:14px 0;box-shadow:0 2px 8px #1722350a}
.toolbar{display:flex;flex-wrap:wrap;align-items:center;gap:10px}
button,select{font:inherit;padding:9px 13px;border:1px solid #9eacbf;border-radius:8px;background:white;color:var(--ink)}
button{cursor:pointer}
button:disabled{opacity:.4;cursor:default}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(135px,1fr));gap:10px;margin-top:14px}
.card{background:#f5f8fc;border-radius:9px;padding:11px}
.card span{display:block;color:var(--muted);font-size:.82rem}
.card strong{display:block;margin-top:4px;overflow-wrap:anywhere}
.diagram-wrap{overflow-x:auto}
svg{display:block;min-width:1200px;width:100%;height:auto;background:#fff;border:1px solid var(--border);border-radius:10px}
.node rect{fill:#f5f7fb;stroke:#7f8da2;stroke-width:2;rx:9}
.node text{fill:#1d2a3d;text-anchor:middle;font-size:13px;pointer-events:none}
.node.active rect{fill:var(--active-bg);stroke:var(--active);stroke-width:3}
.edge{fill:none;stroke:var(--line);stroke-width:2.2;marker-end:url(#arrow)}
.edge.active{stroke:var(--active);stroke-width:4}
.columns{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:14px}
pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f5f8fc;border-radius:9px;padding:13px;margin:0;font-size:.88rem}
.badge{display:inline-block;border-radius:99px;padding:3px 9px;background:#e8f1ff;font-size:.82rem;font-weight:650}
footer{margin:18px 0;color:var(--muted);font-size:.86rem}
</style>
</head>
<body>
<main>
<h1>Single-Cycle MIPS Datapath Viewer</h1>
<p class="muted">Select an instruction to inspect its recorded values and conceptual active path.</p>

<section class="panel">
<div class="toolbar">
<label for="instructionSelect"><b>Instruction:</b></label>
<select id="instructionSelect"></select>
<button id="first">First</button>
<button id="previous">Previous</button>
<button id="next">Next</button>
<span id="position" class="muted"></span>
<span id="pcSource" class="badge"></span>
</div>
<div class="cards">
<div class="card"><span>Instruction</span><strong id="mInstruction">—</strong></div>
<div class="card"><span>PC</span><strong id="mPC">—</strong></div>
<div class="card"><span>PC + 4</span><strong id="mPC4">—</strong></div>
<div class="card"><span>Next PC</span><strong id="mNextPC">—</strong></div>
<div class="card"><span>ALU result</span><strong id="mALU">—</strong></div>
<div class="card"><span>Write-back data</span><strong id="mWB">—</strong></div>
</div>
</section>

<section class="panel">
<h2>Conceptual single-cycle MIPS datapath</h2>
<div class="diagram-wrap">
<svg viewBox="0 0 1450 820" role="img" aria-label="Conceptual single-cycle MIPS datapath">
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#087f5b"/></marker></defs>
<g id="edges">
<!-- Fetch/decode and instruction fields -->
<path id="e-pc-im" class="edge" d="M140 105 H195"/>
<path id="e-im-reg" class="edge" d="M345 105 H390"/>
<path id="e-im-control" class="edge" d="M345 120 H365 V265 H390"/>
<path id="e-im-regdst" class="edge" d="M345 95 H365 V175 H560"/>
<path id="e-im-signext" class="edge" d="M345 130 H365 V475 H390"/>

<!-- Register operands, destination selection and ALU -->
<path id="e-reg-alu-a" class="edge" d="M545 105 H790 V355"/>
<path id="e-reg-alu-b" class="edge" d="M545 135 H650 V395 H690"/>
<path id="e-regdst" class="edge" d="M560 178 H575 V190 H365 V155 H390"/>
<path id="e-memtoreg-reg" class="edge" d="M1270 575 H1390 V35 H375 V135 H390"/>
<path id="e-regwrite-reg" class="edge" d="M545 292 H590 V215 H350 V165 H390"/>
<path id="e-signext-alu" class="edge" d="M545 475 H650 V430 H690"/>
<path id="e-alusrc-alu" class="edge" d="M775 405 H790"/>
<path id="e-control-alusrc" class="edge" d="M545 270 H650 V375 H690"/>
<path id="e-control-aluctrl" class="edge" d="M545 250 H800 V250 H850"/>
<path id="e-aluctrl-alu" class="edge" d="M920 290 V320 H845 V345"/>

<!-- Memory and write-back -->
<path id="e-alu-dmem" class="edge" d="M900 390 H1000"/>
<path id="e-reg-dmem" class="edge" d="M545 145 H965 V465 H1000"/>
<path id="e-alu-memtoreg" class="edge" d="M900 390 H950 V575 H1120"/>
<path id="e-dmem-memtoreg" class="edge" d="M1135 405 H1160 V575 H1120"/>

<!-- Sequential PC, branch and jump paths -->
<path id="e-pc-pc4" class="edge" d="M80 155 V690 H195"/>
<path id="e-pc4-branchadder" class="edge" d="M345 690 H620"/>
<path id="e-signext-shift" class="edge" d="M465 510 V585 H390"/>
<path id="e-shift-branch" class="edge" d="M545 620 H590 V690 H620"/>
<!-- Branch target calculation and branch decision are separate paths. -->
<path id="e-branchadder-pcmux" class="edge" d="M780 690 H995 V730 H1010"/>
<path id="e-control-branch" class="edge" d="M545 285 H580 V650 H820"/>
<path id="e-alu-zero-branch" class="edge" d="M900 435 H960 V680 H820"/>
<path id="e-branchselect-pcmux" class="edge" d="M980 655 H995 V755 H1010"/>
<path id="e-instr-jump" class="edge" d="M345 80 H365 V785 H620"/>
<path id="e-pc4-jump" class="edge" d="M345 690 H570 V820 H700 V815"/>
<path id="e-jump-pcmux" class="edge" d="M780 785 H950 V765 H1010"/>
<path id="e-pc4-pcmux" class="edge" d="M345 690 H900 V745 H1010"/>
<path id="e-pcmux-pc" class="edge" d="M1160 745 H1210 V105 H140"/>
</g>

<!-- Components -->
<g id="n-pc" class="node"><rect x="20" y="55" width="120" height="100"/><text x="80" y="94">Program Counter</text><text x="80" y="117">(PC)</text></g>
<g id="n-imem" class="node"><rect x="195" y="55" width="150" height="100"/><text x="270" y="94">Instruction</text><text x="270" y="117">Memory</text></g>
<g id="n-regfile" class="node"><rect x="390" y="55" width="155" height="115"/><text x="467" y="88">Register File</text><text x="467" y="112">Read rs / rt</text><text x="467" y="132">Write register</text><text x="467" y="150">Write data / enable</text></g>
<g id="n-regdst" class="node"><rect x="560" y="145" width="150" height="65"/><text x="635" y="173">RegDst MUX</text><text x="635" y="194">rt or rd</text></g>
<g id="n-control" class="node"><rect x="390" y="225" width="155" height="85"/><text x="467" y="260">Main Control</text><text x="467" y="284">Control signals</text></g>
<g id="n-signext" class="node"><rect x="390" y="440" width="155" height="70"/><text x="467" y="469">Sign Extension</text><text x="467" y="492">16 → 32 bits</text></g>
<g id="n-alusrc" class="node"><rect x="690" y="365" width="85" height="80"/><text x="732" y="398">ALUSrc</text><text x="732" y="421">MUX</text></g>
<g id="n-aluctrl" class="node"><rect x="850" y="225" width="140" height="65"/><text x="920" y="253">ALU Control</text><text x="920" y="275">Decoder</text></g>
<g id="n-alu" class="node"><rect x="790" y="345" width="110" height="90"/><text x="845" y="382">ALU</text><text x="845" y="407">Result / Zero</text></g>
<g id="n-dmem" class="node"><rect x="1000" y="345" width="135" height="110"/><text x="1067" y="382">Data Memory</text><text x="1067" y="406">Read / Write</text><text x="1067" y="430">LW / SW</text></g>
<g id="n-memtoreg" class="node"><rect x="1120" y="540" width="150" height="75"/><text x="1195" y="570">MemToReg MUX</text><text x="1195" y="593">ALU / Memory</text></g>
<g id="n-pc4" class="node"><rect x="195" y="655" width="150" height="70"/><text x="270" y="684">PC + 4</text><text x="270" y="707">Adder</text></g>
<g id="n-branchshift" class="node"><rect x="390" y="585" width="155" height="70"/><text x="467" y="614">Shift left 2</text><text x="467" y="637">Branch offset</text></g>
<g id="n-branchadder" class="node"><rect x="620" y="655" width="160" height="70"/><text x="700" y="684">Branch Target</text><text x="700" y="707">Adder</text></g>
<g id="n-branchlogic" class="node"><rect x="820" y="620" width="160" height="75"/><text x="900" y="650">Branch Decision</text><text x="900" y="674">Branch AND Zero</text></g>
<g id="n-jumpgen" class="node"><rect x="620" y="750" width="160" height="65"/><text x="700" y="772">Jump Address Generation</text><text x="700" y="791">{PC+4[31:28], instr[25:0], 00}</text><text x="700" y="808">26-bit target + upper PC bits</text></g>
<g id="n-pcmux" class="node"><rect x="1010" y="710" width="150" height="75"/><text x="1085" y="740">Next-PC</text><text x="1085" y="763">Selection MUX</text></g>
</svg>
</div>
<p class="muted">Green highlights indicate conceptual components associated with the selected instruction. Signal routes are illustrative architectural paths, not a gate-level netlist.</p>
</section>

<section class="panel columns">
<div><h2>Control signals</h2><pre id="controls"></pre></div>
<div><h2>Register / ALU / memory</h2><pre id="datavalues"></pre></div>
<div><h2>Branch / jump / PC</h2><pre id="pcvalues"></pre></div>
<div><h2>Complete trace record</h2><pre id="rawtrace"></pre></div>
</section>

<footer>This is an educational architectural visualization. Assigned model cycles do not establish physical timing. The gem5 experiment uses an existing gem5 CPU model, not a custom single-cycle CPU.</footer>
</main>

<script>
"use strict";

const rows=__TRACE_DATA__;
const select=document.getElementById("instructionSelect");
const $=id=>document.getElementById(id);
const val=(r,k)=>r[k]===undefined||r[k]===""?"—":r[k];
const hex=v=>{if(v===undefined||v===null||v==="")return "—";const n=Number(v);return Number.isFinite(n)?"0x"+(n>>>0).toString(16).toUpperCase().padStart(8,"0"):String(v)};

function clearHighlights(){document.querySelectorAll(".node,.edge").forEach(e=>e.classList.remove("active"))}
function activate(nodes,edges){nodes.forEach(id=>{const e=$("n-"+id);if(e)e.classList.add("active")});edges.forEach(id=>{const e=$("e-"+id);if(e)e.classList.add("active")})}

function highlight(r,op){
    let n=["pc","imem","pc4"],e=["pc-im","im-reg","pc-pc4"];

    if(["ADD","SUB","AND","OR","SLT"].includes(op)){
        n.push("regfile","regdst","control","aluctrl","alu","memtoreg");
        e.push("reg-alu-a","reg-alu-b","im-regdst","regdst","control-aluctrl","aluctrl-alu","alu-memtoreg","memtoreg-reg","regwrite-reg");
    }
    else if(op==="ADDI"){
        n.push("regfile","control","signext","alusrc","aluctrl","alu","regdst","memtoreg");
        e.push("reg-alu-a","im-regdst","regdst","signext","signext-alu","control-alusrc","control-aluctrl","aluctrl-alu","alusrc-alu","alu-memtoreg","memtoreg-reg","regwrite-reg");
    }
    else if(op==="LW"){
        n.push("regfile","control","signext","alusrc","aluctrl","alu","dmem","memtoreg","regdst");
        e.push("reg-alu-a","im-regdst","regdst","signext","signext-alu","control-alusrc","control-aluctrl","aluctrl-alu","alusrc-alu","alu-dmem","dmem-memtoreg","memtoreg-reg","regwrite-reg");
    }
    else if(op==="SW"){
        n.push("regfile","control","signext","alusrc","aluctrl","alu","dmem");
        e.push("reg-alu-a","reg-dmem","signext","signext-alu","control-alusrc","control-aluctrl","aluctrl-alu","alusrc-alu","alu-dmem");
    }
    else if(op==="BEQ"){
        n.push("regfile","control","aluctrl","alu","branchshift","branchadder","branchlogic","pcmux");
        e.push("reg-alu-a","reg-alu-b","control-aluctrl","aluctrl-alu","pc4-branchadder","signext-shift","shift-branch","branchadder-pcmux","control-branch","alu-zero-branch","branchselect-pcmux");
    }
    else if(op==="J"){
        n.push("jumpgen","pcmux");
        e.push("instr-jump","pc4-jump","jump-pcmux","pc-pcmux");
    }

    if(r.PCSource==="BRANCH")n.push("branchshift","branchadder","branchlogic","pcmux");
    if(r.PCSource==="JUMP")n.push("jumpgen","pcmux");

    activate(n,e);
}

function show(i){
    i=Math.max(0,Math.min(rows.length-1,i));
    select.value=String(i);
    const r=rows[i];
    const op=String(val(r,"Instruction")).trim().split(/\s+/)[0].toUpperCase();

    $("position").textContent=`Instruction ${i+1} of ${rows.length}`;
    $("pcSource").textContent="PC source: "+val(r,"PCSource");

    $("mInstruction").textContent=val(r,"Instruction");
    $("mPC").textContent=hex(r.PC);
    $("mPC4").textContent=hex(r.PCPlus4);
    $("mNextPC").textContent=hex(r.NextPC);
    $("mALU").textContent=val(r,"ALUResult");
    $("mWB").textContent=val(r,"RegisterWriteData");

    const c=["RegDst","ALUSrc","MemToReg","RegWrite","MemRead","MemWrite","Branch","Jump","ALUControl"];
    $("controls").textContent=c.map(k=>`${k.padEnd(12)} : ${val(r,k)}`).join("\n");

    const d=[
        "ReadRegister1","ReadRegister2","ReadData1","ReadData2",
        "DestinationRegister","RegisterWriteEnable","RegisterWriteData",
        "WritebackSource","SignExtendedImmediate","ALUInputB",
        "ALUResult","Zero","MemoryAddress","MemoryReadData",
        "RegDstInput0","RegDstInput1","RegDstSelected",
        "ALUSrcInput0","ALUSrcInput1","ALUSrcSelected",
        "MemToRegInput0","MemToRegInput1","MemToRegSelected"
    ];
    $("datavalues").textContent=d.map(k=>`${k.padEnd(24)} : ${val(r,k)}`).join("\n");

    const p=[
        "PC","PCPlus4","NextPC","PCSource",
        "ShiftedBranchOffset","BranchTarget","BranchTaken",
        "JumpTarget26","ShiftedJumpTarget","PCUpper4","JumpAddress",
        "PCMuxInput0","PCMuxInput1","PCMuxInput2","PCMuxSelected"
    ];
    $("pcvalues").textContent=p.map(k=>`${k.padEnd(24)} : ${val(r,k)}`).join("\n");

    $("rawtrace").textContent=JSON.stringify(r,null,2);
    clearHighlights();
    highlight(r,op);

    $("first").disabled=i===0;
    $("previous").disabled=i===0;
    $("next").disabled=i===rows.length-1;
}

rows.forEach((r,i)=>{
    const o=document.createElement("option");
    o.value=String(i);
    o.textContent=`Cycle ${r.Cycle}: ${r.Instruction}`;
    select.appendChild(o);
});

select.addEventListener("change",()=>show(Number(select.value)));
$("first").addEventListener("click",()=>show(0));
$("previous").addEventListener("click",()=>show(Number(select.value)-1));
$("next").addEventListener("click",()=>show(Number(select.value)+1));
show(0);
</script>
</body>
</html>'''


def main():
    rows = load_trace()
    trace_json = json.dumps(rows, ensure_ascii=True).replace("</", "<\\/")
    page = HTML.replace("__TRACE_DATA__", trace_json)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(page, encoding="utf-8")

    print("Datapath viewer generated successfully.")
    print(f"Trace records: {len(rows)}")
    print(f"Trace columns: {len(rows[0])}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()