
# Code Information for data directory

The data folder contains code for the configuration of our game:

```filtered_words.json``` -
Simplifies possible outputs from the API to vocabulary appropriate for a child

```prompts.json``` -
Converts user inputs/choices to appropriate responses by sending designated prompts to the API based on previous actions. 

These are merely json files and therefore have little room for bugs. The inspiration for the prompts stemmed in part from the Ambient Adventures research paper by Zexin Chen, Eric Zhou, Kenneth Eaton, Xiangyu Peng, and Mark Riedl found at https://arxiv.org/abs/2308.01734. One future improvement would be to continue to improve prompting to get more reliable and consistent responses from ChatGPT, as well as adding more filtering to the filtered words list.

