(function () {
  'use strict';

  const VIEW_LABEL = { main: 'Main', left: 'Left', right: 'Right', back: 'Back' };
  const STAT_ROWS = [
    ['health', 'Health'], ['attackDamage', 'Attack damage'], ['attacksPerSecond', 'Attacks per second'],
    ['range', 'Range (cells)'], ['armor', 'Armour'], ['resistance', 'Magic resistance'], ['moveSpeed', 'Move speed'],
  ];
  const FACTS = [
    ['form', 'Look'], ['decision', 'What it does for you'], ['positioning', 'Where to place it'],
    ['allies', 'Works well with'], ['counterplay', 'How to beat it'], ['recognition', 'How to spot the skill'],
  ];
  const SKILL_TYPE = { passive: 'Passive skill', mana: 'Active skill · costs mana', planned: 'Skill' };
  const FILTERS = ['race', 'class', 'cost', 'status', 'sort'];
  const SVG = 'http://www.w3.org/2000/svg';

  // One 24-unit line drawing per race and class, plus a gem for relics.
  const ring = (cx, cy, r) => 'M' + (cx - r) + ' ' + cy + 'a' + r + ' ' + r + ' 0 1 0 ' + 2 * r + ' 0a' + r + ' ' + r + ' 0 1 0 ' + -2 * r + ' 0';
  const dot = (x, y) => 'M' + x + ' ' + y + 'h.01';
  const ICONS = {
    human: 'M4 19h16M4 19L3 8l5 4 4-7 4 7 5-4-1 11',
    elf: 'M5 19C5 11 10 5 19 5c0 9-6 14-14 14zM5 19l8-8',
    dwarf: 'M3 7h13v2c0 2-2 3-4 3v3h3v4H6v-4h3v-3C6 12 3 10 3 7zM16 7h5',
    goblin: ring(12, 12, 8) + 'M12 8l3 4-3 4-3-4z',
    orc: 'M5 20L15 6M12 5c3-2 7-1 8 3-2 2-5 2-7 1z',
    beastkin: ring(6, 10, 1.5) + ring(10, 6, 1.5) + ring(14, 6, 1.5) + ring(18, 10, 1.5) + 'M12 12c-3 0-5 3-5 5s2 2 5 2 5 0 5-2-2-5-5-5z',
    demon: 'M7 11v2a5 5 0 0 0 10 0v-2zM7 11C5 9 4 6 5 3M17 11c2-2 3-5 2-8',
    undead: 'M12 3a7 7 0 0 0-7 7c0 3 1 4 3 5v4h8v-4c2-1 3-2 3-5a7 7 0 0 0-7-7zM10 19v-2M14 19v-2' + dot(9.5, 10.5) + dot(14.5, 10.5),
    elemental: 'M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z',
    dragonkin: 'M12 3l5 5-5 5-5-5zM7 12l5 5 5-5M7 16l5 5 5-5',
    tank: 'M12 3l7 3v5c0 5-3 8-7 10-4-2-7-5-7-10V6z',
    fighter: 'M20 4l-1 5-8 8-3-3 8-8zM6 12l6 6M8 16l-4 4',
    assassin: 'M12 21l-2.5-9h5zM8 12h8M12 12V6' + ring(12, 4.5, 1.5),
    mage: 'M12 3l2 7 7 2-7 2-2 7-2-7-7-2 7-2z',
    sniper: ring(12, 12, 6) + 'M12 2v6M12 16v6M2 12h6M16 12h6',
    engineer: ring(12, 12, 3) + ring(12, 12, 6.5) + 'M12 2.5v3M12 18.5v3M2.5 12h3M18.5 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M5.3 18.7l2.1-2.1M16.6 7.4l2.1-2.1',
    warlock: 'M19 14A8 8 0 1 1 10 5a6 6 0 0 0 9 9z',
    priest: ring(12, 12, 9) + 'M12 7v10M7 12h10',
    shaman: 'M13 2L5 14h6l-1 8 8-12h-6z',
    summoner: ring(12, 12, 9) + ring(12, 12, 5) + dot(12, 12),
    relic: 'M6 4h12l4 6-10 11L2 10zM2 10h20M9 10l3 11 3-11M6 4l3 6 3-6 3 6 3-6',
  };

  const $ = (id) => document.getElementById(id);
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function svg(tag, attributes) {
    const node = document.createElementNS(SVG, tag);
    for (const key in attributes) node.setAttribute(key, attributes[key]);
    return node;
  }
  function icon(name) {
    const root = svg('svg', { viewBox: '0 0 24 24', class: 'icon', 'aria-hidden': 'true' });
    root.appendChild(svg('path', { d: ICONS[name] }));
    return root;
  }
  function silhouette() {
    const root = svg('svg', { viewBox: '0 0 64 80', 'aria-hidden': 'true' });
    root.appendChild(svg('circle', { cx: 32, cy: 20, r: 14, fill: 'currentColor' }));
    root.appendChild(svg('path', { d: 'M12 78c0-18 8-32 20-32s20 14 20 32z', fill: 'currentColor' }));
    return root;
  }
  function art(path, alt, size, eager) {
    if (path) {
      const img = el('img');
      img.width = size; img.height = size; img.alt = alt; img.decoding = 'async';
      if (!eager) img.loading = 'lazy';
      img.src = path;
      return img;
    }
    const box = el('div', 'placeholder');
    box.appendChild(silhouette());
    box.appendChild(el('span', '', 'Art pending'));
    return box;
  }
  const thumb = (path) => path && path.replace('.webp', '-thumb.webp');
  function statusTag(hero) {
    return hero.status === 'playable' ? el('span', 'tag live', 'In the game') : el('span', 'tag', 'Planned');
  }
  function costBadge(cost) {
    const badge = el('span', 'cost', String(cost));
    badge.title = 'Cost ' + cost;
    return badge;
  }
  function button(className, text, onClick) {
    const node = el('button', className, text);
    node.type = 'button';
    node.addEventListener('click', onClick);
    return node;
  }

  let data = null;
  let shown = [];
  let current = null;
  let rendered = false;
  const bySlug = new Map();
  const byId = new Map();
  const traits = new Map();
  const slug = (hero) => hero.id.replace('wc_vn_', '');

  function traitLabel(id) {
    const label = el('span', 'trait-label');
    label.appendChild(icon(id));
    label.appendChild(document.createTextNode(traits.get(id).name));
    return label;
  }

  // ---- address bar: ?hero=shieldbearer&race=orc&sort=cost ----
  function address(heroSlug) {
    const params = new URLSearchParams();
    if (heroSlug) params.set('hero', heroSlug);
    if ($('search').value.trim()) params.set('q', $('search').value.trim());
    for (const key of FILTERS) if ($(key).value) params.set(key, $(key).value);
    const query = params.toString();
    return location.pathname + (query ? '?' + query : '') + (heroSlug ? '' : location.hash);
  }
  function readAddress() {
    const params = new URLSearchParams(location.search);
    const before = rendered && address();
    $('search').value = params.get('q') || '';
    for (const key of FILTERS) {
      const value = params.get(key) || '';
      $(key).value = [...$(key).options].some((option) => option.value === value) ? value : '';
    }
    // Closing a hero keeps the same list; leaving it alone keeps keyboard focus on the card.
    if (address() !== before) render();
    const hero = bySlug.get(params.get('hero'));
    if (hero) show(hero);
    else if ($('detail').open) $('detail').close();
  }

  function card(hero, index) {
    const item = el('li');
    const node = button('card cost-' + hero.cost, undefined, () => open(hero));
    const frame = el('div', 'card-art');
    frame.appendChild(art(thumb(hero.art.main), hero.name + ', main view', 384, index < 8));
    frame.appendChild(statusTag(hero));
    const body = el('div', 'card-body');
    const name = el('div', 'card-name');
    name.appendChild(el('span', '', hero.name));
    name.appendChild(costBadge(hero.cost));
    body.appendChild(name);
    const meta = el('div', 'card-meta');
    meta.appendChild(traitLabel(hero.race));
    meta.appendChild(traitLabel(hero.class));
    body.appendChild(meta);
    node.appendChild(frame);
    node.appendChild(body);
    item.appendChild(node);
    return item;
  }

  function gallery(hero) {
    const box = el('div', 'gallery cost-' + hero.cost);
    const stage = el('div', 'stage');
    box.appendChild(stage);
    const views = data.views.filter((view) => hero.art[view]);
    if (!views.length) {
      stage.appendChild(art(null));
      return box;
    }
    const picker = el('div', 'views');
    const buttons = views.map((view) => {
      const node = button('view', undefined, () => choose(view));
      node.appendChild(art(thumb(hero.art[view]), '', 384, true));
      node.appendChild(el('span', '', VIEW_LABEL[view]));
      picker.appendChild(node);
      return node;
    });
    function choose(view) {
      stage.replaceChildren(art(hero.art[view], hero.name + ', ' + VIEW_LABEL[view].toLowerCase() + ' view', 768, true));
      buttons.forEach((node, index) => node.setAttribute('aria-pressed', String(views[index] === view)));
    }
    choose(views[0]);
    box.appendChild(picker);
    return box;
  }

  function statRow(hero, key, label) {
    const values = data.heroes.map((other) => other.stats[key]);
    const top = Math.max(...values);
    const average = values.reduce((sum, value) => sum + value, 0) / values.length;
    const row = el('tr');
    const th = el('th', '', label);
    th.scope = 'row';
    row.appendChild(th);
    const cell = el('td', 'bar-cell');
    const bar = svg('svg', { viewBox: '0 0 100 6', preserveAspectRatio: 'none', class: 'bar', 'aria-hidden': 'true' });
    bar.appendChild(svg('rect', { class: 'bar-fill', width: 100 * hero.stats[key] / top, height: 6 }));
    bar.appendChild(svg('rect', { class: 'bar-mark', x: 100 * average / top - 0.75, width: 1.5, height: 6 }));
    cell.appendChild(bar);
    row.appendChild(cell);
    row.appendChild(el('td', 'num', String(hero.stats[key])));
    return row;
  }

  function fillDetail(hero) {
    const body = $('detail-body');
    body.replaceChildren();

    const head = el('div', 'd-top');
    head.appendChild(gallery(hero));
    const info = el('div');
    const title = el('div', 'd-head');
    const name = el('h2', '', hero.name);
    name.id = 'detail-name';
    title.appendChild(name);
    const cost = costBadge(hero.cost);
    cost.classList.add('cost-' + hero.cost);
    title.appendChild(cost);
    title.appendChild(statusTag(hero));
    info.appendChild(title);
    const sub = el('p', 'd-sub');
    for (const kind of ['race', 'class']) {
      const chip = button('chip', undefined, () => filterBy(kind, hero[kind]));
      chip.title = 'Show every ' + traits.get(hero[kind]).name;
      chip.appendChild(traitLabel(hero[kind]));
      sub.appendChild(chip);
    }
    sub.appendChild(el('span', 'muted', hero.role));
    info.appendChild(sub);

    const skill = el('div', 'skill');
    skill.appendChild(el('span', 'muted small', SKILL_TYPE[hero.skill.type]));
    skill.appendChild(el('strong', '', hero.skill.name));
    skill.appendChild(el('span', '', hero.skill.text));
    info.appendChild(skill);

    info.appendChild(el('h3', '', 'Stats'));
    const table = el('table', 'stats');
    const tbody = el('tbody');
    for (const [key, label] of STAT_ROWS) tbody.appendChild(statRow(hero, key, label));
    table.appendChild(tbody);
    info.appendChild(table);
    info.appendChild(el('p', 'note', (hero.status === 'playable'
      ? 'One-star values currently in the game. Untuned.'
      : 'Design targets. This hero is not in the game yet.') +
      ' Each bar is measured against the highest value in the roster; the tick is the roster average.'));
    head.appendChild(info);
    body.appendChild(head);

    const cols = el('div', 'd-cols');
    const facts = el('dl', 'facts');
    for (const [key, label] of FACTS) {
      const pair = el('div');
      pair.appendChild(el('dt', '', label));
      pair.appendChild(el('dd', '', hero.description[key]));
      facts.appendChild(pair);
    }
    cols.appendChild(facts);
    const syn = el('div', 'syn');
    syn.appendChild(el('h3', '', 'Synergies'));
    for (const kind of ['race', 'class']) {
      const trait = traits.get(hero[kind]);
      const line = el('p');
      const link = button('link strong', trait.name + ' (' + trait.thresholds.join(' / ') + ')', () => filterBy(kind, trait.id));
      link.title = 'Show every ' + trait.name;
      line.appendChild(link);
      line.appendChild(document.createTextNode(' ' + trait.bonus));
      syn.appendChild(line);
    }
    cols.appendChild(syn);
    body.appendChild(cols);
  }

  // Previous and next walk the heroes currently listed; a hero outside the filter walks the whole roster.
  const walk = () => (shown.includes(current) ? shown : data.heroes);
  function show(hero) {
    current = hero;
    fillDetail(hero);
    const list = walk();
    $('position').textContent = (list.indexOf(hero) + 1) + ' of ' + list.length;
    document.title = hero.name + ' — Wonder Chess';
    if (!$('detail').open) $('detail').showModal();
    $('detail').scrollTop = 0;
  }
  function open(hero) {
    history.pushState({ hero: true }, '', address(slug(hero)));
    show(hero);
  }
  function step(offset) {
    const list = walk();
    const hero = list[(list.indexOf(current) + offset + list.length) % list.length];
    history.replaceState(history.state, '', address(slug(hero)));
    show(hero);
  }
  function closed() {
    current = null;
    document.title = 'Wonder Chess — Hero Catalogue';
    if (!new URLSearchParams(location.search).has('hero')) return;
    // Opened from a card: Back closes it. Opened from a shared link: there is nothing to go back to.
    if (history.state && history.state.hero) history.back();
    else history.replaceState(null, '', address());
  }

  function sorted(heroes) {
    const sort = $('sort').value;
    if (!sort) return heroes;
    const order = (kind) => (hero) => data.traits.findIndex((trait) => trait.id === hero[kind]);
    const key = { cost: (hero) => hero.cost, 'cost-desc': (hero) => -hero.cost, race: order('race'), class: order('class') }[sort];
    return heroes.slice().sort((a, b) => (key ? key(a) - key(b) : 0) || a.name.localeCompare(b.name));
  }
  function render() {
    const query = $('search').value.trim().toLowerCase();
    const race = $('race').value, cls = $('class').value, cost = $('cost').value, status = $('status').value;
    shown = sorted(data.heroes.filter((hero) =>
      (!race || hero.race === race) && (!cls || hero.class === cls) &&
      (!cost || String(hero.cost) === cost) && (!status || hero.status === status) &&
      (!query || (hero.name + ' ' + hero.skill.name + ' ' + hero.skill.text).toLowerCase().includes(query))));
    rendered = true;
    $('grid').replaceChildren(...shown.map(card));
    $('count').textContent = shown.length === data.heroes.length
      ? 'Showing all ' + shown.length + ' heroes'
      : 'Showing ' + shown.length + ' of ' + data.heroes.length + ' heroes';
    $('empty').hidden = shown.length > 0;
    $('reset').hidden = !(query || race || cls || cost || status);
  }
  function changed() {
    render();
    history.replaceState(history.state, '', address());
  }
  function reset(keep) {
    $('search').value = '';
    for (const key of FILTERS) if (key !== 'sort') $(key).value = '';
    if (keep) $(keep.kind).value = keep.id;
    changed();
  }
  function filterBy(kind, id) {
    if ($('detail').open) $('detail').close();
    reset({ kind, id });
    $('heroes').scrollIntoView();
  }

  function traitCard(trait) {
    const item = el('li', 'trait');
    const head = el('div', 'trait-head');
    head.appendChild(traitLabel(trait.id));
    head.appendChild(el('span', 'steps-at', trait.thresholds.join(' / ')));
    head.appendChild(trait.status === 'in_engine' ? el('span', 'tag live', 'Built') : el('span', 'tag', 'Planned'));
    item.appendChild(head);
    item.appendChild(el('p', '', trait.bonus));
    const members = el('div', 'members');
    for (const id of trait.members) {
      const hero = byId.get(id);
      members.appendChild(button('chip', hero.name, () => open(hero)));
    }
    item.appendChild(members);
    item.appendChild(button('link small', 'Show in the hero list', () => filterBy(trait.kind, trait.id)));
    return item;
  }
  function relicCard(relic) {
    const item = el('li', 'relic');
    item.appendChild(icon('relic'));
    const text = el('div');
    text.appendChild(el('strong', '', relic.name));
    text.appendChild(el('span', '', relic.text));
    item.appendChild(text);
    return item;
  }
  function steps(rules) {
    const list = [
      ['Build between fights', rules.seatCount + ' players each build their own team. Before every fight you buy heroes from your own shop of ' +
        rules.shopSlots + ', place them on your half of the ' + rules.columns + ' by ' + rules.rows + ' board and keep spares on a ' +
        rules.benchCapacity + '-slot bench. You start with ' + rules.startingGold + ' gold; refreshing the shop costs ' + rules.rerollCost + '.'],
      ['Fights run themselves', 'Once a fight starts you only watch. Heroes move, attack and use their skill on their own, so where you placed them decides the fight. ' +
        'Losing a fight costs health, and everyone starts with ' + rules.startingHealth + '.'],
      ['Stack synergies', 'Every hero has one race and one class. Deploy 2 different heroes that share one to switch its bonus on, and 4 for the stronger version.'],
      ['Pick relics', 'At rounds ' + rules.relicRounds.slice(0, -1).join(', ') + ' and ' + rules.relicRounds.slice(-1) + ' you choose one of ' +
        rules.relicOffers + ' relics. Any hero can carry a relic, one per hero.'],
    ];
    return list.map(([title, text]) => {
      const item = el('li');
      item.appendChild(el('strong', '', title));
      item.appendChild(el('span', '', text));
      return item;
    });
  }

  function fill(select, entries) {
    for (const [value, label] of entries) {
      const option = el('option', '', label);
      option.value = value;
      select.appendChild(option);
    }
  }

  fetch('data/catalogue.json')
    .then((response) => {
      if (!response.ok) throw new Error('HTTP ' + response.status);
      return response.json();
    })
    .then((loaded) => {
      data = loaded;
      for (const hero of data.heroes) { byId.set(hero.id, hero); bySlug.set(slug(hero), hero); }
      for (const trait of data.traits) traits.set(trait.id, trait);
      const races = data.traits.filter((t) => t.kind === 'race');
      const classes = data.traits.filter((t) => t.kind === 'class');
      const playable = data.heroes.filter((h) => h.status === 'playable').length;
      $('summary').textContent = data.heroes.length + ' heroes across ' + races.length + ' races and ' +
        classes.length + ' classes. ' + playable + ' are in the game today; the rest are planned.';
      fill($('race'), races.map((t) => [t.id, t.name]));
      fill($('class'), classes.map((t) => [t.id, t.name]));
      fill($('cost'), [1, 2, 3, 4, 5].map((c) => [String(c), 'Cost ' + c]));
      $('races').replaceChildren(...races.map(traitCard));
      $('classes').replaceChildren(...classes.map(traitCard));
      $('relic-intro').textContent = 'All ' + data.relics.length + ' relics fit every hero and give a plain stat bonus with no drawback.';
      $('relic-list').replaceChildren(...data.relics.map(relicCard));
      $('steps').replaceChildren(...steps(data.rules));

      $('filters').addEventListener('input', changed);
      $('filters').addEventListener('submit', (event) => event.preventDefault());
      $('reset').addEventListener('click', () => reset());
      $('empty-reset').addEventListener('click', () => reset());
      $('prev').addEventListener('click', () => step(-1));
      $('next').addEventListener('click', () => step(1));
      $('close').addEventListener('click', () => $('detail').close());
      $('detail').addEventListener('close', closed);
      $('detail').addEventListener('click', (event) => { if (event.target === $('detail')) $('detail').close(); });
      $('detail').addEventListener('keydown', (event) => {
        if (event.key === 'ArrowLeft') step(-1);
        if (event.key === 'ArrowRight') step(1);
      });
      window.addEventListener('popstate', readAddress);
      readAddress();
      // The sections only get their height now, so a link to one has to be followed again.
      const target = location.hash.length > 1 && document.getElementById(location.hash.slice(1));
      const jump = () => target.scrollIntoView({ behavior: 'instant' });
      if (target && !current) {
        jump();
        if (document.readyState !== 'complete') window.addEventListener('load', jump, { once: true });
      }
    })
    .catch((error) => {
      $('summary').textContent = 'The catalogue could not be loaded (' + error.message + ').';
    });
}());
