const out=s=>document.querySelector(s);
let simNow=new Date(2026,8,9,12).getTime();
let simWord={word:'reluctant',status:'New',memory:MemoryModel.initial(simNow)};
function showSim(message='Первый ответ — только начало. Попробуйте вспомнить слово сейчас, затем вернуться к следующей проверке.'){
 const m=simWord.memory;
 out('#sim-status').innerHTML=`<span>${simWord.status}</span>`;
 out('#sim-stats').textContent=`${new Date(simNow).toLocaleDateString('ru-RU',{day:'numeric',month:'long'})} · ${m.successfulDays.length} успешных дней · S ${m.stability.toFixed(1)} дн. · D ${m.difficulty.toFixed(1)}`;
 out('#sim-message').textContent=message;
 showCurve();
}
function showCurve(){const days=Number(out('#sim-delay').value);out('#sim-days').textContent=days;const m=simWord.memory;const r=MemoryModel.recallEstimate(m,(m.lastReviewedAt??simNow)+days*MemoryModel.DAY);out('#sim-retention').textContent=r===null?'—':`${Math.round(r*100)}%`}
out('#sim-now').onclick=()=>{simWord=MemoryModel.answer(simWord,'Know','daily',simNow);showSim('Повторные ответы в ту же минуту не увеличивают устойчивость и число успешных дней.')};
out('#sim-later').onclick=()=>{simNow=Math.max(simNow+MemoryModel.DAY,simWord.memory.dueAt);simWord=MemoryModel.answer(simWord,'Know','daily',simNow);showSim(simWord.status==='Familiar'?'Условия Familiar выполнены. Следующая проверка всё равно запланирована.':'Успешная проверка после паузы: появляется новое свидетельство устойчивости.')};
out('#sim-forgot').onclick=()=>{simWord=MemoryModel.answer(simWord,'Forgot','daily',simNow);showSim('Статус Weak. Устойчивость снизилась, серия подтверждений сброшена. Нужна новая встреча.')};
out('#sim-reset').onclick=()=>{simNow=new Date(2026,8,9,12).getTime();simWord={word:'reluctant',status:'New',memory:MemoryModel.initial(simNow)};out('#sim-delay').value=0;showSim()};
out('#sim-delay').oninput=showCurve;
document.querySelectorAll('[data-screen]').forEach(button=>button.onclick=()=>{document.querySelectorAll('[data-screen]').forEach(b=>b.classList.toggle('selected',b===button));out('#app-preview').src=`./?brand=vokiri#${button.dataset.screen}`});showSim();
