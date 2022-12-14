'''
Author: Caleb Ehrisman
Course- Advanced AI CSC-549

I was tasked to create inverted pendulum controller using Temporal Difference learning.

The method I wanted to try to implement was Q learning. And then the Double Q method was mentioned in class. The one
disadvantage to Q-learning on its own is that it is not very effective in large state spaces where there can be many
possible states and multiple actions possible at each move. The reason is that it is not able to infer Q values for new
states from previous states. So, with Deep Q learning it is possible to use a neural network to approximate Q values to
make up for that limitation. So, I am implementing the Double Q learning with neural nets to create an agent to play
the inverted pendulum.

I am also using the OpenGymAI CartPole-v1 simulator as there is plenty of examples and documentation on how to use it.
But it should be possible to use the agent with any environment model with some tweaks.

The way this model is trained is episodic. If the pole falls too far or if the cart moves to where the center reaches the edges
it resets.

'''
import collections
import gym
from torch import optim
from agent import Agent
import argparse
import torch

def train(agent, env, target, num_epochs):
    scores = []
    recent = collections.deque(maxlen=100)

    for i in range(num_epochs):
        state, _ = env.reset()
        score = 0
        done = False
        while not done:
            action = agent.action(state)
            next_state, reward, done, null, _ = env.step(action)
            agent.step(state, action, reward, next_state, done)
            state = next_state
            score += reward
        scores.append(score)
        recent.append(score)

        avg = sum(recent) / len(recent)
        if avg >= target:
            print(f"\nReached target score in {i:d} episodes\t Avg score: {avg}")
            torch.save({"online_q": agent.online_q.state_dict(), "target_q": agent.target_q.state_dict(), "optim": agent.optimizer.state_dict()}, "trained-q")
            break
        if (i + 1) % 100 == 0:
            print(f"\rEpisode {i + 1}\tAvg Score: {avg}")
            #print(agent.online_q.state_dict())
    return scores


def decay_schedule(epoch_num, decay, min_esp):
    return max(decay ** epoch_num, min_esp)


def parse():
    parser = argparse.ArgumentParser()
    parser.add_argument('--checkpoint', type=str, help='Specify trained model to start with')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse()

    if args.checkpoint is not None:
        env = gym.make("CartPole-v1", render_mode="human")

    else:
        env = gym.make("CartPole-v1")

    env.action_space.seed(10)

    print(args.checkpoint)
    sched = lambda n: decay_schedule(n, 0.99, 1e-2)

    agent = Agent(env.observation_space.shape[0], env.action_space.n, 64, 64, 100000, sched, 1e-3,
                  0.99, 4, 42, args.checkpoint)
    ddqn_scores = train(agent, env, 3000, 8000)
