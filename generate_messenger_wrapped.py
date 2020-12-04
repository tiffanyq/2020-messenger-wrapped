"""
Run this script after downloading Messenger data from
January 1 2020 - December 1 2020 (or some later date in 2020)
in JSON format. Put the `messages` folder in the `2020messengerwrapped`
directory.

In this directory: run `python generate_messenger_wrapped.py`
to generate the file that index.html will use to generate
your 2020 Messenger Wrapped!
"""

import json
import os
import string

MESSENGER_DIR = './messages/inbox'
OUTPUT_FILE_DIR = './js'
OUTPUT_FILENAME = 'your_messenger_wrapped.js'
NUM_TOP_PEOPLE_AND_PHRASES = 5
NUM_PEOPLE_TO_PRINT = 25
NUM_PHRASES_TO_PRINT = 200
total_messages = 0
total_reacts_and_stickers = 0
people = {}
phrases = {}
top_people = []
top_phrases = []
phrase_length = 4 # default: 4

if __name__ == "__main__":
  print(string.punctuation)
  your_name = input('\nPlease input your name as shown on Messenger (so your top person is not you in the generated data!). Capitalization and whitespace matter:\n')
  # determine phrase length to search for
  temp_phrase_length = input('\nHow many words should your most frequent phrases contain? Enter 3, 4, 5, or 6 (default is 4):\n')
  if int(temp_phrase_length) in {3,4,5,6}:
    phrase_length = int(temp_phrase_length)

  for dir, _, files in os.walk(MESSENGER_DIR):
    for file in files:
      if file == 'message_1.json':
        with open(os.path.join(dir, file)) as json_file:
          data = json.load(json_file)

          # Track number of messages sent by different people
          for m in data['messages']:
            if m['sender_name'] in people:
              people[m['sender_name']] = people[m['sender_name']] + 1
            else: 
              people[m['sender_name']] = 1

            # Track reacts that you give
            if 'reactions' in m:
              for react in m['reactions']:
                if react['actor'] == your_name:
                  total_reacts_and_stickers = total_reacts_and_stickers + 1

            # Also track stickers that you send
            if 'sticker' in m and m['sender_name'] == your_name:
              total_reacts_and_stickers = total_reacts_and_stickers + 1

            # Extract 5-word phrases from your messages
            if 'content' in m and m['sender_name'] == your_name:
              s = m['content'].encode('latin1').decode('utf8').lower().translate(str.maketrans('', '', string.punctuation))
              words = s.split()
              print(words)
              num_words = len(words)
              if num_words >= phrase_length:
                for i in range(0, num_words-phrase_length):
                  phrase = " ".join(words[i:phrase_length+i])
                  # this is kind of fun to see if you want to see this all print out
                  # print(phrase)
                  if phrase in phrases:
                    phrases[phrase] = phrases[phrase] + 1
                  else:
                    phrases[phrase] = 1

  # Generate top list of people
  # first, identify how many messages you sent
  # remove yourself from the list
  if your_name in people:
    total_messages = people[your_name]
  people.pop(your_name, None)

  people = sorted(people.items(), key=lambda x: x[1], reverse=True)

  print_people = input('\nWould you like to view the names and number of messages sent by the top 25 people who sent you the most messages this year? (yes/no)\n').lower()
  if print_people == 'yes' or print_people == 'y':
    for i in range(0, min(len(people), NUM_PEOPLE_TO_PRINT)):
      print(people[i])
      print('\n')

  print('\nWould you like to display names or the number of messages people sent in your Messenger Wrapped?')
  share_names = input('Type "names" (with no quotation marks) for names; type anything else to substitute in the number of messages instead:\n')
  top_people = [p[0] for p in people[:min(len(people), NUM_TOP_PEOPLE_AND_PHRASES)]] if share_names == 'names' else [p[1] for p in people[:min(len(people), NUM_TOP_PEOPLE_AND_PHRASES)]]
  
  phrases = sorted(phrases.items(), key=lambda x: x[1], reverse=True)

  print_phrases = input('\nWould you like to view your top 200 most frequently used phrases? (yes/no)\n').lower()
  if print_phrases == 'yes' or print_phrases == 'y': 
    for i in range(0, min(len(phrases), NUM_PHRASES_TO_PRINT)):
      print(phrases[i])
      print("\n")
  
  top_phrases = [p[0] for p in phrases[:min(len(phrases), NUM_TOP_PEOPLE_AND_PHRASES)]]

  output_data = {
    "total_messages": total_messages,
    "total_reacts_and_stickers": total_reacts_and_stickers,
    "share_names": share_names == 'names',
    "top_people": top_people,
    "top_phrases": top_phrases,
  }

  with open(os.path.join(OUTPUT_FILE_DIR, OUTPUT_FILENAME), 'w') as outfile:
    outfile.write("yourData=")
    json.dump(output_data, outfile)