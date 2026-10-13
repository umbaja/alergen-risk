const targets = [
  ['rs4143332','G','hla'],['rs3128927','T','core'],['rs2301226','G','core'],['rs6937061','G','core'],
  ['rs1611710','T','core'],['rs13132308','G','core'],['rs2030519','G','core'],['rs1359062','C','core'],
  ['rs17264332','G','core'],['rs6715106','G','core'],['rs55743914','T','core'],['rs990171','A','core'],
  ['rs1980422','C','core'],['rs3184504','T','core'],['rs61907765','T','core'],['rs13003464','G','core'],
  ['rs11875687','C','core'],['rs12068671','C','core'],['rs1250552','G','core'],['rs10892258','A','core'],
  ['rs1018326','C','core'],['rs182429','A','core'],['rs7104791','T','core'],['rs4821124','C','core'],
  ['rs4445406','C','core'],['rs12142280','A','core'],['rs6498114','G','core'],['rs1353248','T','core'],
  ['rs2387397','G','core'],['rs1893592','C','core'],['rs11851414','C','core'],['rs1378938','T','core'],
  ['rs10800746','T','core'],['rs1050976','T','core'],['rs7616215','C','core'],['rs2561288','T','core'],
  ['rs61579022','A','core'],['rs10167650','G','core'],
  ['rs17849502','T','research'],['rs6806528','T','research'],['rs2364484','C','research'],['rs9610686','C','research'],
  ['rs2187668','T','hla'],['rs1617322','A','hla'],['rs7454108','C','hla'],['rs3957146','C','hla'],
  ['rs1049124','A','hla'],['rs7775228','C','hla'],['rs73405471','T','hla'],['rs79550239','A','hla']
];

const base = 'https://rest.ensembl.org';
const headers = {'Content-Type':'application/json','Accept':'application/json'};
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

async function getJson(url, attempt=0){
  const response = await fetch(url,{headers,signal:AbortSignal.timeout(45000)});
  if((response.status===429 || response.status>=500) && attempt<5){
    await delay(500*(2**attempt));
    return getJson(url,attempt+1);
  }
  if(!response.ok) throw new Error(`${response.status} ${url}`);
  return response.json();
}

async function postJson(url,body,attempt=0){
  const response=await fetch(url,{method:'POST',headers,body:JSON.stringify(body),signal:AbortSignal.timeout(150000)});
  if((response.status===429 || response.status>=500) && attempt<4){
    await delay(1000*(2**attempt));
    return postJson(url,body,attempt+1);
  }
  if(!response.ok)throw new Error(`${response.status} ${url}: ${await response.text()}`);
  return response.json();
}

async function pool(items, worker, concurrency=6){
  const output = new Array(items.length);
  let index=0;
  await Promise.all(Array.from({length:concurrency},async()=>{
    while(index<items.length){
      const current=index++;
      try{ output[current]=await worker(items[current],current); }
      catch(error){ output[current]={error:error.message}; }
    }
  }));
  return output;
}

const panelResponse=await fetch('https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/integrated_call_samples_v3.20130502.ALL.panel');
if(!panelResponse.ok)throw new Error(`Panel ${panelResponse.status}`);
const eurSamples=new Set((await panelResponse.text()).split(/\r?\n/).slice(1).map(line=>line.split('\t')).filter(parts=>parts[2]==='EUR').map(parts=>parts[0]));
const targetIds=new Set(targets.map(row=>row[0]));

const ldRows=await pool(targets,async ([id,risk,group])=>{
  const rows=await getJson(`${base}/ld/human/${id}/1000GENOMES:phase_3:EUR?r2=0.80`);
  const candidates=rows
    .map(row=>({id:row.variation1===id?row.variation2:row.variation1,r2:+row.r2,dPrime:+row.d_prime}))
    .filter(row=>/^rs\d+$/.test(row.id)&&!targetIds.has(row.id))
    .sort((a,b)=>b.r2-a.r2||b.dPrime-a.dPrime)
    .slice(0,3);
  return {id,risk,group,candidates};
},5);

const variantIds=[...new Set(ldRows.flatMap(row=>row.error?[]:[row.id,...row.candidates.map(item=>item.id)]))];
const chunks=[];
for(let index=0;index<variantIds.length;index+=50)chunks.push(variantIds.slice(index,index+50));
process.stderr.write(`LD hotové; načítavam ${variantIds.length} variantov v ${chunks.length} dávkach.\n`);
const batchParts=await Promise.all(chunks.map(ids=>postJson(`${base}/variation/human?genotypes=1;pops=1`,{ids})));
const batch=Object.assign({},...batchParts);
const variantResults=variantIds.map(id=>{
  const value=batch[id]||{};
  const genotypes=new Map();
  for(const call of value.genotypes||[]){
    const sample=String(call.sample||'').replace(/^1000GENOMES:phase_3:/,'');
    if(eurSamples.has(sample)&&/^[ACGT]\|[ACGT]$/.test(call.genotype||''))genotypes.set(sample,call.genotype);
  }
  return {id,genotypes};
});
const genotypeById=new Map(variantResults.filter(row=>!row.error).map(row=>[row.id,row.genotypes]));

function phaseStats(targetId,targetRisk,proxyId){
  const targetCalls=genotypeById.get(targetId),proxyCalls=genotypeById.get(proxyId);
  if(!targetCalls||!proxyCalls)return null;
  const haplotypes=[];
  for(const [sample,targetCall] of targetCalls){
    const proxyCall=proxyCalls.get(sample);
    if(!proxyCall)continue;
    const ta=targetCall.split('|'),pa=proxyCall.split('|');
    haplotypes.push([ta[0],pa[0]],[ta[1],pa[1]]);
  }
  const proxyAlleles=[...new Set(haplotypes.map(row=>row[1]))];
  if(haplotypes.length<900||proxyAlleles.length!==2)return null;
  const summaries=proxyAlleles.map(allele=>{
    const matching=haplotypes.filter(row=>row[1]===allele);
    return {allele,n:matching.length,p:matching.filter(row=>row[0]===targetRisk).length/matching.length};
  }).sort((a,b)=>b.p-a.p);
  const targetFrequency=haplotypes.filter(row=>row[0]===targetRisk).length/haplotypes.length;
  return {
    proxyRiskAllele:summaries[0].allele,
    proxyOtherAllele:summaries[1].allele,
    pRiskIfProxy:summaries[0].p,
    pRiskIfOther:summaries[1].p,
    targetFrequency,
    haplotypes:haplotypes.length
  };
}

const results=ldRows.map(row=>{
  if(row.error)return row;
  return {...row,candidates:row.candidates.map(candidate=>({...candidate,...phaseStats(row.id,row.risk,candidate.id)})).filter(candidate=>candidate.proxyRiskAllele)};
});

const compact=results.map((row,index)=>{
  const [fallbackId,fallbackRisk,fallbackGroup]=targets[index];
  return {
    t:row.id||fallbackId,r:row.risk||fallbackRisk,g:row.group||fallbackGroup,
    p:(row.candidates||[]).filter(item=>item.r2>=.90).slice(0,2).map(item=>[
      item.id,item.proxyRiskAllele,+item.r2.toFixed(6),+item.dPrime.toFixed(6),
      +item.pRiskIfProxy.toFixed(6),+item.pRiskIfOther.toFixed(6)
    ])
  };
});
console.log(JSON.stringify({population:'1000GENOMES:phase_3:EUR',eurSamples:eurSamples.size,results:compact}));
