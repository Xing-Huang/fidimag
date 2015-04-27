import clib
from energy import Energy

class DMI(Energy):
    """
    Hamiltonian = D*[S_i x S_j]
        ==> H = D x S_j
    """
    def __init__(self,D, name='dmi', dmi_type='bulk'):
        self.D = D
        
        self.name = name
        self.dmi_type = dmi_type
        
        self.Dx = D
        self.Dy = D
        self.Dz = D
        self.jac = True
        
    def compute_field(self, t=0, spin=None):
        
        if spin is not None:
            m = spin
        else:
            m = self.spin
            
        if self.dmi_type == 'bulk':
            clib.compute_dmi_field(m,
                                self.field,
                                self.energy,
                                self.Dx,
                                self.Dy,
                                self.Dz,
                                self.nx,
                                self.ny,
                                self.nz,
                                self.xperiodic,
                                self.yperiodic)

        elif self.dmi_type == 'interfacial':
            clib.compute_dmi_field_interfacial(m,
                                                self.field,
                                                self.energy,
                                                self.D,
                                                self.nx,
                                                self.ny,
                                                self.nz,
                                                self.xperiodic,
                                                self.yperiodic)
        
        return self.field*self.mu_s_inv
    
    
    def compute_energy_direct(self):
        """
        mainly for testing
        """
        energy=clib.compute_dmi_energy(self.spin,
                                            self.D,
                                            self.nx,
                                            self.ny,
                                            self.nz,
                                            self.xperiodic,
                                            self.yperiodic)
        
        
        return energy