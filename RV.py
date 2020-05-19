import numpy as np
from posm import osmotic_pressure_TX
class ReverseNormalize():
    def __init__(self):
        #layout the factors that I want for the functions
        pass
    def set_reference(self,Q_p, Q_f, Temp, Conc_f, Conc_p, P_f, P_p, dp):      
        self.Temp = Temp
        self.Qp = Q_p
        self.Qf = Q_f
        self.Cf = Conc_f
        self.Cp = Conc_p
        self.Pf = P_f
        self.Pp = P_p
        self.dp = dp
        self.Tcf = self.TCF(Temp)
    
    def TCF(self, T):
        temps = []
        try:
            for t in T:
                if t<25:
                    temps.append(np.exp(3020*(1/(298)-1/(273+t))))
                else:
                    temps.append(np.exp(2640*(1/(298)-1/(273+t))))
        except:
            if T<25:
                temps = np.exp(3020*(1/298-1/(273+T)))
            else:
                temps = np.exp(2640*(1/298-1/(273+T)))
        return temps
    def TMP(self, Pf, Pp, dp, Cf, Cp, Temp):
        OB_f = osmotic_pressure_TX(Cf, Temp)
        OB_p = osmotic_pressure_TX(Cp, Temp)
        TMP = Pf-(dp/2+Pp+OB_f-OB_p)
        return TMP
    
    def SPnorm(self, Qp, TCF, Cf):
        return Qp/self.Qp/TCF/self.Tcf*Cf/self.Cf
    
    def DPnorm(self,Qf, Qp):
        return (2*self.Qf-self.Qp)/(2*Qf-Qp)
    
    def Concentrate(self,Cf, Pf, Cp, Qp, Qf):
        Cfc = -Cf*np.log(1-Qp/Qf)/(Qp/Qf)
        R = (Cf-Cp)/Cf
        return Cfc/Cf*Pf-(1-R)
    
    def SPB(self, SP, TCF, Qp):
        return SP/TCF*Qp
    
    def Flow(self,Qp, Qf, Temp, Cf, Cp, Pf, Pp, dp):
        TCF = self.TCF(Temp)
        TMP = self.TMP(Pf, Pp, dp, Cf, Cp, Temp)
        AS = Qp/TMP
        TCFref = self.Tcf
        TMPref = self.TMP(self.Pf, self.Pp, self.dp, self.Cf, self.Cp, self.Temp)
        ASref = self.Qp/TMPref
        Qrefpress = TMPref*AS
        QNM = TMP*ASref
        Qtemp = TMP*AS
        return Qrefpress, QNM, Qtemp
    
    def SP(self, Cf, Cp, Qf, Qp, T):
        SP = Cp/Cf*100
        self.Sp = self.Cp/self.Cf*100
        TCF =  self.TCF(T)
        TCFref = self.TCF(self.Temp)
        B = self.SPB(SP, TCF, Qp)
        Bref = self.SPB(self.Sp,TCFref,self.Qp)
        SPtemp = B*TCFref/Qp
        SPNM = Bref*(TCF/Qp)
        return SP, SPtemp, SPNM
    
    def DP(self,Qp, Qf, T):
        TCF = self.TCF(T)
        DPNM = self.dp/self.DPnorm(Qf, Qp)
        return DPNM