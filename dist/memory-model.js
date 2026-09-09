/* Prototype scheduling policy v0.2. Deliberately NOT an implementation of FSRS.
 * Thresholds and growth factors are product hypotheses, not calibrated probabilities.
 * Scheduled retrieval and optional practice are separate evidence streams.
 */
const MemoryModel = (() => {
  const DAY = 86400000;
  const clamp = (v, min, max) => Math.max(min, Math.min(max, v));
  function initial(now = Date.now()) {
    return {version: 2, stability: 1, difficulty: 5, lastReviewedAt: null,
      dueAt: now, successfulDays: [], firstSuccessAt: null, lapses: 0,
      scheduledCount: 0, practiceCount: 0, history: []};
  }
  function key(now) {
    const d = new Date(now);
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  }
  function migrate(word, now = Date.now()) {
    const w = {...word};
    if (!w.memory || w.memory.version !== 2) {
      w.memory = initial(now);
      // Old “Learned” labels were produced by a single click, not delayed evidence.
      if (w.status === 'Learned' || w.status === 'Familiar') w.status = 'Learning';
    }
    return w;
  }
  function recallEstimate(memory, now = Date.now()) {
    if (memory.lastReviewedAt === null) return null;
    return Math.pow(0.9, Math.max(0, now - memory.lastReviewedAt) / DAY / memory.stability);
  }
  function answer(word, rating, mode = 'daily', now = Date.now()) {
    if (!['Forgot','Hard','Know'].includes(rating)) throw new Error('Unknown rating');
    const w = migrate(word, now), m = structuredClone(w.memory);
    w.memory = m;
    m.history.push({at: now, rating, mode});
    if (mode === 'free') {
      m.practiceCount++;
      return w; // No extra mastery or postponed due date from massed practice.
    }
    const elapsed = m.lastReviewedAt === null ? null : (now - m.lastReviewedAt) / DAY;
    const independent = elapsed === null || elapsed >= 1;
    m.scheduledCount++;
    if (rating === 'Forgot') {
      m.difficulty = clamp(m.difficulty + 1, 1, 10);
      m.stability = Math.max(1, m.stability * 0.45);
      m.lapses++;
      m.successfulDays = [];
      m.firstSuccessAt = null;
      m.dueAt = now + 10 * 60000;
      w.status = 'Weak';
    } else {
      if (rating === 'Know' && independent) {
        m.successfulDays = [...new Set([...m.successfulDays, key(now)])];
        m.firstSuccessAt ??= now;
        m.difficulty = clamp(m.difficulty - 0.25, 1, 10);
        if (elapsed !== null) m.stability = clamp(m.stability * (1.6 + (10-m.difficulty)*0.12), 1, 180);
      } else if (rating === 'Hard') {
        m.difficulty = clamp(m.difficulty + 0.25, 1, 10);
        if (independent) m.stability = Math.max(1, m.stability * 0.8);
      }
      const gap = rating === 'Hard' ? Math.max(1, Math.round(m.stability * 0.5)) : Math.max(1, Math.round(m.stability));
      m.dueAt = now + gap * DAY;
      const familiar = m.successfulDays.length >= 3 && m.firstSuccessAt !== null &&
        now - m.firstSuccessAt >= 7 * DAY && m.stability >= 7;
      w.status = familiar ? 'Familiar' : 'Learning';
    }
    m.lastReviewedAt = now;
    return w;
  }
  return {DAY, initial, migrate, answer, key, recallEstimate};
})();
