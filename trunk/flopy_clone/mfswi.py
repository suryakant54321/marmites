from numpy import ones, zeros, empty
from mbase import package

class mfswi(package):
    'Salt Water Intrusion (SWI) package class'
    def __init__(self, model, npln=1, istrat=1, iswizt=53, nprn=1, toeslope=0.05, tipslope=0.05, \
                 zetamin=0.005, delzeta=0.05, nu=0.025, zeta=[], ssz=[], isource=0, extension='swi', fname_output='swi.zta'):
        package.__init__(self, model) # Call ancestor's init to set self.parent
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        self.unit_number = [29,53]
        self.extension = extension
        self.file_name = [ self.parent.name + '.' + self.extension, fname_output ]
        self.name = [ 'SWI', 'DATA(BINARY)' ]
        self.heading = '# Salt Water Intrusion package file for MODFLOW-2000, generated by Flopy.'
        self.npln = npln
        self.istrat = istrat
        self.iswizt = iswizt
        self.nprn = nprn
        self.toeslope = toeslope
        self.tipslope = tipslope
        self.zetamin = zetamin
        self.delzeta = delzeta
        # Create arrays so that they have the correct size
        if self.istrat == 1:
            self.nu = empty( self.npln+1 )
        else:
            self.nu = empty( self.npln+2 )
        self.zeta = []
        for i in range(nlay):
            self.zeta.append( empty((nrow, ncol, self.npln)) )
        self.ssz = empty((nrow, ncol, nlay))
        self.isource = empty((nrow, ncol, nlay),dtype='int32')
        # Set values of arrays
        self.assignarray( self.nu, nu )
        for i in range(nlay):
            self.assignarray( self.zeta[i], zeta[i] )
        self.assignarray( self.ssz, ssz )
        self.assignarray( self.isource, isource )
        self.parent.add_package(self)
    def __repr__( self ):
        return 'Salt Water Intrusion package class'
    def write_file(self):
        nrow, ncol, nlay, nper = self.parent.nrow_ncol_nlay_nper
        # Open file for writing
        f_swi = open(self.fn_path, 'w')
        # First line: heading
        #f_swi.write('%s\n' % self.heading)  # Writing heading not allowed in SWI???
        f_swi.write( '%10d%10d%10d%10d\n' % (self.npln, self.istrat, self.iswizt, self.nprn) )
        f_swi.write( '%10f%10f%10f%10f\n' % (self.toeslope, self.tipslope, self.zetamin, self.delzeta) )
        self.parent.write_array( f_swi, self.nu, self.unit_number[0], True, 13, 20 )
        for isur in range(self.npln):
            for ilay in range(nlay):
                self.parent.write_array( f_swi, self.zeta[ilay][:,:,isur], self.unit_number[0], True, 13, ncol )
        for ilay in range(nlay):
                self.parent.write_array( f_swi, self.ssz[:,:,ilay], self.unit_number[0], True, 13, ncol )
        for ilay in range(nlay):
                self.parent.write_array( f_swi, self.isource[:,:,ilay], self.unit_number[0], True, 13, ncol )

        # Close file
        f_swi.close()

