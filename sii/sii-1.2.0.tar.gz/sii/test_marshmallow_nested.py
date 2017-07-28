from expects import *
with description('1'):
    with before.all:
        self.a = 'a'

    with it('2'):
        expect(self.a).to(equal('a'))

    with context('3'):
        with before.all:
            self.a = 'b'

        with it('4'):
            expect(self.a).to(equal('b'))
    with it('5'):
        expect(self.a).to(equal('a'))