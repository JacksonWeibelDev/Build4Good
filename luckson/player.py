'''
Simple example pokerbot, written in Python.
'''
from skeleton.actions import FoldAction, CallAction, CheckAction, RaiseAction
from skeleton.states import GameState, TerminalState, RoundState
from skeleton.states import NUM_ROUNDS, STARTING_STACK, BIG_BLIND, SMALL_BLIND
from skeleton.bot import Bot
from skeleton.runner import parse_args, run_bot
import eval7
import math
import random


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
        # Initialize opponent modeling variables
        self.opponent_stats = {
            'revealed_hands': [],        # list of (cards, actions) tuples
            'confidence': 0.0,           # measure of how reliable opponent's actions are
            'current_round_actions': []  # track actions in current round
        }

    def evaluate_hand_strength(self, cards):
        '''
        Evaluates hand strength and returns a category (strong, medium, weak)
        
        Arguments:
        cards: List of card strings
        
        Returns:
        str: 'strong', 'medium', or 'weak'
        '''
        strength = self.evaluate_hand(cards)
        if strength > 0.7:
            return 'strong'
        elif strength > 0.4:
            return 'medium'
        return 'weak'

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
        previous_state = terminal_state.previous_state
        
        # Get opponent's cards if revealed
        opp_cards = previous_state.hands[1-active]
        if opp_cards:  # If opponent's cards were revealed
            # Record the revealed hand and actions
            self.opponent_stats['revealed_hands'].append((opp_cards, self.opponent_stats['current_round_actions']))
            
            # Calculate confidence based on action consistency
            total_revealed = len(self.opponent_stats['revealed_hands'])
            if total_revealed > 0:
                consistent_actions = 0
                for cards, actions in self.opponent_stats['revealed_hands']:
                    strength = self.evaluate_hand_strength(cards)
                    # Check if actions are consistent with hand strength
                    if strength == 'strong' and 'fold' not in actions:
                        consistent_actions += 1
                    elif strength == 'weak' and 'raise' not in actions:
                        consistent_actions += 1
                
                self.opponent_stats['confidence'] = consistent_actions / total_revealed
        
        # Reset current round actions
        self.opponent_stats['current_round_actions'] = []

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
        pass

    def evaluate_hand(self, cards):
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

    def evaluate_opportunity(self, my_cards, board_cards, deck):
        '''
        Evaluates the strength of our hand against all possible opponent hands.
        
        Arguments:
        board_cards: List of community cards
        deck: List of remaining cards in the deck
        
        Returns:
        float: Average hand strength against all possible opponent hands
        '''
        NTotal = 52
        
        # Create a set of all used cards (our cards + board cards)
        used_cards = set(my_cards + board_cards)
        
        # Create a set of all remaining cards
        remaining_cards = set(deck)
        
        # Calculate number of possible opponent hands
        n_opponent_hands = 0
        total_strength = 0
        
        # Iterate through all possible opponent hands
        for card1 in remaining_cards:
            for card2 in remaining_cards:
                if card1 != card2:  # Ensure we don't use the same card twice
                    # Create opponent's hand
                    opp_hand = [card1, card2]
                    
                    # Evaluate our hand vs opponent's hand
                    our_hand = my_cards + board_cards
                    opp_hand_with_board = opp_hand + board_cards
                    
                    our_strength = self.evaluate_hand(our_hand)
                    opp_strength = self.evaluate_hand(opp_hand_with_board)
                    
                    # Compare hands
                    if our_strength > opp_strength:
                        total_strength += 1
                    elif our_strength == opp_strength:
                        total_strength += 0.5
                    
                    n_opponent_hands += 1
        
        # Calculate equity (probability of winning)
        if n_opponent_hands > 0:
            equity = total_strength / n_opponent_hands
            return equity
        return 0.0  # Return 0 if no possible opponent hands

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
        legal_actions = round_state.legal_actions()
        street = round_state.street
        my_cards = round_state.hands[active]
        board_cards = round_state.deck[:street]
        my_pip = round_state.pips[active]
        opp_pip = round_state.pips[1-active]
        my_stack = round_state.stacks[active]
        opp_stack = round_state.stacks[1-active]
        continue_cost = opp_pip - my_pip
        my_contribution = STARTING_STACK - my_stack
        opp_contribution = STARTING_STACK - opp_stack

        # Evaluate current hand strength and equity
        current_hand = my_cards + board_cards
        hand_strength = self.evaluate_hand(current_hand)
        equity = self.evaluate_opportunity(my_cards, board_cards, round_state.deck)
        remaining_rounds = 5000 - game_state.round_num

        # Only fold if we're winning by a lot - instant win condition
        if game_state.bankroll > 0 and game_state.bankroll > ((remaining_rounds+1) * 7.5):
            return FoldAction()

        
        if RaiseAction in legal_actions:
            min_raise, max_raise = round_state.raise_bounds()
            
            # Very strong hand with high equity
            if hand_strength > 0.7 and equity > 0.6:
                return RaiseAction(max_raise)
            # Strong hand with good equity
            elif hand_strength > 0.5 and equity > 0.5:
                return RaiseAction(max_raise)
            # Decent hand with good equity
            elif hand_strength > 0.4 and equity > 0.4:
                return RaiseAction(min_raise)
            # Marginal hand but decent equity
            elif equity > 0.4:
                return RaiseAction(min_raise)
            # More frequent bluffs
            elif random.random() < 0.3:
                return RaiseAction(min_raise)
        
        if CheckAction in legal_actions:
            return CheckAction()
            
        # Only fold in absolutely desperate situations
        if hand_strength < 0.2 and equity < 0.2 and random.random() < 0.1:
            return FoldAction()
            
        return CallAction()  # Default to calling with decent hands


if __name__ == '__main__':
    run_bot(Player(), parse_args())
