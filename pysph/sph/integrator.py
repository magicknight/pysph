"""Basic code for the templated integrators.

Currently we only support two-step integrators.

These classes are used to generate the code for the actual integrators
from the `sph_eval` module.
"""

import inspect

# Local imports.
from pysph.sph.equation import get_array_names
from pysph.base.cython_generator import CythonGenerator

###############################################################################
# `IntegratorStep` class
###############################################################################
class IntegratorStep(object):
    """Subclass this and implement the methods ``predictor`` and ``corrector``.
    Use the same conventions as the equations.
    """
    def initialize(self):
        pass
    def predictor(self):
        pass
    def corrector(self):
        pass


###############################################################################
# `EulerStep` class
###############################################################################
class EulerStep(IntegratorStep):
    def initialize(self):
        pass
    def predictor(self):
        pass
    def corrector(self, d_idx, d_u, d_v, d_w, d_au, d_av, d_aw, d_x, d_y,
                  d_z, d_rho, d_arho, dt=0.0):
        d_u[d_idx] += dt*d_au[d_idx]
        d_v[d_idx] += dt*d_av[d_idx]
        d_w[d_idx] += dt*d_aw[d_idx]

        d_x[d_idx] += dt*d_u[d_idx]
        d_y[d_idx] += dt*d_v[d_idx]
        d_z[d_idx] += dt*d_w[d_idx]

        d_rho[d_idx] += dt*d_arho[d_idx]

###############################################################################
# `WCSPHStep` class
###############################################################################
class WCSPHStep(IntegratorStep):
    def initialize(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                   d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho):
        d_x0[d_idx] = d_x[d_idx]
        d_y0[d_idx] = d_y[d_idx]
        d_z0[d_idx] = d_z[d_idx]

        d_u0[d_idx] = d_u[d_idx]
        d_v0[d_idx] = d_v[d_idx]
        d_w0[d_idx] = d_w[d_idx]

        d_rho0[d_idx] = d_rho[d_idx]

    def predictor(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                   d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho, d_au, d_av,
                   d_aw, d_ax, d_ay, d_az, d_arho, dt=0.0):
        dtb2 = 0.5*dt
        d_u[d_idx] = d_u0[d_idx] + dtb2*d_au[d_idx]
        d_v[d_idx] = d_v0[d_idx] + dtb2*d_av[d_idx]
        d_w[d_idx] = d_w0[d_idx] + dtb2*d_aw[d_idx]

        d_x[d_idx] = d_x0[d_idx] + dtb2 * d_ax[d_idx]
        d_y[d_idx] = d_y0[d_idx] + dtb2 * d_ay[d_idx]
        d_z[d_idx] = d_z0[d_idx] + dtb2 * d_az[d_idx]

        # Update densities and smoothing lengths from the accelerations
        d_rho[d_idx] = d_rho0[d_idx] + dtb2 * d_arho[d_idx]

    def corrector(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                   d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho, d_au, d_av,
                   d_aw, d_ax, d_ay, d_az, d_arho, dt=0.0):

        d_u[d_idx] = d_u0[d_idx] + dt*d_au[d_idx]
        d_v[d_idx] = d_v0[d_idx] + dt*d_av[d_idx]
        d_w[d_idx] = d_w0[d_idx] + dt*d_aw[d_idx]

        d_x[d_idx] = d_x0[d_idx] + dt * d_ax[d_idx]
        d_y[d_idx] = d_y0[d_idx] + dt * d_ay[d_idx]
        d_z[d_idx] = d_z0[d_idx] + dt * d_az[d_idx]

        # Update densities and smoothing lengths from the accelerations
        d_rho[d_idx] = d_rho0[d_idx] + dt * d_arho[d_idx]

