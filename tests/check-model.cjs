const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const ctx={structuredClone};vm.createContext(ctx);vm.runInContext(fs.readFileSync('dist/memory-model.js','utf8'),ctx);const M=vm.runInContext('MemoryModel',ctx);
const base=new Date(2026,8,9,12).getTime(),DAY=M.DAY;
let w={id:'reluctant',word:'reluctant',translation:'неохотный',status:'New'};
w=M.answer(w,'Know','daily',base);assert.equal(w.status,'Learning');assert.equal(w.memory.successfulDays.length,1);assert.equal(w.memory.dueAt,base+DAY);
const stability=w.memory.stability;
for(let i=0;i<100;i++)w=M.answer(w,'Know','daily',base+1000*i);
assert.equal(w.status,'Learning');assert.equal(w.memory.stability,stability);assert.equal(w.memory.successfulDays.length,1);
let now=base+DAY+100000;
for(let i=0;i<4;i++){now=Math.max(now,w.memory.dueAt);w=M.answer(w,'Know','daily',now)}
assert.equal(w.status,'Familiar');assert(w.memory.dueAt>now);
const scheduled=JSON.stringify({...w.memory,history:[],practiceCount:0}),status=w.status;
for(const rating of ['Know','Hard','Forgot']){w=M.answer(w,rating,'free',now+1);assert.equal(w.status,status);assert.equal(JSON.stringify({...w.memory,history:[],practiceCount:0}),scheduled)}
assert.equal(w.memory.practiceCount,3);
w=M.answer(w,'Forgot','daily',now+DAY);assert.equal(w.status,'Weak');assert.equal(w.memory.successfulDays.length,0);assert.equal(w.memory.dueAt,now+DAY+600000);
w=M.answer(w,'Know','daily',now+DAY+600000);assert.equal(w.status,'Learning');assert.equal(w.memory.successfulDays.length,0);
let legacy=M.migrate({word:'effort',status:'Learned',translation:'усилие'},base);assert.equal(legacy.status,'Learning');assert.equal(legacy.translation,'усилие');assert.equal(legacy.memory.scheduledCount,0);
const newWord=M.migrate({word:'new',status:'New'},base);assert.equal(newWord.status,'New');
assert.equal(M.recallEstimate(newWord.memory,base),null);
const m={...M.initial(base),lastReviewedAt:base,stability:7};assert(Math.abs(M.recallEstimate(m,base+7*DAY)-0.9)<1e-10);
assert.throws(()=>M.answer(w,'invalid'));
console.log('PASS: single recall, anti-inflation, delayed familiarity, future due dates, free isolation, lapse reset, migration, model curve.');
