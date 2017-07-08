
# -*- coding: utf-8 -*-

# Test module attributes.

__all__ = ('Tests',)
__version__ = '17.06.25'

from base import TestsBase

from pygeodesy import R_NM, F_DM, F_DMS, F_RAD, \
                      degrees, isclockwise, isconvex, \
                      m2NM  # PYCHOK expected


class Tests(TestsBase):

    def testLatLon(self, module, Sph=False):  # MCCABE expected

        self.subtitle(module, 'LatLon')

        LatLon = module.LatLon

        # basic LatLon class tests
        p = LatLon(52.20472, 0.14056)
        self.test('isEllipsoidal', p.isEllipsoidal, not Sph)
        self.test('isSpherical', p.isSpherical, Sph)

        self.test('lat/lonDMS', p, '52.20472°N, 000.14056°E')  # 52.20472°N, 000.14056°E
        self.test('lat/lonDMS F_DM', p.toStr(F_DM, 3),  '''52°12.283'N, 000°08.434'E''')
        self.test('lat/lonDMS F_DM', p.toStr(F_DM, 4),  '''52°12.2832'N, 000°08.4336'E''')
        self.test('lat/lonDMS F_DMS', p.toStr(F_DMS, 0), '''52°12'17"N, 000°08'26"E''')
        self.test('lat/lonDMS F_DMS', p.toStr(F_DMS, 1), '''52°12'17.0"N, 000°08'26.0"E''')
        self.test('lat/lonDMS F_RAD', p.toStr(F_RAD, 6), '0.911144N, 0.002453E')
        q = LatLon(*map(degrees, p.to2ab()))
        self.test('equals', q.equals(p), True)

        # <http://www.edwilliams.org/avform.htm#XTE>
        LAX = LatLon(33.+57./60, -(118.+24./60))
        JFK = LatLon(degrees(0.709186), -degrees(1.287762))
        Rav = m2NM(6366710)  # av earth radius in NM

        p = LatLon(52.205, 0.119)
        q = LatLon(48.857, 2.351)
        self.test('equals', p.equals(q), False)

        if hasattr(LatLon, 'initialBearingTo'):
            b = p.initialBearingTo(q)
            self.test('initialBearingTo', b, 156.1666 if Sph else 156.1106, fmt='%.4f')  # 156.2
            b = p.finalBearingTo(q)
            self.test('finalBearingTo', b, 157.8904 if Sph else 157.8345, fmt='%.4f')
            b = LAX.initialBearingTo(JFK)
            self.test('initialBearingTo', b, 65.8921 if Sph else 65.9335, fmt='%.4f')  # PYCHOK false?  66

        c = p.copy()
        self.test('copy', p.equals(c), 'True')

        if hasattr(LatLon, 'distanceTo'):
            d = p.distanceTo(q)
            self.test('distanceTo', d, '404279.720589' if Sph else '404607.805988', fmt='%.6f')  # 404300
            d = q.distanceTo(p)
            self.test('distanceTo', d, '404279.720589' if Sph else '404607.805988', fmt='%.6f')  # 404300
            d = LAX.distanceTo(JFK, radius=R_NM) if Sph else LAX.distanceTo(JFK)
            self.test('distanceTo', d, 2145 if Sph else 3981601, fmt='%.0f')  # PYCHOK false?

        if hasattr(LatLon, 'intermediateTo'):
            i = p.intermediateTo(q, 0.25)
            self.test('intermediateTo', i, '51.372084°N, 000.707337°E' if Sph
                                      else '51.372294°N, 000.707192°E')
            self.test('intermediateTo', isinstance(i, LatLon), True)

            if hasattr(p, 'distanceTo'):
                d = p.distanceTo(q)
                self.test('intermediateTo', d, '404279.721', fmt='%.3f')  # PYCHOK false?

            i = p.intermediateTo(q, 5)
            self.test('intermediateTo+5', i, '35.160975°N, 008.989542°E' if Sph
                                        else '35.560239°N, 008.833512°E')
            if hasattr(p, 'distanceTo'):
                self.test('intermediateTo+5', p.distanceTo(i) / d, '5.000', fmt='%.3f')  # PYCHOK false?

            i = p.intermediateTo(q, -4)
            self.test('intermediateTo-4', i, '64.911647°N, 013.726301°W' if Sph
                                        else '64.570387°N, 013.156352°W')
            if hasattr(p, 'distanceTo'):
                self.test('intermediateTo-4', p.distanceTo(i) / d, '4.000', fmt='%.3f')  # PYCHOK false?

        if hasattr(LatLon, 'intermediateChordTo'):
            i = p.intermediateChordTo(q, 0.25)
            self.test('intermediateChordTo', i, '51.372294°N, 000.707192°E')
            self.test('intermediateChordTo', isinstance(i, LatLon), True)  # PYCHOK false?

        if hasattr(LatLon, 'midpointTo'):
            m = p.midpointTo(q)
            self.test('midpointTo', m, '50.536327°N, 001.274614°E')  # PYCHOK false?  # 50.5363°N, 001.2746°E

        if hasattr(LatLon, 'destination'):
            p = LatLon(51.4778, -0.0015)
            d = p.destination(7794, 300.7)
            self.test('destination', d, '51.513546°N, 000.098345°W' if Sph
                                   else '51.513526°N, 000.098038°W')  # 51.5135°N, 0.0983°W ???
            self.test('destination', d.toStr(F_DMS, 0), '51°30′49″N, 000°05′54″W' if Sph
                                                   else '51°30′49″N, 000°05′53″W')
            d = LAX.destination(100, 66, radius=R_NM) if Sph else LAX.destination(100, 66)
            self.test('destination', d.toStr(F_DM, prec=0), "34°37′N, 116°33′W" if Sph
                                                       else "33°57′N, 118°24′W")
            self.test('destination', d, '34.613647°N, 116.55116°W' if Sph
                                   else '33.950367°N, 118.399012°W')  # PYCHOK false?

        if hasattr(LatLon, 'alongTrackDistanceTo'):
            s = LatLon(53.3206, -1.7297)
            e = LatLon(53.1887, 0.1334)
            p = LatLon(53.2611, -0.7972)
            try:
                d = p.alongTrackDistanceTo(s, 96)
                self.test('alongTrackDistanceTo', d, 62331.59, fmt='%.2f')  # 62331
            except TypeError as x:
                self.test('alongTrackDistanceTo', x, 'type(end) mismatch: int vs sphericalTrigonometry.LatLon')  # PYCHOK false?
            d = p.alongTrackDistanceTo(s, e)
            self.test('alongTrackDistanceTo', d, 62331.58, fmt='%.2f')  # PYCHOK false?

            # <http://www.edwilliams.org/avform.htm#XTE>
            p = LatLon(34.5, -116.5)  # 34:30N, 116:30W
            d = p.alongTrackDistanceTo(LAX, JFK, radius=Rav)
            self.test('alongTrackDistanceTo', d, 99.588, fmt='%.3f')  # NM

            # courtesy of Rimvydas Naktinis
            p = LatLon(53.36366, -1.83883)
            d = p.alongTrackDistanceTo(s, e)
            self.test('alongTrackDistanceTo', d, -7702.7, fmt='%.1f')

            p = LatLon(53.35423, -1.60881)
            d = p.alongTrackDistanceTo(s, e)
            self.test('alongTrackDistanceTo', d, 7587.6, fmt='%.1f')  # PYCHOK false?

        if hasattr(LatLon, 'crossTrackDistanceTo'):
            s = LatLon(53.3206, -1.7297)
            e = LatLon(53.1887, 0.1334)
            p = LatLon(53.2611, -0.7972)
            try:
                d = p.crossTrackDistanceTo(s, 96)
                self.test('crossTrackDistanceTo', d, -305.67, fmt='%.2f')  # -305.7
            except TypeError as x:
                self.test('crossTrackDistanceTo', x, 'type(end) mismatch: int vs sphericalTrigonometry.LatLon')  # PYCHOK false?
            d = p.crossTrackDistanceTo(s, e)
            self.test('crossTrackDistanceTo', d, -307.55, fmt='%.2f')  # PYCHOK false?  # -307.5

            # <http://www.edwilliams.org/avform.htm#XTE>
            p = LatLon(34.5, -116.5)  # 34:30N, 116:30W
            d = p.crossTrackDistanceTo(LAX, JFK, radius=Rav)
            self.test('crossTrackDistanceTo', d, 7.4524, fmt='%.4f')  # PYCHOK false? # XXX 7.4512 NM

        if hasattr(LatLon, 'greatCircle'):
            p = LatLon(53.3206, -1.7297)
            gc = p.greatCircle(96.0)
            self.test('greatCircle', gc, '(-0.79408, 0.12856, 0.59406)')  # PYCHOK false?

        if hasattr(LatLon, 'greatCircleTo'):
            p = LatLon(53.3206, -1.7297)
            q = LatLon(53.1887, 0.1334)
            gc = p.greatCircleTo(q)
            self.test('greatCircleTo', gc, '(-0.79408, 0.12859, 0.59406)')  # PYCHOK false?

        if isclockwise:
            f = LatLon(45,1), LatLon(45,2), LatLon(46,2), LatLon(46,1)
            self.test('isclockwise', isclockwise(f), False)
            t = LatLon(45,1), LatLon(46,1), LatLon(46,2), LatLon(45,1)
            self.test('isclockwise', isclockwise(t), True)
            try:
                self.test('isclockwise', isclockwise(t[:2]), ValueError)
            except ValueError as x:
                self.test('isclockwise', x, 'too few points: 2')  # PYCHOK false?

        if isconvex:
            f = LatLon(45,1), LatLon(46,2), LatLon(45,2), LatLon(46,1)
            self.test('isconvex', isconvex(f), False)
            t = LatLon(45,1), LatLon(46,1), LatLon(46,2), LatLon(45,1)
            self.test('isconvex', isconvex(t), True)
            try:
                self.test('isconvex', isconvex(t[:2]), ValueError)
            except ValueError as x:
                self.test('isconvex', x, 'too few points: 2')  # PYCHOK false?


if __name__ == '__main__':

    from pygeodesy import ellipsoidalNvector, ellipsoidalVincenty, \
                          sphericalNvector, sphericalTrigonometry

    t = Tests(__file__, __version__)

    t.testLatLon(ellipsoidalNvector, Sph=False)
    t.testLatLon(ellipsoidalVincenty, Sph=False)

    t.testLatLon(sphericalNvector, Sph=True)
    t.testLatLon(sphericalTrigonometry, Sph=True)

    t.results()
    t.exit()
