// التطبيقات المثبّتة (عيّنة للمعاينة) وصف المفضلة. تعديل: الحد الأدنى صار تطبيقًا واحدًا بدل ٥ (Dock.MIN في Dock.java).
const ALL_APPS = {
  seen: ['Seen', '#e50914'], movieboxpro: ['MovieBoxPro', '#2b2b2e'], appletv: ['Apple TV', '#1c1c1e'], youtube: ['يوتيوب', '#c4302b'],
  shahid: ['شاهد', '#13a59c'], osn: ['OSN+', '#111111'], crunchyroll: ['Crunchyroll', '#f47521'], jellyfin: ['Jellyfin', '#1d2457'],
  netflix: ['نتفليكس', '#b20710'], prime: ['Prime Video', '#1a98ff'], disney: ['ديزني+', '#0e2a6b'], spotify: ['سبوتيفاي', '#1db954'],
  stctv: ['stc tv', '#4f008c'], plex: ['Plex', '#e5a00d'], vlc: ['VLC', '#ff8800']
};
const DOCK_MIN = 1, DOCK_MAX = 10;
const DOCK_DEFAULT = ['youtube', 'seen'];   // تعديل: البداية يوتيوب وSeen فقط
function loadDock() {
  try { const d = JSON.parse(localStorage.getItem('dock2')); if (Array.isArray(d) && d.length >= DOCK_MIN) return d.filter(k => ALL_APPS[k]); } catch (e) {}
  return DOCK_DEFAULT.slice();
}
function saveDock(d) { try { localStorage.setItem('dock2', JSON.stringify(d)); } catch (e) {} }
