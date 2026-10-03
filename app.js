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
  const SVG = 'http://www.w3.org/2000/svg';

  const $ = (id) => document.getElementById(id);
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function silhouette() {
    const svg = document.createElementNS(SVG, 'svg');
    svg.setAttribute('viewBox', '0 0 64 80');
    svg.setAttribute('aria-hidden', 'true');
    const head = document.createElementNS(SVG, 'circle');
    head.setAttribute('cx', '32'); head.setAttribute('cy', '20'); head.setAttribute('r', '14');
    const body = document.createElementNS(SVG, 'path');
    body.setAttribute('d', 'M12 78c0-18 8-32 20-32s20 14 20 32z');
    for (const part of [head, body]) { part.setAttribute('fill', 'currentColor'); svg.appendChild(part); }
    return svg;
  }
  function art(path, alt, label) {
    if (path) {
      const img = el('img');
      img.src = path; img.alt = alt; img.loading = 'lazy';
      return img;
    }
    const box = el('div', 'placeholder');
    box.appendChild(silhouette());
    box.appendChild(el('span', '', label));
    return box;
  }
  function statusTag(hero) {
    return hero.status === 'playable' ? el('span', 'tag live', 'In the game') : el('span', 'tag', 'Planned');
  }
  function costBadge(cost) {
    const badge = el('span', 'cost cost-' + cost, String(cost));
    badge.title = 'Cost ' + cost;
    return badge;
  }

  let data = null;
  const byId = new Map();
  const traitName = (id) => data.traits.find((t) => t.id === id).name;

  function card(hero) {
    const item = el('li');
    const button = el('button', 'card');
    button.type = 'button';
    const frame = el('div', 'card-art');
    frame.appendChild(art(hero.art.main, hero.name + ', main view', 'Art pending'));
    frame.appendChild(statusTag(hero));
    const body = el('div', 'card-body');
    const name = el('div', 'card-name');
    name.appendChild(el('span', '', hero.name));
    name.appendChild(costBadge(hero.cost));
    body.appendChild(name);
    body.appendChild(el('div', 'card-meta', traitName(hero.race) + ' · ' + traitName(hero.class)));
    button.appendChild(frame);
    button.appendChild(body);
    button.addEventListener('click', () => open(hero));
    item.appendChild(button);
    return item;
  }

  function open(hero) {
    const body = $('detail-body');
    body.replaceChildren();

    const head = el('div', 'd-head');
    const title = el('h2', '', hero.name);
    title.id = 'detail-name';
    head.appendChild(title);
    head.appendChild(costBadge(hero.cost));
    head.appendChild(statusTag(hero));
    body.appendChild(head);
    body.appendChild(el('p', 'd-sub', traitName(hero.race) + ' · ' + traitName(hero.class) + ' · ' + hero.role));

    const views = el('div', 'views');
    for (const view of data.views) {
      const figure = el('figure', 'view');
      const frame = el('div', 'view-frame');
      frame.appendChild(art(hero.art[view], hero.name + ', ' + VIEW_LABEL[view].toLowerCase() + ' view', 'Art pending'));
      figure.appendChild(frame);
      figure.appendChild(el('figcaption', '', VIEW_LABEL[view]));
      views.appendChild(figure);
    }
    body.appendChild(views);

    const cols = el('div', 'd-cols');
    const left = el('div');
    const skill = el('div', 'skill');
    skill.appendChild(el('span', 'muted small', SKILL_TYPE[hero.skill.type]));
    skill.appendChild(el('strong', '', hero.skill.name));
    skill.appendChild(el('span', '', hero.skill.text));
    left.appendChild(skill);
    const facts = el('dl', 'facts');
    for (const [key, label] of FACTS) {
      facts.appendChild(el('dt', '', label));
      facts.appendChild(el('dd', '', hero.description[key]));
    }
    left.appendChild(facts);

    const right = el('div');
    right.appendChild(el('h3', '', 'Stats'));
    const table = el('table', 'stats');
    const tbody = el('tbody');
    for (const [key, label] of STAT_ROWS) {
      const row = el('tr');
      const th = el('th', '', label);
      th.scope = 'row';
      row.appendChild(th);
      row.appendChild(el('td', '', String(hero.stats[key])));
      tbody.appendChild(row);
    }
    table.appendChild(tbody);
    right.appendChild(table);
    right.appendChild(el('p', 'note', hero.status === 'playable'
      ? 'One-star values currently in the game. Untuned.'
      : 'Design targets. This hero is not in the game yet.'));
    const syn = el('div', 'syn');
    syn.appendChild(el('h3', '', 'Synergies'));
    for (const id of [hero.race, hero.class]) {
      const trait = data.traits.find((t) => t.id === id);
      const line = el('p');
      line.appendChild(el('strong', '', trait.name + ' (' + trait.thresholds.join(' / ') + '): '));
      line.appendChild(document.createTextNode(trait.bonus));
      syn.appendChild(line);
    }
    right.appendChild(syn);

    cols.appendChild(left);
    cols.appendChild(right);
    body.appendChild(cols);
    $('detail').showModal();
    $('detail').scrollTop = 0;
  }

  function render() {
    const query = $('search').value.trim().toLowerCase();
    const race = $('race').value, cls = $('class').value, cost = $('cost').value, status = $('status').value;
    const shown = data.heroes.filter((hero) =>
      (!race || hero.race === race) && (!cls || hero.class === cls) &&
      (!cost || String(hero.cost) === cost) && (!status || hero.status === status) &&
      (!query || (hero.name + ' ' + hero.skill.name + ' ' + hero.skill.text).toLowerCase().includes(query)));
    $('grid').replaceChildren(...shown.map(card));
    $('count').textContent = shown.length === data.heroes.length
      ? 'Showing all ' + shown.length + ' heroes'
      : 'Showing ' + shown.length + ' of ' + data.heroes.length + ' heroes';
  }

  function traitCard(trait) {
    const item = el('li', 'trait');
    const head = el('div', 'trait-head');
    head.appendChild(el('span', '', trait.name));
    head.appendChild(trait.status === 'in_engine' ? el('span', 'tag live', 'Built') : el('span', 'tag', 'Planned'));
    item.appendChild(head);
    item.appendChild(el('p', '', trait.bonus));
    item.appendChild(el('div', 'members', trait.members.map((id) => byId.get(id).name).join(' · ')));
    return item;
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
      for (const hero of data.heroes) byId.set(hero.id, hero);
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
      $('filters').addEventListener('input', render);
      $('filters').addEventListener('submit', (event) => event.preventDefault());
      $('detail').addEventListener('click', (event) => { if (event.target === $('detail')) $('detail').close(); });
      render();
    })
    .catch((error) => {
      $('summary').textContent = 'The catalogue could not be loaded (' + error.message + ').';
    });
}());
