package sa.urtv.home.tilawah;

import android.app.AlarmManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.AudioManager;
import android.media.ToneGenerator;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.PowerManager;
import android.widget.Toast;

import java.util.Calendar;
import java.util.Locale;
import java.util.TimeZone;

/**
 * Ramadan on its own, every year, by the Umm al-Qura calendar: an hour before Fajr a short chime and «السحور» on screen,
 * and half an hour before Maghrib the Quran radio, unless something else is already playing. One alarm, the nearest of
 * the two, put back with the adhan's (AdhanScheduler.schedule) and after each one fires; AdhanReceiver passes it here.
 * Like the adhan, nothing happens to a TV in standby, and nothing is made up later.
 */
public final class RamadanAlarms {
    static final String ACTION = "sa.urtv.home.RAMADAN_ALARM";
    static final String EXTRA_KIND = "kind";
    static final int SUHOOR = 1, RADIO = 2;
    static final long SUHOOR_BEFORE = 60 * 60_000L, RADIO_BEFORE = 30 * 60_000L;
    private static final int REQUEST = 48;

    private RamadanAlarms() {}

    static void schedule(Context c) {
        AlarmManager am = (AlarmManager) c.getSystemService(Context.ALARM_SERVICE);
        if (am == null) return;
        long now = System.currentTimeMillis();
        long at = 0;
        int kind = 0;
        Place place = Place.get(c);
        Calendar day = Calendar.getInstance(TimeZone.getTimeZone(place.tz), Locale.US);
        for (int d = 0; d < 3 && at == 0; d++) {
            PrayerTimes t = d == 0 ? PrayerTimes.today(c, place) : PrayerTimes.of(day, place);
            if (t.ramadan()) {
                long suhoor = t.at[PrayerTimes.FAJR] - SUHOOR_BEFORE, radio = t.at[PrayerTimes.MAGHRIB] - RADIO_BEFORE;
                if (suhoor > now + 30_000) { at = suhoor; kind = SUHOOR; }
                else if (radio > now + 30_000) { at = radio; kind = RADIO; }
            }
            day.add(Calendar.DAY_OF_MONTH, 1);
        }
        PendingIntent pending = pending(c, kind);
        am.cancel(pending);
        if (at == 0) return;   // not Ramadan within two days: nothing set
        try {
            if (AdhanScheduler.exactAllowed(c) && Build.VERSION.SDK_INT >= 23) am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pending);
            else am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pending);
        } catch (SecurityException e) {
            am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, at, pending);
        }
    }

    /** The alarm went off: the chime and the words, or the radio; then the next one. */
    static void fire(Context c, Intent intent) {
        int kind = intent.getIntExtra(EXTRA_KIND, 0);
        PowerManager pm = (PowerManager) c.getSystemService(Context.POWER_SERVICE);
        if (pm == null || pm.isInteractive()) {
            if (kind == SUHOOR) {
                chime();
                Toast.makeText(c, "السحور: بقيت ساعة على أذان الفجر", Toast.LENGTH_LONG).show();
            } else if (kind == RADIO) {
                AudioManager audio = (AudioManager) c.getSystemService(Context.AUDIO_SERVICE);
                // never over what the family is watching or listening to
                if ((audio == null || !audio.isMusicActive()) && !NowPlaying.quranRadioOn()) {
                    NowPlaying.playQuranRadio(c);
                    Toast.makeText(c, "إذاعة القرآن: بقيت نصف ساعة على الإفطار", Toast.LENGTH_LONG).show();
                }
            }
        }
        schedule(c);
    }

    /** Two soft beeps, on the media volume (a TV may have no notification sound). */
    private static void chime() {
        try {
            final ToneGenerator tone = new ToneGenerator(AudioManager.STREAM_MUSIC, 70);
            tone.startTone(ToneGenerator.TONE_PROP_BEEP2, 900);
            new Handler(Looper.getMainLooper()).postDelayed(tone::release, 1500);
        } catch (RuntimeException ignored) { }   // no tone on this TV: the words still show
    }

    /** Ramadan, between Fajr and Maghrib today: when the iftar is (the home screen's Ramadan window counts down to it); else 0. */
    public static long iftarAt(Context c) {
        try {
            PrayerTimes t = PrayerTimes.today(c);
            long now = System.currentTimeMillis();
            return t.ramadan() && now >= t.at[PrayerTimes.FAJR] && now < t.at[PrayerTimes.MAGHRIB] ? t.at[PrayerTimes.MAGHRIB] : 0;
        } catch (RuntimeException e) {
            return 0;
        }
    }

    private static PendingIntent pending(Context c, int kind) {
        Intent intent = new Intent(c, AdhanReceiver.class).setAction(ACTION).putExtra(EXTRA_KIND, kind);
        int flags = PendingIntent.FLAG_UPDATE_CURRENT;
        if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
        return PendingIntent.getBroadcast(c, REQUEST, intent, flags);
    }
}
