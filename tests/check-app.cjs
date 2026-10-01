const fs=require('fs'),vm=require('vm'),assert=require('node:assert/strict');
const nodes={},listeners={};const element=()=>({innerHTML:'',value:'',textContent:'',focus(){},classList:{add(){},remove(){}},style:{}});
let saved=null;const ctx={console,structuredClone,URLSearchParams,setTimeout:()=>0,clearTimeout(){},requestAnimationFrame(){},localStorage:{getItem(){return saved},setItem(k,v){saved=v}},document:{title:'',querySelector(s){return nodes[s]??=element()},querySelectorAll(){return []},body:element(),activeElement:null,addEventListener(k,fn){listeners[k]=fn}},location:{hash:'#today',search:''},window:{addEventListener(){},scrollTo(){}}};vm.createContext(ctx);
for(const f of ['data.js','memory-model.js','reading-levels.js','app.js'])vm.runInContext(fs.readFileSync('dist/'+f,'utf8'),ctx);
const run=s=>vm.runInContext(s,ctx);const click=(action,value)=>listeners.click({target:{classList:{contains(){return false}},closest(){return {dataset:{action,value},disabled:false}}}});
assert.equal(run('dailyQueue().length'),20);assert.equal(run("state.words.filter(w=>w.status==='Learned').length"),0);
run("addWord(lookup('reluctant'))");run('startReview()');assert.equal(run('session.words[0].word'),'reluctant');
// Ignore accidental ratings before the answer is revealed.
click('answer','Know');assert.equal(run('session.index'),0);
click('flip');click('answer','Know');assert.equal(run("wordById('reluctant').status"),'Learning');
click('flip');click('answer','Forgot');assert.equal(run('session.words.length'),21);
let safety=0;while(!run('session.done')){click('flip');click('answer','Know');assert(++safety<50)}
assert.equal(run('dailyReviewedIds().size'),20);assert.equal(run('dailyRemaining()'),0);assert.equal(run('dailyQueue().length'),0);assert(run("today().includes('Free Practice')"));
const before=run("JSON.stringify(state.words.map(w=>[w.id,w.status,w.memory.dueAt,w.memory.stability]))");run("beginSession(state.words.slice(0,3),'free')");for(const rating of ['Know','Hard','Forgot']){click('flip');click('answer',rating)}
assert.equal(run('session.done'),true);assert.equal(run('dailyReviewedIds().size'),20);assert.equal(run("JSON.stringify(state.words.map(w=>[w.id,w.status,w.memory.dueAt,w.memory.stability]))"),before);
for(const level of ['A2','B1','B2']){click('reading-level',level);assert.equal(run('state.readingLevel'),level);assert(JSON.parse(saved).readingLevel===level);for(const topic of ['Mind & life','Travel','Work & ideas']){run(`topic=${JSON.stringify(topic)}`);assert(run('getArticle(topic).paragraphs.length')>=7);assert(run("getArticle(topic).paragraphs.join(' ').toLowerCase().includes('reluctant')"));}}
const a2=run("state.readingLevel='A2';getArticle('Mind & life').paragraphs.join(' ')");const b2=run("state.readingLevel='B2';getArticle('Mind & life').paragraphs.join(' ')");assert.notEqual(a2,b2);assert(b2.length>a2.length);
run("analyzeImport('word;translation\\nreluctant;неохотный\\nembrace;принимать\\nembrace;принимать\\n123;bad\\nunknownterm;')");assert.equal(run('importPreview.ready.length'),1);assert.equal(run('importPreview.duplicates.length'),2);assert.equal(run('importPreview.skipped.length'),2);click('confirm-import');assert(run("wordById('embrace').memory.version===2"));
for(const screen of ['today','vocabulary','reading','translator','review'])run(`screen='${screen}';render()`);
run("articleOpen=true;screen='reading';render()");assert(nodes['#app'].innerHTML.includes('B2'));assert(run("definition(state.words[0],true).includes('memory-summary')"));assert(!run("definition(state.words[0],true).includes('word-status')"));
console.log('PASS: quota and completion, add priority, one retry, premature click guard, free mode, all nine level texts, persistence, import, routes and evidence summary.');