###############################################################################
# `SolidMechStep` class
###############################################################################
class SolidMechStep(IntegratorStep):
    def initialize(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                   d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho,
                   d_s00, d_s01, d_s02, d_s11, d_s12, d_s22,
                   d_s000, d_s010, d_s020, d_s110, d_s120, d_s220,
                   d_e0, d_e):
        d_x0[d_idx] = d_x[d_idx]
        d_y0[d_idx] = d_y[d_idx]
        d_z0[d_idx] = d_z[d_idx]

        d_u0[d_idx] = d_u[d_idx]
        d_v0[d_idx] = d_v[d_idx]
        d_w0[d_idx] = d_w[d_idx]

        d_rho0[d_idx] = d_rho[d_idx]
        d_e0[d_idx] = d_e[d_idx]

        d_s000[d_idx] = d_s00[d_idx]
        d_s010[d_idx] = d_s01[d_idx]
        d_s020[d_idx] = d_s02[d_idx]
        d_s110[d_idx] = d_s11[d_idx]
        d_s120[d_idx] = d_s12[d_idx]
        d_s220[d_idx] = d_s22[d_idx]

    def predictor(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                  d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho, d_au, d_av,
                  d_aw, d_ax, d_ay, d_az, d_arho, d_e, d_e0, d_ae,
                  d_s00, d_s01, d_s02, d_s11, d_s12, d_s22, 
                  d_s000, d_s010, d_s020, d_s110, d_s120, d_s220, 
                  d_as00, d_as01, d_as02, d_as11, d_as12, d_as22,
                  dt=0.0):
        dtb2 = 0.5*dt
        d_u[d_idx] = d_u0[d_idx] + dtb2*d_au[d_idx]
        d_v[d_idx] = d_v0[d_idx] + dtb2*d_av[d_idx]
        d_w[d_idx] = d_w0[d_idx] + dtb2*d_aw[d_idx]

        d_x[d_idx] = d_x0[d_idx] + dtb2 * d_ax[d_idx]
        d_y[d_idx] = d_y0[d_idx] + dtb2 * d_ay[d_idx]
        d_z[d_idx] = d_z0[d_idx] + dtb2 * d_az[d_idx]

        # Update densities and smoothing lengths from the accelerations
        d_rho[d_idx] = d_rho0[d_idx] + dtb2 * d_arho[d_idx]
        d_e[d_idx] = d_e0[d_idx] + dtb2 * d_ae[d_idx]

        # update deviatoric stress components
        d_s00[d_idx] = d_s000[d_idx] + dtb2 * d_as00[d_idx]
        d_s01[d_idx] = d_s010[d_idx] + dtb2 * d_as01[d_idx]
        d_s02[d_idx] = d_s020[d_idx] + dtb2 * d_as02[d_idx]
        d_s11[d_idx] = d_s110[d_idx] + dtb2 * d_as11[d_idx]
        d_s12[d_idx] = d_s120[d_idx] + dtb2 * d_as12[d_idx]
        d_s22[d_idx] = d_s220[d_idx] + dtb2 * d_as22[d_idx]

    def corrector(self, d_idx, d_x0, d_y0, d_z0, d_x, d_y, d_z,
                  d_u0, d_v0, d_w0, d_u, d_v, d_w, d_rho0, d_rho, d_au, d_av,
                  d_aw, d_ax, d_ay, d_az, d_arho, d_e, d_ae, d_e0,
                  d_s00, d_s01, d_s02, d_s11, d_s12, d_s22,
                  d_s000, d_s010, d_s020, d_s110, d_s120, d_s220, 
                  d_as00, d_as01, d_as02, d_as11, d_as12, d_as22,
                  dt=0.0):

        d_u[d_idx] = d_u0[d_idx] + dt*d_au[d_idx]
        d_v[d_idx] = d_v0[d_idx] + dt*d_av[d_idx]
        d_w[d_idx] = d_w0[d_idx] + dt*d_aw[d_idx]

        d_x[d_idx] = d_x0[d_idx] + dt * d_ax[d_idx]
        d_y[d_idx] = d_y0[d_idx] + dt * d_ay[d_idx]
        d_z[d_idx] = d_z0[d_idx] + dt * d_az[d_idx]

        # Update densities and smoothing lengths from the accelerations
        d_rho[d_idx] = d_rho0[d_idx] + dt * d_arho[d_idx]
        d_e[d_idx] = d_e0[d_idx] + dt * d_ae[d_idx]

        # update deviatoric stress components
        d_s00[d_idx] = d_s000[d_idx] + dt * d_as00[d_idx]
        d_s01[d_idx] = d_s010[d_idx] + dt * d_as01[d_idx]
        d_s02[d_idx] = d_s020[d_idx] + dt * d_as02[d_idx]
        d_s11[d_idx] = d_s110[d_idx] + dt * d_as11[d_idx]
        d_s12[d_idx] = d_s120[d_idx] + dt * d_as12[d_idx]
        d_s22[d_idx] = d_s220[d_idx] + dt * d_as22[d_idx]

###############################################################################
# `TransportVelocityStep` class
###############################################################################
class TransportVelocityStep(IntegratorStep):
    def initialize(self):
        pass

    def predictor(self, d_idx, d_u, d_v, d_au, d_av, d_uhat, d_auhat, d_vhat,
                  d_avhat, d_x, d_y, dt=0.0):
        dtb2 = 0.5*dt
        d_u[d_idx] += dtb2*d_au[d_idx]
        d_v[d_idx] += dtb2*d_av[d_idx]
        d_uhat[d_idx] = d_u[d_idx] + dtb2*d_auhat[d_idx]
        d_vhat[d_idx] = d_v[d_idx] + dtb2*d_avhat[d_idx]

        d_x[d_idx] += dt*d_uhat[d_idx]
        d_y[d_idx] += dt*d_vhat[d_idx]

    def corrector(self, d_idx, d_u, d_v, d_au, d_av, d_vmag, dt=0.0):
        dtb2 = 0.5*dt
        # Update velocities avoiding impulsive starts
        d_u[d_idx] += dtb2*d_au[d_idx]
        d_v[d_idx] += dtb2*d_av[d_idx]

        # magnitude of velocity squared
        d_vmag[d_idx] = d_u[d_idx]*d_u[d_idx] + d_v[d_idx]*d_v[d_idx]


