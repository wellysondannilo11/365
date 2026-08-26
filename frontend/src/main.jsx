import React,{useEffect,useState} from "react";
import {createRoot} from "react-dom/client";
import "./style.css";
const API=import.meta.env.VITE_API_URL||"http://localhost:8080/api";
async function get(p){const r=await fetch(API+p);if(!r.ok)throw Error(String(r.status));return r.json()}
function App(){
 const [s,setS]=useState(null),[d,setD]=useState(null),[a,setA]=useState(null),[i,setI]=useState(null),[err,setErr]=useState("");
 const load=async()=>{try{const [x,y,z,w]=await Promise.all([get("/v25/status"),get("/v25/dataset"),get("/v25/analytics"),get("/v25/infra/health")]);setS(x);setD(y);setA(z);setI(w);setErr("")}catch(e){setErr(e.message)}};
 useEffect(()=>{load();const id=setInterval(load,15000);return()=>clearInterval(id)},[]);
 const perf=d?.performance||{}, paper=d?.paper||{}, shadow=d?.shadow||{}, feed=s?.feed||{};
 const cards=[["Hoje","P/L",perf.pnl_units??0," u"],["Hoje","ROI",perf.roi==null?"—":(perf.roi*100).toFixed(2),"%"],["Histórico","Eventos",d?.stats?.events??0,""],["Histórico","Snapshots",d?.stats?.snapshots??0,""],["Decisões","BET",d?.stats?.bets??0,""],["Decisões","NO BET",d?.stats?.no_bets??0,""]];
 return <main><header><div><h1>ROBO DA BET <span>V25</span></h1><small>FEED REAL · PAPER / SHADOW · DINHEIRO REAL DESATIVADO · EDGE NÃO DETERMINADO</small></div><Status feed={feed}/></header>
 {err&&<div className="error">API indisponível: {err}</div>}
 <section className="cards">{cards.map((c,i)=><div className="card" key={i}><small>{c[0]} · {c[1]}</small><strong>{c[2]}{c[3]}</strong></div>)}</section>
 <section><h2>Operação</h2><div className="grid"><Panel title="Feed de dados" body={{provedor:feed.provider,configurado:feed.configured,status:feed.status}}/><Panel title="Interruptor de segurança" body={s?.kill_switch||{}}/><Panel title="Conjunto de dados" body={d?.stats||{}}/><Panel title="Infraestrutura" body={i||{}}/><Panel title="Status científico" body={{edge:"EDGE_NOT_DETERMINED",status:a?.status,n:a?.n}}/><Panel title="Mercado de cartões" body={s?.card_markets||{}}/></div></section>
 <section><h2>Paper × Shadow</h2><div className="grid"><Panel title="PAPER" body={paper}/><Panel title="SHADOW" body={shadow}/></div></section>
 <section><h2>Pesquisa e desempenho</h2><div className="grid"><Panel title="Mercados" body={a?.by_market||{}}/><Panel title="Ligas" body={a?.by_league||{}}/><Panel title="Casas" body={a?.by_bookmaker||{}}/><Panel title="Evidência científica" body={{edge:a?.edge_evidence||"EDGE_NOT_DETERMINED",amostra:a?.n??0}}/></div></section>
 <footer>O Robo está em modo exclusivamente observacional. Nenhum resultado sintético, replay ou demonstração é tratado como evidência real. Edge = NÃO DETERMINADO até existir amostra e validação suficientes.</footer>
 </main>
}
function Status({feed}){return <b className={feed.status==="FEED_ONLINE"?"ok":"warn"}>{feed.configured?feed.status:"CREDENCIAIS INDISPONÍVEIS"}</b>}
function Panel({title,body}){return <div className="panel"><h3>{title}</h3><pre>{JSON.stringify(body,null,2)}</pre></div>}
createRoot(document.getElementById("root")).render(<App/>);
