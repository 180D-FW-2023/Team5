import speech_processing as sp
import text_to_bear_audio as tba
import stream_test as st
import llm_handler as llm_h
import random

import time

def main():
    """
    Runs the choose your own adventure game.
    """

    # Initialize the game state
    game_state=[]

    # Create initial game state prompt that starts the choose your own adventure game
    # TODO: Experiment with this
    init_prompt = """
                    You are a stuffed teddy bear children's toy. You are going to lead a choose your own adventure game/story
                    with a child that is audio only where you explain what is happening to the child and then you wait for the
                    child to respond (at this point, you stop and DO NOT RESPOND FOR THE CHILD). Make the story exactly 10 
                    decisions long. When the game is over, say "thanks for playing" so that the child knows to stop responding.
                    Make each choice revolve around a problem and make there be an overall goal the player is 
                    trying to accomplish throughout the whole game where the player either achieves their goal or fails after the last decision.
                    Make your responses at most 100 words long. Don't say "option 1 is ... and option 2 is ...", instead make it flow naturally.
                    Make sure the story you generate is appropriate for children. When you respond, NEVER SAY "Teddy Bear: " or anything similar to that.
                    I repeat, When you respond, NEVER SAY "Teddy Bear: " or anything similar to that. 
                    If you ever have to say I'm an AI model, say I'm a teddy bear instead. First, ask the child for their name and call them by their 
                    name for the rest of the game. After waiting for the child to reply (i.e. stopping and waiting), proceed by asking them what theme they want 
                    the game to have (for example: pirates, forest, etc...). Then begin the story phase where you repeatedly explain what is 
                    happening and tell the child what their options are and then WAIT FOR THE CHILD TO RESPOND. Remember, don't start with "teddy bear:". 
                    Now, ask what the child's name is, you should say "Hello, what's your name":
                  """

    # ROUND 1: GET NAME
    # Add initial prompt to game state
    game_state.append(llm_h.create_game_state_addition("user", init_prompt))
    # Send initial request to GPT 3.5 Turbo to get the game started
    LLM_reponse = llm_h.send_openai_api_request(game_state)
    game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))
    speech = sp.gather_speech_data()
    print("you said: " + speech)
    game_state.append(llm_h.create_game_state_addition("user", speech))

    # ROUND 2: CHOOSE STORY SETTING
    LLM_reponse = llm_h.send_openai_api_request(game_state)
    game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))
    speech = sp.gather_speech_data()
    print("you said: " + speech)
    game_state.append(llm_h.create_game_state_addition("user", speech))
    
    # Variables for the game logic
    random_round_next_round = False
    random_round = False

    # ROUNDS 3+: MAIN GAME LOOP
    while True:

        # Get current round's story output
        LLM_reponse = llm_h.send_openai_api_request(game_state)

        # Game is over, stop asking for reponses from the child
        if "for playing" in LLM_reponse:
            break

        game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))

        speech = sp.gather_speech_data()
        print("you said: " + speech)

        # The child has a chance of losing the game this round
        if random_round_next_round:
            random_round = True
            random_round_next_round = False

        # 10% chance of a potentially game ending round
        if random.randint(1,10) == 1:
            print("It's random time")
            speech += """ (Also, for this round only, present THREE options and MAKE IT CLEAR that one of them
            is game ending. If the child chooses this option they will lose the game. Don't assume they know that one option will lose
            them the game (i.e. don't say 'remember')."""
            random_round_next_round = True

        # If this is a random round, we use randomness to determine if the child keeps playing or not
        if random_round and random.randint(1,3) == 2:
            speech += """ (By the way, the child chose the wrong option this round so the game should end. Come up with a kid friendly 
                        reason why the child lost the game and tell them thanks for playing. Don't start the response by saying great 
                        job, since they lost game.)
                        """
            random_round = False

        game_state.append(llm_h.create_game_state_addition("user", speech))


if __name__ == '__main__':
    main()