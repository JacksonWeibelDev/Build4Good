'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import eval7
import random

def evaluate_hand(cards):
    '''
    Evaluates the strength of a poker hand using eval7.
    
    Arguments:
    cards: List of card strings (e.g., ['As', 'Ks', 'Qs', 'Js', '10s'])
    
    Returns:
    float: Hand strength score (higher is better)
    '''
    # Convert card strings to eval7 Card objects
    eval7_cards = [eval7.Card(card) for card in cards]
    # Evaluate the hand
    return eval7.evaluate(eval7_cards)

class Player(Bot):
    '''
    A pokerbot.
    '''

    def __init__(self):
        '''
        Called when a new game starts. Called exactly once.

        Arguments:
        Nothing.

        Returns:
        Nothing.
        '''
        pass

    def handle_new_round(self, game_state, round_state, active):
        '''
        Called when a new round starts. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_bankroll = game_state.bankroll  # the total number of chips you've gained or lost from the beginning of the game to the start of this round
        #game_clock = game_state.game_clock  # the total number of seconds your bot has left to play this game
        #round_num = game_state.round_num  # the round number from 1 to NUM_ROUNDS
        #my_cards = round_state.hands[active]  # your cards
        #big_blind = bool(active)  # True if you are the big blind
        pass

    def handle_round_over(self, game_state, terminal_state, active):
        '''
        Called when a round ends. Called NUM_ROUNDS times.

        Arguments:
        game_state: the GameState object.
        terminal_state: the TerminalState object.
        active: your player's index.

        Returns:
        Nothing.
        '''
        #my_delta = terminal_state.deltas[active]  # your bankroll change from this round
        previous_state = terminal_state.previous_state  # RoundState before payoffs
        #street = previous_state.street  # 0, 3, 4, or 5 representing when this round ended
        #my_cards = previous_state.hands[active]  # your cards
        #opp_cards = previous_state.hands[1-active]  # opponent's cards or [] if not revealed
        pass

    def get_action(self, game_state, round_state, active):
        '''
        Where the magic happens - your code should implement this function.
        Called any time the engine needs an action from your bot.

        Arguments:
        game_state: the GameState object.
        round_state: the RoundState object.
        active: your player's index.

        Returns:
        Your action.
        '''
        legal_actions = round_state.legal_actions()  # the actions you are allowed to take
        street = round_state.street  # 0, 3, 4, or 5 representing pre-flop, flop, turn, or river respectively
        my_cards = round_state.hands[active]  # your cards
        board_cards = round_state.deck[:street]  # the board cards
        my_pip = round_state.pips[active]  # the number of chips you have contributed to the pot this round of betting
        opp_pip = round_state.pips[1-active]  # the number of chips your opponent has contributed to the pot this round of betting
        my_stack = round_state.stacks[active]  # the number of chips you have remaining
        opp_stack = round_state.stacks[1-active]  # the number of chips your opponent has remaining
        continue_cost = opp_pip - my_pip  # the number of chips needed to stay in the pot
        my_contribution = STARTING_STACK - my_stack  # the number of chips you have contributed to the pot
        opp_contribution = STARTING_STACK - opp_stack  # the number of chips your opponent has contributed to the pot

        # Calculate remaining rounds and chip difference
        remaining_rounds = NUM_ROUNDS - game_state.round_num
        chip_difference = my_stack - opp_stack
        
        # # If we're ahead and there's not enough rounds to overcome our lead (assuming we fold from now on)
        if game_state.bankroll > 0 and game_state.bankroll > ((remaining_rounds+1) * 6):
            return FoldAction()

        # Evaluate current hand strength
        current_hand = my_cards + board_cards
        hand_strength = evaluate_hand(current_hand)
        
        # Adjust betting strategy based on hand strength
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()
            min_cost = min_raise - my_pip
            max_cost = max_raise - my_pip
            
            if(random.random() > 0.5):
                return RaiseAction(max_raise)
            else:
                # More aggressive with stronger hands
                if hand_strength > 0.7:  # Strong hand
                    return RaiseAction(max_raise)
                elif hand_strength > 0.5:  # Decent hand
                    return RaiseAction(min_raise)
                elif random.random() < 0.3:  # Occasional bluff
                    return RaiseAction(min_raise)
        
        if CheckAction in legal_actions:
            return CheckAction()
            
        # Fold more often with weak hands
        # if hand_strength < 0.3 and random.random() < 0.5:
        #     return FoldAction()
            
        return CallAction()  # Default to calling if we can't raise


if __name__ == '__main__':
    run_bot(Player(), parse_args())
