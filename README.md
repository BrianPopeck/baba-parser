# baba-parser
A recursive descent parser for parsing rules from the game [Baba is You](https://en.wikipedia.org/wiki/Baba_Is_You), with experimental support for new features such as "NOT" and "IF". Inspired by Arvi Teikari's [talk](https://www.youtube.com/watch?v=Jf5O8S5GiOo) at GDC 2020.

# Usage
Requires Python 3.
To input rules manually:
```
python3 baba_parser.py
```

To parse all rules from a file (e.g. a file from the examples directory):
```
python3 baba_parser.py input_file
```
# Notes
The negation from "NOT" is represented by a "~" in the parsed rule.

Uses the following context-free grammar, where terminal symbols are prefixed with "T_":
```
S -> Rule If Noun Verb Preposition_phrase_list | Rule
Rule -> Noun_phrase_list Predicate_list
Noun_phrase_list -> Noun_phrase T_And Noun_phrase_list | Noun_phrase
Noun_phrase -> Adjective Noun Preposition_phrase_list
Preposition_phrase_list -> Preposition_phrase T_And Preposition_phrase_list | Preposition_phrase | epsilon
Preposition_phrase -> Preposition Noun | Preposition Property
Predicate_list -> Predicate T_And Predicate_list | Predicate
Predicate -> Verb Property_list | Verb Noun
Property_list -> Property T_And Property_list | Property
Not_list -> T_Not Not_list | epsilon
Noun -> Not_list T_Noun
Verb -> Not_list T_Verb
Property -> Not_list T_Property
Adjective -> Not_list T_Adjective | epsilon
Preposition -> Not_list T_Preposition
Condition -> Not_list T_Condition
If -> Not_list T_if
```
