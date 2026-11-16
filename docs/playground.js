const $ = (id) => document.getElementById(id);
const W = 18, H = 12, PATCHES = W * H;
const clamp = (x, lo, hi) => Math.max(lo, Math.min(hi, x));
const sigmoid = (x) => 1 / (1 + Math.exp(-clamp(x, -20, 20)));
function rngFactory(seed) {
  let a = seed >>> 0;
  return function() {
    a += 0x6D2B79F5;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function normal(rand) {
  const u = Math.max(rand(), 1e-12), v = rand();
  return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
}
function buildField(t, mode, rand) {
  const values = new Float32Array(PATCHES);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) {
    const k = y * W + x;
    const phase = t / 10;
    const drift = mode === "volatile" ? Math.sin(t / 17) * 3.2 : 0;
    const cx = 5.2 + drift + 2.1 * Math.sin(phase * .31);
    const cy = 5.1 + (mode === "volatile" ? 2.0 * Math.cos(t / 13) : 1.1 * Math.cos(phase * .26));
    const dx = x - cx, dy = y - cy;
    const hotspot = .19 * Math.exp(-(dx * dx + dy * dy) / 15);
    const broad = .12 * Math.cos((x / W) * Math.PI * 2 + phase * .55)
                + .10 * Math.sin((y / H) * Math.PI * 2 - phase * .4);
    const regular = .43 + hotspot + broad;
    const weather = (mode === "volatile" ? .15 : .045) * normal(rand);
    values[k] = clamp(regular + weather, .06, 1.05);
  }
  return values;
}
function stats(values) {
  let m = 0;
  for (const v of values) m += v;
  m /= values.length;
  let v = 0;
  for (const x of values) v += (x - m) * (x - m);
  return { mean: m, sd: Math.sqrt(v / values.length) };
}
function neighbours(p) {
  const x = p % W, y = Math.floor(p / W), out = [];
  for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
    const xx = (x + dx + W) % W, yy = (y + dy + H) % H;
    out.push(yy * W + xx);
  }
  return out;
}
function initAgent(rand, information, movement) {
  return {
    p: Math.floor(rand() * PATCHES),
    collector: clamp(.58 + .12 * normal(rand), .2, .95),
    sensing: information ? clamp(.14 + .06 * normal(rand), 0, .7) : 0,
    processing: information ? clamp(.13 + .06 * normal(rand), 0, .7) : 0,
    prediction: information ? clamp(.12 + .06 * normal(rand), 0, .7) : 0,
    planning: information ? clamp(.12 + .06 * normal(rand), 0, .7) : 0,
    action: movement === "directed" ? clamp(.2 + .08 * normal(rand), 0, .8) : 0,
    cooperation: clamp(.12 + .05 * normal(rand), 0, .6)
  };
}
function mutate(parent, rand, information, movement) {
  const child = {...parent};
  const mutateTrait = (key, rate) => clamp(parent[key] + rate * normal(rand), 0, 1);
  child.p = parent.p;
  child.collector = mutateTrait("collector", .035);
  child.cooperation = mutateTrait("cooperation", .035);
  child.sensing = information ? mutateTrait("sensing", .04) : 0;
  child.processing = information ? mutateTrait("processing", .04) : 0;
  child.prediction = information ? mutateTrait("prediction", .04) : 0;
  child.planning = information ? mutateTrait("planning", .04) : 0;
  child.action = movement === "directed" ? mutateTrait("action", .04) : 0;
  return child;
}
function runToy({environment, noise, movement, information, generations, seed}) {
  const rand = rngFactory(seed);
  let agents = Array.from({length: 120}, () => initAgent(rand, information, movement));
  const history = [];
  let lastField = new Float32Array(PATCHES);
  for (let t = 0; t < generations; t++) {
    const field = buildField(t, environment, rand);
    const future = buildField(t + 1, environment, rand);
    lastField = field;
    const fieldStats = stats(field);
    const obsNoise = noise * fieldStats.sd;
    const predNoise = noise * stats(future).sd;
    for (const a of agents) {
      if (movement === "still") continue;
      const moveChance = movement === "random" ? .22 : clamp(.025 + .90 * a.action, 0, .92);
      if (rand() >= moveChance) continue;
      if (movement === "random") {
        const opts = neighbours(a.p);
        a.p = opts[Math.floor(rand() * opts.length)];
        continue;
      }
      const opts = neighbours(a.p);
      let bestPatch = a.p, bestScore = -Infinity;
      const futureWeight = information ? .70 * a.planning * a.prediction : 0;
      const attenuation = information ? a.sensing * a.processing : 0;
      for (const p of opts) {
        const observed = field[p] + normal(rand) * (obsNoise * (1 - attenuation) + .005);
        const predicted = future[p] + normal(rand) * (predNoise * (1 - (information ? a.prediction * a.processing : 0)) + .005);
        const score = (1 - futureWeight) * observed + futureWeight * predicted;
        if (score > bestScore) { bestScore = score; bestPatch = p; }
      }
      a.p = bestPatch;
    }
    const caps = new Float64Array(PATCHES);
    const individualCap = agents.map(a => .35 + 1.1 * a.collector + .25 * a.cooperation);
    for (let i = 0; i < agents.length; i++) caps[agents[i].p] += individualCap[i];
    const captures = new Float64Array(agents.length);
    const net = new Float64Array(agents.length);
    let totalCapture = 0, totalNet = 0;
    for (let i = 0; i < agents.length; i++) {
      const a = agents[i], p = a.p, sumCap = caps[p];
      const fraction = 1 - Math.exp(-.42 * sumCap);
      const gross = field[p] * fraction * individualCap[i] / Math.max(sumCap, 1e-9);
      const infoCost = information ? .018 * (a.sensing*a.sensing + a.processing*a.processing + a.prediction*a.prediction + a.planning*a.planning) : 0;
      const actionCost = movement === "directed" ? .012 * a.action * a.action : 0;
      const cost = .045 + infoCost + actionCost;
      captures[i] = gross;
      net[i] = gross - cost;
      totalCapture += gross;
      totalNet += net[i];
    }
    const meanNet = totalNet / Math.max(agents.length, 1);
    const survivors = [];
    let aliveCapture = 0;
    for (let i = 0; i < agents.length; i++) {
      const survive = .55 + .40 * sigmoid((net[i] - .025) * 8);
      if (rand() < survive) { survivors.push(agents[i]); aliveCapture += captures[i]; }
    }
    const birthRate = .045 + .28 * sigmoid((meanNet - .035) * 9);
    const births = Math.min(500, Math.max(0, Math.round(survivors.length * birthRate)));
    const weights = survivors.map((a, i) => Math.max(.015, net[agents.indexOf(a)] + .08));
    const weightSum = weights.reduce((s, x) => s + x, 0) || 1;
    const next = survivors.slice();
    for (let b = 0; b < births; b++) {
      let target = rand() * weightSum, chosen = survivors[survivors.length - 1];
      for (let i = 0; i < survivors.length; i++) { target -= weights[i]; if (target <= 0) { chosen = survivors[i]; break; } }
      next.push(mutate(chosen, rand, information, movement));
    }
    if (next.length > 500) {
      next.sort((a,b) => (b.collector + b.cooperation + b.sensing + b.processing + b.prediction + b.planning + b.action) -
                         (a.collector + a.cooperation + a.sensing + a.processing + a.prediction + a.planning + a.action));
      next.length = 500;
    }
    agents = next;
    history.push({generation:t+1,population:agents.length,total:totalCapture,per:totalCapture / Math.max(1,agents.length),agency:agents.length ? agents.reduce((s,a)=>s+a.sensing+a.processing+a.prediction+a.planning+a.action,0)/(agents.length*5) : 0});
    if (!agents.length) break;
  }
  return {agents,history,field:lastField};
}
function drawMap(field, agents) {
  const c = $("map"), x = c.getContext("2d"), cw = c.width/W, ch = c.height/H;
  const max = Math.max(...field), min = Math.min(...field);
  x.clearRect(0,0,c.width,c.height);
  for (let p=0;p<PATCHES;p++) {
    const v=(field[p]-min)/Math.max(.001,max-min);
    x.fillStyle = "hsl(" + (180 - v*145) + " 40% " + (15+v*42) + "%)";
    x.fillRect((p%W)*cw,Math.floor(p/W)*ch,cw+1,ch+1);
  }
  x.fillStyle = "#f2dfb5";
  for (const a of agents) {
    const px=(a.p%W)*cw+cw/2, py=Math.floor(a.p/W)*ch+ch/2;
    x.beginPath();x.arc(px,py,2.5,0,Math.PI*2);x.fill();
  }
}
function drawHistory(history) {
  const c=$("history"),x=c.getContext("2d"),w=c.width,h=c.height;
  x.clearRect(0,0,w,h);x.strokeStyle="#31434a";x.lineWidth=1;
  for(let i=0;i<5;i++){const y=18+i*(h-44)/4;x.beginPath();x.moveTo(42,y);x.lineTo(w-12,y);x.stroke();}
  x.fillStyle="#a7b7b2";x.font="12px system-ui";x.fillText("start",42,h-8);x.fillText("generation",w-85,h-8);
  const series=[{key:"population",color:"#9bd6bd"},{key:"total",color:"#e6bd79"},{key:"per",color:"#89b9d6"}];
  for(const s of series){
    const vals=history.map(z=>z[s.key]),max=Math.max(...vals,1);
    x.strokeStyle=s.color;x.lineWidth=2.5;x.beginPath();
    vals.forEach((v,i)=>{const px=42+i*(w-58)/Math.max(1,vals.length-1);const py=h-30-(v/max)*(h-52);if(i===0)x.moveTo(px,py);else x.lineTo(px,py);});x.stroke();
  }
  x.font="12px system-ui";
  let lx=45;for(const s of series){x.fillStyle=s.color;x.fillRect(lx,6,9,9);x.fillStyle="#c7d3ce";x.fillText(s.key==="per"?"per entity":s.key,lx+14,15);lx+=s.key==="population"?112:95;}
}
function execute() {
  const params={
    environment:$("env").value,
    noise:Number($("noise").value),
    movement:$("movement").value,
    information:$("info").checked,
    generations:Number($("gens").value),
    seed:Math.max(1,Number($("seed").value)||42)
  };
  $("playstatus").textContent="Running the browser model…";
  const result=runToy(params);
  drawMap(result.field,result.agents);
  drawHistory(result.history);
  const last=result.history[result.history.length-1]||{population:0,total:0,per:0,agency:0};
  $("m-pop").textContent=last.population.toLocaleString();
  $("m-per").textContent=last.per.toFixed(3);
  $("m-total").textContent=last.total.toFixed(1);
  $("playstatus").textContent="Completed " + result.history.length + " generations. Final mean agency-trait score: " + last.agency.toFixed(3) + ". Change one setting at a time and rerun with the same seed for a more interpretable comparison.";
}
$("noise").addEventListener("input",()=>{$("noiseout").textContent=Number($("noise").value).toFixed(1)+"×";});
$("gens").addEventListener("input",()=>{$("gensout").textContent=$("gens").value;});
$("run").addEventListener("click",execute);
$("reset").addEventListener("click",()=>{$("env").value="predictable";$("noise").value="0.5";$("noiseout").textContent="0.5×";$("movement").value="directed";$("gens").value="120";$("gensout").textContent="120";$("info").checked=true;$("seed").value="42";execute();});
execute();