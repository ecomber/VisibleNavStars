import datetime
import operator

import NavStarMagnitudes
from astroCalculator import AstroCalcs


def hours_to_hms(hours):
    mnt, sec = divmod(abs(hours) * 3600, 60)
    hr, mnt = divmod(mnt, 60)
    return f"{int(hr)}h {int(mnt)}m {round(sec)}s"


def is_between(t, start, end):
    if start <= end:
        return start <= t <= end
    else:  # crosses 0 deg
        return t >= start or t <= end


if __name__ == '__main__':
    HoFromSextant = 30
    MaxIntercept = 1 # degrees !!
    print(f'Sextant height: {AstroCalcs.deg_to_dm(HoFromSextant)}')
    localLat = 51  # Horta or near enough
    localLong = -0.5
    lowerAlt = 20
    upperAlt = 50
    leftWindow = 340
    rightWindow = 45
    minimumMagnitude = 3  # = 3 takes in all


    def displayStar(item, HoFromSextant,HoHcRange):
        asterix = "*" if abs(item[2] - HoFromSextant) < abs(HoHcRange) else ""
        # print(f'{item[0]:<15}Az:{item[1]:03.0f}°  Al:{item[2]:02.0f}°  Mag:{item[3]:+5.2f}  {AstroCalcs.deg_to_dm(item[2])} {AstroCalcs.deg_to_dm(item[2] - HoFromSextant)}  {asterix}')
        print(f'{item[0]:<15}Az:{item[1]:03.0f}°  Mag:{item[3]:+5.2f}  {AstroCalcs.deg_to_dm(item[2])} {AstroCalcs.deg_to_dm(item[2] - HoFromSextant)}  {asterix}')


    now = AstroCalcs.now()
    observation_time = datetime.datetime(year=2026, month=5, day=1, hour=22, minute=0, second=4, tzinfo=datetime.timezone.utc)

    targetTime = now #observation_time  # + datetime.timedelta(hours=12)
    print(f"Navigation Stars between Alt {lowerAlt}° and {upperAlt}°, visible at Lat:{localLat:.2f} Lon:{localLong:.2f}, at {str(targetTime)[:19]} UTC")
    jd = AstroCalcs.julian_day(targetTime)
    gst = AstroCalcs.greenwich_sidereal_time(jd)
    print(f"GST = GHA of Aires {gst:.2f}° {AstroCalcs.deg_to_dm(gst)} {hours_to_hms(gst / 15)}")
    lst = AstroCalcs.local_sidereal_time_from_gst(gst, localLong)
    print(f"LST at Long {localLong:.2f}: {lst:.2f}° {AstroCalcs.deg_to_dm(lst)} {hours_to_hms(lst / 15)}")

    allNavStars = {}
    with open("StarsSHA.txt") as f:  # Copied and processed from NA
        lines = f.read().splitlines()
    for line in lines:
        l = line.split()
        allNavStars[l[0]] = (float(l[1]), float(l[2]), float(NavStarMagnitudes.magnitudes[l[0]]))

    outputStars = []

    for starName in allNavStars.keys():
        sha = allNavStars[starName][0]
        lha = (lst + sha) % 360
        decl = allNavStars[starName][1]
        mag = allNavStars[starName][2]
        Alt, Zn = AstroCalcs.sightReduction(localLat, decl, lha)
        if lowerAlt < Alt < upperAlt and mag < minimumMagnitude:
            # if Zn > leftWindow or Zn < rightWindow:
            outputStars.append((starName, Zn, Alt, mag))
    byMagnitude = sorted(outputStars, key=operator.itemgetter(3))
    byAzimuth = sorted(outputStars, key=operator.itemgetter(1))

    print("\nBy Magnitude:")
    for item in byMagnitude:
        displayStar(item, HoFromSextant, MaxIntercept)

    print()
    print("\nBy Azimuth:")
    for item in byAzimuth:
        displayStar(item, HoFromSextant, MaxIntercept)

    print()
    print("Likely candidates:")
    for item in byAzimuth:
        if abs(item[2] - HoFromSextant) < abs(MaxIntercept):
            displayStar(item, HoFromSextant, MaxIntercept)
            if HoFromSextant > item[2]:
                direction = "Towards"
            else:
                direction = "Away"

            # outputTable.append([f"Intercept ({direction})", f"{deg_to_dm(item[2] - HoFromSextant)}"])
            print(f'  {"Azimuth":<20}{round(item[1]):5.0f} °')
            dir = f'Intercept({direction})'
            print(f'  {dir:<18} {abs((item[2] - HoFromSextant) * 60):6.2f} nm')
            print(f'  Intercept{abs((item[2] - HoFromSextant) * 60):16.2f} nm {direction}')
            print(f'  LoP{round((item[1]+90)%360):22.0f} °\n')
