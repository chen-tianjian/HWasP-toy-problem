import gym

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' # only show warning and errors in TF
import tensorflow as tf
import numpy as np

from garage.envs import normalize
from garage.experiment import run_experiment
from garage.np.algos import CMAES
from garage.tf.baselines import GaussianMLPBaseline
from garage.np.baselines import LinearFeatureBaseline

from garage.tf.envs import TfEnv
from garage.tf.experiment import LocalTFRunner
from garage.tf.models.mlp_model import MLPModel

from mass_spring_envs.envs.mass_spring_env_opt_k import MassSpringEnv_OptK_HwAsPolicy
from policies.opt_k.models import MechPolicyModel_OptK_HwAsPolicy
from policies.opt_k.policies import CompMechPolicy_OptK_HwAsPolicy

from shared_params import params_opt_k as params

from launchers.utils.zip_project import zip_project

from datetime import datetime
import sys
import argparse


def run_task(snapshot_config, *_):
    """Run task."""
    with LocalTFRunner(snapshot_config=snapshot_config) as runner:

        zip_project(log_dir=runner._snapshotter._snapshot_dir)

        env = TfEnv(MassSpringEnv_OptK_HwAsPolicy(params))

        comp_policy_model = MLPModel(output_dim=1, 
            hidden_sizes=params.comp_policy_network_size, 
            hidden_nonlinearity=tf.nn.tanh,
            output_nonlinearity=tf.nn.tanh)

        mech_policy_model = MechPolicyModel_OptK_HwAsPolicy(params)

        policy = CompMechPolicy_OptK_HwAsPolicy(name='comp_mech_policy', 
                env_spec=env.spec, 
                comp_policy_model=comp_policy_model, 
                mech_policy_model=mech_policy_model)

        # baseline = GaussianMLPBaseline(
        #     env_spec=env.spec,
        #     regressor_args=dict(
        #         hidden_sizes=params.baseline_network_size,
        #         hidden_nonlinearity=tf.nn.tanh,
        #         use_trust_region=True,
        #     ),
        # )
        baseline = LinearFeatureBaseline(env_spec=env.spec)

        algo = CMAES(env_spec=env.spec, policy=policy, baseline=baseline, **params.cmaes_algo_kwargs)

        runner.setup(algo, env)

        runner.train(**params.cmaes_train_kwargs)

    
if __name__=='__main__':
    now = datetime.now()
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', default=int(now.timestamp()), type=int, help='seed')
    parser.add_argument('--exp_id', default=now.strftime("%Y_%m_%d_%H_%M_%S"), help='experiment id (suffix to data directory name)')

    args = parser.parse_args()

    run_experiment(run_task, exp_prefix='cmaes_opt_k_hw_as_policy_{}_'.format(args.exp_id) + str(params.n_springs)+'_params', snapshot_mode='last', seed=args.seed, force_cpu=True)