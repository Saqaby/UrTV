#!/usr/bin/env python3
"""This copy's own changes (Saqaby/UrTV): the 8-hour card and the sayings of the salaf, no markets line, the time left in the prayers
card, the weather icon, the home screen's four pills and settings menu, the Ramadan window, a dock of one app and up, and the links
that point at this copy so its own updates reach the TV.   Run: python3 tests/custom_test.py"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT / "android/launcher/src/main/java/sa/urtv/home"
failed = 0
def check(name, ok, detail=""):
    global failed
    print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {detail}"))
    failed += not ok
text = lambda p: p.read_text(encoding="utf-8")

# ---- the sayings of the salaf
salaf = json.loads(text(ROOT / "assets/shared/salaf.json"))
check("salaf.json: at least 30 sayings", len(salaf) >= 30, len(salaf))
bad = [s for s in salaf if set(s) != {"who", "text", "src"} or not all(str(s[k]).strip() for k in s)]
check("salaf.json: each has who said it, the words and the book", not bad, bad[:2])
check("salaf.json: no saying twice", len({s["text"] for s in salaf}) == len(salaf))

# ---- the screensaver's page
page = text(ROOT / "src/template.html")
check("the card beside the clock changes every 8 hours: verse, hadith, salaf",
      "Math.floor(riyadhParts().h / 8)" in page and "part === 0" in page and "part === 2" in page and "'من أقوال السلف'" in page)
check("the page repaints that card when the part of the day changes", page.count("quotePart() !== lastPart") == 2)
check("build.py puts the sayings in the page", "__SALAF__" in text(ROOT / "src/build.py") and "__SALAF__" in page)
dist = text(ROOT / "dist/tv.html")
check("dist/tv.html carries the sayings", "__SALAF__" not in dist and salaf[0]["text"] in dist)
check("no markets line at the top left, and no prices asked for it", "html:not(.mk-on) .mk,html:not(.mk-on) #mk-up{display:none!important}" in page
      and "if(CONFIG.mkLine || CONFIG.slot === 'markets' || USES('stocks')) loadMarkets();" in page)
check("the prayers card says the time left under the next prayer", 'class="left">- ' in page and "' دقيقة'" in page and "' س '" in page)
check("the weather icon before the temperature", 'id="wx-icon"' in page and "setHTML(document.getElementById('wx-icon'), wxIcon(" in page)
check("no «يُتلى الآن» card", "nowPlayingTick" not in page and 'id="np"' not in page)

# ---- the links: this copy's own page, photos and builds
for path, needle in [("android/app/src/main/java/sa/urtv/screensaver/PhotoCache.java", "Saqaby/UrTV/"),
                     ("android/app/src/main/java/sa/urtv/screensaver/Updater.java", "github.com/Saqaby/UrTV/releases/latest"),
                     ("src/build.py", "raw.githubusercontent.com/Saqaby/UrTV/master/"),
                     ("optimize/install.sh", "github.com/Saqaby/UrTV/releases/download")]:
    check(f"{path} points at this copy", needle in text(ROOT / path))
check("the workflows do not need the private fonts", all("urtv-fonts" not in text(ROOT / ".github/workflows" / f)
      for f in ("android.yml", "checks.yml", "screens.yml")))
check("the fonts are in place (IBM Plex Sans Arabic under the names the code loads)",
      all((ROOT / "assets/fonts" / f"{n}.woff2").exists() and (ROOT / "android/launcher/src/main/assets/fonts" / f"{n}.otf").exists()
          for n in ("Thmanyah-Light", "Thmanyah-Regular", "Thmanyah-Medium", "ThmanyahDisplay-Bold"))
      and (ROOT / "assets/fonts/IBMPlexSansArabic-OFL.txt").exists())

# ---- the home screen
main = text(HOME / "MainActivity.java")
check("five pills: sources, network, settings, sleep, the Quran radio (and al-Kahf on Fridays)", "Arrays.asList(inputs, wifiPill, settings, sleepPill, radioPill, kahfPill)" in main
      and 'pill("المهام"' not in main and 'pill("شاشة التوقف"' not in main and 'pill("تلاوة وأذان"' not in main)
check("«الإعدادات» opens a menu: الأذان، ترتيب المفضلة، المهام، شاشة التوقف، إعدادات التلفزيون",
      "settings.setOnClickListener(v -> showSettings(v));" in main
      and all(f'inputRow("{w}"' in main for w in ("الأذان", "ترتيب المفضلة", "المهام", "شاشة التوقف", "إعدادات التلفزيون")))
check("no «يُتلى الآن» card on the home screen", "NowCard" not in main and "nowCard" not in main and "updateNowPlaying" not in main and not (HOME / "NowCard.java").exists())
check("the Hijri date is the main line, the Gregorian under it", "gregLine.setText(" in main and "date.setText(arabicDigits(hijri.isEmpty() ? greg : hijri));" in main)
check("the Ramadan window counts by Umm al-Qura", "islamic-umalqura" in main and "RamadanText.text(" in main)
check("the dock: five or fewer apps centred and larger", "boolean fit = dock.size() <= 5;" in main and "dp(160)" in main)
check("a dock of one app is allowed", "static final int MIN = 1;" in text(HOME / "Dock.java"))
greeting = text(HOME / "Greeting.java")
check("the weather line has its icon", "GreetingText.icon(" in greeting and "setCompoundDrawablesRelative(" in greeting)
drawables = ROOT / "android/launcher/src/main/res/drawable"
check("the weather icons exist", all((drawables / f"wx_{n}.xml").exists() for n in ("sun", "moon", "part", "partnight", "cloud", "fog", "rain", "snow", "storm")))
service = text(HOME / "tilawah/MusicService.java")
check("«إذاعة القرآن» plays the Saudi Quran Radio and starts the screensaver, and stops it when pressed again",
      "playQuranRadio(this)" in main and "Somnambulator" in main and 'SAVER_PKG + ".MainActivity"' in main
      and "NowPlaying.stop(this)" in main and 'radioPill.setLabel(on ? "إيقاف الإذاعة" : "إذاعة القرآن")' in main)
check("the adhan asks for the sound for a while only, so what played carries on after it", "AUDIOFOCUS_GAIN_TRANSIENT" in service)

# ---- Friday's al-Kahf, the Ramadan alarms, the night clock and the iftar countdown
main = text(HOME / "MainActivity.java")
check("al-Kahf: a pill from Thursday 18:00 to Friday 18:00, and while it plays", "kahfPill" in main
      and "dow == Calendar.THURSDAY && hour >= 18" in main and "dow == Calendar.FRIDAY && hour < 18" in main and "boolean show = on ||" in main)
check("al-Kahf: the reciters to choose from, then surah 18 alone", "NowPlaying.reciters(this)" in main and "NowPlaying.playKahf(this, r[0])" in main)
svc = text(HOME / "tilawah/MusicService.java")
check("al-Kahf: played once, stopped at its end, not on to the next surah",
      "if (source == Prefs.SOURCE_SURAH && once) stopPlayback();" in svc and "putExtra(EXTRA_ONCE, true)" in svc)
check("hidden pills are stepped over by the D-pad", "if (p.getVisibility() == View.VISIBLE) shown.add(p);" in main)
ram = text(HOME / "tilawah/RamadanAlarms.java")
check("Ramadan: the chime an hour before Fajr, the radio half an hour before Maghrib",
      "SUHOOR_BEFORE = 60 * 60_000L" in ram and "RADIO_BEFORE = 30 * 60_000L" in ram and "t.ramadan()" in ram)
check("Ramadan: the radio never over something already playing", "!audio.isMusicActive()" in ram and "!NowPlaying.quranRadioOn()" in ram)
check("Ramadan: set with the adhan's alarm, fired through its receiver",
      "RamadanAlarms.schedule(c);" in text(HOME / "tilawah/AdhanScheduler.java")
      and "RamadanAlarms.fire(context, intent)" in text(HOME / "tilawah/AdhanReceiver.java"))
check("Ramadan: the home window counts down to the iftar", "RamadanAlarms.iftarAt(this)" in main and "RamadanText.iftarIn(" in main)
page = text(ROOT / "src/template.html")
check("screensaver: the clock is the time left to the iftar in Ramadan", "function iftarLeft(" in page and "'على الإفطار · الساعة '" in page)
check("screensaver: midnight to Fajr, a faint clock alone", "classList.toggle('nightclock'" in page and "html.nightclock .clock{opacity:.3" in page)

# ---- the words: RamadanText and GreetingText.icon, run with javac
if shutil.which("javac") and shutil.which("java"):
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / "Run.java"
        run.write_text("""package sa.urtv.home;
