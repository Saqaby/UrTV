package sa.urtv.home;

/**
 * The home screen's fasting reminder, under the Ramadan window: «غدًا صيام الإثنين», «اليوم يوم عرفة». Only Arafah, Ashura,
 * the white days and Mondays (the owner's choice), never on the days fasting is forbidden, and nothing in Ramadan (the
 * Ramadan window says it). The same days as the screensaver's fasting slot (fastReasons in src/template.html).
 * Months are Hijri from 1 (Muharram); weekdays from 0 (Sunday). MainActivity reads the Umm al-Qura dates in the city's zone.
 */
final class FastingText {
    /** From this hour (the city's) today's fast is behind us: the reminder speaks of tomorrow. As the screensaver's slot. */
    static final int TODAY_UNTIL = 18;

    private FastingText() {}

    /** The best reason to fast that day, or null. */
    static String reason(int month, int day, int weekday) {
        if ((month == 10 && day == 1) || (month == 12 && day >= 10 && day <= 13)) return null;   // the Eids, Tashreeq
        if (month == 9) return null;   // Ramadan: the Ramadan window
        if (month == 12 && day == 9) return "يوم عرفة";
        if (month == 1 && day == 10) return "صيام عاشوراء";
        if (day >= 13 && day <= 15) return "صيام الأيام البيض";
        if (weekday == 1) return "صيام الإثنين";
        return null;
    }

    /** What the chip says now, or null for no chip: today until TODAY_UNTIL, else tomorrow. */
    static String text(int hour, int[] today, int[] tomorrow) {
        if (hour < TODAY_UNTIL) {
            String r = reason(today[0], today[1], today[2]);
            if (r != null) return "اليوم " + r;
        }
        String r = reason(tomorrow[0], tomorrow[1], tomorrow[2]);
        return r == null ? null : "غدًا " + r;
    }
}
