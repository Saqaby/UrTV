package sa.urtv.home;

/**
 * The words of the home screen's Ramadan window, under the date: «باقٍ على رمضان ١٠٧ يومًا» until it begins, then
 * «رمضان مبارك · اليوم ٥». The days come from the Umm al-Qura calendar in the city's zone (MainActivity); here only the
 * Arabic count: يوم واحد، يومان، ٣–١٠ أيام، ١١ يومًا فأكثر. Digits as the setting says (Digits.of, by the caller).
 */
final class RamadanText {
    private RamadanText() {}

    /** daysLeft > 0: before Ramadan; day 1..30: in it (daysLeft is then 0). */
    static String text(int daysLeft, int dayOfRamadan) {
        if (daysLeft <= 0) return "رمضان مبارك · اليوم " + dayOfRamadan;
        return "باقٍ على رمضان " + days(daysLeft);
    }

    static String days(int n) {
        if (n == 1) return "يوم واحد";
        if (n == 2) return "يومان";
        if (n <= 10) return n + " أيام";
        return n + " يومًا";
    }
}
