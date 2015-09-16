from __future__ import division
import numpy as np
import matplotlib.pyplot as plt

from pyhsmm.basic.distributions import Regression, Gaussian, PoissonDuration
from autoregressive.distributions import AutoRegression
from pyhsmm.util.text import progprint_xrange

from pyslds.models import WeakLimitStickyHDPHMMSLDS

np.random.seed(0)


###################
#  generate data  #
###################

import autoregressive

As = [np.array([[np.cos(theta), -np.sin(theta)],
                [np.sin(theta), np.cos(theta)]])
      for alpha, theta in ((1.1,0.1), (1.0,-0.1), (1., 0.))]

truemodel = autoregressive.models.ARHSMM(
    alpha=4.,init_state_concentration=4.,
    obs_distns=[AutoRegression(A=A,sigma=0.05*np.eye(2)) for A in As],
    dur_distns=[PoissonDuration(alpha_0=5*50,beta_0=5) for _ in As])

data, labels = truemodel.generate(500)
data = data[truemodel.nlags:]

plt.figure()
plt.plot(data[:,0],data[:,1],'bx-')


#################
#  build model  #
#################

Nmax = 5           # number of latnt discrete states
P = 2              # latent linear dynamics' dimension
D = data.shape[1]  # data dimension

dynamics_distns = [
    AutoRegression(
        A=np.eye(P),sigma=np.eye(P),
        nu_0=2*P,S_0=2*P*np.eye(P),M_0=np.zeros((P,P)),K_0=np.eye(P))
    for _ in xrange(Nmax)]

emission_distns = [
    Regression(
        A=np.eye(D),sigma=0.1*np.eye(D), # TODO remove special case
        nu_0=5,S_0=np.eye(D),M_0=np.zeros((D,P)),K_0=np.eye(P))
    for _ in xrange(Nmax)]

init_dynamics_distns = [
    Gaussian(nu_0=5,sigma_0=np.eye(P),mu_0=np.zeros(P),kappa_0=1.)
    for _ in xrange(Nmax)]

model = WeakLimitStickyHDPHMMSLDS(
    dynamics_distns=dynamics_distns,
    emission_distns=emission_distns,
    init_dynamics_distns=init_dynamics_distns,
    kappa=50.,alpha=5.,gamma=5.,init_state_concentration=1.)


##################
#  run sampling  #
##################

def resample():
    model.resample_model()
    return model.stateseqs[0].copy()


model.add_data(data)
samples = [resample() for _ in progprint_xrange(1000)]

plt.matshow(np.vstack(samples+[np.tile(labels,(10,1))]))

plt.show()
