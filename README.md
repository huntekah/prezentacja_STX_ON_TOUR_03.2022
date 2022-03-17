# prezentacja_STX_ON_TOUR_03.2022

1. First create an account on Twitter, and register as a developer.
2. Use [crawler](get_tweets.py) to download tweets according to [topics](topics.py)
   1. You might need to filter retweets and similar tweets with a [simple script](filter_repetitive_tweets.sh).
   2. remove nasty '^M' with another [script](utils/remove_ctrl_m_in_this_folder.sh) 
3. [Translate](translate_tweets.py) your tweets.
4. [Classify](classify_tweets.py) sentences.