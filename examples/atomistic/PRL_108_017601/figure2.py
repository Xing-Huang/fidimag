import numpy as np
from fidimag.atomistic import Sim, DMI, UniformExchange, Zeeman, TimeZeeman
from fidimag.common import CuboidMesh, DataReader
import matplotlib as mpl
mpl.use("Agg")
import matplotlib.pyplot as plt


def sinc_fun(t):

    w0 = 0.01

    return np.sinc(w0 * t)


def excite_system(mesh):

    sim = Sim(mesh, name='dyn')

    # sim.set_options(rtol=1e-10,atol=1e-14)
    sim.driver.alpha = 0.04
    sim.driver.gamma = 1.0
    sim.mu_s = 1.0

    sim.set_m(np.load('m0.npy'))

    J = 1.0
    exch = UniformExchange(J)
    sim.add(exch)

    D = 0.09
    dmi = DMI(D)
    sim.add(dmi)

    zeeman = Zeeman([0, 0, 3.75e-3], name='H')
    sim.add(zeeman)

    w0 = 0.02

    def time_fun(t):
        return np.exp(-w0 * t)

    hx = TimeZeeman([0, 0, 1e-5], sinc_fun, name='h')
    sim.add(hx, save_field=True)

    ts = np.linspace(0, 20000, 5001)
    for t in ts:
        sim.run_until(t)
        print 'sim t=%g' % t


def deal_plot():
    data = DataReader('dyn.txt')
    ts = data['time']
    N = len(ts)
    dt = ts[1] - ts[0]
    print 'dt=', dt

    freq = np.fft.fftshift(np.fft.fftfreq(N, dt))

    H = data['h_z']
    M = data['m_z']

    fH = np.fft.fftshift(np.fft.fft(H))
    fM = np.fft.fftshift(np.fft.fft(M))

    a = fH.real
    b = fH.imag
    c = fM.real
    d = fM.imag

    rx = (a * c + b * d) / (a * a + b * b)
    ix = (b * c - a * d) / (a * a + b * b)

    plt.plot(freq * 2 * np.pi, ix, '.-')
    # plt.legend()
    plt.xlim([0, 0.012])
    #plt.ylim([-5, 100])
    plt.xlabel(r'$w$')
    plt.ylabel('Susceptibility')
    plt.savefig('res.pdf')


if __name__ == '__main__':

    #mesh = CuboidMesh(nx=288,ny=288,nz=1)
    mesh = CuboidMesh(nx=166, ny=96 * 2, nz=1, periodicity=(True, True, False))

    excite_system(mesh)

    deal_plot()
