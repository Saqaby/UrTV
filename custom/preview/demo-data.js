// بيانات تجريبية للمعاينة فقط: تحل محل الطقس والمباريات والأسواق حتى تظهر الشاشة كاملة خارج التلفزيون.
(function () {
  const H = 3600e3, now = Date.now();
  const iso = t => new Date(t).toISOString().replace('.000Z', '');
  const json = o => Promise.resolve(new Response(JSON.stringify(o), { status: 200, headers: { 'Content-Type': 'application/json' } }));
  const ev = (id, home, hid, away, aid, t, hs, as, st) => ({
    idEvent: id, strEvent: home + ' vs ' + away, strHomeTeam: home, idHomeTeam: hid, strAwayTeam: away, idAwayTeam: aid,
    strTimestamp: iso(t), dateEvent: iso(t).slice(0, 10), strTime: iso(t).slice(11), strSport: 'Soccer',
    strLeague: 'Saudi-Arabian Pro League', intHomeScore: hs, intAwayScore: as, strStatus: st || 'NS'
  });
  const day = [...Array(5)].map((_, i) => new Date(now + i * 24 * H).toISOString().slice(0, 10));
  const hrs = [...Array(120)].map((_, i) => { const d = new Date(now - (now % H) + i * H); return d.toISOString().slice(0, 13) + ':00'; });
  const routes = [
    [/api\.open-meteo\.com/, () => ({
      current: { temperature_2m: 31, weather_code: 1 },
      daily: { time: day, temperature_2m_max: [36, 35, 34, 33, 35], temperature_2m_min: [22, 21, 21, 20, 22], weather_code: [1, 2, 0, 3, 1],
               sunrise: day.map(d => d + 'T06:12'), sunset: day.map(d => d + 'T17:31') },
      hourly: { time: hrs, temperature_2m: hrs.map((_, i) => 24 + Math.round(8 * Math.sin(i / 4))), weather_code: hrs.map(i => 1) }
    })],
    [/air-quality-api/, () => ({ current: { pm10: 40, dust: 10 } })],
    [/eventsnext\.php\?id=136013/, () => ({ events: [ev('901', 'Al-Hilal', '136013', 'Al-Nassr', '136022', now + 20 * H)] })],
    [/eventslast\.php\?id=136013/, () => ({ results: [ev('900', 'Al-Ittihad', '136018', 'Al-Hilal', '136013', now - 20 * H, '1', '2', 'FT')] })],
    [/eventsnext\.php/, () => ({ events: [] })],
    [/eventslast\.php/, () => ({ results: [] })],
    [/markets\.json/, () => ({ updated: new Date(now).toISOString(), quotes: {
      '^TASI.SR': { p: 11820, v: 11764, c: 0.48, t: now / 1e3 }, '^GSPC': { p: 5980, v: 5960, c: 0.34, t: now / 1e3 },
      'BTC-USD': { p: 98000, v: 99000, c: -1.0, t: now / 1e3 } } })]
  ];
  const real = window.fetch.bind(window);
  window.fetch = function (url, opt) {
    const u = String(url && url.url || url);
    for (const [re, body] of routes) if (re.test(u)) return json(body());
    return real(url, opt);
  };
})();