###############################################################################
# `AdamiVerletStep` class
###############################################################################
class AdamiVerletStep(IntegratorStep):
    def initialize(self):
        pass

    def predictor(self, d_idx, d_u, d_v, d_au, d_av, d_x, d_y, dt=0.0):
        dtb2 = 0.5*dt
        d_u[d_idx] += dtb2*d_au[d_idx]
        d_v[d_idx] += dtb2*d_av[d_idx]

        d_x[d_idx] += dtb2*d_u[d_idx]
        d_y[d_idx] += dtb2*d_v[d_idx]


    def corrector(self, d_idx, d_u, d_v, d_au, d_av, d_x, d_y, d_rho, d_arho,
                  d_vmag, dt=0.0):
        dtb2 = 0.5*dt
        d_u[d_idx] += dtb2*d_au[d_idx]
        d_v[d_idx] += dtb2*d_av[d_idx]

        # udpate positions
        d_x[d_idx] += dtb2*d_u[d_idx]
        d_y[d_idx] += dtb2*d_v[d_idx]

        # update densities
        d_rho[d_idx] += dt * d_arho[d_idx]

        # magnitude of velocity squared
        d_vmag[d_idx] = d_u[d_idx]*d_u[d_idx] + d_v[d_idx]*d_v[d_idx]


###############################################################################
# `Integrator` class
###############################################################################
class Integrator(object):

    def __init__(self, **kw):
        """Pass fluid names and suitable `IntegratorStep` instances.

        For example::

            >>> integrator = Integrator(fluid=WCSPHStep(), solid=WCSPHStep())

        where "fluid" and "solid" are the names of the particle arrays.
        """
        self.cfl = 0.5
        self.steppers = kw
        self.parallel_manager = None
        # This is set later when the underlying compiled integrator is created
        # by the SPHEval.
        self.integrator = None

    def compute_time_step(self, dt):
        calc = self.integrator.sph_calc
        cfl = self.cfl
        dt_cfl = calc.dt_cfl
        hmin = 1.0

        # if the dt_cfl is not defined, return default dt
        if dt_cfl <= 0.0:
            return dt

        # iterate over particles and find the stable time step
        for pa in calc.particle_arrays:
            h = pa.get_carray('h')
            h.update_min_max()

            if h.minimum < hmin:
                hmin = h.minimum

        # return the courant limited time step
        return cfl * hmin/dt_cfl

    def get_stepper_code(self):
        classes = {}
        for dest, stepper in self.steppers.iteritems():
            cls = stepper.__class__.__name__
            classes[cls] = stepper

        wrappers = []
        code_gen = CythonGenerator()
        for cls in sorted(classes.keys()):
            code_gen.parse(classes[cls])
            wrappers.append(code_gen.get_code())
        return '\n'.join(wrappers)

    def get_stepper_defs(self):
        lines = []
        for dest, stepper in self.steppers.iteritems():
            cls_name = stepper.__class__.__name__
            code = 'cdef public {cls} {name}'.format(cls=cls_name,
                                                     name=dest+'_stepper')
            lines.append(code)
        return '\n'.join(lines)

    def get_stepper_init(self):
        lines = []
        for dest, stepper in self.steppers.iteritems():
            cls_name = stepper.__class__.__name__
            code = 'self.{name} = {cls}(steppers["{dest}"])'\
                        .format(name=dest+'_stepper', cls=cls_name,
                                dest=dest)
            lines.append(code)
        return '\n'.join(lines)

    def get_args(self, dest, method):
        stepper = self.steppers[dest]
        meth = getattr(stepper, method)
        return inspect.getargspec(meth).args

    def get_array_declarations(self, method):
        arrays = set()
        for dest in self.steppers:
            s, d = get_array_names(self.get_args(dest, method))
            arrays.update(s | d)

        decl = []
        for arr in sorted(arrays):
            decl.append('cdef double* %s'%arr)
        return '\n'.join(decl)

    def get_array_setup(self, dest, method):
        s, d = get_array_names(self.get_args(dest, method))
        lines = ['%s = dst.%s.data'%(n, n[2:]) for n in s|d]
        return '\n'.join(lines)

    def get_stepper_loop(self, dest, method):
        args = self.get_args(dest, method)
        if 'self' in args:
            args.remove('self')
        call_args = ', '.join(args)
        c = 'self.{obj}.{method}({args})'\
                .format(obj=dest+'_stepper', method=method, args=call_args)
        return c

    def integrate(self, time, dt, count):
        self.integrator.integrate(time, dt, count)

    def set_parallel_manager(self, pm):
        self.integrator.set_parallel_manager(pm)

    def set_integrator(self, integrator):
        self.integrator = integrator
