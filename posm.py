import numpy as np

a1 = 0.89453233003
a2 = 0.00041560737424
a3 = -4.6262121398E-06
a4 = 2.2211195897E-11
a5 = -0.00011445456438
a6 = -1.4783462366E-06
a7 = -1.3526263499E-11
a8 = 7.0132355546E-06
a9 = 5.6960486681E-08
a10 = -2.8624032584E-10
b1 = 9.9992293295E+2
b2 = 2.0341179217E-2
b3 = -6.1624591598E-3
b4 = 2.2614664708E-5
b5 = -4.6570659168E-8
MW_s = 31.4038218
T0 = 273.16
R = 8.3145


def osmotic_pressure_TX(S, T=25.0, **kwargs):
    '''
        T: Temperature (Celsius)
        S: Salinity (mg/kg)

        Returns: Osmotic Pressure (bar)

        Description:
        http://web.mit.edu/seawater/

        Further reading: 
            - Pani Digital/Project Scoping folder
            - Tom Fyles

        Sample Test Points:
        osmoticPressure(S=35000,T=25) = 25.884339919556318
        osmoticPressure(S=1500,T=15) = 1.072884547907449

    '''

    try:
        iter(S)
        S = np.asarray(S, dtype=np.float64)
    except TypeError:
        S = np.asarray([S], dtype=np.float64)
    try:
        iter(T)
        T = np.asarray(T, dtype=np.float64)
    except TypeError:
        T = np.asarray([T], dtype=np.float64)

    S = S/1000  # g/kg to mg/kg

    rho = b1 + b2 * T + b3 * T ** 2 + b4 * T ** 3 + b5 * T ** 4
    # 'Define molality as a function of salinity
    m_sum = S / (1000 - S) * (1000 / MW_s)

    # vectorize
    S_eq = 10  # 'Correlation matches function at S_equivalent = 10
    Phi_corr_eq = a1 + a2*T + a3*T**2 + a4*T ** 4 + a5 * S_eq + a6 * T * S_eq + a7 * \
        S_eq * T ** 3 + a8 * S_eq ** 2 + a9 * S_eq ** 2 * T + a10 * S_eq ** 2 * T ** 2
    dPhi_corr_eq = a5 + a6 * T + a7 * T ** 3 + 2 * a8 * \
        S_eq + 2 * a9 * S_eq * T + 2 * a10 * S_eq * T ** 2
    m_sum_eq = S_eq / (1000 - S_eq) * (1000 / MW_s)
    dmds_eq = (1000 / MW_s) * (1 / (1000 - S_eq) + S_eq / (1000 - S_eq) ** 2)
    # 'Pitzer-Bronsted equation:
    # = 1 - (beta) * m_sum ** (0.5) + lambda * m_sum
    # 'The 2 constants are determined by equating the F and dF/dS of Bromley's correlation with Pitzer's equation"
    beta = -2 * (m_sum_eq ** (-0.5) * (Phi_corr_eq - 1) -
                 dPhi_corr_eq * m_sum_eq ** (0.5) / dmds_eq)
    lamb = (Phi_corr_eq + beta * m_sum_eq ** (0.5) - 1) / m_sum_eq

    Phi = np.zeros(np.size(S))
    Phi[(S >= 0) & (S < 10)] = (1 - (beta) * m_sum **
                                (0.5) + lamb * m_sum)[(S >= 0) & (S < 10)]
    Phi[S >= 10] = (a1 + a2 * T + a3 * T ** 2 + a4 * T ** 4 + a5 * S + a6 * T *
                    S + a7 * S * T ** 3 + a8 * S ** 2 + a9 * S ** 2 * T + a10 * S ** 2 * T ** 2)[S >= 10]
    Phi[S < 0] = 0
    Phi[np.isnan(S)] = 0

    posm = (rho * R * (T0 + T) * Phi * m_sum) / 100000

    if np.size(posm) <= 1:
        posm = float(posm)

    return posm

