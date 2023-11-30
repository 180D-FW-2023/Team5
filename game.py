import speech_processing as sp
import text_to_bear_audio as tba
import stream_test as st
import llm_handler as llm_h



def main():
    # #Test call to speech recognition program
    # sp.recognize_wav("test/test_capstone.wav")
    # return
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
                    decisions long. Make each choice revolve around a problem and make there be an overall goal the player is 
                    trying to accomplish throughout the whole game where the player either achieves their goal or fails after the last decision.
                    Make your responses at most 100 words long. Don't say "option 1 is ... and option 2 is ...", instead make it flow naturally.
                    Make sure the story you generate is appropriate for children. When you respond, NEVER SAY "Teddy Bear: " or anything similar to that.
                    I repeat, When you respond, NEVER SAY "Teddy Bear: " or anything similar to that. First, ask the child for their name and call them by their 
                    name for the rest of the game. After waiting for the child to reply (i.e. stopping and waiting), proceed by asking them what theme they want 
                    the game to have (for example: pirates, forest, etc...). Then begin the story phase where you repeatedly explain what is 
                    happening and tell the child what their options are and then WAIT FOR THE CHILD TO RESPOND. Remember, don't start with "teddy bear:". 
                    Now, ask what the child's name is, you should say "Hello, what's your name":
                  """

    # Add initial prompt to game state
    game_state.append(llm_h.create_game_state_addition("user", init_prompt))

    # Send initial request to GPT 3.5 Turbo to get the game started
    LLM_reponse = llm_h.send_openai_api_request(game_state)
    # print("\n\nFIRST LLM RESPONSE RECEIVED\n\n")
    game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))

    while True:

        speech = sp.gather_speech_data()
        print("you said: " + speech)

        game_state.append(llm_h.create_game_state_addition("user", speech))

        LLM_reponse = llm_h.send_openai_api_request(game_state)

        game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))


if __name__ == '__main__':
    main()