public class Run { public static void main(String[] a) {
  System.out.println(RamadanText.text(107, 0)); System.out.println(RamadanText.text(1, 0)); System.out.println(RamadanText.text(2, 0));
  System.out.println(RamadanText.text(5, 0)); System.out.println(RamadanText.text(0, 5));
  System.out.println(RamadanText.iftarIn(45)); System.out.println(RamadanText.iftarIn(134)); System.out.println(RamadanText.iftarIn(0));
  int[] mon = {5, 3, 1}, tue = {5, 4, 2}, sun = {5, 2, 0}, arafah = {12, 9, 3}, eid = {12, 10, 1}, tashreeq = {12, 13, 4}, ashura = {1, 10, 6},
        white = {7, 14, 2}, ramadanMon = {9, 5, 1}, thu = {5, 6, 4};
  System.out.println(FastingText.text(9, sun, mon) + "|" + FastingText.text(9, mon, tue) + "|" + FastingText.text(19, mon, tue) + "|"
    + FastingText.text(9, new int[]{12, 8, 2}, arafah) + "|" + FastingText.text(9, arafah, eid) + "|" + FastingText.text(9, eid, new int[]{12, 11, 2}) + "|"
    + FastingText.text(9, new int[]{12, 12, 3}, tashreeq) + "|" + FastingText.text(9, new int[]{1, 9, 5}, ashura) + "|" + FastingText.text(9, white, white) + "|"
    + FastingText.text(9, new int[]{9, 4, 0}, ramadanMon) + "|" + FastingText.text(9, new int[]{5, 5, 3}, thu));
  System.out.println(GreetingText.icon(0, 0, false) + " " + GreetingText.icon(1, 0, true) + " " + GreetingText.icon(2, 0, true) + " "
    + GreetingText.icon(3, 0, false) + " " + GreetingText.icon(61, 0, false) + " " + GreetingText.icon(0, 200, false) + " " + GreetingText.icon(95, 0, false));
} }""", encoding="utf-8")
        subprocess.run(["javac", "-encoding", "UTF-8", "-d", tmp, str(HOME / "RamadanText.java"), str(HOME / "FastingText.java"), str(HOME / "GreetingText.java"), str(HOME / "DigitsText.java"), str(run)], check=True, capture_output=True)
        out = subprocess.run(["java", "-Dfile.encoding=UTF-8", "-cp", tmp, "sa.urtv.home.Run"], capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
    want = ["باقٍ على رمضان 107 يومًا", "باقٍ على رمضان يوم واحد", "باقٍ على رمضان يومان", "باقٍ على رمضان 5 أيام", "رمضان مبارك · اليوم 5",
            "الإفطار بعد 45 دقيقة", "الإفطار بعد 2 س 14 د", "الإفطار بعد 1 دقيقة",
            "غدًا صيام الإثنين|اليوم صيام الإثنين|null|غدًا يوم عرفة|اليوم يوم عرفة|null|null|غدًا صيام عاشوراء|اليوم صيام الأيام البيض|null|null",
            "sun moon partnight cloud rain fog storm"]
    for got, exp in zip(out, want):
        check(f"words: {exp}", got == exp, got)
    check("words: every case ran", len(out) == len(want), out)
else:
    print("note: no javac here, the words were not run")

sys.exit(1 if failed else 0)
