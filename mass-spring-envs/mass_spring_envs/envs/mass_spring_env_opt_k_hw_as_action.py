'''
illustration of the system:

        --------------
        ^      \
        |       \
        |       /  spring, stiffness k, masless, zero natural length 
        |      /
        |      \
        |       \
        |    +-----+
        |    |     |
        |    |     |  point mass m1, position y1
 dist h |    +--+--+
        |       |
        |       | bar, length l, massless
        |       |
        |    +--+--+
        |    |     |
        |    |     |  point mass m2, position y2
        |    +-----+
        |                               
        |               |               |
        |               |               |
        |               |               |
        v      Goal     v input f       v g
        --------------

'''

import gym
import numpy as np

from shared_params import params

half_force_range = params.half_force_range
k_lb = params.k_lb
k_ub = params.k_ub
pos_range = params.pos_range
half_vel_range = params.half_vel_range
m1 = params.m1
m2 = params.m2
h = params.h
l = params.l
g = params.g
dt = params.dt
n_steps_per_action = params.n_steps_per_action

reward_alpha = params.reward_alpha
reward_beta = params.reward_beta
reward_gamma = params.reward_gamma

class MassSpringEnv_OptK_HwAsAction(gym.Env):
    '''
    1D mass-spring toy problem.
    Case I: optimizing the spring stiffness k
    Action: f, k
    observation: y1, v1
    '''

    def __init__(self):
        self.action_space = gym.spaces.Box(low=np.array([-half_force_range, k_lb]), high=np.array([half_force_range, k_ub]), dtype=np.float32) # 1st: redifined action pi, 2nd: original action f
        self.observation_space = gym.spaces.Box(low=np.array([0, -half_vel_range]), high=np.array([pos_range, half_vel_range]), dtype=np.float32) # obs y1 and v1
        self.v1 = np.random.uniform(-half_vel_range, half_vel_range) # vel of both masses
        self.y1 = np.random.uniform(0, pos_range)
        # self.y1 = 0.0
        # self.v1 = 0.0
        self.step_cnt = 0

    def step(self, action):
        """
        Run one timestep of the environment's dynamics. When end of episode
        is reached, reset() should be called to reset the environment's internal state.
        Input
        -----
        action : an action provided by the policy, here a combination of f and k
        
        Outputs
        -------
        (observation, reward, done, info)
        observation : agent's observation of the current environment
        reward [Float] : amount of reward due to the previous action
        done : a boolean, indicating whether the episode has ended
        info : a dictionary containing other diagnostic information from the previous action
        """
        action = np.clip(action.copy(), self.action_space.low, self.action_space.high)

        f = action[0] # input force
        k = action[1] # spring stiffness

        f_total = f + (m1+ m2) * g - k*self.y1
        a = f_total / (m1+ m2)

        for _ in range(n_steps_per_action):
            v1_curr = self.v1
            y1_curr = self.y1
            v1_next = v1_curr + a * dt
            y1_next = y1_curr + v1_curr * dt  + 0.5 * a * dt**2 # mid-point Euler integration
            self.v1 = v1_next
            self.y1 = y1_next

        self.y1 = np.clip(self.y1, 0.0, pos_range)
        self.v1 = np.clip(self.v1, -half_vel_range, half_vel_range)

        y2 = self.y1 + l

        obs = np.array([self.y1, self.v1])

        reward = -reward_alpha * (y2 - h)**2 - reward_beta*f**2 - reward_gamma*self.v1**2

        done = False
        info = {}

        # self.step_cnt += 1
        # if self.step_cnt == 499:
            # print()
            # print('f: ', f)
            # print('k: ', k)
            # print('y2: ', y2)
            # print()
        return obs, reward, done, info

    def reset(self):
        self.v1 = np.random.uniform(-half_vel_range, half_vel_range) # vel of both masses
        self.y1 = np.random.uniform(0, pos_range)
        # self.y1 = 0.0
        # self.v1 = 0.0
        self.step_cnt = 0
        return np.array([self.y1, self.v1])
    
    def render(self, mode='human'):
        pass