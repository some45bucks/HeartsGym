import gym
import random
import numpy as np
import os

class Card():

    spade = 0
    clubs = 1
    hearts = 2
    dimonds = 3

    jack = 11
    queen = 12
    king = 13
    ace = 14

    def __init__(self,suit,number):
        self.suit = suit
        self.number = number
        self.id = (number-2) + suit*13

    def __str__(self):
        cardString = ""

        if self.number == 11:
            cardString += "j"
        elif self.number == 12:
            cardString += "q"
        elif self.number == 13:
            cardString += "k"
        elif self.number == 14:
            cardString += "a"
        else:
            cardString += str(self.number)

        if self.suit == 0:
            cardString += "s"
        if self.suit == 1:
            cardString += "c"
        if self.suit == 2:
            cardString += "h"
        if self.suit == 3:
            cardString += "d"

        return cardString
    
    def __eq__(self, other):
        return other.suit == self.suit and other.number == self.number
    
    # creates new deck of cards
    def newDeck():
        deck = []

        for suit in range(4):
            for number in range(2,15):
                deck.append(Card(suit,number))

        return deck

    # returns true if list contains card 
    def listContainCard(list,suit=-1,number=-1):
        hasCard = False

        for card in list:
            if (card.suit == suit or suit == -1) and (card.number == number or number == -1):
                hasCard = True
                break
        
        return hasCard

    # helper function to prints lists of cards
    def print(list,printOut=False):
        string = "| "

        for i in list:
            string += f"{i} "
        
        string += "|"

        if printOut:
            print(string)

        return string

    # gives you the card with the inputed ID
    def cardById(id):
        for n in range(2,15):
            for s in range(4):
                if (n-2) + s*13 == id:
                    return Card(s,n)

