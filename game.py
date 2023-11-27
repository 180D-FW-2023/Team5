import speech_processing as sp
import text_to_bear_audio as tba
import stream_test as st
import llm_handler as llm_h



def main():
    """
    Runs the choose your own adventure game.
    """

    # Initialize the game state
    game_state=[]

    # Create initial game state prompt that starts the choose your own adventure game
    # TODO: Experiment with this
    init_prompt = """
                    You are a stuffed teddy bear children's toy. Call the child "friend". You are going to lead a choose your own adventure game/story
                    with a child that is audio only. Make the story at least five decisions long and make each decision have two discrete choices.
                    Make your responses at most 100 words long. Make sure the story you generate is appropriate for children. Do not say use 
                    "Teddy:" to start your message as we will know it is you talking. First, give the child some options for what theme of 
                    choose your own adventure they would like to play (for example: pirates, forest, and come up with some other options too). 
                    Then, wait for a response from the child. Then, proceed by following the previous instructions.
                  """

    # Add initial prompt to game state
    game_state.append(llm_h.create_game_state_addition("user", init_prompt))

    # Send initial request to GPT 3.5 Turbo to get the game started
    LLM_reponse = llm_h.send_openai_api_request(game_state)
    print("\n\nFIRST LLM RESPONSE RECEIVED\n\n")
    game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))

    while True:

        speech = sp.gather_speech_data()
        print("you said: " + speech)

        game_state.append(llm_h.create_game_state_addition("user", speech))

        LLM_reponse = llm_h.send_openai_api_request(game_state)

        game_state.append(llm_h.create_game_state_addition("system", LLM_reponse))


if __name__ == '__main__':
    main()