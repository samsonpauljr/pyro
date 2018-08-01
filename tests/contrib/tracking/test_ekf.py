from __future__ import absolute_import, division, print_function

import torch

from pyro.contrib.tracking.extended_kalman_filter import EKFState
from pyro.contrib.tracking.dynamic_models import NcpContinuous, NcvContinuous
from pyro.contrib.tracking.measurements import PositionMeasurement
from tests.common import assert_equal


def test_EKFState_with_NcpContinuous():
    d = 3
    ncp = NcpContinuous(dimension=d, sv2=2.0)
    x = torch.rand(d)
    P = torch.eye(d)
    t = 0.0
    dt = 2.0
    ekf_state = EKFState(dynamic_model=ncp, mean=x, cov=P, time=t)

    assert ekf_state.dynamic_model.__class__ == NcpContinuous
    assert ekf_state.dimension == d
    assert ekf_state.dimension_pv == 2*d

    assert_equal(x, ekf_state.mean, prec=1e-5)
    assert_equal(P, ekf_state.cov, prec=1e-5)
    assert_equal(x, ekf_state.mean_pv[:d], prec=1e-5)
    assert_equal(P, ekf_state.cov_pv[:d, :d], prec=1e-5)
    assert_equal(t, ekf_state.time, prec=1e-5)

    ekf_state.init(2*x, 2*P, t + 2.0)
    assert_equal(2*x, ekf_state.mean, prec=1e-5)
    assert_equal(2*P, ekf_state.cov, prec=1e-5)
    assert_equal(t + 2.0, ekf_state.time, prec=1e-5)

    ekf_state.init(2*x, 2*P, t)
    ekf_state1 = ekf_state.copy()
    ekf_state1.predict(dt)
    assert ekf_state1.dynamic_model.__class__ == NcpContinuous

    measurement = PositionMeasurement(
        mean=torch.rand(d),
        cov=torch.eye(d),
        time=t + dt)
    l = ekf_state1.likelihood_of_update(measurement)
    assert (l < 1.).all()
#     old_mean = ekf_state1.mean.clone()
    dz, S = ekf_state1.update(measurement)
    assert dz.shape == (measurement.dimension,)
    assert S.shape == (measurement.dimension, measurement.dimension)
#     assert not assert_equal(ekf_state1.mean, old_mean, prec=1e-5)

    ekf_state2 = ekf_state1.copy()
    assert ekf_state2.dynamic_model.__class__ == NcpContinuous


def test_EKFState_with_NcvContinuous():
    d = 6
    ncv = NcvContinuous(dimension=d, sa2=2.0)
    x = torch.rand(d)
    P = torch.eye(d)
    t = 0.0
    dt = 2.0
    ekf_state = EKFState(
        dynamic_model=ncv, mean=x, cov=P, time=t)

    assert ekf_state.dynamic_model.__class__ == NcvContinuous
    assert ekf_state.dimension == d
    assert ekf_state.dimension_pv == d

    assert_equal(x, ekf_state.mean, prec=1e-5)
    assert_equal(P, ekf_state.cov, prec=1e-5)
    assert_equal(x, ekf_state.mean_pv, prec=1e-5)
    assert_equal(P, ekf_state.cov_pv, prec=1e-5)
    assert_equal(t, ekf_state.time, prec=1e-5)

    ekf_state.init(2*x, 2*P, t + 2.0)
    assert_equal(2*x, ekf_state.mean, prec=1e-5)
    assert_equal(2*P, ekf_state.cov, prec=1e-5)
    assert_equal(t + 2.0, ekf_state.time, prec=1e-5)

    ekf_state.init(2*x, 2*P, t)
    ekf_state1 = ekf_state.copy()
    ekf_state1.predict(dt)
    assert ekf_state1.dynamic_model.__class__ == NcvContinuous

    measurement = PositionMeasurement(
        mean=torch.rand(d),
        cov=torch.eye(d),
        time=t + dt)
    l = ekf_state1.likelihood_of_update(measurement)
    assert (l < 1.).all()
#     old_mean = ekf_state1.mean.clone()
    dz, S = ekf_state1.update(measurement)
    assert dz.shape == (measurement.dimension,)
    assert S.shape == (measurement.dimension, measurement.dimension)
#     assert not assert_equal(ekf_state1.mean, old_mean)

    ekf_state2 = ekf_state1.copy()
    assert ekf_state2.dynamic_model.__class__ == NcvContinuous
