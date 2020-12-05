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
NUM_PHRASES_TO_PRINT = 100
total_messages = 0
total_reacts_and_stickers = 0
people = {}
phrases = {}
top_people = []
top_phrases = []
phrase_length = 4 # default: 4

if __name__ == "__main__":
  print('\nYOUR NAME')
  your_name = input('Please input your name as shown on Messenger (so your top person is not you in the generated data!). Capitalization and whitespace matter:\n')
  # determine phrase length to search for
  print('\nPHRASE LENGTH')
  temp_phrase_length = input('How many words should your most frequent phrases contain? Enter 3, 4, 5, or 6 (default is 4):\n')
  if int(temp_phrase_length) in {3,4,5,6}:
    phrase_length = int(temp_phrase_length)
  # ignore certain phrases upon request. If an ignorable phrase is found in a message, the whole message will be ignored.
  print('\nPHRASES TO IGNORE')
  print('(Press ENTER if there are no phrases you wish to ignore.)')
  phrases_to_ignore = input('Are there any phrases you would like to ignore when identifying your top phrases of the year? If any of these phrases are found in a message, the whole message will be ignored for the purpose of identifying top phrases.\n Please ignore punctuation (parentheses, apostrophes, etc) and separate phrases with commas, e.g. Words with Friends, The video chat ended, missed your call\n')
  phrases_to_ignore = [] if not phrases_to_ignore else [p.strip() for p in phrases_to_ignore.lower().split(',')]
  # ignore certain senders upon request.
  print('\nSENDERS TO IGNORE')
  print('(Press ENTER if there are no senders you wish to ignore.)')
  senders_to_ignore = input('Are there any senders you would like to ignore when identifying your top senders of the year? \n Please separate phrases with commas. Capitalization and whitespace matter: e.g. Abcd Efgh, Ijkl Mnop, Qrst Uvwx\n')
  senders_to_ignore = [] if not senders_to_ignore else [p.strip() for p in senders_to_ignore.split(',')]

  for dir, _, files in os.walk(MESSENGER_DIR):
    for file in files:
      if file == 'message_1.json':
        with open(os.path.join(dir, file)) as json_file:
          data = json.load(json_file)

          # Track number of messages sent by different people
          for m in data['messages']:
            sender_name = m['sender_name']
            if sender_name in people:
              people[sender_name] = people[sender_name] + 1
            else: 
              people[sender_name] = 1

            # Track reacts that you give
            if 'reactions' in m:
              for react in m['reactions']:
                if react['actor'] == your_name:
                  total_reacts_and_stickers = total_reacts_and_stickers + 1

            # Also track stickers that you send
            if 'sticker' in m and sender_name == your_name:
              total_reacts_and_stickers = total_reacts_and_stickers + 1

            # Extract 5-word phrases from your messages
            if 'content' in m and m['sender_name'] == your_name:
              s = m['content'].encode('latin1').decode('utf8').lower().translate(str.maketrans('', '', string.punctuation))
              ignore_phrase = False
              for ignorable_phrase in phrases_to_ignore:
                if ignorable_phrase in s:
                  ignore_phrase = True
                  break
              if not ignore_phrase:
                words = s.split()
                num_words = len(words)
                if num_words >= phrase_length:
                  for i in range(0, num_words-phrase_length):
                    phrase = " ".join(words[i:phrase_length+i])
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

  # remove ignored senders from the list
  for sender_name in senders_to_ignore:
    people.pop(sender_name, None)

  people = sorted(people.items(), key=lambda x: x[1], reverse=True)

  print('\nVIEW TOP MESSAGE SENDERS')
  print_people = input('Would you like to view the names and number of messages sent by the top 25 people who sent you the most messages this year? (yes/no)\n').lower()
  if print_people == 'yes' or print_people == 'y':
    for i in range(0, min(len(people), NUM_PEOPLE_TO_PRINT)):
      print(people[i])

  print('\nSHARE NAMES OR NUMBERS OF MESSAGES')
  print('Would you like to display names or the number of messages people sent in your Messenger Wrapped?')
  share_names = input('Type "names" (with no quotation marks) for names; type anything else to substitute in the number of messages instead:\n').lower()
  top_people = [p[0] for p in people[:min(len(people), NUM_TOP_PEOPLE_AND_PHRASES)]] if share_names == 'names' else [p[1] for p in people[:min(len(people), NUM_TOP_PEOPLE_AND_PHRASES)]]

  phrases = sorted(phrases.items(), key=lambda x: x[1], reverse=True)
  print('\nVIEW MOST COMMON PHRASES')
  print_phrases = input('Would you like to view your top 100 most frequently used phrases? (yes/no)\n').lower()
  if print_phrases == 'yes' or print_phrases == 'y': 
    for i in range(0, min(len(phrases), NUM_PHRASES_TO_PRINT)):
      print(phrases[i])
  
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