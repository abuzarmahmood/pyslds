from __future__ import division

import pyhsmm

from states import HMMSLDSStatesPython, HMMSLDSStatesEigen, HSMMSLDSStatesPython, \
    HSMMSLDSStatesEigen


class _SLDSMixin(object):
    def __init__(self,dynamics_distns,emission_distns,init_dynamics_distns,**kwargs):
        self.init_dynamics_distns = init_dynamics_distns
        self.dynamics_distns = dynamics_distns
        self.emission_distns = emission_distns
        super(_SLDSMixin,self).__init__(obs_distns=self.dynamics_distns,**kwargs)


class _SLDSGibbsMixin(_SLDSMixin):
    def resample_parameters(self):
        self.resample_init_dynamics_distns()
        self.resample_dynamics_distns()
        self.resample_emission_distns()
        super(_SLDSGibbsMixin,self).resample_parameters()

    def resample_init_dynamics_distns(self):
        for state, d in enumerate(self.init_dynamics_distns):
            d.resample(
                [s.gaussian_states[0] for s in self.states_list
                    if s.stateseq[0] == state])
        self._clear_caches()

    def resample_dynamics_distns(self):
        for state, d in enumerate(self.dynamics_distns):
            d.resample(
                [s.strided_gaussian_states[s.stateseq[:-1] == state]
                 for s in self.states_list])
        self._clear_caches()

    def resample_emission_distns(self):
        for state, d in enumerate(self.emission_distns):
            d.resample([
                (s.gaussian_states[s.stateseq == state],
                 s.data[s.stateseq == state])
                for s in self.states_list])
        self._clear_caches()

    def resample_obs_distns(self):
        pass


class HMMSLDSPython(_SLDSGibbsMixin, pyhsmm.models.HMMPython):
    _states_class = HMMSLDSStatesPython


class HMMSLDS(_SLDSGibbsMixin, pyhsmm.models.HMM):
    _states_class = HMMSLDSStatesEigen


class HSMMSLDSPython(_SLDSGibbsMixin, pyhsmm.models.HSMMPython):
    _states_class = HSMMSLDSStatesPython


class HSMMSLDS(_SLDSGibbsMixin, pyhsmm.models.HSMM):
    _states_class = HSMMSLDSStatesEigen


class WeakLimitHDPHMMSLDS(_SLDSGibbsMixin, pyhsmm.models.WeakLimitHDPHMM):
    _states_class = HMMSLDSStatesEigen


class WeakLimitStickyHDPHMMSLDS(
        _SLDSGibbsMixin,
        pyhsmm.models.WeakLimitStickyHDPHMM):
    _states_class = HMMSLDSStatesEigen


class WeakLimitHDPHSMMSLDS(_SLDSGibbsMixin, pyhsmm.models.WeakLimitHDPHSMM):
    _states_class = HSMMSLDSStatesEigen
