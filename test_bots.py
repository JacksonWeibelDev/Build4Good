import subprocess
import os
import time
from pathlib import Path

def run_game():
    """
    Runs a single game and returns the winner from the gamelog.
    Returns:
        int: 0 for player 0 win, 1 for player 1 win, -1 for error
    """
    try:
        # Run the engine
        subprocess.run(['python', 'engine.py'], check=True)
        
        # Read the last line of gamelog.txt
        with open('gamelog.txt', 'r') as f:
            lines = f.readlines()
            if not lines:
                return -1
                
            last_line = lines[-1].strip()
            
            # Parse the winner from the last line
            if "Player 0 wins" in last_line:
                return 0
            elif "Player 1 wins" in last_line:
                return 1
            else:
                print(f"Unexpected last line: {last_line}")
                return -1
                
    except Exception as e:
        print(f"Error running game: {e}")
        return -1

def run_test_series(num_games=100):
    """
    Runs multiple games and tracks win rates.
    
    Args:
        num_games: Number of games to run
    """
    # Initialize counters
    player0_wins = 0
    player1_wins = 0
    errors = 0
    
    print(f"Starting test series of {num_games} games...")
    
    # Run games
    for i in range(num_games):
        print(f"\nRunning game {i+1}/{num_games}")
        winner = run_game()
        
        if winner == 0:
            player0_wins += 1
            print("Player 0 won")
        elif winner == 1:
            player1_wins += 1
            print("Player 1 won")
        else:
            errors += 1
            print("Error in game")
            
        # Small delay to prevent system overload
        time.sleep(0.1)
    
    # Calculate win rates
    successful_games = num_games - errors
    if successful_games > 0:
        player0_win_rate = (player0_wins / successful_games) * 100
        player1_win_rate = (player1_wins / successful_games) * 100
        
        print("\n=== Test Results ===")
        print(f"Total games played: {num_games}")
        print(f"Successful games: {successful_games}")
        print(f"Errors: {errors}")
        print(f"\nPlayer 0 wins: {player0_wins} ({player0_win_rate:.2f}%)")
        print(f"Player 1 wins: {player1_wins} ({player1_win_rate:.2f}%)")
    else:
        print("\nNo successful games completed!")

if __name__ == "__main__":
    # Get the number of games from command line or use default
    import sys
    num_games = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    
    # Ensure we're in the correct directory
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    # Run the test series
    run_test_series(num_games) 