class Hearts(gym.Env):

    def __init__(self):
        self.action_space = gym.spaces.Discrete(13)
        self.observation_space = gym.spaces.Discrete(52*13 + 52*3 + 52 + 4)
        self.log = ''

    # deals the hands randomly from deck    
    def dealHands(self):
        deck = Card.newDeck()

        random.shuffle(deck)

        hands = [[],[],[],[]]

        while len(deck) > 0:
            for i in range(4):
                hands[i].append(deck.pop(0))

        return hands

    # tells you if action is valid with respect to current state
    def isActionValid(self,action):
        currentHand = self.getCurrentPlayersHand()

        if action >= len(currentHand) or action < 0:
            return False

        actionCard = currentHand[action]
        currentTrick = self.state["currentTrick"]

        if Card.listContainCard(currentHand,Card.clubs,2):
            return actionCard == Card(Card.clubs,2)

        if len(currentTrick) == 0:
            if actionCard.suit == Card.hearts:
                return (Card.listContainCard(self.state["pastCards"],Card.hearts) or 
                    Card.listContainCard(self.state["pastCards"],Card.spade,Card.queen) or

                    (not Card.listContainCard(self.getCurrentPlayersHand(),Card.spade) and 
                     not Card.listContainCard(self.getCurrentPlayersHand(),Card.clubs) and
                     not Card.listContainCard(self.getCurrentPlayersHand(),Card.dimonds))
                    )
            else:
                return True
        else:
            if Card.listContainCard(currentHand,currentTrick[0].suit):
                return actionCard.suit == currentTrick[0].suit
            else:
                return True

    # helper function to get current player
    def getCurrentPlayer(self):
        return self.state["currentPlayer"]
    
    # helper function to see current players hand
    def getCurrentPlayersHand(self):
        return self.state['hands'][self.getCurrentPlayer()]

    # function to send out the observations of the env
    def observation(self):
        obvs = []

        for i in range(13):
            if i >= len(self.getCurrentPlayersHand()):
                for j in range(52):
                        obvs.append(0)

            else:
                card = self.getCurrentPlayersHand()[i]

                for j in range(52):
                    if card.id != j:
                        obvs.append(0)
                    else:
                        obvs.append(1)

        for i in range(3):
            if i >= len(self.state["currentTrick"]):
                for j in range(52):
                        obvs.append(0)

            else:
                card = self.state["currentTrick"][i]

                for j in range(52):
                    if card.id != j:
                        obvs.append(0)
                    else:
                        obvs.append(1)
        temp = []
        for i in range(52):
            temp.append(0)

        for card in self.state["pastCards"]:
            temp[card.id] = 1
        
        for i in range(52):
            obvs.append(temp[i])

        for i in range(4):
            obvs.append(self.state["scores"][(self.getCurrentPlayer()+i) % 4]/26)

        return np.array(obvs)

    def isRoundOver(self):
        return len(self.state["currentTrick"]) == 0

    # resets the env
    def reset(self):
        self.state = {
            "hands": self.dealHands(),
            "currentTrick": [],
            "scores": [0,0,0,0],
            "pastCards": [],
            "currentPlayer": 0,
            "shootingTheMoon": -1,
        }

        self.log = ''

        while not Card.listContainCard(self.getCurrentPlayersHand(),Card.clubs,2):
            self.state["currentPlayer"]+=1

        return self.observation()

    # main stepping function (returns the reward as a list)
    def step(self, action):
        reward = [0,0,0,0]
        done = False

        self.log += f""

        if not self.isActionValid(action):
            for i in range(13):
                if self.isActionValid(i):
                    action = i
                    break
        if self.getCurrentPlayersHand()[action].suit == Card.hearts or self.getCurrentPlayersHand()[action] == Card(Card.spade,Card.queen):
                self.log += f"Player {self.getCurrentPlayer()} plays: \033[91m{self.getCurrentPlayersHand()[action]}\033[0m "
        else:
            self.log += f"Player {self.getCurrentPlayer()} plays: {self.getCurrentPlayersHand()[action]} "
        self.state["currentTrick"].append(self.getCurrentPlayersHand().pop(action))

        if len(self.state["currentTrick"]) == 4:

            startSuit = self.state["currentTrick"][0].suit
            biggestCardNum = -1
            biggestCardNumPlayer = -1
            score = 0

            currentPlayer = self.getCurrentPlayer()

            while len(self.state["currentTrick"]) > 0:
                tempCard = self.state["currentTrick"].pop()

                if tempCard.suit == startSuit and tempCard.number > biggestCardNum:
                    biggestCardNum = tempCard.number
                    biggestCardNumPlayer = currentPlayer

                currentPlayer = (currentPlayer-1) % 4

                if tempCard.suit == Card.hearts:
                    score += 1
                
                if tempCard == Card(Card.spade,Card.queen):
                    score += 13

                self.state["pastCards"].append(tempCard)
            
            self.state["scores"][biggestCardNumPlayer] += score
            self.log += f"  *Round Over: Player {biggestCardNumPlayer} wins the trick and gets {score} point(s)*\n"

            if score > 0:
                if self.state["shootingTheMoon"] == -1:
                    self.state["shootingTheMoon"] = biggestCardNumPlayer
                else:
                    self.state["shootingTheMoon"] = -2

            if len(self.state["pastCards"]) == 52:
                
                if not self.state["shootingTheMoon"] == -2:
                    self.log += "Over The MOON!\n"
                    for i in range(4):
                        if i == self.state["shootingTheMoon"]:
                            self.state["scores"][i] -= 26
                        else:
                            self.state["scores"][i] += 26
                
                for i in range(4):
                    reward[i] = 1-(self.state["scores"][i]/26)

                done = True
                self.log += f"\n**Game over**\n"
                self.log += f"\nReward: {reward}\n"


            else:
              self.state["currentPlayer"] = biggestCardNumPlayer  

        else:
            self.state["currentPlayer"] = (self.state["currentPlayer"]+1) % 4

        self.log += "\n"

        return self.observation(), reward, done

    # renders the game using text    
    def render(self):
        os.system('cls' if os.name=='nt' else 'clear')

        stateString = ""

        for i in range(4):
            if i == self.getCurrentPlayer() and len(self.getCurrentPlayersHand()) != 0:
                stateString += f"                                                  \033[94mPlayer {i} score: {self.state['scores'][i]}\033[0m\n"

            else:
                stateString += f"                                                  Player {i} score: {self.state['scores'][i]}\n"
        if len(self.getCurrentPlayersHand()) != 0:    
            stateString += f"\n          Trick: "

        for i in self.state['currentTrick']:
            if i.suit == Card.hearts or i == Card(Card.spade,Card.queen):
                stateString += "\033[91m"

            if i == self.state['currentTrick'][0]:
                stateString += f"\033[1m{i}\033[0m "
            else:
                stateString += f"{i} "

            if i.suit == Card.hearts or i == Card(Card.spade,Card.queen):
                stateString += "\033[0m"

        if len(self.getCurrentPlayersHand()) != 0:
            stateString += f"\n\n\n\n          Hand: "

        for i in range(len(self.getCurrentPlayersHand())):
            if self.getCurrentPlayersHand()[i].suit == Card.hearts or self.getCurrentPlayersHand()[i] == Card(Card.spade,Card.queen):
                stateString += "\033[91m"

            if self.isActionValid(i):
                stateString += "\033[1m{:7s}\033[0m".format(str(self.getCurrentPlayersHand()[i]))
            else:
                stateString += "{:7s}".format(str(self.getCurrentPlayersHand()[i]))

            if self.getCurrentPlayersHand()[i].suit == Card.hearts or self.getCurrentPlayersHand()[i] == Card(Card.spade,Card.queen):
                stateString += "\033[0m"
            

        stateString += f"\n                "

        for i in range(13):
            if self.isActionValid(i):
                stateString += "\033[1m{:7s}\033[0m".format(str(i))
            else:
                stateString += "{:7s}".format("")

        print(self.log)
        print(stateString)

        self.log = ''

    # lets you play the game manualy with random actions filling in the other players
    def playHearts(players=1):

        env = Hearts()

        playState = env.reset()
        done = False

        if env.getCurrentPlayer() <= players-1:
            env.render()

        while not done:
            if env.getCurrentPlayer() <= players-1:
                action = int(input("Enter Action: "))
            else:
                action = 0
            playState, playReward, done = env.step(action)
            Hearts.translateState(playState)
            if env.getCurrentPlayer() <= players-1:
                env.render()

        if env.getCurrentPlayer() > players-1 or players == 0:
            env.render()

    # makes the state into a human readable form
    def translateState(state):
        
        hand = state[0:13*52]
        pHand = []

        trick = state[13*52:3*52+13*52]
        pTrick = []

        past = state[3*52+13*52:3*52+13*52+52]
        pPast = []

        scores = state[3*52+13*52+52:3*52+13*52+52+4]
        pScores = []

        for i in range(13):
            for j in range(52):
                if hand[i*52 + j] == 1:
                    pHand.append(Card.cardById(j))
                    break
        
        for i in range(3):
            for j in range(52):
                if trick[i*52 + j] == 1:
                    pTrick.append(Card.cardById(j))
                    break

        for i in range(52):
            if past[i] == 1:
                pPast.append(Card.cardById(i))

        for i in scores:
            pScores.append(i * 26)

        return pHand, pTrick, pPast, pScores

Hearts.playHearts(1)